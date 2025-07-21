#!/bin/bash

# AI Enhancement Framework - Simple Installation Script
# Wrapper for the Python installer with easy command-line usage

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}"
    echo "🚀 AI Enhancement Framework Installer"
    echo "====================================="
    echo -e "${NC}"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check Python availability
check_python() {
    if command -v python3 >/dev/null 2>&1; then
        PYTHON_CMD="python3"
    elif command -v python >/dev/null 2>&1; then
        PYTHON_CMD="python"
    else
        print_error "Python not found. Please install Python 3.8+ first."
        exit 1
    fi
    
    # Check Python version
    PYTHON_VERSION=$($PYTHON_CMD -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
    
    if [ "$PYTHON_MAJOR" -lt 3 ] || [ "$PYTHON_MAJOR" -eq 3 -a "$PYTHON_MINOR" -lt 8 ]; then
        print_error "Python 3.8+ required. Found: $PYTHON_VERSION"
        exit 1
    fi
    
    print_info "Using Python $PYTHON_VERSION"
}

# Show usage information
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -t, --type TYPE         Installation type: interactive, automated, minimal, full"
    echo "  -d, --destination DIR   Installation destination directory"
    echo "  -q, --quiet             Quiet mode (less output)"
    echo "  -h, --help              Show this help message"
    echo ""
    echo "Installation Types:"
    echo "  interactive (default)   Run interactive installation wizard"
    echo "  automated              Automated installation with default settings"
    echo "  minimal                Core framework only (~50MB)"
    echo "  full                   Complete installation with all modules (~1GB)"
    echo ""
    echo "Examples:"
    echo "  $0                     # Interactive installation"
    echo "  $0 -t minimal          # Minimal installation"
    echo "  $0 -t full -d ./myapp  # Full installation to specific directory"
}

# Parse command line arguments
INSTALLATION_TYPE="interactive"
DESTINATION=""
QUIET=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -t|--type)
            INSTALLATION_TYPE="$2"
            shift 2
            ;;
        -d|--destination)
            DESTINATION="$2"
            shift 2
            ;;
        -q|--quiet)
            QUIET="--quiet"
            shift
            ;;
        -h|--help)
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

# Validate installation type
case $INSTALLATION_TYPE in
    interactive|automated|minimal|full)
        ;;
    *)
        print_error "Invalid installation type: $INSTALLATION_TYPE"
        show_usage
        exit 1
        ;;
esac

# Main installation function
main() {
    print_header
    
    print_info "Starting AI Enhancement Framework installation..."
    print_info "Installation type: $INSTALLATION_TYPE"
    
    if [ -n "$DESTINATION" ]; then
        print_info "Destination: $DESTINATION"
    fi
    
    # Check Python
    check_python
    
    # Get script directory
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    INSTALLER_SCRIPT="$SCRIPT_DIR/INSTALL.py"
    
    if [ ! -f "$INSTALLER_SCRIPT" ]; then
        print_error "Installer script not found: $INSTALLER_SCRIPT"
        exit 1
    fi
    
    # Build command
    CMD=("$PYTHON_CMD" "$INSTALLER_SCRIPT" "--type" "$INSTALLATION_TYPE")
    
    if [ -n "$DESTINATION" ]; then
        CMD+=("--destination" "$DESTINATION")
    fi
    
    if [ -n "$QUIET" ]; then
        CMD+=("$QUIET")
    fi
    
    # Run installer
    print_info "Running installer..."
    "${CMD[@]}"
    
    # Check result
    if [ $? -eq 0 ]; then
        print_success "Installation completed successfully!"
        echo ""
        echo "🎉 Next steps:"
        echo "1. Navigate to your project directory"
        echo "2. Test the installation: python -c \"import ai_enhancement_framework; print('✅ Success!')\""
        echo "3. Read the user guide for more information"
    else
        print_error "Installation failed!"
        exit 1
    fi
}

# Check if script is being sourced or executed
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi 