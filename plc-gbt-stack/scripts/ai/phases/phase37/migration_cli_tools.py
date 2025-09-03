#!/usr/bin/env python3
"""
Enhanced Migration CLI Tools for PLC Format Conversion
====================================================

This module provides comprehensive CLI tools for migrating PLC files between
ACD and L5X formats using the enhanced plc-format-converter library.

Enhanced Features:
- Full acd-tools integration for enhanced ACD parsing
- Comprehensive error handling and reporting
- Batch processing capabilities
- Validation and verification
- Dry-run support for testing
"""

import json
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / 'src'))

try:
    # Use import utility
    from plc_converter_import import import_plc_converter
    PLCConverter = import_plc_converter()
    from plc_format_converter.core.models import ConversionResult
    print("✅ Successfully imported PLCConverter with enhanced functionality")
except ImportError as e:
    print(f"❌ Failed to import PLCConverter: {e}")
    sys.exit(1)

class MigrationCLI:
    """Enhanced CLI interface for PLC file migration"""

    def __init__(self):
        """Initialize the migration CLI with enhanced converter"""
        try:
            self.converter = PLCConverter()
            self.errors = []
            self.warnings = []
            self.processed_files = []
            print("✅ MigrationCLI initialized with enhanced converter")
        except Exception as e:
            print(f"❌ Failed to initialize MigrationCLI: {e}")
            raise

    def validate_file(self, file_path: str) -> bool:
        """
        Validate a PLC file

        Args:
            file_path: Path to the PLC file to validate

        Returns:
            bool: True if file is valid, False otherwise
        """
        try:
            if not os.path.exists(file_path):
                self.errors.append(f"File not found: {file_path}")
                return False

            # Use the converter's validate_file method
            result = self.converter.validate_file(file_path)

            if result:
                print(f"✅ File validation successful: {file_path}")
                return True
            else:
                self.errors.append(f"File validation failed: {file_path}")
                return False

        except Exception as e:
            error_msg = f"Validation error for {file_path}: {str(e)}"
            self.errors.append(error_msg)
            print(f"❌ {error_msg}")
            return False

    def convert_file(self, input_path: str, output_path: str, dry_run: bool = False) -> bool:
        """
        Convert a single PLC file

        Args:
            input_path: Path to input file
            output_path: Path for output file
            dry_run: If True, perform validation only without writing output

        Returns:
            bool: True if conversion successful, False otherwise
        """
        try:
            if not os.path.exists(input_path):
                self.errors.append(f"Input file not found: {input_path}")
                return False

            # Determine conversion type based on file extensions
            input_ext = Path(input_path).suffix.lower()
            output_ext = Path(output_path).suffix.lower()

            print(f"🔄 Converting {input_ext} → {output_ext}: {Path(input_path).name}")

            if dry_run:
                print("  (Dry run - validation only)")
                # For dry run, just validate the input file
                return self.validate_file(input_path)

            # Perform actual conversion
            if input_ext in ['.acd'] and output_ext in ['.l5x']:
                result = self.converter.acd_to_l5x(input_path, output_path)
            elif input_ext in ['.l5x'] and output_ext in ['.acd']:
                result = self.converter.l5x_to_acd(input_path, output_path)
            else:
                result = self.converter.convert_file(input_path, output_path)

            if result:
                self.processed_files.append({
                    'input': input_path,
                    'output': output_path,
                    'timestamp': datetime.now().isoformat(),
                    'success': True
                })
                print(f"✅ Conversion successful: {output_path}")
                return True
            else:
                self.errors.append(f"Conversion failed: {input_path} → {output_path}")
                return False

        except Exception as e:
            error_msg = f"Conversion error: {input_path} → {output_path}: {str(e)}"
            self.errors.append(error_msg)
            print(f"❌ {error_msg}")
            return False

    def batch_convert(self, input_files: List[str], output_dir: str, dry_run: bool = False) -> bool:
        """
        Convert multiple PLC files in batch

        Args:
            input_files: List of input file paths
            output_dir: Directory for output files
            dry_run: If True, perform validation only

        Returns:
            bool: True if all conversions successful, False otherwise
        """
        try:
            if not dry_run:
                # Create output directory if it doesn't exist
                os.makedirs(output_dir, exist_ok=True)

            success_count = 0
            total_files = len(input_files)

            print(f"📦 Batch processing {total_files} files")
            if dry_run:
                print("  (Dry run - validation only)")

            for i, input_file in enumerate(input_files, 1):
                print(f"\n[{i}/{total_files}] Processing: {Path(input_file).name}")

                if dry_run:
                    # For dry run, just validate
                    if self.validate_file(input_file):
                        success_count += 1
                else:
                    # Determine output file name and path
                    input_path = Path(input_file)
                    if input_path.suffix.lower() == '.acd':
                        output_name = input_path.stem + '.L5X'
                    else:
                        output_name = input_path.stem + '.ACD'

                    output_path = os.path.join(output_dir, output_name)

                    # Convert file
                    if self.convert_file(input_file, output_path, dry_run=False):
                        success_count += 1

            success_rate = (success_count / total_files) * 100
            print(f"\n📊 Batch processing complete: {success_count}/{total_files} files processed successfully ({success_rate:.1f}%)")

            return success_count == total_files

        except Exception as e:
            error_msg = f"Batch conversion error: {str(e)}"
            self.errors.append(error_msg)
            print(f"❌ {error_msg}")
            return False

    def migrate_repository(self, repo_path: str, output_path: str, dry_run: bool = False) -> bool:
        """
        Migrate an entire repository of PLC files

        Args:
            repo_path: Path to repository containing PLC files
            output_path: Path for migrated repository
            dry_run: If True, perform validation only

        Returns:
            bool: True if migration successful, False otherwise
        """
        try:
            repo_path = Path(repo_path)
            if not repo_path.exists():
                self.errors.append(f"Repository not found: {repo_path}")
                return False

            # Find all PLC files in the repository
            plc_files = []
            for pattern in ['*.acd', '*.ACD', '*.l5x', '*.L5X']:
                plc_files.extend(repo_path.rglob(pattern))

            if not plc_files:
                self.warnings.append(f"No PLC files found in repository: {repo_path}")
                return True

            print(f"🏗️  Migrating repository: {repo_path}")
            print(f"   Found {len(plc_files)} PLC files")

            if dry_run:
                print("   (Dry run - validation only)")
                # For dry run, validate all files
                return self.batch_convert([str(f) for f in plc_files], str(output_path), dry_run=True)
            else:
                # Create output directory structure
                output_path = Path(output_path)
                output_path.mkdir(parents=True, exist_ok=True)

                # Copy repository structure
                shutil.copytree(repo_path, output_path, dirs_exist_ok=True)

                # Convert PLC files in place
                success_count = 0
                for plc_file in plc_files:
                    # Calculate relative path and output location
                    rel_path = plc_file.relative_to(repo_path)
                    output_file = output_path / rel_path

                    # Convert file
                    if self.convert_file(str(plc_file), str(output_file)):
                        success_count += 1

                success_rate = (success_count / len(plc_files)) * 100
                print(f"✅ Repository migration complete: {success_count}/{len(plc_files)} files migrated ({success_rate:.1f}%)")

                return success_count == len(plc_files)

        except Exception as e:
            error_msg = f"Repository migration error: {str(e)}"
            self.errors.append(error_msg)
            print(f"❌ {error_msg}")
            return False

    def generate_report(self, output_file: Optional[str] = None) -> Dict:
        """
        Generate a comprehensive migration report

        Args:
            output_file: Optional file path to save the report

        Returns:
            Dict: Migration report data
        """
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_files_processed': len(self.processed_files),
                'successful_conversions': len([f for f in self.processed_files if f.get('success', False)]),
                'errors': len(self.errors),
                'warnings': len(self.warnings)
            },
            'processed_files': self.processed_files,
            'errors': self.errors,
            'warnings': self.warnings,
            'converter_info': {
                'acd_tools_available': True,  # We have enhanced functionality
                'studio5000_available': False,  # Windows COM dependency
                'enhanced_parsing': True
            }
        }

        if output_file:
            with open(output_file, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"📄 Report saved: {output_file}")

        return report

    def print_summary(self):
        """Print a summary of the migration session"""
        print("\n" + "="*60)
        print("📊 Migration Summary")
        print("="*60)
        print(f"Files processed: {len(self.processed_files)}")
        print(f"Successful conversions: {len([f for f in self.processed_files if f.get('success', False)])}")
        print(f"Errors: {len(self.errors)}")
        print(f"Warnings: {len(self.warnings)}")

        if self.errors:
            print("\n❌ Errors:")
            for error in self.errors:
                print(f"  - {error}")

        if self.warnings:
            print("\n⚠️  Warnings:")
            for warning in self.warnings:
                print(f"  - {warning}")

def main():
    """Main CLI entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Enhanced PLC Migration CLI Tools')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate PLC files')
    validate_parser.add_argument('files', nargs='+', help='PLC files to validate')

    # Convert command
    convert_parser = subparsers.add_parser('convert', help='Convert PLC files')
    convert_parser.add_argument('input', help='Input file path')
    convert_parser.add_argument('output', help='Output file path')
    convert_parser.add_argument('--dry-run', action='store_true', help='Validation only, no output')

    # Batch convert command
    batch_parser = subparsers.add_parser('batch', help='Batch convert PLC files')
    batch_parser.add_argument('input_dir', help='Input directory')
    batch_parser.add_argument('output_dir', help='Output directory')
    batch_parser.add_argument('--dry-run', action='store_true', help='Validation only, no output')

    # Migrate repository command
    migrate_parser = subparsers.add_parser('migrate', help='Migrate entire repository')
    migrate_parser.add_argument('repo_path', help='Repository path')
    migrate_parser.add_argument('output_path', help='Output repository path')
    migrate_parser.add_argument('--dry-run', action='store_true', help='Validation only, no output')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Initialize CLI
    cli = MigrationCLI()

    try:
        if args.command == 'validate':
            success = True
            for file_path in args.files:
                if not cli.validate_file(file_path):
                    success = False
            sys.exit(0 if success else 1)

        elif args.command == 'convert':
            success = cli.convert_file(args.input, args.output, dry_run=args.dry_run)
            sys.exit(0 if success else 1)

        elif args.command == 'batch':
            # Find all PLC files in input directory
            input_path = Path(args.input_dir)
            plc_files = []
            for pattern in ['*.acd', '*.ACD', '*.l5x', '*.L5X']:
                plc_files.extend(input_path.rglob(pattern))

            success = cli.batch_convert([str(f) for f in plc_files], args.output_dir, dry_run=args.dry_run)
            sys.exit(0 if success else 1)

        elif args.command == 'migrate':
            success = cli.migrate_repository(args.repo_path, args.output_path, dry_run=args.dry_run)
            sys.exit(0 if success else 1)

    finally:
        cli.print_summary()

if __name__ == '__main__':
    main()
