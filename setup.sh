#!/bin/bash
# MLE-Bench Technique Tasks Setup Script
# This script sets up the environment for running technique-tasks demos

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_step() {
    echo -e "${BLUE}==>${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# -----------------------------------------------------------------------------
# 1. Check Python version
# -----------------------------------------------------------------------------
print_step "Checking Python version..."

PYTHON_CMD=""
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    print_error "Python not found. Please install Python 3.9 or higher."
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
PYTHON_MAJOR=$($PYTHON_CMD -c 'import sys; print(sys.version_info.major)')
PYTHON_MINOR=$($PYTHON_CMD -c 'import sys; print(sys.version_info.minor)')

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 9 ]); then
    print_error "Python 3.9+ required. Found: $PYTHON_VERSION"
    exit 1
fi
print_success "Python $PYTHON_VERSION found"

# -----------------------------------------------------------------------------
# 2. Check Docker (and detect Colima)
# -----------------------------------------------------------------------------
print_step "Checking Docker..."

# Auto-detect Colima socket if DOCKER_HOST not set
if [ -z "$DOCKER_HOST" ]; then
    COLIMA_SOCKET="$HOME/.colima/default/docker.sock"
    if [ -S "$COLIMA_SOCKET" ]; then
        export DOCKER_HOST="unix://$COLIMA_SOCKET"
        print_success "Detected Colima socket: $DOCKER_HOST"
    fi
fi

if ! command -v docker &> /dev/null; then
    print_error "Docker not found. Please install Docker Desktop or Colima."
    exit 1
fi

if ! docker info &> /dev/null; then
    print_error "Docker is not running. Please start Docker Desktop or run 'colima start'."
    exit 1
fi
print_success "Docker is running"

# -----------------------------------------------------------------------------
# 3. Create/activate environment (Conda or venv)
# -----------------------------------------------------------------------------
print_step "Setting up Python environment..."

ENV_NAME="mlebench-env"
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

if command -v conda &> /dev/null; then
    # Use Conda
    print_step "Conda detected, creating conda environment..."
    
    if conda env list | grep -q "^${ENV_NAME} "; then
        print_warning "Conda environment '$ENV_NAME' already exists. Activating..."
    else
        conda create -n "$ENV_NAME" python=3.11 -y
        print_success "Conda environment '$ENV_NAME' created"
    fi
    
    # Activate conda environment
    eval "$(conda shell.bash hook)"
    conda activate "$ENV_NAME"
    print_success "Conda environment activated"
    
    PYTHON_CMD="python"
else
    # Use venv
    print_step "Conda not found, using Python venv..."
    
    VENV_DIR="$SCRIPT_DIR/.venv"
    
    if [ -d "$VENV_DIR" ]; then
        print_warning "Virtual environment already exists. Activating..."
    else
        $PYTHON_CMD -m venv "$VENV_DIR"
        print_success "Virtual environment created at $VENV_DIR"
    fi
    
    source "$VENV_DIR/bin/activate"
    print_success "Virtual environment activated"
    
    PYTHON_CMD="python"
fi

# -----------------------------------------------------------------------------
# 4. Install dependencies
# -----------------------------------------------------------------------------
print_step "Installing Python dependencies..."

cd "$SCRIPT_DIR"

# Upgrade pip
$PYTHON_CMD -m pip install --upgrade pip -q

# Install the package in editable mode
$PYTHON_CMD -m pip install -e . -q

# Install additional server dependencies
$PYTHON_CMD -m pip install fastapi uvicorn python-dotenv requests -q

print_success "Dependencies installed"

# -----------------------------------------------------------------------------
# 5. Pull Docker images
# -----------------------------------------------------------------------------
print_step "Pulling Docker images..."
echo ""
echo -e "    ${YELLOW}⚠ First-time download is ~12GB per image and may take 10-30 minutes.${NC}"
echo -e "    ${YELLOW}  Go grab a coffee ☕${NC}"
echo ""

# Check if images exist locally first
if docker images | grep -q "mlebench-env"; then
    print_warning "mlebench-env image already exists locally"
else
    # Try to pull from registry, fall back to local build
    if docker pull ghcr.io/sanket-so-fleet/mle-bench-ss/mlebench-env:latest 2>/dev/null; then
        docker tag ghcr.io/sanket-so-fleet/mle-bench-ss/mlebench-env:latest mlebench-env
        print_success "Pulled mlebench-env from registry"
    else
        print_warning "Could not pull from registry. Building locally (this takes even longer)..."
        docker build -t mlebench-env -f environment/Dockerfile environment/
        print_success "Built mlebench-env locally"
    fi
fi

if docker images | grep -q "^aide "; then
    print_warning "aide image already exists locally"
else
    # Try to pull from registry, fall back to local build
    if docker pull ghcr.io/sanket-so-fleet/mle-bench-ss/aide:latest 2>/dev/null; then
        docker tag ghcr.io/sanket-so-fleet/mle-bench-ss/aide:latest aide
        print_success "Pulled aide from registry"
    else
        print_warning "Could not pull from registry. Building locally (this takes even longer)..."
        docker build -t aide -f agents/aide/Dockerfile agents/aide/
        print_success "Built aide locally"
    fi
fi

# -----------------------------------------------------------------------------
# 6. Check .env file
# -----------------------------------------------------------------------------
print_step "Checking environment configuration..."

ENV_FILE="$SCRIPT_DIR/.env"

if [ ! -f "$ENV_FILE" ]; then
    echo "OPENAI_API_KEY=sk-your-key-here" > "$ENV_FILE"
    print_warning "Created .env file. Please edit it and add your OpenAI API key."
    echo ""
    echo "    Edit .env and replace 'sk-your-key-here' with your actual API key:"
    echo "    ${BLUE}nano .env${NC}"
    echo ""
    ENV_NEEDS_UPDATE=true
else
    if grep -q "sk-your-key-here" "$ENV_FILE" || ! grep -q "OPENAI_API_KEY" "$ENV_FILE"; then
        print_warning ".env exists but OPENAI_API_KEY may not be set correctly."
        ENV_NEEDS_UPDATE=true
    else
        print_success ".env file configured"
        ENV_NEEDS_UPDATE=false
    fi
fi

# Add DOCKER_HOST to .env if Colima detected and not already set
if [ -n "$DOCKER_HOST" ] && [[ "$DOCKER_HOST" == *"colima"* ]]; then
    if ! grep -q "DOCKER_HOST" "$ENV_FILE"; then
        echo "DOCKER_HOST=$DOCKER_HOST" >> "$ENV_FILE"
        print_success "Added DOCKER_HOST to .env for Colima"
    fi
fi

# -----------------------------------------------------------------------------
# 7. Check Kaggle credentials (required for data download)
# -----------------------------------------------------------------------------
print_step "Checking Kaggle credentials..."

KAGGLE_DIR="$HOME/.kaggle"
KAGGLE_JSON="$KAGGLE_DIR/kaggle.json"

if [ -f "$KAGGLE_JSON" ]; then
    print_success "Kaggle credentials found"
else
    print_error "Kaggle credentials not found at ~/.kaggle/kaggle.json"
    echo ""
    echo "    Kaggle credentials are required to download competition data."
    echo ""
    echo "    To set up Kaggle API credentials:"
    echo "    1. Go to https://www.kaggle.com/settings"
    echo "    2. Click 'Create New Token' under API section"
    echo "    3. Move the downloaded kaggle.json to ~/.kaggle/"
    echo "    4. Run: chmod 600 ~/.kaggle/kaggle.json"
    echo ""
    echo "    Then re-run this script."
    exit 1
fi

# -----------------------------------------------------------------------------
# Done!
# -----------------------------------------------------------------------------
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Setup complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

if [ "$ENV_NEEDS_UPDATE" = true ]; then
    echo -e "${YELLOW}Before running, make sure to:${NC}"
    echo "  1. Add your OpenAI API key to .env"
    echo ""
fi

# If using Colima, remind user to set DOCKER_HOST
if [ -n "$DOCKER_HOST" ] && [[ "$DOCKER_HOST" == *"colima"* ]]; then
    echo -e "${YELLOW}Colima detected. Add this to your shell profile (.zshrc or .bashrc):${NC}"
    echo "  export DOCKER_HOST=\"$DOCKER_HOST\""
    echo ""
fi

echo "To start the demo:"
echo ""
if command -v conda &> /dev/null; then
    echo "  1. Activate environment:  ${BLUE}conda activate $ENV_NAME${NC}"
else
    echo "  1. Activate environment:  ${BLUE}source .venv/bin/activate${NC}"
fi
echo "  2. Open demo.ipynb in VS Code or Jupyter"
echo ""
echo "Note: The server must be started separately in its own terminal. See RUN_DEMO.md for instructions."
echo ""
echo "Happy experimenting! 🚀"
