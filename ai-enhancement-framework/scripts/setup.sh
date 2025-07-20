#!/bin/bash

# AI Enhancement Framework - Cross-Platform Setup Script
# This script automates the complete setup of the AI Enhancement Framework
# across macOS, Linux, and Windows (Git Bash/WSL)

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
FRAMEWORK_VERSION="1.0.0"
DOCKER_COMPOSE_VERSION="2.20.0"
PYTHON_MIN_VERSION="3.8"

# Print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Platform detection
detect_platform() {
    case "$(uname -s)" in
        Darwin*)
            echo "macos"
            ;;
        Linux*)
            if grep -q microsoft /proc/version 2>/dev/null; then
                echo "wsl"
            else
                echo "linux"
            fi
            ;;
        CYGWIN*|MINGW*|MSYS*)
            echo "windows"
            ;;
        *)
            echo "unknown"
            ;;
    esac
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check Python version
check_python_version() {
    if command_exists python3; then
        PYTHON_CMD="python3"
    elif command_exists python; then
        PYTHON_CMD="python"
    else
        print_error "Python is not installed. Please install Python $PYTHON_MIN_VERSION or later."
        exit 1
    fi
    
    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
    print_status "Found Python $PYTHON_VERSION"
    
    # Simple version check (assumes format X.Y.Z)
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
    
    if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
        print_error "Python $PYTHON_MIN_VERSION or later is required. Found $PYTHON_VERSION"
        exit 1
    fi
}

# Install Docker on macOS
install_docker_macos() {
    if command_exists docker; then
        print_status "Docker is already installed"
        return 0
    fi
    
    print_status "Installing Docker Desktop for macOS..."
    
    if command_exists brew; then
        print_status "Installing Docker via Homebrew..."
        brew install --cask docker
    else
        print_warning "Homebrew not found. Please install Docker Desktop manually from:"
        print_warning "https://docs.docker.com/desktop/mac/install/"
        read -p "Press Enter after installing Docker Desktop..."
    fi
    
    print_status "Starting Docker Desktop..."
    open /Applications/Docker.app
    
    # Wait for Docker to start
    print_status "Waiting for Docker to start..."
    while ! docker system info >/dev/null 2>&1; do
        sleep 2
        echo -n "."
    done
    echo
}

# Install Docker on Linux
install_docker_linux() {
    if command_exists docker; then
        print_status "Docker is already installed"
        return 0
    fi
    
    print_status "Installing Docker on Linux..."
    
    # Detect Linux distribution
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        DISTRO=$ID
    else
        print_error "Cannot detect Linux distribution"
        exit 1
    fi
    
    case $DISTRO in
        ubuntu|debian)
            print_status "Installing Docker on Ubuntu/Debian..."
            sudo apt-get update
            sudo apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release
            
            # Add Docker's official GPG key
            curl -fsSL https://download.docker.com/linux/$DISTRO/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
            
            # Add Docker repository
            echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/$DISTRO $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
            
            # Install Docker
            sudo apt-get update
            sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
            ;;
        fedora|centos|rhel)
            print_status "Installing Docker on RHEL/CentOS/Fedora..."
            sudo dnf install -y dnf-plugins-core
            sudo dnf config-manager --add-repo https://download.docker.com/linux/fedora/docker-ce.repo
            sudo dnf install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
            ;;
        *)
            print_error "Unsupported Linux distribution: $DISTRO"
            print_warning "Please install Docker manually: https://docs.docker.com/engine/install/"
            exit 1
            ;;
    esac
    
    # Start and enable Docker
    sudo systemctl start docker
    sudo systemctl enable docker
    
    # Add user to docker group
    sudo usermod -aG docker $USER
    print_warning "Please log out and log back in for Docker group membership to take effect"
}

# Install Docker on WSL/Windows
install_docker_windows() {
    if command_exists docker; then
        print_status "Docker is already installed"
        return 0
    fi
    
    print_warning "Docker Desktop for Windows must be installed manually"
    print_warning "Please download and install from: https://docs.docker.com/desktop/windows/install/"
    print_warning "Make sure to enable WSL 2 integration if using WSL"
    read -p "Press Enter after installing Docker Desktop..."
}

# Install Docker Compose
install_docker_compose() {
    if command_exists docker-compose || docker compose version >/dev/null 2>&1; then
        print_status "Docker Compose is already available"
        return 0
    fi
    
    print_status "Installing Docker Compose..."
    PLATFORM=$(detect_platform)
    
    case $PLATFORM in
        macos)
            if command_exists brew; then
                brew install docker-compose
            else
                # Docker Desktop includes Compose
                print_status "Docker Compose included with Docker Desktop"
            fi
            ;;
        linux)
            # Install Docker Compose
            sudo curl -L "https://github.com/docker/compose/releases/download/v$DOCKER_COMPOSE_VERSION/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
            sudo chmod +x /usr/local/bin/docker-compose
            ;;
        wsl|windows)
            print_status "Docker Compose included with Docker Desktop"
            ;;
    esac
}

# Create Python virtual environment
setup_python_environment() {
    print_status "Setting up Python virtual environment..."
    
    if [ ! -d "ai-enhancement-env" ]; then
        print_status "Creating virtual environment..."
        $PYTHON_CMD -m venv ai-enhancement-env
    fi
    
    print_status "Activating virtual environment..."
    source ai-enhancement-env/bin/activate
    
    print_status "Upgrading pip..."
    pip install --upgrade pip
    
    if [ -f "requirements.txt" ]; then
        print_status "Installing Python dependencies..."
        pip install -r requirements.txt
    fi
    
    if [ -f "requirements-dev.txt" ]; then
        print_status "Installing development dependencies..."
        pip install -r requirements-dev.txt
    fi
}

# Generate environment configuration
generate_env_config() {
    print_status "Generating environment configuration..."
    
    if [ ! -f ".env" ]; then
        cat > .env << EOF
# AI Enhancement Framework - Development Configuration
AI_FRAMEWORK_ENV=development
AI_FRAMEWORK_LOG_LEVEL=INFO
AI_FRAMEWORK_DEBUG=true

# Database Connections
AI_FRAMEWORK_REDIS_URL=redis://localhost:6379
AI_FRAMEWORK_NEO4J_URI=bolt://localhost:7687
AI_FRAMEWORK_NEO4J_USER=neo4j
AI_FRAMEWORK_NEO4J_PASSWORD=ai_framework_password
AI_FRAMEWORK_POSTGRES_URL=postgresql://ai_framework_user:ai_framework_password@localhost:5432/ai_framework
AI_FRAMEWORK_QDRANT_URL=http://localhost:6333

# Security Settings (Change in production!)
AI_FRAMEWORK_JWT_SECRET=ai_framework_development_secret_key_change_in_production
AI_FRAMEWORK_API_RATE_LIMIT=1000

# Performance Settings
AI_FRAMEWORK_MAX_WORKERS=4
AI_FRAMEWORK_TIMEOUT=30
AI_FRAMEWORK_CACHE_SIZE=256MB
AI_FRAMEWORK_MEMORY_LIMIT=2GB

# OpenAI Configuration (Optional - add your API key)
# OPENAI_API_KEY=your_openai_api_key_here
EOF
        print_success "Created .env configuration file"
    else
        print_status ".env file already exists"
    fi
}

# Setup Cursor IDE configuration
setup_cursor_config() {
    print_status "Setting up Cursor IDE configuration..."
    
    if [ ! -f ".cursorrules" ]; then
        cat > .cursorrules << 'EOF'
# AI Enhancement Framework - Cursor Configuration

ai_framework:
  version: "1.0.0"
  enabled: true
  mode: "development"

project:
  name: "ai-enhancement-framework"
  type: "python"
  complexity: "extensive"

assistant:
  task_orchestrator:
    enabled: true
    analysis_depth: "comprehensive"
    methodical_approach: true
    systematic_planning: true
  
  memory:
    enabled: true
    project_scoped: true
    cross_session_persistence: true
    auto_cleanup: true
  
  code_analysis:
    enabled: true
    real_time: true
    validation_on_save: true
    hallucination_detection: true

standards:
  code_quality:
    type_hints: "required"
    docstrings: "required"
    test_coverage: 95
    complexity_limit: 10
  
  documentation:
    auto_generate: true
    mermaid_diagrams: true
    api_documentation: true
  
  validation:
    syntax_checking: true
    security_analysis: true
    performance_analysis: true
EOF
        print_success "Created .cursorrules configuration"
    fi
    
    # Create VSCode/Cursor workspace settings
    mkdir -p .vscode
    if [ ! -f ".vscode/settings.json" ]; then
        cat > .vscode/settings.json << 'EOF'
{
  "ai.framework.enabled": true,
  "ai.framework.config_file": ".cursorrules",
  "ai.framework.auto_init": true,
  "python.defaultInterpreterPath": "./ai-enhancement-env/bin/python",
  "python.testing.pytestEnabled": true,
  "python.linting.enabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true,
    "source.fixAll": true
  }
}
EOF
        print_success "Created VSCode/Cursor workspace settings"
    fi
}

# Start Docker services
start_services() {
    print_status "Starting Docker services..."
    
    # Ensure we're in the correct directory
    cd "$(dirname "$0")/.."
    
    if [ -f "docker/docker-compose.yml" ]; then
        print_status "Starting services with docker-compose..."
        docker-compose -f docker/docker-compose.yml up -d
        
        print_status "Waiting for services to be ready..."
        sleep 10
        
        # Check service health
        print_status "Checking service health..."
        docker-compose -f docker/docker-compose.yml ps
    else
        print_error "docker-compose.yml not found in docker/ directory"
        exit 1
    fi
}

# Verify installation
verify_installation() {
    print_status "Verifying installation..."
    
    # Check Docker
    if ! docker system info >/dev/null 2>&1; then
        print_error "Docker is not running"
        return 1
    fi
    print_success "✓ Docker is running"
    
    # Check services
    if docker-compose -f docker/docker-compose.yml ps | grep -q "Up"; then
        print_success "✓ Docker services are running"
    else
        print_warning "Some Docker services may not be running"
    fi
    
    # Check Python environment
    if [ -d "ai-enhancement-env" ]; then
        print_success "✓ Python virtual environment created"
    fi
    
    # Check configuration files
    if [ -f ".env" ]; then
        print_success "✓ Environment configuration created"
    fi
    
    if [ -f ".cursorrules" ]; then
        print_success "✓ Cursor IDE configuration created"
    fi
    
    print_success "Installation verification complete!"
}

# Display usage information
show_usage() {
    echo "AI Enhancement Framework Setup Script"
    echo ""
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  --docker-only    Install only Docker and Docker Compose"
    echo "  --python-only    Setup only Python environment"
    echo "  --verify-only    Only verify existing installation"
    echo "  --help           Show this help message"
    echo ""
    echo "Default: Full installation (Docker + Python + Configuration)"
}

# Main execution
main() {
    echo "======================================"
    echo "AI Enhancement Framework Setup"
    echo "Version: $FRAMEWORK_VERSION"
    echo "======================================"
    
    PLATFORM=$(detect_platform)
    print_status "Detected platform: $PLATFORM"
    
    # Parse command line arguments
    DOCKER_ONLY=false
    PYTHON_ONLY=false
    VERIFY_ONLY=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --docker-only)
                DOCKER_ONLY=true
                shift
                ;;
            --python-only)
                PYTHON_ONLY=true
                shift
                ;;
            --verify-only)
                VERIFY_ONLY=true
                shift
                ;;
            --help)
                show_usage
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done
    
    # Verify only mode
    if [ "$VERIFY_ONLY" = true ]; then
        verify_installation
        exit 0
    fi
    
    # Docker installation
    if [ "$PYTHON_ONLY" = false ]; then
        print_status "Installing Docker..."
        case $PLATFORM in
            macos)
                install_docker_macos
                ;;
            linux)
                install_docker_linux
                ;;
            wsl|windows)
                install_docker_windows
                ;;
            *)
                print_error "Unsupported platform: $PLATFORM"
                exit 1
                ;;
        esac
        
        install_docker_compose
    fi
    
    # Python environment setup
    if [ "$DOCKER_ONLY" = false ]; then
        check_python_version
        setup_python_environment
        generate_env_config
        setup_cursor_config
    fi
    
    # Start services (full installation only)
    if [ "$DOCKER_ONLY" = false ] && [ "$PYTHON_ONLY" = false ]; then
        start_services
        verify_installation
        
        echo ""
        echo "======================================"
        print_success "Setup completed successfully!"
        echo "======================================"
        echo ""
        echo "Next steps:"
        echo "1. Activate Python environment: source ai-enhancement-env/bin/activate"
        echo "2. Start development: cursor . (or open in your preferred editor)"
        echo "3. View services: docker-compose -f docker/docker-compose.yml ps"
        echo "4. Access services:"
        echo "   - Redis: localhost:6379"
        echo "   - Neo4j: http://localhost:7474"
        echo "   - PostgreSQL: localhost:5432"
        echo "   - Qdrant: http://localhost:6333"
        echo "   - Adminer (DB admin): http://localhost:8080"
        echo ""
        echo "Configuration files created:"
        echo "- .env (environment variables)"
        echo "- .cursorrules (Cursor IDE configuration)"
        echo "- .vscode/settings.json (VSCode/Cursor settings)"
        echo ""
        print_warning "Remember to add your OpenAI API key to .env if using AI features"
    fi
}

# Execute main function
main "$@"
