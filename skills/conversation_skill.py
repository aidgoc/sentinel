#!/usr/bin/env python3
"""
Sentinel Conversation Skill - Safety Questioning Protocol
Engineer #3: LLM & Memory Architect

Implements 3-question safety workflow with SQLite RAG memory and Ollama integration.
Returns JSON to OpenClaw via STDIO.
"""

import sys
import json
import sqlite3
import os
from datetime import datetime
from pathlib import Path

try:
    import ollama
except ImportError:
    print(json.dumps({"error": "ollama-python not installed", "action": "error"}))
    sys.exit(1)

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    print(json.dumps({"error": "sentence-transformers not installed", "action": "error"}))
    sys.exit(1)


class SentinelMemory:
    """SQLite-based RAG memory with vector search"""

    def __init__(self, db_path):
        self.db_path = os.path.expanduser(db_path)
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        self.conn = sqlite3.connect(self.db_path)
        # Force CPU usage to avoid CUDA compatibility issues with MX130
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')  # 384-dim, CPU
        self._init_schema()

    def _init_schema(self):
        """Initialize database schema"""
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                role TEXT CHECK(role IN ('user', 'assistant', 'system')),
                content TEXT NOT NULL,
                embedding BLOB,
                metadata TEXT
            )
        """)

        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS agent_state (
                session_id TEXT PRIMARY KEY,
                current_step INTEGER DEFAULT 0,
                last_question TEXT,
                awaiting_reply BOOLEAN DEFAULT 0,
                context_json TEXT,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_session
            ON conversations(session_id, timestamp)
        """)

        self.conn.commit()

    def store_interaction(self, session_id, role, content, metadata=None):
        """Store conversation with vector embedding"""
        embedding = self.encoder.encode(content).tobytes()

        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO conversations (session_id, role, content, embedding, metadata)
            VALUES (?, ?, ?, ?, ?)
        """, (session_id, role, content, embedding, json.dumps(metadata) if metadata else None))

        self.conn.commit()
        return cursor.lastrowid

    def get_state(self, session_id):
        """Retrieve conversation state"""
        row = self.conn.execute(
            "SELECT current_step, last_question, awaiting_reply, context_json FROM agent_state WHERE session_id = ?",
            (session_id,)
        ).fetchone()

        if not row:
            return {"step": 0, "last_question": None, "awaiting": False, "context": {}}

        return {
            "step": row[0],
            "last_question": row[1],
            "awaiting": bool(row[2]),
            "context": json.loads(row[3]) if row[3] else {}
        }

    def update_state(self, session_id, step=None, question=None, awaiting=None, context=None):
        """Update conversation state"""
        state = self.get_state(session_id)

        if step is not None:
            state["step"] = step
        if question is not None:
            state["last_question"] = question
        if awaiting is not None:
            state["awaiting"] = awaiting
        if context is not None:
            state["context"].update(context)

        self.conn.execute("""
            INSERT INTO agent_state (session_id, current_step, last_question, awaiting_reply, context_json, updated_at)
            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(session_id) DO UPDATE SET
                current_step = excluded.current_step,
                last_question = excluded.last_question,
                awaiting_reply = excluded.awaiting_reply,
                context_json = excluded.context_json,
                updated_at = CURRENT_TIMESTAMP
        """, (session_id, state["step"], state["last_question"], state["awaiting"], json.dumps(state["context"])))

        self.conn.commit()

    def retrieve_context(self, session_id, limit=5):
        """Retrieve recent conversation history"""
        rows = self.conn.execute("""
            SELECT role, content, metadata, timestamp
            FROM conversations
            WHERE session_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (session_id, limit)).fetchall()

        return [{"role": r[0], "content": r[1], "metadata": json.loads(r[2]) if r[2] else None, "timestamp": r[3]} for r in rows]


class ConversationSkill:
    """Safety questioning protocol with state management"""

    QUESTIONS = [
        {
            "id": "task_identification",
            "text": "What task are you performing?",
            "type": "open_ended",
            "required": True
        },
        {
            "id": "safety_confirmation",
            "text": "Are safety protocols confirmed?",
            "type": "boolean",
            "required": True
        },
        {
            "id": "tool_requirements",
            "text": "Do you require tool access?",
            "type": "conditional",
            "required": False
        }
    ]

    def __init__(self, config=None):
        self.config = config or {}

        # LLM configuration
        self.ollama_host = self.config.get("ollama_host", "http://127.0.0.1:11434")
        self.model = self.config.get("model", "qwen2.5:3b")
        self.temperature = self.config.get("temperature", 0.7)

        # Memory
        db_path = self.config.get("db_path", "~/.openclaw-sentinel/sentinel_memory.db")
        self.memory = SentinelMemory(db_path)

    def query_llm(self, prompt, context_history=None):
        """Query Ollama local LLM"""
        messages = []

        # Add system prompt
        messages.append({
            "role": "system",
            "content": "You are Sentinel, a safety monitoring assistant. Ask clear questions and record responses."
        })

        # Add conversation history
        if context_history:
            for msg in reversed(context_history):  # Reverse to chronological order
                messages.append({"role": msg["role"], "content": msg["content"]})

        # Add current prompt
        messages.append({"role": "user", "content": prompt})

        try:
            response = ollama.chat(
                model=self.model,
                messages=messages,
                options={"temperature": self.temperature}
            )
            return response["message"]["content"], None
        except Exception as e:
            return None, str(e)

    def execute(self, context=None):
        """Main execution: manage conversation state and questioning"""
        context = context or {}

        session_id = context.get("session_id", f"session_{datetime.now().timestamp()}")
        user_input = context.get("user_input")
        trigger_conversation = context.get("trigger_conversation", False)

        # Get current state
        state = self.memory.get_state(session_id)

        # If not triggered and no active conversation, skip
        if not trigger_conversation and state["step"] == 0:
            return {
                "action": "idle",
                "session_id": session_id,
                "message": "No conversation active"
            }

        # If awaiting reply, process user input
        if state["awaiting"] and user_input:
            # Store user's reply
            self.memory.store_interaction(
                session_id,
                "user",
                user_input,
                metadata={"question_id": self.QUESTIONS[state["step"] - 1]["id"]}
            )

            # Update state: not awaiting, move to next step
            self.memory.update_state(
                session_id,
                step=state["step"],
                awaiting=False,
                context={"last_reply": user_input}
            )

            state = self.memory.get_state(session_id)

        # Check if conversation complete
        if state["step"] >= len(self.QUESTIONS):
            # Generate summary
            history = self.memory.retrieve_context(session_id, limit=10)

            return {
                "action": "complete",
                "session_id": session_id,
                "summary": f"Completed safety check with {len(history)} interactions",
                "message": "Conversation completed. Returning to monitoring."
            }

        # Get next question
        current_question = self.QUESTIONS[state["step"]]

        # Check if conditional question should be skipped
        if current_question["type"] == "conditional":
            # Check if previous answer indicates need for this question
            last_reply = state["context"].get("last_reply", "").lower()
            if "maintenance" not in last_reply and "tool" not in last_reply:
                # Skip this question
                self.memory.update_state(
                    session_id,
                    step=state["step"] + 1,
                    awaiting=False
                )
                return self.execute(context)  # Recurse to next question

        # Store question
        self.memory.store_interaction(
            session_id,
            "assistant",
            current_question["text"],
            metadata={"question_id": current_question["id"]}
        )

        # Update state: awaiting reply, increment step
        self.memory.update_state(
            session_id,
            step=state["step"] + 1,
            question=current_question["text"],
            awaiting=True
        )

        return {
            "action": "ask",
            "session_id": session_id,
            "question": current_question["text"],
            "question_type": current_question["type"],
            "required": current_question["required"],
            "step": state["step"] + 1,
            "total_steps": len(self.QUESTIONS)
        }


def main():
    """STDIO interface for OpenClaw"""
    # Read context from stdin
    try:
        if not sys.stdin.isatty():
            context = json.load(sys.stdin)
        else:
            context = {}
    except json.JSONDecodeError:
        context = {}

    # Load configuration
    config = {
        "ollama_host": context.get("ollama_host", "http://127.0.0.1:11434"),
        "model": context.get("model", "qwen2.5:3b"),
        "temperature": context.get("temperature", 0.7),
        "db_path": context.get("db_path", "~/.openclaw-sentinel/sentinel_memory.db"),
    }

    # Execute conversation skill
    try:
        skill = ConversationSkill(config)
        result = skill.execute(context)
        print(json.dumps(result))
    except Exception as e:
        print(json.dumps({
            "action": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }))
        sys.exit(1)


if __name__ == "__main__":
    main()
