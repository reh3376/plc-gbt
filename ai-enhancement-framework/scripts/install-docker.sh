#!/bin/bash

# AI Enhancement Framework - Docker Installation Helper
# Standalone script for Docker and Docker Compose installation

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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
        Darwin*) echo "macos" ;;
        Linux*)
            if grep -q microsoft /proc/version 2>/dev/null; then
                echo "wsl"
            else
                echo "linux"
            fi
            ;;
        CYGWIN*|MINGW*|MSYS*) echo "windows" ;;
        *) echo "unknown" ;;
    esac
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Install Docker on macOS
install_docker_macos() {
    print_status "Installing Docker Desktop for macOS..."
    
    if command_exists docker; then
        print_success "Docker is already installed"
        return 0
    fi
    
    if command_exists brew; then
        print_status "Installing Docker via Homebrew..."
        brew install --cask docker
        print_status "Starting Docker Desktop..."
        open /Applications/Docker.app
    else
        print_warning "Homebrew not found."
        print_status "Please install Docker Desktop manually:"
        print_status "1. Download from: https://docs.docker.com/desktop/mac/install/"
        print_status "2. Install the .dmg file"
        print_status "3. Start Docker Desktop from Applications"
        read -p "Press Enter after installing Docker Desktop..."
    fi
    
    # Wait for Docker to start
    print_status "Waiting for Docker to start..."
    while ! docker system info >/dev/null 2>&1; do
        sleep 2
        printf "."
    done
    echo
    print_success "Docker is running!"
}

# Install Docker on Linux
install_docker_linux() {
    print_status "Installing Docker on Linux..."
    
    if command_exists docker; then
        print_success "Docker is already installed"
        return 0
    fi
    
    # Detect Linux distribution
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        DISTRO=$ID
        VERSION_ID=$VERSION_ID
    else
        print_error "Cannot detect Linux distribution"
        exit 1
    fi
    
    case $DISTRO in
        ubuntu|debian)
            print_status "Installing Docker on $DISTRO..."
            
            # Update package index
            sudo apt-get update
            
            # Install prerequisites
            sudo apt-get install -y \
                apt-transport-https \
                ca-certificates \
                curl \
                gnupg \
                lsb-release
            
            # Add Docker's official GPG key
            curl -fsSL https://download.docker.com/linux/$DISTRO/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
            
            # Add Docker repository
            echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/$DISTRO $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
            
            # Install Docker Engine
            sudo apt-get update
            sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
            ;;
            
        fedora)
            print_status "Installing Docker on Fedora..."
            
            # Install DNF plugins
            sudo dnf -y install dnf-plugins-core
            
            # Add Docker repository
            sudo dnf config-manager --add-repo https://download.docker.com/linux/fedora/docker-ce.repo
            
            # Install Docker Engine
            sudo dnf install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
            ;;
            
        centos|rhel)
            print_status "Installing Docker on CentOS/RHEL..."
            
            # Install required packages
            sudo yum install -y yum-utils
            
            # Add Docker repository
            sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
            
            # Install Docker Engine
            sudo yum install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
            ;;
            
        arch)
            print_status "Installing Docker on Arch Linux..."
            sudo pacman -S --noconfirm docker docker-compose
            ;;
            
        opensuse*|sles)
            print_status "Installing Docker on openSUSE/SLES..."
            sudo zypper install -y docker docker-compose
            ;;
            
        *)
            print_error "Unsupported Linux distribution: $DISTRO"
            print_status "Please install Docker manually: https://docs.docker.com/engine/install/"
            exit 1
            ;;
    esac
    
    # Start and enable Docker service
    print_status "Starting Docker service..."
    sudo systemctl start docker
    sudo systemctl enable docker
    
    # Add current user to docker group
    print_status "Adding user to docker group..."
    sudo usermod -aG docker $USER
    
    print_success "Docker installed successfully!"
    print_warning "Please log out and log back in for Docker group membership to take effect"
    print_status "Or run: newgrp docker"
}

# Install Docker on Windows/WSL
install_docker_windows() {
    print_status "Installing Docker on Windows/WSL..."
    
    if command_exists docker; then
        print_success "Docker is already installed"
        return 0
    fi
    
    print_warning "Docker Desktop for Windows must be installed manually"
    print_status "Installation steps:"
    print_status "1. Download Docker Desktop from: https://docs.docker.com/desktop/windows/install/"
    print_status "2. Run the installer as Administrator"
    print_status "3. Enable WSL 2 integration in Docker Desktop settings"
    print_status "4. Restart your computer after installation"
    print_status "5. Start Docker Desktop from the Start menu"
    
    read -p "Press Enter after installing Docker Desktop..."
    
    # Wait for Docker to be available
    print_status "Waiting for Docker to be available..."
    while ! docker system info >/dev/null 2>&1; do
        sleep 5
        printf "."
    done
    echo
    print_success "Docker is running!"
}

# Install Docker Compose (standalone)
install_docker_compose() {
    # Check if Docker Compose is already available
    if command_exists docker-compose || docker compose version >/dev/null 2>&1; then
        print_success "Docker Compose is already available"
        return 0
    fi
    
    print_status "Installing Docker Compose..."
    
    PLATFORM=$(detect_platform)
    case $PLATFORM in
        macos)
            if command_exists brew; then
                brew install docker-compose
            else
                print_status "Docker Compose is included with Docker Desktop"
            fi
            ;;
        linux)
            # Install Docker Compose standalone
            DOCKER_COMPOSE_VERSION="2.20.0"
            print_status "Installing Docker Compose v$DOCKER_COMPOSE_VERSION..."
            
            sudo curl -L "https://github.com/docker/compose/releases/download/v$DOCKER_COMPOSE_VERSION/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
            sudo chmod +x /usr/local/bin/docker-compose
            
            # Create symlink for 'docker compose' command
            sudo ln -sf /usr/local/bin/docker-compose /usr/local/bin/docker-compose-v2
            ;;
        wsl|windows)
            print_status "Docker Compose is included with Docker Desktop"
            ;;
    esac
}

# Verify Docker installation
verify_docker() {
    print_status "Verifying Docker installation..."
    
    # Check Docker daemon
    if ! docker system info >/dev/null 2>&1; then
        print_error "Docker daemon is not running"
        print_status "Please start Docker:"
        case $(detect_platform) in
            macos)
                print_status "  - Open Docker Desktop from Applications"
                ;;
            linux)
                print_status "  - Run: sudo systemctl start docker"
                ;;
            wsl|windows)
                print_status "  - Start Docker Desktop from Start menu"
                ;;
        esac
        return 1
    fi
    
    print_success "✓ Docker daemon is running"
    
    # Check Docker version
    DOCKER_VERSION=$(docker --version)
    print_success "✓ $DOCKER_VERSION"
    
    # Check Docker Compose
    if command_exists docker-compose; then
        COMPOSE_VERSION=$(docker-compose --version)
        print_success "✓ $COMPOSE_VERSION"
    elif docker compose version >/dev/null 2>&1; then
        COMPOSE_VERSION=$(docker compose version)
        print_success "✓ Docker Compose (plugin): $COMPOSE_VERSION"
    else
        print_warning "Docker Compose not found"
    fi
    
    # Test Docker with hello-world
    print_status "Testing Docker with hello-world..."
    if docker run --rm hello-world >/dev/null 2>&1; then
        print_success "✓ Docker test successful"
    else
        print_warning "Docker test failed - this may indicate permission issues"
        if [ $(detect_platform) = "linux" ]; then
            print_status "Try running: newgrp docker"
        fi
    fi
}

# Show usage
show_usage() {
    echo "Docker Installation Helper for AI Enhancement Framework"
    echo ""
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  --compose-only   Install only Docker Compose"
    echo "  --verify-only    Only verify existing installation"
    echo "  --help          Show this help message"
    echo ""
    echo "Default: Install Docker and Docker Compose"
}

# Main function
main() {
    echo "==========================================="
    echo "Docker Installation Helper"
    echo "AI Enhancement Framework"
    echo "==========================================="
    
    # Parse arguments
    COMPOSE_ONLY=false
    VERIFY_ONLY=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --compose-only)
                COMPOSE_ONLY=true
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
    
    PLATFORM=$(detect_platform)
    print_status "Detected platform: $PLATFORM"
    
    if [ "$VERIFY_ONLY" = true ]; then
        verify_docker
        exit 0
    fi
    
    if [ "$COMPOSE_ONLY" = false ]; then
        # Install Docker
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
    fi
    
    # Install Docker Compose
    install_docker_compose
    
    # Verify installation
    verify_docker
    
    echo ""
    print_success "Docker installation completed!"
    echo ""
    print_status "Next steps:"
    print_status "1. Verify Docker is working: docker run hello-world"
    print_status "2. Start AI Framework services: docker-compose up -d"
    print_status "3. Check service status: docker-compose ps"
    
    if [ $(detect_platform) = "linux" ] && [ "$COMPOSE_ONLY" = false ]; then
        echo ""
        print_warning "Remember to log out and log back in, or run 'newgrp docker'"
        print_warning "to use Docker without sudo"
    fi
}

# Execute main function
main "$@" 