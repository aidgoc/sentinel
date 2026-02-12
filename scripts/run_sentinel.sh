#!/bin/bash
# Sentinel Runtime Script - Orchestrates Vision + Conversation
# This script runs as the main Sentinel loop

set -e

SENTINEL_HOME="$HOME/sentinel"
VENV="$SENTINEL_HOME/.venv"
CONFIG="$SENTINEL_HOME/config/sentinel.yaml"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Activate virtual environment
source "$VENV/bin/activate"

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}🛡️  Sentinel Ambient Intelligence Agent${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Check dependencies
check_dependency() {
    if ! command -v $1 &> /dev/null; then
        echo -e "${RED}✗ $1 not found${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ $1${NC}"
}

echo "Checking dependencies..."
check_dependency python3
check_dependency ollama
check_dependency openclaw

# Check Ollama is running
if ! curl -s http://localhost:11434/api/tags &> /dev/null; then
    echo -e "${YELLOW}Starting Ollama...${NC}"
    ollama serve &> /dev/null &
    sleep 3
fi

# Initialize session
SESSION_ID="sentinel_$(date +%s)"
echo -e "${GREEN}Session ID: $SESSION_ID${NC}"

# Heartbeat loop
HEARTBEAT_INTERVAL=60  # seconds
LAST_CAPTURE=0

echo -e "${BLUE}Starting heartbeat loop (${HEARTBEAT_INTERVAL}s interval)...${NC}"

while true; do
    CURRENT_TIME=$(date +%s)
    TIME_SINCE_LAST=$((CURRENT_TIME - LAST_CAPTURE))

    if [ $TIME_SINCE_LAST -ge $HEARTBEAT_INTERVAL ]; then
        echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] Heartbeat: Running vision capture${NC}"

        # Run vision skill
        VISION_OUTPUT=$(python3 "$SENTINEL_HOME/skills/vision_skill.py" 2>&1)
        VISION_STATUS=$?

        if [ $VISION_STATUS -ne 0 ]; then
            echo -e "${RED}Vision skill failed: $VISION_OUTPUT${NC}"
            sleep 10
            continue
        fi

        # Parse vision output
        PERSON_PRESENT=$(echo "$VISION_OUTPUT" | jq -r '.person_present // false')
        CONFIDENCE=$(echo "$VISION_OUTPUT" | jq -r '.confidence // 0')
        IMAGE_PATH=$(echo "$VISION_OUTPUT" | jq -r '.image_path // "unknown"')

        echo -e "${GREEN}Vision: person_present=$PERSON_PRESENT, confidence=$CONFIDENCE${NC}"

        # If person detected, trigger conversation
        if [ "$PERSON_PRESENT" = "true" ]; then
            echo -e "${BLUE}━━━ Person Detected - Starting Safety Protocol ━━━${NC}"

            # Run conversation skill
            CONV_INPUT=$(jq -n \
                --arg sid "$SESSION_ID" \
                --argjson trigger true \
                '{session_id: $sid, trigger_conversation: $trigger}')

            CONV_OUTPUT=$(echo "$CONV_INPUT" | python3 "$SENTINEL_HOME/skills/conversation_skill.py" 2>&1)
            CONV_STATUS=$?

            if [ $CONV_STATUS -eq 0 ]; then
                ACTION=$(echo "$CONV_OUTPUT" | jq -r '.action // "unknown"')
                QUESTION=$(echo "$CONV_OUTPUT" | jq -r '.question // ""')

                echo -e "${GREEN}Conversation: action=$ACTION${NC}"

                if [ "$ACTION" = "ask" ]; then
                    echo -e "${YELLOW}Question: $QUESTION${NC}"
                    echo -e "${YELLOW}(Waiting for Telegram reply...)${NC}"

                    # In production, this would be handled by Telegram webhook
                    # For now, simulate with manual input
                    # read -p "User reply: " USER_REPLY

                    # TODO: Integrate with Telegram bot for real-time replies
                fi
            else
                echo -e "${RED}Conversation skill failed: $CONV_OUTPUT${NC}"
            fi
        fi

        LAST_CAPTURE=$CURRENT_TIME
    fi

    # Sleep for 1 second, then check again
    sleep 1
done
