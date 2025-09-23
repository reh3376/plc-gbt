#!/usr/bin/env python3
"""
Check naming conventions in the PLC Task Orchestrator codebase.

This script verifies that naming conventions follow the standards defined
in NAMING_CONVENTIONS.md.
"""

import ast
import re
import sys
from pathlib import Path


class NamingConventionChecker(ast.NodeVisitor):
    """AST visitor to check naming conventions."""

    def __init__(self, filepath: Path):
        self.filepath = filepath
        self.errors: list[tuple[int, str]] = []
        self.warnings: list[tuple[int, str]] = []

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Check class naming conventions."""
        # Classes should be PascalCase
        if not self._is_pascal_case(node.name):
            self.errors.append((node.lineno, f"Class '{node.name}' should be PascalCase"))

        # Check for type suffixes
        if node.name.endswith(("Py", "Python", "TS", "TypeScript")):
            self.errors.append(
                (node.lineno, f"Class '{node.name}' should not have language-specific suffix")
            )

        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Check function/method naming conventions."""
        # Skip special methods
        if node.name.startswith("__") and node.name.endswith("__"):
            self.generic_visit(node)
            return

        # Skip AST visitor methods (visit_NodeName pattern)
        if node.name.startswith("visit_") and len(node.name) > 6 and node.name[6].isupper():
            self.generic_visit(node)
            return

        # Methods should be snake_case
        if not self._is_snake_case(node.name):
            # Check if it's camelCase (wrong for Python)
            if self._is_camel_case(node.name):
                self.errors.append(
                    (node.lineno, f"Method '{node.name}' should be snake_case, not camelCase")
                )
            else:
                self.errors.append((node.lineno, f"Method '{node.name}' should be snake_case"))

        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        """Check constant naming conventions."""
        # Only check module-level assignments
        if (
            isinstance(node.value, ast.Constant)
            and hasattr(node, "col_offset")
            and node.col_offset == 0
        ):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    # Constants should be UPPER_SNAKE_CASE
                    if target.id.isupper():
                        if not self._is_upper_snake_case(target.id):
                            self.errors.append(
                                (node.lineno, f"Constant '{target.id}' should be UPPER_SNAKE_CASE")
                            )

        self.generic_visit(node)

    @staticmethod
    def _is_pascal_case(name: str) -> bool:
        """Check if name is PascalCase."""
        return bool(re.match(r"^[A-Z][a-zA-Z0-9]*$", name))

    @staticmethod
    def _is_snake_case(name: str) -> bool:
        """Check if name is snake_case."""
        return bool(re.match(r"^[a-z_][a-z0-9_]*$", name))

    @staticmethod
    def _is_camel_case(name: str) -> bool:
        """Check if name is camelCase."""
        return bool(re.match(r"^[a-z][a-zA-Z0-9]*$", name))

    @staticmethod
    def _is_upper_snake_case(name: str) -> bool:
        """Check if name is UPPER_SNAKE_CASE."""
        return bool(re.match(r"^[A-Z][A-Z0-9_]*$", name))


def check_file(filepath: Path) -> tuple[list[tuple[int, str]], list[tuple[int, str]]]:
    """Check a single Python file for naming convention violations."""
    try:
        with open(filepath, encoding="utf-8") as f:
            content = f.read()

        tree = ast.parse(content, filename=str(filepath))
        checker = NamingConventionChecker(filepath)
        checker.visit(tree)

        return checker.errors, checker.warnings

    except SyntaxError as e:
        return [(e.lineno or 0, f"Syntax error: {e.msg}")], []
    except Exception as e:
        return [(0, f"Error processing file: {str(e)}")], []


def check_enum_consistency(filepath: Path) -> list[tuple[int, str]]:
    """Check enum value consistency."""
    errors = []

    try:
        with open(filepath, encoding="utf-8") as f:
            content = f.read()

        # Look for enum definitions
        enum_pattern = re.compile(
            r'class\s+(\w+)\(Enum\):\s*\n((?:\s+\w+\s*=\s*["\'][\w-]+["\']\s*\n)+)', re.MULTILINE
        )

        for match in enum_pattern.finditer(content):
            enum_name = match.group(1)
            enum_body = match.group(2)

            # Check each enum value
            value_pattern = re.compile(r'\s+(\w+)\s*=\s*["\']([\w-]+)["\']')
            for value_match in value_pattern.finditer(enum_body):
                const_name = value_match.group(1)
                const_value = value_match.group(2)

                # Enum members should be UPPER_SNAKE_CASE
                if not re.match(r"^[A-Z][A-Z0-9_]*$", const_name):
                    line_no = content[: match.start()].count("\n") + 1
                    errors.append(
                        (
                            line_no,
                            f"Enum member '{const_name}' in '{enum_name}' should be UPPER_SNAKE_CASE",
                        )
                    )

                # Enum values should be lowercase
                if const_value != const_value.lower():
                    line_no = content[: value_match.start()].count("\n") + 1
                    errors.append((line_no, f"Enum value '{const_value}' should be lowercase"))

    except Exception as e:
        errors.append((0, f"Error checking enums: {str(e)}"))

    return errors


def main():
    """Main entry point."""
    # Find all Python files in the package
    package_dir = Path(__file__).parent / "plc_orchestrator"

    if not package_dir.exists():
        print("Error: plc_orchestrator package not found!")
        sys.exit(1)

    python_files = list(package_dir.rglob("*.py"))

    total_errors = 0
    total_warnings = 0

    print("🔍 Checking naming conventions in PLC Task Orchestrator...\n")

    for filepath in sorted(python_files):
        # Skip __pycache__ and test files
        if "__pycache__" in str(filepath) or "test_" in filepath.name:
            continue

        errors, warnings = check_file(filepath)
        enum_errors = check_enum_consistency(filepath)
        errors.extend(enum_errors)

        if errors or warnings:
            rel_path = filepath.relative_to(package_dir.parent)
            print(f"📄 {rel_path}")

            for line_no, error in sorted(errors):
                print(f"  ❌ Line {line_no}: {error}")
                total_errors += 1

            for line_no, warning in sorted(warnings):
                print(f"  ⚠️  Line {line_no}: {warning}")
                total_warnings += 1

            print()

    # Summary
    print("\n" + "=" * 60)
    print(f"✅ Checked {len(python_files)} files")

    if total_errors == 0 and total_warnings == 0:
        print("🎉 All naming conventions are correct!")
        sys.exit(0)
    else:
        print(f"❌ Found {total_errors} errors and {total_warnings} warnings")

        if total_errors > 0:
            print("\nPlease fix the errors to comply with naming conventions.")
            print("See NAMING_CONVENTIONS.md for guidelines.")
            sys.exit(1)
        else:
            sys.exit(0)


if __name__ == "__main__":
    main()
