#!/bin/bash
# Setup script for AI Task Orchestrator environment

echo "🔧 AI Task Orchestrator Environment Setup"
echo "========================================"

# Check Python version
PYTHON_CMD=""

# Check for Python 3.12 first (preferred)
if command -v python3.12 &> /dev/null; then
    PYTHON_CMD="python3.12"
elif [ -f "/opt/homebrew/bin/python3.12" ]; then
    PYTHON_CMD="/opt/homebrew/bin/python3.12"
# Check for Python 3.11
elif command -v python3.11 &> /dev/null; then
    PYTHON_CMD="python3.11"
# Check for Python 3.10
elif command -v python3.10 &> /dev/null; then
    PYTHON_CMD="python3.10"
else
    # Check if default python3 is >= 3.10
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
        if (( $(echo "$PYTHON_VERSION >= 3.10" | bc -l) )); then
            PYTHON_CMD="python3"
        fi
    fi
fi

if [ -z "$PYTHON_CMD" ]; then
    echo "❌ Error: Python 3.10 or later is required!"
    echo "Please install Python 3.10+ and try again."
    exit 1
fi

echo "✅ Found Python: $PYTHON_CMD"
$PYTHON_CMD --version

# Create virtual environment if it doesn't exist
VENV_DIR="venv"
if [ ! -d "$VENV_DIR" ]; then
    echo ""
    echo "📦 Creating virtual environment..."
    $PYTHON_CMD -m venv $VENV_DIR
fi

# Activate virtual environment
echo ""
echo "🚀 Activating virtual environment..."
source $VENV_DIR/bin/activate

# Upgrade pip
echo ""
echo "📈 Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo ""
echo "📚 Installing requirements..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    # Install minimal requirements
    pip install pydantic structlog
fi

# Install the package in development mode
echo ""
echo "🔗 Installing plc_orchestrator in development mode..."
pip install -e .

echo ""
echo "✨ Environment setup complete!"
echo ""
echo "To activate the environment in the future, run:"
echo "  source venv/bin/activate"
echo ""
echo "To run workflows, use:"
echo "  python workflows/simple_task_workflow.py"
echo ""
