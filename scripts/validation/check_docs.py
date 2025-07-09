#!/usr/bin/env python3
"""
Documentation Validation Script

This script validates that the repository documentation is complete and up-to-date.
"""

import logging
import sys
from pathlib import Path
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def check_required_files() -> Dict[str, Any]:
    """Check for required documentation files."""
    required_files = [
        'README.md',
        'INSTALLATION.md',
        'docs/architecture-decisions.md',
        'docs/coding-standards.md'
    ]
    
    results = {
        'missing_files': [],
        'found_files': [],
        'total_required': len(required_files)
    }
    
    for file_path in required_files:
        path = Path(file_path)
        if path.exists():
            results['found_files'].append(file_path)
            logger.info(f"✅ Found: {file_path}")
        else:
            results['missing_files'].append(file_path)
            logger.warning(f"❌ Missing: {file_path}")
    
    return results


def check_readme_content() -> Dict[str, Any]:
    """Check README.md content for required sections."""
    readme_path = Path('README.md')
    results = {
        'has_readme': False,
        'missing_sections': [],
        'found_sections': []
    }
    
    required_sections = [
        'Installation',
        'Usage',
        'Features',
        'Requirements'
    ]
    
    if not readme_path.exists():
        results['missing_sections'] = required_sections
        return results
    
    results['has_readme'] = True
    
    try:
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read().lower()
        
        for section in required_sections:
            if section.lower() in content:
                results['found_sections'].append(section)
                logger.info(f"✅ README section found: {section}")
            else:
                results['missing_sections'].append(section)
                logger.warning(f"❌ README section missing: {section}")
                
    except Exception as e:
        logger.error(f"Error reading README.md: {e}")
        results['missing_sections'] = required_sections
    
    return results


def check_docs_directory() -> Dict[str, Any]:
    """Check docs directory structure."""
    docs_path = Path('docs')
    results = {
        'has_docs_dir': False,
        'doc_files': [],
        'missing_docs': []
    }
    
    if not docs_path.exists():
        logger.warning("❌ docs/ directory not found")
        return results
    
    results['has_docs_dir'] = True
    logger.info("✅ docs/ directory found")
    
    # Find all markdown files in docs
    doc_files = list(docs_path.rglob('*.md'))
    results['doc_files'] = [str(f.relative_to(docs_path)) for f in doc_files]
    
    logger.info(f"📄 Found {len(doc_files)} documentation files:")
    for doc_file in doc_files:
        logger.info(f"  - {doc_file.relative_to(docs_path)}")
    
    return results


def check_changelog() -> Dict[str, Any]:
    """Check for changelog file."""
    changelog_files = ['CHANGELOG.md', 'HISTORY.md', 'CHANGES.md']
    results = {
        'has_changelog': False,
        'changelog_file': None
    }
    
    for filename in changelog_files:
        path = Path(filename)
        if path.exists():
            results['has_changelog'] = True
            results['changelog_file'] = filename
            logger.info(f"✅ Found changelog: {filename}")
            break
    
    if not results['has_changelog']:
        logger.warning("❌ No changelog file found")
    
    return results


def validate_documentation() -> Dict[str, Any]:
    """Run all documentation validation checks."""
    logger.info("🔍 Starting documentation validation...")
    
    validation_results = {
        'required_files': check_required_files(),
        'readme_content': check_readme_content(),
        'docs_directory': check_docs_directory(),
        'changelog': check_changelog()
    }
    
    # Calculate overall status
    required_files = validation_results['required_files']
    readme_content = validation_results['readme_content']
    
    total_issues = (
        len(required_files['missing_files']) +
        len(readme_content['missing_sections'])
    )
    
    validation_results['summary'] = {
        'status': 'PASS' if total_issues == 0 else 'FAIL',
        'total_issues': total_issues,
        'files_found': len(required_files['found_files']),
        'files_required': required_files['total_required'],
        'readme_sections_found': len(readme_content['found_sections']),
        'has_docs_directory': validation_results['docs_directory']['has_docs_dir'],
        'has_changelog': validation_results['changelog']['has_changelog']
    }
    
    return validation_results


def print_summary(results: Dict[str, Any]) -> None:
    """Print validation summary."""
    summary = results['summary']
    
    print(f"\n📋 Documentation Validation Summary")
    print(f"Status: {summary['status']}")
    print(f"Required files: {summary['files_found']}/{summary['files_required']} found")
    print(f"README sections: {summary['readme_sections_found']}/4 found")
    print(f"Docs directory: {'✅ Yes' if summary['has_docs_directory'] else '❌ No'}")
    print(f"Changelog: {'✅ Yes' if summary['has_changelog'] else '❌ No'}")
    
    if summary['total_issues'] > 0:
        print(f"\n❌ Issues to resolve ({summary['total_issues']}):")
        
        missing_files = results['required_files']['missing_files']
        if missing_files:
            print(f"  Missing files:")
            for file in missing_files:
                print(f"    - {file}")
        
        missing_sections = results['readme_content']['missing_sections']
        if missing_sections:
            print(f"  Missing README sections:")
            for section in missing_sections:
                print(f"    - {section}")
    else:
        print("\n✅ All documentation requirements met!")


def main():
    """Main entry point."""
    try:
        results = validate_documentation()
        print_summary(results)
        
        # Exit with appropriate code
        if results['summary']['status'] == 'PASS':
            logger.info("Documentation validation passed")
            sys.exit(0)
        else:
            logger.error("Documentation validation failed")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Documentation validation error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main() 