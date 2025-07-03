# PLC File Conversion Library - How To Guide

**Complete ACD ↔ L5X Conversion Capability**  
**Version**: 1.0.0  
**Date**: January 1, 2025  
**Library Components**: Studio 5000 Integration + Format Compatibility Checker

## Table of Contents

1. [Overview](#overview)
2. [Installation & Setup](#installation--setup)
3. [Quick Start Guide](#quick-start-guide)
4. [Studio 5000 Integration](#studio-5000-integration)
5. [Format Compatibility Checking](#format-compatibility-checking)
6. [CLI Tools](#cli-tools)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)

---

## Overview

The PLC File Conversion Library provides comprehensive support for converting between Rockwell Automation's PLC file formats:

- **ACD Files** - Automation Control Database (Studio 5000 native format)
- **L5X Files** - Logix Designer Export format (XML-based)

### Key Features

✅ **Bidirectional Conversion** - ACD ↔ L5X with full fidelity  
✅ **Studio 5000 Integration** - COM automation for direct software control  
✅ **Batch Processing** - Convert multiple files with progress tracking  
✅ **Data Integrity Validation** - Ensure conversion accuracy  
✅ **Round-trip Testing** - Validate A→B→A conversion integrity  
✅ **Cross-platform Support** - Works on Windows (Studio 5000) and other platforms (validation only)  

### Architecture

```
┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│   ACD Files         │    │  Studio 5000        │    │   L5X Files         │
│   (Native Format)   │◄──►│  Integration        │◄──►│   (XML Format)      │
└─────────────────────┘    └─────────────────────┘    └─────────────────────┘
                                      │
                                      ▼
                           ┌─────────────────────┐
                           │  Compatibility      │
                           │  Checker            │
                           │  (Validation)       │
                           └─────────────────────┘
```

---

## Installation & Setup

### Prerequisites

- **Python 3.8+** (tested with Python 3.12)
- **Windows OS** (required for Studio 5000 integration)
- **Studio 5000 Logix Designer** (for ACD/L5X conversion)
- **Required Python packages**: `structlog`, `pathlib`, `typing`

### Installation Steps

1. **Clone or Download the Library**
   ```bash
   cd plc-gpt-stack/scripts/etl/
   # Files: studio5000_integration.py, format_compatibility_checker.py
   ```

2. **Install Dependencies**
   ```bash
   pip install structlog
   
   # Windows-specific (for Studio 5000 COM automation)
   pip install pywin32
   ```

3. **Verify Studio 5000 Installation**
   ```bash
   python studio5000_integration.py --validate
   ```

---

## Quick Start Guide

### Example 1: Convert Single ACD to L5X

```python
from etl.studio5000_integration import Studio5000AutomationClient

# Initialize client
client = Studio5000AutomationClient()

# Connect to Studio 5000
if client.connect():
    # Open ACD file
    if client.open_project("C:/MyProject.ACD"):
        # Export to L5X
        success = client.export_to_l5x("C:/MyProject.L5X")
        print(f"Conversion {'successful' if success else 'failed'}")
    
    # Cleanup
    client.disconnect()
```

### Example 2: Batch Convert Multiple Files

```python
from etl.studio5000_integration import Studio5000BatchProcessor

# Initialize batch processor
processor = Studio5000BatchProcessor()

# Convert multiple ACD files to L5X
acd_files = [
    "C:/Project1.ACD",
    "C:/Project2.ACD", 
    "C:/Project3.ACD"
]

results = processor.convert_acd_to_l5x(
    acd_files=acd_files,
    output_dir="C:/ConvertedFiles/",
    max_retries=3
)

print(f"Converted {results['successful']}/{results['total_files']} files")
processor.cleanup()
```

### Example 3: Validate Conversion Quality

```python
from etl.format_compatibility_checker import FormatCompatibilityChecker

# Initialize checker
checker = FormatCompatibilityChecker()

# Check compatibility between original and converted files
report = checker.check_file_compatibility(
    source_file="C:/Original.ACD",
    target_file="C:/Converted.L5X"
)

print(f"Compatibility: {report.compatibility_level.value}")
print(f"Score: {report.overall_score:.1f}%")
print(f"Components: {report.matched_components}/{report.total_components} matched")

checker.cleanup()
```

---

## Studio 5000 Integration

### Studio5000AutomationClient

**Primary class for Studio 5000 COM automation control.**

#### Key Methods

```python
client = Studio5000AutomationClient()

# Connection Management
client.connect()                    # Connect to Studio 5000
client.disconnect()                 # Disconnect and cleanup
client.find_studio_installation()   # Locate Studio 5000 executable

# Project Operations
client.open_project(acd_path)       # Open ACD project
client.close_project()             # Close current project

# File Operations  
client.export_to_l5x(output_path,   # Export project to L5X
    include_routines=True,
    include_udt=True, 
    include_aoi=True)

client.import_from_l5x(l5x_path,    # Import L5X to new ACD
    target_acd_path)
```

### Studio5000BatchProcessor

**Handles multiple file conversions with progress tracking.**

```python
processor = Studio5000BatchProcessor(temp_dir="C:/Temp/")

# Convert multiple files
results = processor.convert_acd_to_l5x(
    acd_files=["file1.acd", "file2.acd"],
    output_dir="C:/Output/",
    max_retries=3
)

# Results structure
{
    'total_files': 2,
    'successful': 2,
    'failed': 0,
    'conversions': [
        {
            'input_file': 'file1.acd',
            'output_file': 'file1.L5X',
            'success': True,
            'error': None,
            'file_size_mb': 5.2
        }
    ],
    'errors': []
}
```

---

## Format Compatibility Checking

### FormatCompatibilityChecker

**Comprehensive validation for PLC file format conversions.**

```python
from etl.format_compatibility_checker import FormatCompatibilityChecker

checker = FormatCompatibilityChecker()

# Compare two files
report = checker.check_file_compatibility(
    source_file="project.acd",
    target_file="project.L5X"
)

# Report analysis
print(f"Compatibility Level: {report.compatibility_level.value}")
print(f"Overall Score: {report.overall_score:.1f}%")
print(f"Processing Time: {report.processing_time_ms:.1f}ms")

# Component details
print(f"\nComponent Analysis:")
print(f"  Total Components: {report.total_components}")
print(f"  Matched: {report.matched_components}")
print(f"  Missing: {report.missing_components}")
print(f"  Modified: {report.modified_components}")
```

### Round-Trip Conversion Validation

```python
# Test A → B → A conversion integrity
results = checker.validate_round_trip_conversion(
    original_file="project.acd",
    intermediate_format=FileFormat.L5X
)

print(f"Round-trip Success: {results['overall_success']}")
print(f"Data Loss: {results['data_loss_percentage']:.1f}%")

# Conversion steps
for conversion in results['conversions']:
    print(f"{conversion['step']}: {'✅' if conversion['success'] else '❌'}")
```

---

## CLI Tools

### Studio 5000 Integration CLI

```bash
# Validate Studio 5000 installation
python studio5000_integration.py --validate

# Convert ACD files to L5X
python studio5000_integration.py \
    --convert-acd file1.acd file2.acd \
    --output-dir ./converted/ \
    --temp-dir ./temp/

# Convert L5X files to ACD
python studio5000_integration.py \
    --convert-l5x file1.L5X file2.L5X \
    --output-dir ./converted/
```

### Format Compatibility Checker CLI

```bash
# Check compatibility between two files
python format_compatibility_checker.py \
    --check source.acd target.L5X \
    --output compatibility_report.json

# Perform round-trip validation
python format_compatibility_checker.py \
    --round-trip original.acd \
    --output roundtrip_results.json \
    --temp-dir ./temp/
```

---

## Best Practices

### 1. File Management

```python
# Always use absolute paths
from pathlib import Path

def safe_file_processing(input_file: str, output_dir: str):
    # Convert to absolute paths
    input_path = Path(input_file).resolve()
    output_path = Path(output_dir).resolve()
    
    # Validate paths exist
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    output_path.mkdir(parents=True, exist_ok=True)
    
    return str(input_path), str(output_path)
```

### 2. Resource Management

```python
# Always use context managers or try/finally
class SafeStudio5000Processor:
    def __enter__(self):
        self.processor = Studio5000BatchProcessor()
        return self.processor
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if hasattr(self, 'processor'):
            self.processor.cleanup()

# Usage
with SafeStudio5000Processor() as processor:
    results = processor.convert_acd_to_l5x(files, output_dir)
    # Automatic cleanup on exit
```

---

## Troubleshooting

### Common Issues

#### 1. Studio 5000 Connection Failed

**Problem**: `Failed to connect to Studio 5000 via COM`

**Solutions**:
- Close Studio 5000 and let script start it
- Run Python script as Administrator
- Check if pywin32 is properly installed

#### 2. File Access Denied

**Problem**: `Permission denied when opening ACD/L5X files`

**Solutions**:
- Ensure files are not open in Studio 5000
- Check file permissions (read/write access)
- Run Python script as Administrator

#### 3. COM Automation Not Available

**Problem**: `Windows COM automation not available`

**Solutions**:
```bash
# Install Windows COM support
pip install pywin32

# Register COM components
python -m win32com.client.gencache
```

---

## Support and Contributing

### Getting Help

- **Documentation**: This guide and inline code documentation
- **Issues**: Report bugs and request features via project repository
- **Testing**: Use the comprehensive test suite for validation

### Contributing

The library is designed for extensibility:

1. **Custom Validators** - Extend `FormatCompatibilityChecker`
2. **Additional Formats** - Add support for new PLC file formats
3. **Platform Support** - Enhance cross-platform compatibility
4. **Performance** - Optimize for specific use cases

### Future Enhancements

- **Real-time Conversion** - Monitor directories for automatic conversion
- **Web Interface** - Browser-based conversion and validation
- **API Server** - RESTful API for remote conversion services
- **Enhanced Analytics** - ML-based conversion quality prediction

---

**End of Guide**

*For the latest updates and additional examples, refer to the project repository and documentation.*
