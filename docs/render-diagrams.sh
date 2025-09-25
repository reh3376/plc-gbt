#!/bin/bash
# Script to render Mermaid diagrams to PNG/SVG using Mermaid CLI

# Check if mmdc is installed
if ! command -v mmdc &> /dev/null; then
    echo "Mermaid CLI (mmdc) not found. Install it with:"
    echo "npm install -g @mermaid-js/mermaid-cli"
    exit 1
fi

# Create output directory
mkdir -p docs/diagrams-rendered

# Render each .mmd file
for file in docs/*.mmd; do
    if [ -f "$file" ]; then
        basename=$(basename "$file" .mmd)
        echo "Rendering $basename..."
        
        # Render to SVG
        mmdc -i "$file" -o "docs/diagrams-rendered/${basename}.svg" -t default -b white
        
        # Render to PNG (optional)
        # mmdc -i "$file" -o "docs/diagrams-rendered/${basename}.png" -t default -b white
    fi
done

echo "Done! Check docs/diagrams-rendered/ for the output files."
