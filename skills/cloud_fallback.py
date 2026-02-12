#!/usr/bin/env python3
"""
Sentinel Cloud Fallback - Week 3: Resilience
Anthropic Claude API fallback when Ollama fails or offline
"""

import os
import sys
import json
import logging
from typing import Optional, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CloudFallback:
    """Manages fallback to Anthropic Claude when local LLM fails"""

    def __init__(self):
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        self.ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self.local_model = "qwen2.5:3b"
        self.cloud_model = "claude-3-haiku-20240307"

    def check_ollama_available(self) -> bool:
        """Check if Ollama is running and accessible"""
        try:
            import urllib.request
            import urllib.error

            req = urllib.request.Request(f"{self.ollama_host}/api/tags")
            with urllib.request.urlopen(req, timeout=5) as response:
                return response.status == 200
        except Exception as e:
            logger.warning(f"Ollama unavailable: {e}")
            return False

    def query_ollama(self, prompt: str, system_prompt: str = None) -> Optional[str]:
        """Query local Ollama LLM"""
        try:
            import ollama

            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})

            messages.append({"role": "user", "content": prompt})

            response = ollama.chat(
                model=self.local_model,
                messages=messages,
                options={"temperature": 0.7}
            )

            return response["message"]["content"]

        except Exception as e:
            logger.error(f"Ollama query failed: {e}")
            return None

    def query_anthropic(self, prompt: str, system_prompt: str = None) -> Optional[str]:
        """Query Anthropic Claude API"""
        if not self.anthropic_api_key:
            logger.error("ANTHROPIC_API_KEY not set, cannot use cloud fallback")
            return None

        try:
            import anthropic

            client = anthropic.Anthropic(api_key=self.anthropic_api_key)

            message = client.messages.create(
                model=self.cloud_model,
                max_tokens=1024,
                system=system_prompt or "You are Sentinel, a safety monitoring assistant.",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            return message.content[0].text

        except ImportError:
            logger.error("anthropic package not installed. Install: pip install anthropic")
            return None
        except Exception as e:
            logger.error(f"Anthropic query failed: {e}")
            return None

    def query_with_fallback(self, prompt: str, system_prompt: str = None, prefer_cloud: bool = False) -> Dict[str, Any]:
        """Query LLM with automatic fallback logic"""

        if prefer_cloud:
            # Try cloud first
            result = self.query_anthropic(prompt, system_prompt)
            if result:
                return {
                    "success": True,
                    "response": result,
                    "provider": "anthropic",
                    "model": self.cloud_model
                }

            # Fallback to local
            result = self.query_ollama(prompt, system_prompt)
            if result:
                return {
                    "success": True,
                    "response": result,
                    "provider": "ollama",
                    "model": self.local_model
                }

        else:
            # Try local first (default)
            if self.check_ollama_available():
                result = self.query_ollama(prompt, system_prompt)
                if result:
                    return {
                        "success": True,
                        "response": result,
                        "provider": "ollama",
                        "model": self.local_model
                    }

            # Fallback to cloud
            logger.info("Falling back to Anthropic Claude...")
            result = self.query_anthropic(prompt, system_prompt)
            if result:
                return {
                    "success": True,
                    "response": result,
                    "provider": "anthropic",
                    "model": self.cloud_model
                }

        # Both failed
        return {
            "success": False,
            "error": "Both local and cloud LLM failed",
            "response": None,
            "provider": None
        }


def main():
    """CLI interface for cloud fallback testing"""
    import argparse

    parser = argparse.ArgumentParser(description="Sentinel Cloud Fallback")
    parser.add_argument("--prompt", required=True, help="Prompt to send to LLM")
    parser.add_argument("--system", help="System prompt")
    parser.add_argument("--cloud-first", action="store_true", help="Prefer cloud over local")

    args = parser.parse_args()

    fallback = CloudFallback()
    result = fallback.query_with_fallback(
        prompt=args.prompt,
        system_prompt=args.system,
        prefer_cloud=args.cloud_first
    )

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
