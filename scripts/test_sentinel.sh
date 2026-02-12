#!/bin/bash
# Sentinel Integration Tests - Week 1 Validation

set -e

SENTINEL_HOME="$HOME/sentinel"
VENV="$SENTINEL_HOME/.venv"

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "🧪 Sentinel Integration Tests"
echo "=============================="

source "$VENV/bin/activate"

# Test 1: Vision Skill Execution
echo -e "\n${YELLOW}Test 1: Vision Skill${NC}"
VISION_OUTPUT=$(python3 "$SENTINEL_HOME/skills/vision_skill.py" 2>&1)
if echo "$VISION_OUTPUT" | jq -e '.timestamp' > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Vision skill executed successfully${NC}"
    echo "  Output: $(echo $VISION_OUTPUT | jq -c .)"
else
    echo -e "${RED}✗ Vision skill failed${NC}"
    echo "  Error: $VISION_OUTPUT"
    exit 1
fi

# Test 2: Conversation Skill Execution
echo -e "\n${YELLOW}Test 2: Conversation Skill${NC}"
CONV_INPUT='{"session_id":"test_session","trigger_conversation":true}'
CONV_OUTPUT=$(echo "$CONV_INPUT" | python3 "$SENTINEL_HOME/skills/conversation_skill.py" 2>&1)
if echo "$CONV_OUTPUT" | jq -e '.action' > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Conversation skill executed successfully${NC}"
    echo "  Output: $(echo $CONV_OUTPUT | jq -c .)"
else
    echo -e "${RED}✗ Conversation skill failed${NC}"
    echo "  Error: $CONV_OUTPUT"
    exit 1
fi

# Test 3: Ollama Connectivity
echo -e "\n${YELLOW}Test 3: Ollama Connection${NC}"
if curl -s http://localhost:11434/api/tags > /dev/null; then
    echo -e "${GREEN}✓ Ollama is running${NC}"

    # Check for qwen2.5:3b
    if curl -s http://localhost:11434/api/tags | jq -e '.models[] | select(.name == "qwen2.5:3b")' > /dev/null; then
        echo -e "${GREEN}✓ qwen2.5:3b model available${NC}"
    else
        echo -e "${YELLOW}⚠ qwen2.5:3b not found. Run: ollama pull qwen2.5:3b${NC}"
    fi
else
    echo -e "${RED}✗ Ollama not running${NC}"
    exit 1
fi

# Test 4: YOLO Model Availability
echo -e "\n${YELLOW}Test 4: YOLO Model${NC}"
if [ -f "$SENTINEL_HOME/models/yolov8n.onnx" ]; then
    echo -e "${GREEN}✓ YOLO model found${NC}"
    ls -lh "$SENTINEL_HOME/models/yolov8n.onnx"
else
    echo -e "${RED}✗ YOLO model missing${NC}"
    echo "  Run install.sh to download"
    exit 1
fi

# Test 5: CUDA Availability (MX130)
echo -e "\n${YELLOW}Test 5: GPU Detection${NC}"
if python3 -c "import torch; print('CUDA:', torch.cuda.is_available())" | grep "True" > /dev/null; then
    echo -e "${GREEN}✓ CUDA available (MX130 detected)${NC}"
    python3 -c "import torch; print(f'  Device: {torch.cuda.get_device_name(0)}')"
    python3 -c "import torch; print(f'  VRAM: {torch.cuda.get_device_properties(0).total_memory/1e9:.1f}GB')"
else
    echo -e "${YELLOW}⚠ CUDA not available (CPU fallback)${NC}"
fi

# Test 6: Storage Directory
echo -e "\n${YELLOW}Test 6: Storage Configuration${NC}"
if [ -d "$HOME/sentinel_captures" ]; then
    echo -e "${GREEN}✓ Capture directory exists${NC}"
    echo "  Path: $HOME/sentinel_captures"
    echo "  Permissions: $(stat -c '%A' $HOME/sentinel_captures)"
else
    echo -e "${RED}✗ Capture directory missing${NC}"
    mkdir -p "$HOME/sentinel_captures"
    echo -e "${GREEN}  Created: $HOME/sentinel_captures${NC}"
fi

# Test 7: SQLite Database
echo -e "\n${YELLOW}Test 7: Memory Database${NC}"
DB_PATH="$HOME/.openclaw-sentinel/sentinel_memory.db"
if python3 -c "import sqlite3; conn = sqlite3.connect('$DB_PATH'); print('OK')"; then
    echo -e "${GREEN}✓ SQLite database accessible${NC}"
    echo "  Path: $DB_PATH"
else
    echo -e "${RED}✗ Database initialization failed${NC}"
    exit 1
fi

# Test 8: Configuration File
echo -e "\n${YELLOW}Test 8: Configuration${NC}"
if [ -f "$SENTINEL_HOME/config/sentinel.yaml" ]; then
    echo -e "${GREEN}✓ Configuration file exists${NC}"
    if python3 -c "import yaml; yaml.safe_load(open('$SENTINEL_HOME/config/sentinel.yaml'))"; then
        echo -e "${GREEN}✓ Configuration is valid YAML${NC}"
    else
        echo -e "${RED}✗ Configuration has syntax errors${NC}"
        exit 1
    fi
else
    echo -e "${RED}✗ Configuration file missing${NC}"
    exit 1
fi

# Summary
echo -e "\n${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ All Tests Passed!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "Sentinel is ready to deploy."
echo "Next steps:"
echo "  1. Set TELEGRAM_BOT_TOKEN environment variable"
echo "  2. Run: sudo systemctl start sentinel"
echo "  3. Monitor: journalctl -u sentinel -f"
echo ""
