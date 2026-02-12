#!/bin/bash
# Sentinel Installation Script - Week 1 Setup
# Installs dependencies, downloads models, configures system

set -e

echo "🛡️ Sentinel Installation Script"
echo "================================"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running on Linux
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    echo -e "${RED}Error: This script requires Linux${NC}"
    exit 1
fi

# Check Python version
echo -e "${YELLOW}[1/8] Checking Python version...${NC}"
if ! command -v python3.11 &> /dev/null; then
    echo -e "${RED}Python 3.11+ required. Install: sudo apt install python3.11${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python 3.11 found${NC}"

# Check Ollama
echo -e "${YELLOW}[2/8] Checking Ollama...${NC}"
if ! command -v ollama &> /dev/null; then
    echo -e "${YELLOW}Ollama not found. Installing...${NC}"
    curl -fsSL https://ollama.ai/install.sh | sh
fi

if ! curl -s http://localhost:11434/api/tags &> /dev/null; then
    echo -e "${YELLOW}Starting Ollama service...${NC}"
    ollama serve &> /dev/null &
    sleep 3
fi
echo -e "${GREEN}✓ Ollama running${NC}"

# Check OpenClaw
echo -e "${YELLOW}[3/8] Checking OpenClaw...${NC}"
if ! command -v openclaw &> /dev/null; then
    echo -e "${YELLOW}OpenClaw not found. Installing via npm...${NC}"
    npm install -g openclaw
fi
echo -e "${GREEN}✓ OpenClaw installed${NC}"

# Create Python virtual environment
echo -e "${YELLOW}[4/8] Setting up Python environment...${NC}"
cd ~/sentinel
python3.11 -m venv .venv
source .venv/bin/activate

# Install Python dependencies
echo -e "${YELLOW}[5/8] Installing Python packages...${NC}"
pip install --upgrade pip
pip install \
    opencv-python \
    onnxruntime-gpu \
    numpy \
    ollama \
    sentence-transformers \
    pillow \
    pyyaml

echo -e "${GREEN}✓ Python packages installed${NC}"

# Download Ollama models
echo -e "${YELLOW}[6/8] Downloading LLM models...${NC}"
ollama pull qwen2.5:3b
ollama pull phi3:mini  # Fallback model

echo -e "${GREEN}✓ Models downloaded${NC}"

# Download YOLO model
echo -e "${YELLOW}[7/8] Downloading YOLO model...${NC}"
mkdir -p ~/sentinel/models
cd ~/sentinel/models

if [ ! -f "yolov8n.onnx" ]; then
    # Install ultralytics to export YOLO
    pip install ultralytics
    python3 << EOF
from ultralytics import YOLO
model = YOLO("yolov8n.pt")
model.export(format="onnx", dynamic=False, simplify=True)
import shutil
shutil.move("yolov8n.onnx", "/home/$USER/sentinel/models/yolov8n.onnx")
EOF
fi

echo -e "${GREEN}✓ YOLO model ready${NC}"

# Set up directories and permissions
echo -e "${YELLOW}[8/8] Configuring directories...${NC}"
mkdir -p ~/sentinel_captures
mkdir -p ~/sentinel/logs
mkdir -p ~/.openclaw-sentinel

chmod 700 ~/.openclaw-sentinel
chmod +x ~/sentinel/skills/*.py

echo -e "${GREEN}✓ Directories configured${NC}"

# Create systemd service
echo -e "${YELLOW}Creating systemd service...${NC}"
sudo tee /etc/systemd/system/sentinel.service > /dev/null << EOF
[Unit]
Description=Sentinel Ambient Intelligence Agent
After=network.target ollama.service

[Service]
Type=simple
User=$USER
WorkingDirectory=/home/$USER/sentinel
Environment="PATH=/home/$USER/sentinel/.venv/bin:/usr/bin"
Environment="TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}"
Environment="ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}"

# Resource limits (12GB system)
MemoryMax=10G
CPUQuota=80%

# Security
NoNewPrivileges=yes
PrivateTmp=yes
ProtectSystem=strict
ProtectHome=read-only
ReadWritePaths=/home/$USER/sentinel /home/$USER/sentinel_captures /home/$USER/.openclaw-sentinel

ExecStart=/home/$USER/sentinel/scripts/run_sentinel.sh
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

echo -e "${GREEN}✓ Systemd service created${NC}"

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ Sentinel Installation Complete!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "Next steps:"
echo "1. Set environment variables:"
echo "   export TELEGRAM_BOT_TOKEN='your_token'"
echo "   export ANTHROPIC_API_KEY='your_key'"
echo ""
echo "2. Test vision skill:"
echo "   source ~/sentinel/.venv/bin/activate"
echo "   python3 ~/sentinel/skills/vision_skill.py"
echo ""
echo "3. Start Sentinel:"
echo "   sudo systemctl enable sentinel"
echo "   sudo systemctl start sentinel"
echo ""
echo "4. View logs:"
echo "   journalctl -u sentinel -f"
echo ""
