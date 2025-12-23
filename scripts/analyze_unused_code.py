#!/usr/bin/env python3
"""Analyze Unused/Test-Only Code in gruponos-meltano-native.

This script analyzes the codebase to identify classes, functions, and modules
that are only used in tests but not in actual application code. Such code
can be safely removed to reduce maintenance burden and improve code quality.

Usage:
    python scripts/analyze_unused_code.py [options]

Author: Code Quality Analysis Team
Version: 1.0.0
"""

import argparse
import ast
import logging
import os
import re
import sys
import traceback
from datetime import UTC, datetime
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Import serena tools if available
try:
    from gruponos_meltano_native.core.serena_client import SerenaClient  # noqa: F401

    SERENA_AVAILABLE = True
except ImportError:
    SERENA_AVAILABLE = False


class UnusedCodeAnalyzer:
    """Analyzer for identifying unused/test-only code."""

    def __init__(self, project_root: Path) -> None:
        """Initialize analyzer with project root path."""
        self.project_root = project_root
        self.src_dir = project_root / "src" / "gruponos_meltano_native"
        self.tests_dir = project_root / "tests"
        self.results = {
            "test_only_classes": [],
            "test_only_functions": [],
            "unused_modules": [],
            "exported_but_unused": [],
            "dead_code_candidates": [],
        }

    def analyze(self) -> dict:
        """Perform comprehensive unused code analysis."""
        print("🔍 Analyzing codebase for unused/test-only code...")

        # Get all exported symbols from main package
        exported_symbols = self._get_exported_symbols()

        # Analyze each exported symbol
        for symbol in exported_symbols:
            usage = self._analyze_symbol_usage(symbol)
            if usage["only_in_tests"]:
                self.results["exported_but_unused"].append({
                    "symbol": symbol,
                    "test_files": usage["test_files"],
                    "definition_file": usage["definition_file"],
                })

        # Analyze modules for complete unused status
        self._analyze_module_usage()

        # Identify dead code candidates
        self._identify_dead_code()

        return self.results

    def _get_exported_symbols(self) -> list[str]:
        """Extract all symbols exported from the main package."""
        init_file = self.src_dir / "__init__.py"
        if not init_file.exists():
            return []

        content = Path(init_file).read_text(encoding="utf-8")

        # Find __all__ list
        all_match = re.search(r"__all__\s*=\s*\[([^\]]+)\]", content, re.DOTALL)
        if not all_match:
            return []

        all_content = all_match.group(1)

        # Extract quoted strings
        return re.findall(r'["\']([^"\']+)["\']', all_content)

    def _analyze_symbol_usage(self, symbol: str) -> dict:
        """Analyze where a symbol is used."""
        result = {
            "symbol": symbol,
            "definition_file": None,
            "src_usage": [],
            "test_usage": [],
            "test_files": [],
            "only_in_tests": False,
        }

        # Find definition file
        result["definition_file"] = self._find_symbol_definition(symbol)

        # Find all usages
        result["src_usage"] = self._grep_symbol_usage(
            symbol, self.src_dir, exclude_tests=True
        )
        result["test_usage"] = self._grep_symbol_usage(
            symbol, self.tests_dir, exclude_tests=False
        )

        # Extract test file names
        result["test_files"] = [usage["file"] for usage in result["test_usage"]]

        # Determine if only used in tests
        src_usage_count = len([
            u for u in result["src_usage"] if "__init__.py" not in u["file"]
        ])
        test_usage_count = len(result["test_usage"])

        result["only_in_tests"] = src_usage_count == 0 and test_usage_count > 0

        return result

    def _find_symbol_definition(self, symbol: str) -> str:
        """Find where a symbol is defined."""
        for py_file in self.src_dir.rglob("*.py"):
            try:
                content = Path(py_file).read_text(encoding="utf-8")

                # Check for class definition
                if re.search(rf"^class\s+{re.escape(symbol)}\b", content, re.MULTILINE):
                    return str(py_file.relative_to(self.project_root))

                # Check for function definition
                if re.search(rf"^def\s+{re.escape(symbol)}\b", content, re.MULTILINE):
                    return str(py_file.relative_to(self.project_root))

            except (OSError, ValueError) as e:
                logger.debug(f"Error reading {py_file}: {e}")

        return "unknown"

    def _grep_symbol_usage(
        self, symbol: str, search_dir: Path, *, exclude_tests: bool = True
    ) -> list[dict]:
        """Find all usages of a symbol in a directory.

        Args:
            symbol: The symbol name to search for.
            search_dir: Directory to search in.
            exclude_tests: Whether to exclude test files.

        Returns:
            List of usage dictionaries with file, line, and content.

        """
        usages: list[dict] = []

        for py_file in search_dir.rglob("*.py"):
            if exclude_tests and "test" in str(py_file).lower():
                continue

            try:
                content = Path(py_file).read_text(encoding="utf-8")

                # Find symbol usages (not definitions)
                lines = content.split("\n")
                for i, line in enumerate(lines, 1):
                    # Skip comments and docstrings
                    if line.strip().startswith("#") or '"""' in line or "'''" in line:
                        continue

                    # Skip class/function definitions
                    if re.search(rf"^(class|def)\s+{re.escape(symbol)}\b", line):
                        continue

                    # Check for symbol usage
                    if (
                        symbol in line
                        and not line.strip().startswith("from ")
                        and not line.strip().startswith("import ")
                    ):
                        usages.append({
                            "file": str(py_file.relative_to(self.project_root)),
                            "line": i,
                            "content": line.strip(),
                        })

            except (OSError, ValueError) as e:
                logger.debug(f"Error reading {py_file}: {e}")

        return usages

    def _analyze_module_usage(self) -> None:
        """Analyze which modules are completely unused."""
        modules: list[dict] = []

        # Get all Python modules in src
        for py_file in self.src_dir.rglob("*.py"):
            if "__init__.py" in str(py_file):
                continue

            module_name = (
                str(py_file.relative_to(self.src_dir))
                .replace(".py", "")
                .replace("/", ".")
            )

            # Check if module is imported anywhere
            imported = False
            for other_file in self.src_dir.rglob("*.py"):
                if other_file == py_file:
                    continue

                try:
                    content = Path(other_file).read_text(encoding="utf-8")

                    if (
                        f"from gruponos_meltano_native.{module_name}" in content
                        or f"import {module_name}" in content
                    ):
                        imported = True
                        break
                except (OSError, ValueError) as e:
                    logger.debug(f"Error reading {other_file}: {e}")

            if not imported:
                modules.append({
                    "module": module_name,
                    "file": str(py_file.relative_to(self.project_root)),
                })

        self.results["unused_modules"] = modules

    def _identify_dead_code(self) -> None:
        """Identify potential dead code candidates."""
        dead_candidates: list[dict] = []

        # Look for functions/methods that are never called
        for py_file in self.src_dir.rglob("*.py"):
            try:
                content = Path(py_file).read_text(encoding="utf-8")

                # Parse AST to find function definitions
                tree = ast.parse(content)

                for node in ast.walk(tree):
                    if not isinstance(node, ast.FunctionDef):
                        continue

                    func_name = node.name

                    # Skip special methods
                    if func_name.startswith("_") or func_name in {
                        "__init__",
                        "__post_init__",
                    }:
                        continue

                    # Check if function is called anywhere
                    if not self._is_function_called(func_name, py_file):
                        dead_candidates.append({
                            "function": func_name,
                            "file": str(py_file.relative_to(self.project_root)),
                            "line": node.lineno,
                        })

            except (SyntaxError, OSError, ValueError) as e:
                logger.debug(f"Error parsing {py_file}: {e}")

        self.results["dead_code_candidates"] = dead_candidates

    def _is_function_called(self, func_name: str, current_file: Path) -> bool:
        """Check if a function is called in any other file.

        Args:
            func_name: The function name to search for.
            current_file: The file defining the function.

        Returns:
            True if the function is called somewhere, False otherwise.

        """
        for other_file in self.src_dir.rglob("*.py"):
            if other_file == current_file:
                continue

            try:
                other_content = Path(other_file).read_text(encoding="utf-8")

                if f"{func_name}(" in other_content:
                    return True
            except (OSError, ValueError) as e:
                logger.debug(f"Error reading {other_file}: {e}")

        return False

    def generate_report(self, output_file: Path | None = None) -> str:
        """Generate a comprehensive analysis report.

        Args:
            output_file: Optional path to write the report to.

        Returns:
            The generated report as a string.

        """
        now = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")
        report = f"""# Unused/Test-Only Code Analysis Report

**Generated:** {os.environ.get("USER", "system")} on {now}
**Project:** gruponos-meltano-native
**Analysis Tool:** Custom AST-based analyzer

## Executive Summary

- **Exported Symbols Analyzed:** {len(self._get_exported_symbols())}
- **Test-Only Symbols Found:** {len(self.results["exported_but_unused"])}
- **Unused Modules:** {len(self.results["unused_modules"])}
- **Dead Code Candidates:** {len(self.results["dead_code_candidates"])}

## Test-Only Exported Symbols

These symbols are exported from the main package but only used in tests. They can be safely removed.

"""

        for item in self.results["exported_but_unused"]:
            report += f"""### `{item["symbol"]}`
- **Definition:** `{item["definition_file"]}`
- **Test Files:** {len(item["test_files"])} files
- **Recommendation:** Remove from `__all__` and consider deleting if truly unused

"""

        report += """
## Unused Modules

These modules are not imported by any other module in the codebase.

"""

        for module in self.results["unused_modules"]:
            report += f"""### `{module["module"]}`
- **File:** `{module["file"]}`
- **Status:** Not imported anywhere
- **Recommendation:** Review for necessity; may be safe to remove

"""

        report += """
## Dead Code Candidates

These functions/methods are defined but never called in the codebase.

"""

        for func in self.results["dead_code_candidates"][:20]:  # Limit to 20
            report += f"""### `{func["function"]}`
- **File:** `{func["file"]}:{func["line"]}`
- **Status:** No calls found
- **Recommendation:** Review for necessity; may be unused code

"""

        report += """
## Recommendations

### Immediate Actions (Safe Removals)
1. **Remove test-only exports** from `__init__.py` `__all__` list
2. **Review unused modules** - check if they contain important functionality
3. **Clean up dead code** - remove obviously unused functions

### Careful Considerations
1. **Check for external usage** - symbols might be used by external consumers
2. **Review test coverage** - ensure removing code doesn't break tests
3. **Check documentation** - update docs that reference removed code
4. **Version control** - ensure changes are properly committed

### Long-term Improvements
1. **Implement automated checks** in CI/CD pipeline
2. **Add code coverage reporting** for unused code detection
3. **Establish code ownership** guidelines
4. **Create cleanup schedules** for regular maintenance

## Files to Modify

### `src/gruponos_meltano_native/__init__.py`
Remove the following from `__all__`:
"""
        test_only_symbols = [
            item["symbol"] for item in self.results["exported_but_unused"]
        ]
        for symbol in test_only_symbols:
            report += f"""- `"{symbol}"`\n"""

        report += """
### Files to Review for Deletion
"""
        for module in self.results["unused_modules"]:
            report += f"""- `{module["file"]}` - `{module["module"]}` module\n"""

        report += """
## Risk Assessment

### Low Risk (Safe to Remove)
- Test-only exported symbols
- Obviously unused helper functions
- Duplicate or redundant code

### Medium Risk (Review Required)
- Unused modules with complex functionality
- Functions that might be used by external consumers
- Code referenced in documentation

### High Risk (Careful Analysis Required)
- Core infrastructure code
- Code that might be used in future features
- Code with external API contracts

## Implementation Plan

### Phase 1: Safe Removals (Week 1)
- [ ] Remove test-only symbols from `__all__`
- [ ] Delete obviously unused helper functions
- [ ] Clean up dead code in utility modules

### Phase 2: Module Review (Week 2)
- [ ] Review unused modules for business value
- [ ] Check external dependencies and consumers
- [ ] Update documentation and examples

### Phase 3: Testing & Validation (Week 3)
- [ ] Run full test suite after removals
- [ ] Validate no breaking changes
- [ ] Update CI/CD pipelines
- [ ] Monitor for any issues in production

### Phase 4: Documentation Update (Week 4)
- [ ] Update API documentation
- [ ] Remove references to deleted code
- [ ] Update examples and tutorials
- [ ] Communicate changes to team

## Metrics & Success Criteria

### Quality Metrics
- **Lines of Code Reduced:** Target 20-30% reduction in unused code
- **Test Coverage Maintained:** No decrease in test coverage
- **Build Time Improved:** Faster compilation and testing
- **Maintenance Burden Reduced:** Fewer files to maintain

### Success Criteria
- [ ] All tests pass after cleanup
- [ ] No breaking changes for external consumers
- [ ] Documentation accurately reflects codebase
- [ ] Team feedback positive on code clarity
- [ ] Automated checks prevent future accumulation

---

*This report was generated by automated code analysis. Review all recommendations carefully before implementing changes.*
"""

        if output_file:
            output_file.parent.mkdir(parents=True, exist_ok=True)
            Path(output_file).write_text(report, encoding="utf-8")
            print(f"📄 Report saved to: {output_file}")

        return report


def main() -> int:
    """Main entry point for the unused code analyzer.

    Returns:
        Exit code: 0 on success, 1 on failure.

    """
    parser = argparse.ArgumentParser(
        description="Analyze Unused/Test-Only Code in gruponos-meltano-native",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/analyze_unused_code.py --output reports/unused_code_analysis.md
  python scripts/analyze_unused_code.py --verbose
        """,
    )

    parser.add_argument(
        "--output", "-o", type=str, help="Output file for the analysis report"
    )

    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output"
    )

    args = parser.parse_args()

    # Initialize analyzer
    project_root = Path(__file__).parent.parent
    analyzer = UnusedCodeAnalyzer(project_root)

    try:
        # Run analysis
        results = analyzer.analyze()

        # Generate report
        output_file = Path(args.output) if args.output else None
        analyzer.generate_report(output_file)

        if args.verbose:
            print("\n" + "=" * 50)
            print("ANALYSIS SUMMARY")
            print("=" * 50)
            print(f"Test-only symbols: {len(results['exported_but_unused'])}")
            print(f"Unused modules: {len(results['unused_modules'])}")
            print(f"Dead code candidates: {len(results['dead_code_candidates'])}")

            if results["exported_but_unused"]:
                print("\nTest-only symbols found:")
                for item in results["exported_but_unused"][:5]:  # Show first 5
                    print(
                        f"  - {item['symbol']} (used in {len(item['test_files'])} test files)"
                    )

        print("✅ Unused code analysis completed successfully!")

    except Exception as e:
        print(f"❌ Error during analysis: {e!s}")
        if args.verbose:
            traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
