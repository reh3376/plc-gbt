# Container Usage Guide

This guide explains how to use the containerized version of the PLC Format Converter.

## Quick Start

### Pull the Container

```bash
# Pull the latest version
docker pull ghcr.io/reh3376/acd-l5x-tool-lib:latest

# Or pull a specific version
docker pull ghcr.io/reh3376/acd-l5x-tool-lib:v2.0.1
```

### Basic Usage

```bash
# Show help
docker run --rm ghcr.io/reh3376/acd-l5x-tool-lib:latest

# Convert a file (mount your files directory)
docker run --rm -v /path/to/your/files:/data ghcr.io/reh3376/acd-l5x-tool-lib:latest \
  plc-convert input.acd output.l5x

# Interactive mode
docker run --rm -it -v /path/to/your/files:/data ghcr.io/reh3376/acd-l5x-tool-lib:latest bash
```

## Available Commands

The main CLI command is available in the container:

- `plc-convert` - Main conversion tool with subcommands:
  - `plc-convert convert` - Convert between formats
  - `plc-convert validate` - Validate PLC files
  - `plc-convert batch` - Batch process files
  - `plc-convert info` - Show library information

## Examples

### Convert ACD to L5X

```bash
docker run --rm -v $(pwd):/data ghcr.io/reh3376/acd-l5x-tool-lib:latest \
  plc-convert convert input.acd output.l5x
```

### Convert L5X to ACD

```bash
docker run --rm -v $(pwd):/data ghcr.io/reh3376/acd-l5x-tool-lib:latest \
  plc-convert convert input.l5x output.acd
```

### Validate a PLC File

```bash
docker run --rm -v $(pwd):/data ghcr.io/reh3376/acd-l5x-tool-lib:latest \
  plc-convert validate input.l5x
```

### Batch Processing

```bash
# Process all L5X files in a directory
docker run --rm -v $(pwd):/data ghcr.io/reh3376/acd-l5x-tool-lib:latest \
  plc-convert batch . ./processed --pattern "*.L5X" --validate
```

## Volume Mounting

The container uses `/data` as the working directory. Mount your files here:

```bash
# Mount current directory
-v $(pwd):/data

# Mount specific directory
-v /path/to/plc/files:/data

# Mount with read-only access
-v /path/to/plc/files:/data:ro
```

## Container Features

- **Multi-platform**: Supports both AMD64 and ARM64 architectures
- **Secure**: Runs as non-root user (`plcuser`)
- **Minimal**: Based on Python slim image for smaller size
- **Cached**: Uses GitHub Actions cache for faster builds

## Advanced Usage

### Custom Entry Point

```bash
# Use Python directly
docker run --rm -v $(pwd):/data ghcr.io/reh3376/acd-l5x-tool-lib:latest \
  python -c "from plc_format_converter import convert_file; convert_file('input.acd', 'output.l5x')"
```

### Environment Variables

```bash
# Set logging level
docker run --rm -e LOG_LEVEL=DEBUG -v $(pwd):/data \
  ghcr.io/reh3376/acd-l5x-tool-lib:latest plc-convert input.acd output.l5x
```

## Building Locally

To build the container locally:

```bash
# Build
docker build -t plc-converter .

# Run
docker run --rm -v $(pwd):/data plc-converter plc-convert --help
```

## Troubleshooting

### Permission Issues

If you encounter permission issues:

```bash
# Run as your user ID
docker run --rm -u $(id -u):$(id -g) -v $(pwd):/data \
  ghcr.io/reh3376/acd-l5x-tool-lib:latest plc-convert input.acd output.l5x
```

### File Not Found

Ensure your files are in the mounted directory:

```bash
# List files in container
docker run --rm -v $(pwd):/data ghcr.io/reh3376/acd-l5x-tool-lib:latest ls -la
```

## Integration with CI/CD

Use in GitHub Actions:

```yaml
- name: Convert PLC files
  run: |
    docker run --rm -v ${{ github.workspace }}:/data \
      ghcr.io/reh3376/acd-l5x-tool-lib:latest \
      plc-convert input.acd output.l5x
```

## Container Registry

The container is published to GitHub Container Registry:
- Registry: `ghcr.io`
- Repository: `reh3376/acd-l5x-tool-lib`
- Tags: `latest`, version tags (e.g., `v2.0.1`)

## Security

- Container runs as non-root user
- Minimal attack surface with slim base image
- Signed with GitHub attestations
- Source code transparency via labels 