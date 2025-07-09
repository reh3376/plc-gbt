#!/usr/bin/env python3
"""
Studio 5000 Integration Module
Phase 3.2: ETL Pipeline Development - Studio 5000 Export/Import Integration
Version: 1.0.0

This module provides integration with Rockwell Automation's Studio 5000 software
for automated PLC file format conversion and validation.

Features:
- COM automation interface for Studio 5000
- Automated export/import operations
- Format conversion between ACD and L5X
- Batch processing capabilities
- Error handling and logging
"""

import os
import sys
import time
import json
import logging
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime
import subprocess
import tempfile
import shutil

import structlog

# Windows-specific imports for COM automation
try:
    import win32com.client
    import pythoncom
    WINDOWS_COM_AVAILABLE = True
except ImportError:
    WINDOWS_COM_AVAILABLE = False
    win32com = None
    pythoncom = None

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.dev.ConsoleRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


class Studio5000IntegrationError(Exception):
    """Custom exception for Studio 5000 integration errors"""
    pass


class Studio5000AutomationClient:
    """
    Studio 5000 COM automation client for PLC file operations
    
    This class provides programmatic control of Studio 5000 for:
    - Opening and closing ACD files
    - Exporting to L5X format
    - Importing from L5X format
    - Project validation and verification
    """
    
    def __init__(self, studio_path: Optional[str] = None):
        """
        Initialize Studio 5000 automation client
        
        Args:
            studio_path: Path to Studio 5000 executable (auto-detect if None)
        """
        self.studio_path = studio_path
        self.application = None
        self.is_connected = False
        self.current_project = None
        
        # Studio 5000 default installation paths
        self.default_paths = [
            r"C:\Program Files (x86)\Rockwell Software\Studio 5000\Studio5000Logix.exe",
            r"C:\Program Files\Rockwell Software\Studio 5000\Studio5000Logix.exe",
            r"C:\Program Files (x86)\Rockwell Software\RSLogix 5000\Rslogix.exe",
        ]
        
        if not WINDOWS_COM_AVAILABLE:
            logger.warning("Windows COM automation not available - Studio 5000 integration disabled")
    
    def find_studio_installation(self) -> Optional[str]:
        """
        Find Studio 5000 installation path
        
        Returns:
            Path to Studio 5000 executable or None if not found
        """
        if self.studio_path and Path(self.studio_path).exists():
            return self.studio_path
        
        for path in self.default_paths:
            if Path(path).exists():
                logger.info("Found Studio 5000 installation", path=path)
                return path
        
        logger.warning("Studio 5000 installation not found")
        return None
    
    def connect(self) -> bool:
        """
        Connect to Studio 5000 via COM automation
        
        Returns:
            True if connection successful, False otherwise
        """
        if not WINDOWS_COM_AVAILABLE:
            logger.error("Cannot connect - Windows COM automation not available")
            return False
        
        try:
            # Initialize COM
            pythoncom.CoInitialize()
            
            # Try to connect to existing Studio 5000 instance
            try:
                self.application = win32com.client.GetActiveObject("RSLogix5000.Application")
                logger.info("Connected to existing Studio 5000 instance")
            except:
                # Start new Studio 5000 instance
                studio_path = self.find_studio_installation()
                if not studio_path:
                    raise Studio5000IntegrationError("Studio 5000 not found")
                
                self.application = win32com.client.Dispatch("RSLogix5000.Application")
                self.application.Visible = False  # Run in background
                logger.info("Started new Studio 5000 instance")
            
            self.is_connected = True
            return True
            
        except Exception as e:
            logger.error("Failed to connect to Studio 5000", error=str(e))
            self.is_connected = False
            return False
    
    def disconnect(self):
        """Disconnect from Studio 5000"""
        try:
            if self.current_project:
                self.close_project()
            
            if self.application:
                # Don't quit if we connected to existing instance
                # self.application.Quit()
                self.application = None
            
            pythoncom.CoUninitialize()
            self.is_connected = False
            logger.info("Disconnected from Studio 5000")
            
        except Exception as e:
            logger.warning("Error during disconnect", error=str(e))
    
    def open_project(self, acd_path: str) -> bool:
        """
        Open an ACD project file
        
        Args:
            acd_path: Path to the ACD file
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_connected:
            logger.error("Not connected to Studio 5000")
            return False
        
        try:
            # Close any open project first
            if self.current_project:
                self.close_project()
            
            # Open the ACD file
            acd_path = str(Path(acd_path).resolve())
            self.application.Projects.Open(acd_path)
            self.current_project = acd_path
            
            logger.info("Opened ACD project", path=acd_path)
            return True
            
        except Exception as e:
            logger.error("Failed to open ACD project", path=acd_path, error=str(e))
            return False
    
    def close_project(self):
        """Close the currently open project"""
        try:
            if self.current_project and self.application:
                self.application.Projects.Close()
                self.current_project = None
                logger.info("Closed current project")
        except Exception as e:
            logger.warning("Error closing project", error=str(e))
    
    def export_to_l5x(self, output_path: str, include_routines: bool = True, 
                      include_udt: bool = True, include_aoi: bool = True) -> bool:
        """
        Export current project to L5X format
        
        Args:
            output_path: Path for the L5X output file
            include_routines: Include routine definitions
            include_udt: Include UDT definitions
            include_aoi: Include AOI definitions
            
        Returns:
            True if export successful, False otherwise
        """
        if not self.current_project:
            logger.error("No project open for export")
            return False
        
        try:
            output_path = str(Path(output_path).resolve())
            
            # Configure export options
            export_options = {
                'Routines': include_routines,
                'UDTs': include_udt,
                'AOIs': include_aoi,
                'Tags': True,  # Always include tags
                'Devices': True,  # Always include devices
            }
            
            # Perform export
            project = self.application.Projects.Item(0)  # Get first (current) project
            project.ExportL5X(output_path, **export_options)
            
            logger.info("Exported project to L5X", 
                       input=self.current_project, 
                       output=output_path,
                       options=export_options)
            return True
            
        except Exception as e:
            logger.error("Failed to export to L5X", 
                        output=output_path, 
                        error=str(e))
            return False
    
    def import_from_l5x(self, l5x_path: str, target_acd_path: str) -> bool:
        """
        Import L5X file into a new ACD project
        
        Args:
            l5x_path: Path to the L5X file to import
            target_acd_path: Path for the new ACD file
            
        Returns:
            True if import successful, False otherwise
        """
        if not self.is_connected:
            logger.error("Not connected to Studio 5000")
            return False
        
        try:
            l5x_path = str(Path(l5x_path).resolve())
            target_acd_path = str(Path(target_acd_path).resolve())
            
            # Create new project
            project = self.application.Projects.Add()
            
            # Import from L5X
            project.ImportL5X(l5x_path)
            
            # Save as ACD
            project.SaveAs(target_acd_path)
            
            self.current_project = target_acd_path
            
            logger.info("Imported L5X to new ACD project", 
                       input=l5x_path, 
                       output=target_acd_path)
            return True
            
        except Exception as e:
            logger.error("Failed to import from L5X", 
                        input=l5x_path, 
                        target=target_acd_path, 
                        error=str(e))
            return False


class Studio5000BatchProcessor:
    """
    Batch processor for Studio 5000 operations
    
    Handles multiple file conversions with progress tracking and error recovery
    """
    
    def __init__(self, temp_dir: Optional[str] = None):
        """
        Initialize batch processor
        
        Args:
            temp_dir: Temporary directory for intermediate files
        """
        self.client = Studio5000AutomationClient()
        self.temp_dir = temp_dir or tempfile.mkdtemp(prefix="studio5000_batch_")
        self.results = []
        
        # Ensure temp directory exists
        Path(self.temp_dir).mkdir(parents=True, exist_ok=True)
    
    def convert_acd_to_l5x(self, acd_files: List[str], output_dir: str, 
                          max_retries: int = 3) -> Dict[str, Any]:
        """
        Convert multiple ACD files to L5X format
        
        Args:
            acd_files: List of ACD file paths
            output_dir: Directory for L5X output files
            max_retries: Maximum retry attempts per file
            
        Returns:
            Dictionary with conversion results
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        results = {
            'total_files': len(acd_files),
            'successful': 0,
            'failed': 0,
            'conversions': [],
            'errors': []
        }
        
        # Connect to Studio 5000
        if not self.client.connect():
            results['errors'].append("Failed to connect to Studio 5000")
            return results
        
        try:
            for i, acd_file in enumerate(acd_files):
                acd_path = Path(acd_file)
                l5x_path = output_dir / f"{acd_path.stem}.L5X"
                
                success = False
                last_error = None
                
                # Retry logic
                for attempt in range(max_retries):
                    try:
                        logger.info(f"Converting {acd_path.name} (attempt {attempt + 1}/{max_retries})")
                        
                        # Open ACD file
                        if not self.client.open_project(str(acd_path)):
                            raise Studio5000IntegrationError(f"Failed to open {acd_path}")
                        
                        # Export to L5X
                        if not self.client.export_to_l5x(str(l5x_path)):
                            raise Studio5000IntegrationError(f"Failed to export to {l5x_path}")
                        
                        success = True
                        break
                        
                    except Exception as e:
                        last_error = str(e)
                        logger.warning(f"Conversion attempt {attempt + 1} failed", 
                                     file=acd_path.name, 
                                     error=last_error)
                        time.sleep(2)  # Brief delay before retry
                
                # Record result
                conversion_result = {
                    'input_file': str(acd_path),
                    'output_file': str(l5x_path) if success else None,
                    'success': success,
                    'error': last_error if not success else None,
                    'file_size_mb': acd_path.stat().st_size / (1024 * 1024) if acd_path.exists() else 0
                }
                
                results['conversions'].append(conversion_result)
                
                if success:
                    results['successful'] += 1
                    logger.info(f"Successfully converted {acd_path.name}")
                else:
                    results['failed'] += 1
                    results['errors'].append(f"{acd_path.name}: {last_error}")
                    logger.error(f"Failed to convert {acd_path.name}", error=last_error)
                
                # Progress update
                progress = ((i + 1) / len(acd_files)) * 100
                logger.info(f"Batch conversion progress: {progress:.1f}%")
        
        finally:
            self.client.disconnect()
        
        logger.info("Batch conversion completed", 
                   successful=results['successful'], 
                   failed=results['failed'])
        
        return results
    
    def convert_l5x_to_acd(self, l5x_files: List[str], output_dir: str) -> Dict[str, Any]:
        """
        Convert multiple L5X files to ACD format
        
        Args:
            l5x_files: List of L5X file paths
            output_dir: Directory for ACD output files
            
        Returns:
            Dictionary with conversion results
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        results = {
            'total_files': len(l5x_files),
            'successful': 0,
            'failed': 0,
            'conversions': [],
            'errors': []
        }
        
        # Connect to Studio 5000
        if not self.client.connect():
            results['errors'].append("Failed to connect to Studio 5000")
            return results
        
        try:
            for i, l5x_file in enumerate(l5x_files):
                l5x_path = Path(l5x_file)
                acd_path = output_dir / f"{l5x_path.stem}.ACD"
                
                try:
                    logger.info(f"Converting {l5x_path.name} to ACD")
                    
                    # Import L5X and save as ACD
                    if self.client.import_from_l5x(str(l5x_path), str(acd_path)):
                        results['successful'] += 1
                        logger.info(f"Successfully converted {l5x_path.name}")
                        
                        conversion_result = {
                            'input_file': str(l5x_path),
                            'output_file': str(acd_path),
                            'success': True,
                            'error': None,
                            'file_size_mb': l5x_path.stat().st_size / (1024 * 1024)
                        }
                    else:
                        raise Studio5000IntegrationError(f"Failed to import {l5x_path}")
                
                except Exception as e:
                    error_msg = str(e)
                    results['failed'] += 1
                    results['errors'].append(f"{l5x_path.name}: {error_msg}")
                    logger.error(f"Failed to convert {l5x_path.name}", error=error_msg)
                    
                    conversion_result = {
                        'input_file': str(l5x_path),
                        'output_file': None,
                        'success': False,
                        'error': error_msg,
                        'file_size_mb': l5x_path.stat().st_size / (1024 * 1024)
                    }
                
                results['conversions'].append(conversion_result)
                
                # Progress update
                progress = ((i + 1) / len(l5x_files)) * 100
                logger.info(f"Batch conversion progress: {progress:.1f}%")
        
        finally:
            self.client.disconnect()
        
        logger.info("Batch L5X to ACD conversion completed", 
                   successful=results['successful'], 
                   failed=results['failed'])
        
        return results
    
    def cleanup(self):
        """Clean up temporary files and directories"""
        try:
            if Path(self.temp_dir).exists():
                shutil.rmtree(self.temp_dir)
                logger.info("Cleaned up temporary directory", path=self.temp_dir)
        except Exception as e:
            logger.warning("Failed to clean up temporary directory", 
                          path=self.temp_dir, 
                          error=str(e))


class Studio5000ValidationService:
    """
    Service for validating Studio 5000 operations and file integrity
    """
    
    @staticmethod
    def validate_studio_installation() -> Tuple[bool, str]:
        """
        Validate Studio 5000 installation
        
        Returns:
            Tuple of (is_valid, message)
        """
        if not WINDOWS_COM_AVAILABLE:
            return False, "Windows COM automation not available"
        
        client = Studio5000AutomationClient()
        studio_path = client.find_studio_installation()
        
        if not studio_path:
            return False, "Studio 5000 installation not found"
        
        # Test COM connection
        if not client.connect():
            return False, "Failed to connect to Studio 5000 via COM"
        
        client.disconnect()
        return True, f"Studio 5000 found and accessible at {studio_path}"
    
    @staticmethod
    def validate_conversion_integrity(original_file: str, converted_file: str) -> Dict[str, Any]:
        """
        Validate integrity of file conversion
        
        Args:
            original_file: Path to original file
            converted_file: Path to converted file
            
        Returns:
            Dictionary with validation results
        """
        validation_result = {
            'original_exists': Path(original_file).exists(),
            'converted_exists': Path(converted_file).exists(),
            'file_sizes': {},
            'timestamps': {},
            'integrity_score': 0.0,
            'issues': []
        }
        
        try:
            # File existence check
            original_path = Path(original_file)
            converted_path = Path(converted_file)
            
            if original_path.exists():
                validation_result['file_sizes']['original'] = original_path.stat().st_size
                validation_result['timestamps']['original'] = original_path.stat().st_mtime
            else:
                validation_result['issues'].append("Original file not found")
            
            if converted_path.exists():
                validation_result['file_sizes']['converted'] = converted_path.stat().st_size
                validation_result['timestamps']['converted'] = converted_path.stat().st_mtime
            else:
                validation_result['issues'].append("Converted file not found")
                return validation_result
            
            # Basic integrity checks
            if validation_result['file_sizes']['converted'] > 0:
                validation_result['integrity_score'] += 0.5
            
            # Size comparison (converted files may be different sizes due to format differences)
            size_ratio = validation_result['file_sizes']['converted'] / validation_result['file_sizes']['original']
            if 0.1 <= size_ratio <= 10.0:  # Reasonable size ratio
                validation_result['integrity_score'] += 0.3
            else:
                validation_result['issues'].append(f"Unusual size ratio: {size_ratio:.2f}")
            
            # Timestamp check (converted should be newer)
            if validation_result['timestamps']['converted'] >= validation_result['timestamps']['original']:
                validation_result['integrity_score'] += 0.2
            else:
                validation_result['issues'].append("Converted file is older than original")
            
        except Exception as e:
            validation_result['issues'].append(f"Validation error: {str(e)}")
        
        return validation_result


# CLI interface and utility functions
def main():
    """Main CLI interface for Studio 5000 integration"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Studio 5000 Integration Tool")
    parser.add_argument('--validate', action='store_true', 
                       help='Validate Studio 5000 installation')
    parser.add_argument('--convert-acd', nargs='+', metavar='FILE',
                       help='Convert ACD files to L5X')
    parser.add_argument('--convert-l5x', nargs='+', metavar='FILE',
                       help='Convert L5X files to ACD')
    parser.add_argument('--output-dir', default='./output',
                       help='Output directory for conversions')
    parser.add_argument('--temp-dir', 
                       help='Temporary directory for processing')
    
    args = parser.parse_args()
    
    if args.validate:
        is_valid, message = Studio5000ValidationService.validate_studio_installation()
        print(f"Studio 5000 Validation: {'✅ PASS' if is_valid else '❌ FAIL'}")
        print(f"Message: {message}")
        return 0 if is_valid else 1
    
    if args.convert_acd:
        processor = Studio5000BatchProcessor(args.temp_dir)
        try:
            results = processor.convert_acd_to_l5x(args.convert_acd, args.output_dir)
            print(f"Conversion Results: {results['successful']}/{results['total_files']} successful")
            if results['errors']:
                print("Errors:")
                for error in results['errors']:
                    print(f"  • {error}")
            return 0 if results['failed'] == 0 else 1
        finally:
            processor.cleanup()
    
    if args.convert_l5x:
        processor = Studio5000BatchProcessor(args.temp_dir)
        try:
            results = processor.convert_l5x_to_acd(args.convert_l5x, args.output_dir)
            print(f"Conversion Results: {results['successful']}/{results['total_files']} successful")
            if results['errors']:
                print("Errors:")
                for error in results['errors']:
                    print(f"  • {error}")
            return 0 if results['failed'] == 0 else 1
        finally:
            processor.cleanup()
    
    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main()) 