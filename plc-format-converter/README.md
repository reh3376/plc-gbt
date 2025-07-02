# PLC Format Converter

A Python library for bidirectional conversion between Rockwell .ACD and .L5X PLC file formats with lossless data preservation.

## 🚀 Quick Start

```bash
# Install the library
pip install plc-format-converter

# Basic usage
from plc_format_converter import PLCConverter

converter = PLCConverter()
result = converter.acd_to_l5x("project.acd", "project.L5X")

if result.success:
    print(f"Conversion completed in {result.conversion_time:.2f}s")
else:
    print(f"Conversion failed: {result.issues}")
```

## 📋 Current Implementation Status

### ✅ Completed (January 1, 2025)

#### Environment & Dependencies
- **Python 3.12+** environment with virtual environment setup
- **Core Libraries Installed & Tested**:
  - `acd-tools==0.2a8` - ACD file parsing ✅
  - `l5x==1.6` - L5X file parsing ✅
  - `lxml==5.2.2` - XML processing ✅
  - `pydantic==2.7.4` - Data validation ✅

#### Architecture Design
- **Unified Data Model**: Complete PLCProject, PLCController, PLCProgram, etc.
- **Conversion Engine**: PLCConverter class with format detection and validation
- **Format Handlers**: Abstract base classes for ACD and L5X handlers
- **Validation Framework**: Round-trip validation and data integrity checks
- **Error Handling**: Comprehensive ConversionResult and issue tracking

#### Testing Framework
- **Library Integration Tests**: Validation of acd-tools and l5x libraries
- **Sample Data**: Realistic L5X controller program for testing
- **Test Structure**: Pytest-based testing with coverage reporting
- **Performance Benchmarking**: Framework for testing large files

### 🔄 In Progress

#### Custom Library Development
- **Format Handlers**: ACD and L5X handler implementations
- **Conversion Logic**: Bidirectional transformation algorithms  
- **Data Preservation**: Format-specific metadata handling
- **Studio 5000 Integration**: Export/import bridge capabilities

### ⏳ Planned

#### Phase 3.5 Development (2-4 weeks)
- **Round-trip Conversion**: Full ACD ↔ L5X conversion without data loss
- **Real-world Testing**: Validation with actual PLC project files
- **Performance Optimization**: Large file handling and memory efficiency
- **CLI Tools**: Command-line interface for batch processing
- **Documentation**: Complete API documentation and usage examples

## 🏗️ Architecture

### Unified Data Model

The library uses a format-agnostic internal representation that preserves all PLC components:

```python
PLCProject
├── PLCController (processor info, settings)
├── PLCProgram[] (main programs)
│   ├── PLCRoutine[] (ladder logic, ST, FBD)
│   └── PLCTag[] (program-scoped tags)  
├── PLCAddOnInstruction[] (AOIs with parameters)
├── PLCUserDefinedType[] (UDTs with members)
├── PLCTag[] (controller-scoped tags)
└── PLCDevice[] (I/O modules and configuration)
```

### Conversion Pipeline

```
Source File → Format Handler → Unified Model → Target Handler → Target File
     ↓              ↓              ↓              ↓              ↓
  .ACD/.L5X    Parse & Extract   PLCProject    Generate &     .L5X/.ACD
                                              Validate
```

### Format Handlers

- **ACDHandler**: Uses `acd-tools` library for .ACD file processing
- **L5XHandler**: Uses `l5x` library for .L5X file processing  
- **Validation**: Round-trip testing ensures data integrity
- **Metadata**: Preserves format-specific attributes in unified model

## 📁 Project Structure

```
plc-format-converter/
├── src/plc_format_converter/
│   ├── core/
│   │   ├── models.py          # Unified PLC data models
│   │   └── converter.py       # Main conversion orchestrator
│   ├── formats/
│   │   ├── acd_handler.py     # ACD format handler  
│   │   └── l5x_handler.py     # L5X format handler
│   ├── utils/
│   │   └── validation.py      # Validation and testing utilities
│   └── cli.py                 # Command-line interface
├── tests/
│   ├── test_data/
│   │   └── sample_controller.L5X  # Test data files
│   └── test_library_integration.py
├── docs/                      # Documentation
├── examples/                  # Usage examples
└── pyproject.toml            # Project configuration
```

## 🧪 Testing

The library includes comprehensive testing for:

- **Library Integration**: Validation of acd-tools and l5x libraries
- **Data Model Validation**: Pydantic model testing  
- **Conversion Accuracy**: Round-trip conversion validation
- **Performance**: Benchmarking with various file sizes
- **Error Handling**: Edge cases and failure scenarios

```bash
# Run tests
pytest tests/ -v --cov=plc_format_converter

# Run integration tests only
pytest tests/test_library_integration.py -v

# Performance benchmarks
pytest tests/test_performance.py -k benchmark --benchmark-only
```

## 🎯 Key Features

### Current Capabilities
- ✅ **Format Detection**: Automatic .ACD/.L5X format recognition
- ✅ **Library Integration**: Working acd-tools and l5x parsing
- ✅ **Unified Modeling**: Format-agnostic PLC representation
- ✅ **Validation Framework**: Data integrity and round-trip testing
- ✅ **Error Reporting**: Detailed conversion issue tracking

### Planned Capabilities  
- 🔄 **Bidirectional Conversion**: Full ACD ↔ L5X conversion
- 🔄 **Data Preservation**: Zero-loss format conversion
- ⏳ **Batch Processing**: Multiple file conversion support
- ⏳ **Studio 5000 Bridge**: Integration with Rockwell tools
- ⏳ **Web API**: REST API for remote conversion services

## 📊 Performance Targets

- **Small Files** (<1MB): <1 second conversion time
- **Medium Files** (1-10MB): <10 second conversion time  
- **Large Files** (10-100MB): <60 second conversion time
- **Memory Usage**: <2x source file size during conversion
- **Round-trip Accuracy**: >99.9% data preservation

## 🔧 Development Setup

```bash
# Clone repository
git clone https://github.com/reh3376/plc-format-converter.git
cd plc-format-converter

# Create virtual environment (Python 3.12+)
uv venv --python 3.12
source .venv/bin/activate

# Install development dependencies
uv pip install -e ".[dev,testing]"

# Run tests
pytest

# Run linting
ruff check --fix .
black .
mypy .
```

## 📋 Requirements

### Minimum Requirements
- **Python**: 3.12+
- **Memory**: 1GB RAM (for typical PLC files)
- **Storage**: 100MB+ free space

### Dependencies
- `acd-tools>=0.2a8` - ACD file parsing
- `l5x>=1.6` - L5X file parsing  
- `lxml>=5.2.0` - XML processing
- `pydantic>=2.7.0` - Data validation
- `structlog>=24.2.0` - Logging
- `click>=8.1.0` - CLI interface

## 🚧 Roadmap

See [ROADMAP.md](../docs/roadmap.md) for detailed development timeline.

### Phase 3.5: Custom Library Development (Weeks 2-4)
- [ ] Complete format handler implementations
- [ ] Implement bidirectional conversion algorithms
- [ ] Add comprehensive real-world file testing
- [ ] Optimize performance for large files
- [ ] Create CLI tools and documentation

### Future Phases
- [ ] Studio 5000 integration plugin
- [ ] Web-based conversion service
- [ ] Advanced validation and optimization features
- [ ] Industrial IoT integration capabilities

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Priorities
1. **Real-world Testing**: Need sample .ACD and .L5X files from various PLC projects
2. **Performance Optimization**: Memory usage and conversion speed improvements
3. **Studio 5000 Integration**: Export/import automation scripts
4. **Documentation**: Usage examples and best practices

## 📄 License

This project is licensed under the Apache License 2.0 - see [LICENSE](LICENSE) for details.

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/reh3376/plc-format-converter/issues)
- **Discussions**: [GitHub Discussions](https://github.com/reh3376/plc-format-converter/discussions)
- **Email**: dev@plc-gpt.com

---

**Note**: This library is currently in active development as part of the PLC-Savvy GPT project. While the architecture is solid and libraries are tested, full conversion capabilities are still being implemented. See the roadmap for current status and timeline. 