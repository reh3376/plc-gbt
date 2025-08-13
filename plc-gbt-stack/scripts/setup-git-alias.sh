#!/bin/bash

# Setup script for @git alias
# This creates a convenient alias that can be used from anywhere in the project

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
GIT_SCRIPT="$PROJECT_ROOT/plc-gbt-stack/scripts/git-auto-commit.sh"

echo "Setting up @git alias..."
echo "Project root: $PROJECT_ROOT"
echo "Git script: $GIT_SCRIPT"

# Create alias in .bashrc or .zshrc
if [[ "$SHELL" == *"zsh"* ]]; then
    SHELL_RC="$HOME/.zshrc"
    echo "Detected zsh shell"
elif [[ "$SHELL" == *"bash"* ]]; then
    SHELL_RC="$HOME/.bashrc"
    echo "Detected bash shell"
else
    echo "Unknown shell: $SHELL"
    echo "Please manually add this alias to your shell configuration:"
    echo "alias @git='$GIT_SCRIPT'"
    exit 1
fi

# Check if alias already exists
if grep -q "alias @git=" "$SHELL_RC" 2>/dev/null; then
    echo "Updating existing @git alias in $SHELL_RC"
    # Remove old alias
    sed -i.backup '/alias @git=/d' "$SHELL_RC"
else
    echo "Adding new @git alias to $SHELL_RC"
fi

# Add the alias
echo "" >> "$SHELL_RC"
echo "# @git automation alias - auto-generated" >> "$SHELL_RC"
echo "alias @git='$GIT_SCRIPT'" >> "$SHELL_RC"

echo ""
echo "✅ Alias added successfully!"
echo ""
echo "To use immediately, run: source $SHELL_RC"
echo "Or open a new terminal session"
echo ""
echo "Usage examples:"
echo "  @git                          # Auto-generate commit message"
echo "  @git \"custom commit message\"   # Use custom message"
echo ""
echo "The script will:"
echo "  1. Stage all changes (git add .)"
echo "  2. Commit with contextual message"
echo "  3. Push to remote origin"
echo "  4. Output 'success' or create error report"
