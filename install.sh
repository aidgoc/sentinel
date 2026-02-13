#!/bin/bash
#
# Sentinel V8 - Automated Installation Script
# Privacy-First AI Assistant with Voice & Vision
#
# Usage: curl -fsSL https://raw.githubusercontent.com/aidgoc/sentinel/master/install.sh | bash
# Or: git clone https://github.com/aidgoc/sentinel && cd sentinel && ./install.sh
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SENTINEL_HOME="${HOME}/sentinel"
VENV_PATH="${SENTINEL_HOME}/.venv"
PYTHON_MIN_VERSION="3.11"

# Helper functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Print banner
print_banner() {
    clear
    echo -e "${BLUE}"
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║                                                            ║"
    echo "║               🛡️  SENTINEL V8 INSTALLER                    ║"
    echo "║                                                            ║"
    echo "║        Privacy-First AI Assistant with Voice & Vision     ║"
    echo "║                                                            ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo -e "${NC}\n"
}

# Check system requirements
check_requirements() {
    log_info "Checking system requirements..."

    # Check OS
    if [[ "$OSTYPE" != "linux-gnu"* ]]; then
        log_error "This installer only supports Linux. Detected: $OSTYPE"
        exit 1
    fi
    log_success "OS: Linux ✓"

    # Check Python version
    if ! command_exists python3; then
        log_error "Python 3 is not installed. Please install Python 3.11+ first."
        exit 1
    fi

    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    log_success "Python version: $PYTHON_VERSION ✓"

    # Check pip
    if ! command_exists pip3 && ! python3 -m pip --version &>/dev/null; then
        log_error "pip is not installed. Please install python3-pip first."
        exit 1
    fi
    log_success "pip available ✓"

    # Check git
    if ! command_exists git; then
        log_error "git is not installed. Please install git first."
        exit 1
    fi
    log_success "git available ✓"

    # Check for optional dependencies
    if command_exists ffmpeg; then
        log_success "ffmpeg available ✓ (audio processing enabled)"
    else
        log_warning "ffmpeg not found (audio features may be limited)"
        echo "  Install: sudo apt install ffmpeg"
    fi

    if command_exists v4l2-ctl; then
        log_success "v4l-utils available ✓ (camera support enabled)"
    else
        log_warning "v4l-utils not found (camera features may be limited)"
        echo "  Install: sudo apt install v4l-utils"
    fi

    echo ""
}

# Install system dependencies
install_system_deps() {
    log_info "Checking system dependencies..."

    local missing_deps=()

    # Check for required packages
    dpkg -s portaudio19-dev &>/dev/null || missing_deps+=("portaudio19-dev")
    dpkg -s python3-dev &>/dev/null || missing_deps+=("python3-dev")
    dpkg -s python3-venv &>/dev/null || missing_deps+=("python3-venv")
    dpkg -s build-essential &>/dev/null || missing_deps+=("build-essential")

    if [ ${#missing_deps[@]} -eq 0 ]; then
        log_success "All system dependencies installed ✓"
        return 0
    fi

    log_warning "Missing system dependencies: ${missing_deps[*]}"

    if [ "$EUID" -eq 0 ]; then
        log_info "Installing system dependencies..."
        apt-get update -qq
        apt-get install -y "${missing_deps[@]}"
        log_success "System dependencies installed ✓"
    else
        log_warning "Please install manually or run with sudo:"
        echo "  sudo apt-get update"
        echo "  sudo apt-get install -y ${missing_deps[*]}"
        read -p "Continue anyway? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

# Setup directory structure
setup_directories() {
    log_info "Setting up directories..."

    # Create main directory if not exists
    if [ ! -d "$SENTINEL_HOME" ]; then
        mkdir -p "$SENTINEL_HOME"
        log_success "Created directory: $SENTINEL_HOME"
    fi

    # Create subdirectories
    mkdir -p "${SENTINEL_HOME}/logs"
    mkdir -p "${SENTINEL_HOME}/models"
    mkdir -p "${SENTINEL_HOME}/config"
    mkdir -p "${HOME}/sentinel_captures"
    mkdir -p "${HOME}/.openclaw-sentinel"

    log_success "Directory structure created ✓"
}

# Install Ollama
install_ollama() {
    log_info "Checking Ollama installation..."

    if command_exists ollama; then
        log_success "Ollama already installed ✓"
    else
        log_info "Installing Ollama..."
        curl -fsSL https://ollama.ai/install.sh | sh
        log_success "Ollama installed ✓"
    fi

    # Start Ollama service
    if systemctl is-active --quiet ollama; then
        log_success "Ollama service running ✓"
    else
        log_info "Starting Ollama service..."
        if [ "$EUID" -eq 0 ]; then
            systemctl start ollama
        else
            sudo systemctl start ollama 2>/dev/null || {
                log_warning "Could not start Ollama service. Starting manually..."
                nohup ollama serve > /dev/null 2>&1 &
                sleep 2
            }
        fi
        log_success "Ollama started ✓"
    fi

    # Download required model
    log_info "Downloading LLM model (qwen2.5:3b - ~1.9GB)..."
    if ollama list | grep -q "qwen2.5:3b"; then
        log_success "Model qwen2.5:3b already available ✓"
    else
        ollama pull qwen2.5:3b
        log_success "Model downloaded ✓"
    fi
}

# Setup Python virtual environment
setup_venv() {
    log_info "Setting up Python virtual environment..."

    cd "$SENTINEL_HOME"

    if [ -d "$VENV_PATH" ]; then
        log_warning "Virtual environment already exists. Removing old one..."
        rm -rf "$VENV_PATH"
    fi

    python3 -m venv "$VENV_PATH"
    source "${VENV_PATH}/bin/activate"

    log_info "Upgrading pip..."
    pip install --upgrade pip setuptools wheel -q

    log_success "Virtual environment created ✓"
}

# Install Python dependencies
install_python_deps() {
    log_info "Installing Python dependencies (this may take a few minutes)..."

    cd "$SENTINEL_HOME"
    source "${VENV_PATH}/bin/activate"

    # Install from requirements.txt
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt -q
    else
        # Install core dependencies
        log_info "Installing core packages..."
        pip install -q \
            ollama \
            openai-whisper \
            piper-tts \
            python-telegram-bot \
            onnxruntime \
            sentence-transformers \
            opencv-python \
            numpy \
            sounddevice \
            soundfile \
            psutil \
            pyyaml
    fi

    log_success "Python dependencies installed ✓"
}

# Download models
download_models() {
    log_info "Downloading AI models..."

    cd "$SENTINEL_HOME"

    # Download YOLO model
    if [ ! -f "models/yolov8n.onnx" ]; then
        log_info "Downloading YOLOv8-nano model (~6MB)..."
        curl -L -o "models/yolov8n.onnx" \
            "https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.onnx" \
            2>/dev/null
        log_success "YOLO model downloaded ✓"
    else
        log_success "YOLO model already exists ✓"
    fi

    # Download Piper voice model
    PIPER_DIR="${HOME}/.local/share/piper"
    mkdir -p "$PIPER_DIR"

    if [ ! -f "${PIPER_DIR}/en_US-lessac-medium.onnx" ]; then
        log_info "Downloading Piper TTS voice (~61MB)..."
        curl -L -o "${PIPER_DIR}/en_US-lessac-medium.onnx" \
            "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx" \
            2>/dev/null
        curl -L -o "${PIPER_DIR}/en_US-lessac-medium.onnx.json" \
            "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json" \
            2>/dev/null
        log_success "Piper voice downloaded ✓"
    else
        log_success "Piper voice already exists ✓"
    fi
}

# Setup configuration
setup_config() {
    log_info "Setting up configuration..."

    cd "$SENTINEL_HOME"

    # Create .env template if not exists
    if [ ! -f ".env" ]; then
        cat > .env << 'EOF'
# Sentinel Environment Variables
# IMPORTANT: Add your tokens here

# Required for Telegram bot
TELEGRAM_BOT_TOKEN=your_bot_token_here

# Optional: Cloud LLM fallback
# ANTHROPIC_API_KEY=your_api_key_here
EOF
        chmod 600 .env
        log_success "Created .env template ✓"
        log_warning "Please edit .env and add your TELEGRAM_BOT_TOKEN"
    else
        log_success "Configuration file exists ✓"
    fi

    # Ensure .env is in .gitignore
    if [ -f ".gitignore" ]; then
        grep -q "^.env$" .gitignore || echo ".env" >> .gitignore
    fi
}

# Setup local-talking-llm dependency
setup_talking_llm() {
    log_info "Setting up voice chat dependencies..."

    if [ -d "${HOME}/local-talking-llm" ]; then
        log_success "local-talking-llm already exists ✓"
    else
        log_info "Cloning local-talking-llm..."
        cd "${HOME}"
        git clone https://github.com/remixer-dec/local-talking-llm.git -q 2>/dev/null || {
            log_warning "Could not clone local-talking-llm (voice chat may be limited)"
            return 0
        }
        log_success "local-talking-llm cloned ✓"
    fi
}

# Create startup scripts
create_scripts() {
    log_info "Creating startup scripts..."

    cd "$SENTINEL_HOME"

    # Ensure scripts are executable
    chmod +x cli 2>/dev/null || true
    chmod +x start_bot.sh 2>/dev/null || true
    chmod +x sentinel_cli.py 2>/dev/null || true

    log_success "Startup scripts ready ✓"
}

# Run tests
run_tests() {
    log_info "Running system tests..."

    cd "$SENTINEL_HOME"
    source "${VENV_PATH}/bin/activate"

    # Test Ollama
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        log_success "Ollama connection: ✓"
    else
        log_warning "Ollama not responding (may need manual start)"
    fi

    # Test Python imports
    python3 -c "import ollama; import whisper; import cv2; import sentence_transformers" 2>/dev/null && \
        log_success "Python dependencies: ✓" || \
        log_warning "Some Python dependencies may be missing"

    # Test models
    [ -f "models/yolov8n.onnx" ] && log_success "YOLO model: ✓" || log_warning "YOLO model missing"
    [ -f "${HOME}/.local/share/piper/en_US-lessac-medium.onnx" ] && log_success "Piper voice: ✓" || log_warning "Piper voice missing"

    echo ""
}

# Print installation summary
print_summary() {
    echo -e "${GREEN}"
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║                                                            ║"
    echo "║           ✅  SENTINEL V8 INSTALLED SUCCESSFULLY            ║"
    echo "║                                                            ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo -e "${NC}\n"

    echo -e "${BLUE}📋 NEXT STEPS:${NC}\n"

    echo "1. Configure your Telegram bot token:"
    echo -e "   ${YELLOW}nano ~/sentinel/.env${NC}"
    echo ""

    echo "2. Start the local CLI:"
    echo -e "   ${YELLOW}cd ~/sentinel && ./cli${NC}"
    echo ""

    echo "3. Start the Telegram bot:"
    echo -e "   ${YELLOW}cd ~/sentinel && ./start_bot.sh${NC}"
    echo ""

    echo "4. Test the installation:"
    echo -e "   ${YELLOW}cd ~/sentinel && ./cli${NC}"
    echo "   Then select option 4 (System Status)"
    echo ""

    echo -e "${BLUE}📚 DOCUMENTATION:${NC}"
    echo "   • README: ~/sentinel/README.md"
    echo "   • Voice Guide: ~/sentinel/VOICE_TELEGRAM_GUIDE.md"
    echo "   • Quick Start: ~/sentinel/QUICK_START.md"
    echo ""

    echo -e "${BLUE}🔧 SUPPORT:${NC}"
    echo "   • GitHub: https://github.com/aidgoc/sentinel"
    echo "   • Issues: https://github.com/aidgoc/sentinel/issues"
    echo ""

    echo -e "${GREEN}Happy hacking! 🛡️${NC}\n"
}

# Main installation flow
main() {
    print_banner

    log_info "Starting Sentinel V8 installation...\n"

    check_requirements
    install_system_deps
    setup_directories
    install_ollama
    setup_venv
    install_python_deps
    download_models
    setup_talking_llm
    setup_config
    create_scripts
    run_tests

    echo ""
    print_summary
}

# Run main installation
main "$@"
