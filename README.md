# PLC Format Converter Library

[![PyPI version](https://badge.fury.io/py/plc-format-converter.svg)](https://badge.fury.io/py/plc-format-converter)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://pepy.tech/badge/plc-format-converter)](https://pepy.tech/project/plc-format-converter)

> **Modern ACD ↔ L5X conversion library with industrial-grade validation and motion control support**

## 🚀 Features

- **Bidirectional Conversion**: ACD ↔ L5X format conversion with full data integrity
- **Industrial-Grade Validation**: Multi-tier validation framework with capability checking
- **Motion Control Support**: MAOC, MAPC, MAAT instructions and servo drive integration
- **Safety System Support**: GuardLogix controllers and safety-rated I/O
- **Cross-Platform**: Windows, Linux, macOS (validation only)
- **Modern Architecture**: Type-safe Pydantic models, async-ready design
- **CLI Interface**: Complete command-line tools for batch processing

## 📦 Installation

### From PyPI (Recommended)
```bash
pip install plc-format-converter
```

### From Source
```bash
git clone https://github.com/reh3376/acd-l5x-tool-lib.git
cd acd-l5x-tool-lib
pip install -e .
```

## 🔧 Quick Start

### Command Line Interface
```bash
# Convert ACD to L5X
plc-convert --input controller.ACD --output controller.L5X --format l5x

# Convert L5X to ACD
plc-convert --input controller.L5X --output controller.ACD --format acd

# Validate file without conversion
plc-convert --validate --input controller.L5X

# Batch processing
plc-convert --batch --input-dir ./input --output-dir ./output --format l5x
```

### Python API
```python
from plc_format_converter import PLCConverter
from plc_format_converter.formats import ACDHandler, L5XHandler

# Initialize converter
converter = PLCConverter()

# Convert ACD to L5X
result = converter.convert_file("controller.ACD", "controller.L5X", target_format="l5x")
print(f"Conversion successful: {result.success}")

# Advanced usage with validation
from plc_format_converter.utils import PLCValidator

validator = PLCValidator()
validation_result = validator.validate_file("controller.L5X")
print(f"Validation score: {validation_result.score}%")
```

## 🏗️ Architecture

### Core Components

- **PLCConverter**: Main conversion engine with format detection
- **Format Handlers**: Specialized handlers for ACD and L5X formats
- **Validation Framework**: Multi-tier validation with capability checking
- **CLI Interface**: Command-line tools for batch processing

### Supported Formats

| Format | Extension | Read | Write | Validation |
|--------|-----------|------|-------|------------|
| **ACD** | `.ACD` | ✅ | ✅ | ✅ |
| **L5X** | `.L5X` | ✅ | ✅ | ✅ |

## 🔍 Validation Features

- **Syntax Validation**: XML/binary format structure checking
- **Data Integrity**: Tag references, routine calls, device addressing
- **Capability Checking**: Hardware compatibility, firmware versions
- **Motion Control**: Servo drives, motion instructions, axis configurations
- **Safety Systems**: GuardLogix validation, safety-rated I/O

## 📊 Controller Compatibility

| Controller Family | ACD Support | L5X Support | Motion Control | Safety |
|-------------------|-------------|-------------|----------------|---------|
| **ControlLogix** | ✅ | ✅ | ✅ | ✅ |
| **CompactLogix** | ✅ | ✅ | ✅ | ❌ |
| **GuardLogix** | ✅ | ✅ | ✅ | ✅ |
| **Micro800** | ⚠️ | ✅ | ❌ | ❌ |

## 🛠️ Development

### Setup Development Environment
```bash
# Clone repository
git clone https://github.com/reh3376/acd-l5x-tool-lib.git
cd acd-l5x-tool-lib

# Install in development mode
pip install -e .[dev]

# Run tests
pytest tests/

# Run linting
ruff check src/
```

### Optional Dependencies
```bash
# For ACD format support
pip install plc-format-converter[acd-tools]

# For L5X format support
pip install plc-format-converter[l5x]

# For Studio 5000 integration
pip install plc-format-converter[studio5000]

# All optional dependencies
pip install plc-format-converter[all]
```

## 📖 Documentation

- **[Conversion Guide](docs/plc-file-conversion-howto.md)** - Complete usage documentation
- **[API Reference](docs/api-reference.md)** - Python API documentation
- **[Migration Guide](docs/migration-guide.md)** - Upgrading from 1.x to 2.0

## 🎯 PyPI Publication

**📦 Package Information**:
- **PyPI URL**: https://pypi.org/project/plc-format-converter/
- **Current Version**: 2.0.0
- **Publication Date**: July 3, 2025
- **Package Size**: 46.4 KB (wheel) + 55.5 KB (source)

**🔧 Installation Verification**:
```bash
pip install plc-format-converter
python -c "import plc_format_converter; print(f'Version: {plc_format_converter.__version__}')"
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🏷️ Version History

- **2.0.0** (2025-07-03): Published to PyPI with modern architecture
- **1.0.0** (2024): Initial release with basic conversion support

## 🔗 Links

- **PyPI Package**: https://pypi.org/project/plc-format-converter/
- **GitHub Repository**: https://github.com/reh3376/acd-l5x-tool-lib/
- **Documentation**: https://github.com/reh3376/acd-l5x-tool-lib/blob/main/docs/
- **Issue Tracker**: https://github.com/reh3376/acd-l5x-tool-lib/issues

---

*Industrial-grade PLC format conversion for modern Python applications* 🏭⚙️ 