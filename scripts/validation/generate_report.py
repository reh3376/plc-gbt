#!/usr/bin/env python3
"""
PLC Repository Validation Report Generator

This script generates validation reports for PLC repositories as part of the CI/CD pipeline.
"""

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def validate_plc_files(repo_path: Path) -> Dict[str, Any]:
    """Validate PLC files in the repository."""
    results = {
        'total_files': 0,
        'valid_files': 0,
        'invalid_files': 0,
        'l5x_files': 0,
        'acd_files': 0,
        'errors': [],
        'warnings': []
    }
    
    try:
        # Find L5X files
        l5x_files = list(repo_path.rglob('*.L5X'))
        results['l5x_files'] = len(l5x_files)
        
        # Find ACD files
        acd_files = list(repo_path.rglob('*.ACD'))
        results['acd_files'] = len(acd_files)
        
        results['total_files'] = len(l5x_files) + len(acd_files)
        
        # Validate L5X files
        for l5x_file in l5x_files:
            try:
                import xml.etree.ElementTree as ET
                tree = ET.parse(l5x_file)
                root = tree.getroot()
                
                # Basic validation
                if root.tag == 'RSLogix5000Content':
                    results['valid_files'] += 1
                    logger.info(f"✅ Valid L5X: {l5x_file}")
                else:
                    results['invalid_files'] += 1
                    results['errors'].append(f"Invalid L5X root element in {l5x_file}")
                    
            except ET.ParseError as e:
                results['invalid_files'] += 1
                results['errors'].append(f"XML parse error in {l5x_file}: {e}")
            except Exception as e:
                results['invalid_files'] += 1
                results['errors'].append(f"Error validating {l5x_file}: {e}")
        
        # Validate ACD files (basic size check)
        for acd_file in acd_files:
            try:
                size = acd_file.stat().st_size
                if size > 1024:  # Larger than 1KB
                    results['valid_files'] += 1
                    logger.info(f"✅ Valid ACD: {acd_file} ({size} bytes)")
                else:
                    results['warnings'].append(f"Small ACD file: {acd_file} ({size} bytes)")
                    results['valid_files'] += 1  # Still count as valid for now
                    
            except Exception as e:
                results['invalid_files'] += 1
                results['errors'].append(f"Error checking {acd_file}: {e}")
        
        logger.info(f"Validation complete: {results['valid_files']}/{results['total_files']} files valid")
        return results
        
    except Exception as e:
        logger.error(f"Validation failed: {e}")
        results['errors'].append(f"Validation process failed: {e}")
        return results


def generate_report(repo: str, output_path: Path = None) -> Dict[str, Any]:
    """Generate validation report for the specified repository."""
    logger.info(f"Generating validation report for repository: {repo}")
    
    # Use current directory if no specific repo path provided
    repo_path = Path('.')
    
    report = {
        'repository': repo,
        'generated_at': datetime.now().isoformat(),
        'validation_results': validate_plc_files(repo_path),
        'summary': {}
    }
    
    # Generate summary
    validation = report['validation_results']
    report['summary'] = {
        'status': 'PASS' if validation['invalid_files'] == 0 else 'FAIL',
        'total_files': validation['total_files'],
        'success_rate': validation['valid_files'] / max(validation['total_files'], 1) * 100,
        'error_count': len(validation['errors']),
        'warning_count': len(validation['warnings'])
    }
    
    # Save report if output path specified
    if output_path:
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        logger.info(f"Report saved to {output_path}")
    
    # Print summary
    print(f"\n📊 Validation Report for {repo}")
    print(f"Status: {report['summary']['status']}")
    print(f"Files: {validation['total_files']} total ({validation['l5x_files']} L5X, {validation['acd_files']} ACD)")
    print(f"Valid: {validation['valid_files']}/{validation['total_files']} ({report['summary']['success_rate']:.1f}%)")
    
    if validation['errors']:
        print(f"\n❌ Errors ({len(validation['errors'])}):")
        for error in validation['errors'][:5]:  # Show first 5 errors
            print(f"  - {error}")
        if len(validation['errors']) > 5:
            print(f"  ... and {len(validation['errors']) - 5} more errors")
    
    if validation['warnings']:
        print(f"\n⚠️ Warnings ({len(validation['warnings'])}):")
        for warning in validation['warnings'][:3]:  # Show first 3 warnings
            print(f"  - {warning}")
        if len(validation['warnings']) > 3:
            print(f"  ... and {len(validation['warnings']) - 3} more warnings")
    
    return report


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Generate PLC repository validation report')
    parser.add_argument('--repo', required=True, help='Repository identifier')
    parser.add_argument('--output', type=Path, help='Output file path for JSON report')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        report = generate_report(args.repo, args.output)
        
        # Exit with error code if validation failed
        if report['summary']['status'] == 'FAIL':
            logger.error("Validation failed - exiting with error code 1")
            sys.exit(1)
        else:
            logger.info("Validation passed - exiting with success")
            sys.exit(0)
            
    except Exception as e:
        logger.error(f"Report generation failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main() 