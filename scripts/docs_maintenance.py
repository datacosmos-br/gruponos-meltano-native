#!/usr/bin/env python3
"""Documentation Maintenance & Quality Assurance System.

This script implements a comprehensive documentation maintenance framework
with automated quality assurance, validation, content optimization, and
regular update procedures for the gruponos-meltano-native project.

Usage:
    python scripts/docs_maintenance.py [command] [options]

Commands:
    audit       - Comprehensive content quality audit
    validate    - Link and reference validation
    optimize    - Content optimization and enhancement
    sync        - Automated synchronization with codebase
    report      - Quality assurance reporting
    maintenance - Full maintenance cycle

Author: FLEXT Documentation Team
Version: 1.0.0
"""

import argparse
import json
import re
import subprocess
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import urlopen


# Configuration
class DocsConfig:
    """Configuration for documentation maintenance system."""

    # File patterns
    DOC_EXTENSIONS = [".md", ".mdx"]
    IGNORE_DIRS = [".git", "__pycache__", ".pytest_cache", "dist", "build"]

    # Quality thresholds
    MIN_WORDS_PER_DOC = 50
    MAX_DAYS_SINCE_UPDATE = 90
    MAX_LINK_CHECK_TIMEOUT = 10
    MAX_BROKEN_LINK_RETRIES = 3

    # Style rules
    MAX_HEADING_LENGTH = 80
    MAX_LINE_LENGTH = 88
    REQUIRED_SECTIONS = ["Overview", "Installation", "Usage"]

    # Paths
    DOCS_DIR = Path("docs")
    SCRIPTS_DIR = Path("scripts")
    REPORTS_DIR = Path("docs/reports")


class DocsMaintainer:
    """Main documentation maintenance class."""

    def __init__(self, config: DocsConfig = None) -> None:
        self.config = config or DocsConfig()
        self.docs_dir = self.config.DOCS_DIR
        self.reports_dir = self.config.REPORTS_DIR
        self.reports_dir.mkdir(exist_ok=True)

        # Initialize statistics
        self.stats = {
            "total_files": 0,
            "files_processed": 0,
            "errors_found": 0,
            "warnings_found": 0,
            "links_checked": 0,
            "broken_links": 0,
            "files_updated": 0,
            "optimizations_applied": 0,
        }

        # Initialize data structures
        self.file_index = {}
        self.link_index = defaultdict(list)
        self.reference_index = defaultdict(list)
        self.quality_issues = defaultdict(list)

    def find_docs_files(self) -> list[Path]:
        """Find all documentation files in the project."""
        docs_files = []

        # Search in docs directory
        if self.docs_dir.exists():
            for ext in self.config.DOC_EXTENSIONS:
                docs_files.extend(self.docs_dir.rglob(f"*{ext}"))

        # Search in root directory for main docs
        root_docs = []
        for ext in self.config.DOC_EXTENSIONS:
            root_docs.extend(Path().glob(f"*{ext}"))

        # Filter out ignored directories
        all_files = docs_files + root_docs

        filtered_files = [
            file_path
            for file_path in all_files
            if not any(ignored in str(file_path) for ignored in self.config.IGNORE_DIRS)
        ]

        self.stats["total_files"] = len(filtered_files)
        return filtered_files

    def audit_content_quality(self, files: list[Path]) -> dict:
        """Perform comprehensive content quality audit."""
        print("🔍 Performing content quality audit...")

        audit_results = {
            "file_stats": {},
            "quality_issues": defaultdict(list),
            "content_metrics": {},
            "aging_analysis": {},
            "completeness_check": {},
        }

        for file_path in files:
            try:
                content = file_path.read_text(encoding="utf-8")
                relative_path = file_path.relative_to(Path())

                # File statistics
                word_count = len(content.split())
                line_count = len(content.splitlines())
                last_modified = datetime.fromtimestamp(file_path.stat().st_mtime)

                audit_results["file_stats"][str(relative_path)] = {
                    "word_count": word_count,
                    "line_count": line_count,
                    "last_modified": last_modified.isoformat(),
                    "days_since_update": (datetime.now() - last_modified).days,
                }

                # Quality checks
                issues = self._check_file_quality(file_path, content)
                if issues:
                    audit_results["quality_issues"][str(relative_path)] = issues

                # Aging analysis
                days_old = (datetime.now() - last_modified).days
                if days_old > self.config.MAX_DAYS_SINCE_UPDATE:
                    audit_results["aging_analysis"][str(relative_path)] = {
                        "days_old": days_old,
                        "status": "STALE" if days_old > 180 else "NEEDS_UPDATE",
                    }

                # Completeness check
                completeness = self._check_completeness(content)
                if completeness["score"] < 0.8:
                    audit_results["completeness_check"][str(relative_path)] = (
                        completeness
                    )

                self.stats["files_processed"] += 1

            except Exception as e:
                self.quality_issues[str(file_path)].append({
                    "type": "ERROR",
                    "message": f"Failed to audit file: {e!s}",
                    "severity": "CRITICAL",
                })

        return audit_results

    def validate_links_and_references(self, files: list[Path]) -> dict:
        """Validate links and internal references."""
        print("🔗 Validating links and references...")

        validation_results = {
            "external_links": {},
            "internal_links": {},
            "broken_links": [],
            "missing_references": [],
            "orphaned_files": [],
        }

        # Build reference index
        for file_path in files:
            try:
                content = file_path.read_text(encoding="utf-8")
                relative_path = str(file_path.relative_to(Path()))

                # Find internal references
                internal_refs = re.findall(r"\[([^\]]+)\]\(([^)]+)\)", content)
                for text, link in internal_refs:
                    if not link.startswith("http"):
                        self.reference_index[link].append({
                            "from": relative_path,
                            "text": text,
                        })

                # Find external links
                external_links = re.findall(r"http[s]?://[^\s)]+", content)
                for link in external_links:
                    if link not in validation_results["external_links"]:
                        validation_results["external_links"][link] = []
                    validation_results["external_links"][link].append(relative_path)

            except Exception as e:
                self.quality_issues[str(file_path)].append({
                    "type": "ERROR",
                    "message": f"Failed to process links: {e!s}",
                    "severity": "HIGH",
                })

        # Validate external links
        for link, files_referencing in validation_results["external_links"].items():
            status = self._check_external_link(link)
            validation_results["external_links"][link] = {
                "status": status,
                "referenced_by": files_referencing,
            }

            if status != "OK":
                validation_results["broken_links"].append({
                    "url": link,
                    "status": status,
                    "referenced_by": files_referencing,
                })

            self.stats["links_checked"] += 1

        # Check for broken internal references
        {str(f.relative_to(Path())) for f in files}
        for link, references in self.reference_index.items():
            if link.startswith(("./", "../")):
                # Relative path - check if target exists
                for ref in references:
                    source_dir = Path(ref["from"]).parent
                    target_path = (source_dir / link).resolve()
                    if not target_path.exists():
                        validation_results["missing_references"].append({
                            "link": link,
                            "referenced_from": ref["from"],
                            "text": ref["text"],
                        })

        return validation_results

    def optimize_content(self, files: list[Path]) -> dict:
        """Optimize and enhance documentation content."""
        print("✨ Optimizing documentation content...")

        optimization_results = {
            "files_optimized": [],
            "optimizations_applied": [],
            "formatting_fixes": [],
            "metadata_updates": [],
            "structure_improvements": [],
        }

        for file_path in files:
            try:
                content = file_path.read_text(encoding="utf-8")
                original_content = content
                relative_path = file_path.relative_to(Path())

                # Apply optimizations
                optimized_content = self._optimize_file_content(
                    content, str(relative_path)
                )

                if optimized_content != original_content:
                    # Create backup
                    backup_path = file_path.with_suffix(f"{file_path.suffix}.backup")
                    backup_path.write_text(original_content, encoding="utf-8")

                    # Write optimized content
                    file_path.write_text(optimized_content, encoding="utf-8")

                    optimization_results["files_optimized"].append(str(relative_path))
                    self.stats["files_updated"] += 1

                    # Track what was optimized
                    if (
                        "table_of_contents" in optimized_content
                        and "table_of_contents" not in original_content
                    ):
                        optimization_results["structure_improvements"].append(
                            str(relative_path)
                        )

            except Exception as e:
                self.quality_issues[str(file_path)].append({
                    "type": "ERROR",
                    "message": f"Failed to optimize file: {e!s}",
                    "severity": "MEDIUM",
                })

        return optimization_results

    def synchronize_with_codebase(self, files: list[Path]) -> dict:
        """Synchronize documentation with codebase changes."""
        print("🔄 Synchronizing with codebase...")

        sync_results = {
            "code_changes": [],
            "doc_updates_needed": [],
            "api_changes": [],
            "new_files_detected": [],
            "deprecated_references": [],
        }

        try:
            # Get recent git changes
            result = subprocess.run(
                ["git", "log", "--oneline", '--since="1 month ago"', "--", "src/"],
                check=False,
                capture_output=True,
                text=True,
                cwd=Path(),
            )

            if result.returncode == 0:
                recent_commits = result.stdout.strip().split("\n")
                sync_results["code_changes"] = [
                    commit for commit in recent_commits if commit.strip()
                ]

            # Check for new source files without documentation
            result = subprocess.run(
                ["find", "src/", "-name", "*.py", "-type", "f"],
                check=False,
                capture_output=True,
                text=True,
                cwd=Path(),
            )

            if result.returncode == 0:
                source_files = set(result.stdout.strip().split("\n"))
                documented_modules = set()

                for doc_file in files:
                    try:
                        content = doc_file.read_text(encoding="utf-8")
                        # Look for module references
                        modules = re.findall(
                            r"`([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)`",
                            content,
                        )
                        documented_modules.update(modules)
                    except:
                        pass

                # Find undocumented modules
                for source_file in source_files:
                    if source_file and source_file.endswith(".py"):
                        module_name = (
                            source_file.replace("src/", "")
                            .replace(".py", "")
                            .replace("/", ".")
                        )
                        if (
                            module_name not in documented_modules
                            and len(module_name.split(".")) >= 2
                        ):
                            sync_results["doc_updates_needed"].append(module_name)

        except Exception as e:
            self.quality_issues["sync"].append({
                "type": "ERROR",
                "message": f"Failed to synchronize with codebase: {e!s}",
                "severity": "MEDIUM",
            })

        return sync_results

    def generate_quality_report(
        self,
        audit_results: dict,
        validation_results: dict,
        optimization_results: dict,
        sync_results: dict,
    ) -> dict:
        """Generate comprehensive quality assurance report."""
        print("📊 Generating quality assurance report...")

        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_files": self.stats["total_files"],
                "files_processed": self.stats["files_processed"],
                "quality_score": 0.0,
                "critical_issues": 0,
                "warning_issues": 0,
                "info_issues": 0,
            },
            "detailed_results": {
                "audit": audit_results,
                "validation": validation_results,
                "optimization": optimization_results,
                "synchronization": sync_results,
            },
            "recommendations": [],
            "metrics": self.stats.copy(),
        }

        # Calculate quality score
        total_issues = (
            len(audit_results.get("quality_issues", {}))
            + len(validation_results.get("broken_links", []))
            + len(audit_results.get("aging_analysis", {}))
        )

        if self.stats["files_processed"] > 0:
            quality_score = max(
                0, 100 - (total_issues * 10 / self.stats["files_processed"])
            )
            report["summary"]["quality_score"] = round(quality_score, 1)

        # Categorize issues
        for issues in audit_results.get("quality_issues", {}).values():
            for issue in issues:
                severity = issue.get("severity", "INFO")
                if severity == "CRITICAL":
                    report["summary"]["critical_issues"] += 1
                elif severity == "HIGH":
                    report["summary"]["warning_issues"] += 1
                else:
                    report["summary"]["info_issues"] += 1

        # Generate recommendations
        report["recommendations"] = self._generate_recommendations(
            audit_results, validation_results, sync_results
        )

        return report

    def _check_file_quality(self, file_path: Path, content: str) -> list[dict]:
        """Check quality of a single file."""
        issues = []

        # Check word count
        word_count = len(content.split())
        if word_count < self.config.MIN_WORDS_PER_DOC:
            issues.append({
                "type": "CONTENT",
                "message": f"Document too short: {word_count} words (minimum: {self.config.MIN_WORDS_PER_DOC})",
                "severity": "MEDIUM",
            })

        # Check line length
        for i, line in enumerate(content.splitlines(), 1):
            if len(line) > self.config.MAX_LINE_LENGTH:
                issues.append({
                    "type": "FORMATTING",
                    "message": f"Line {i} too long: {len(line)} chars (max: {self.config.MAX_LINE_LENGTH})",
                    "severity": "LOW",
                })

        # Check heading hierarchy
        headings = re.findall(r"^(#{1,6})\s+(.+)$", content, re.MULTILINE)
        heading_levels = [len(level) for level, _ in headings]

        if heading_levels and heading_levels[0] != 1:
            issues.append({
                "type": "STRUCTURE",
                "message": "Document should start with level 1 heading (#)",
                "severity": "MEDIUM",
            })

        # Check for TODO/FIXME markers
        todos = re.findall(r"(TODO|FIXME|XXX):?\s*(.+)", content, re.IGNORECASE)
        if todos:
            issues.append({
                "type": "MAINTENANCE",
                "message": f"Found {len(todos)} TODO/FIXME markers that need attention",
                "severity": "LOW",
            })

        return issues

    def _check_completeness(self, content: str) -> dict:
        """Check documentation completeness."""
        sections_found = []
        score = 0.0

        # Check for common sections
        for section in self.config.REQUIRED_SECTIONS:
            if re.search(
                rf"^#{1, 3}\s+{section}", content, re.MULTILINE | re.IGNORECASE
            ):
                sections_found.append(section)
                score += 1.0 / len(self.config.REQUIRED_SECTIONS)

        # Check for code examples
        if r"```" in content:
            score += 0.2

        # Check for links
        if re.search(r"\[.*\]\(.*\)", content):
            score += 0.1

        return {
            "score": min(1.0, score),
            "sections_found": sections_found,
            "missing_sections": [
                s for s in self.config.REQUIRED_SECTIONS if s not in sections_found
            ],
        }

    def _check_external_link(self, url: str) -> str:
        """Check if external link is accessible."""
        try:
            response = urlopen(url, timeout=self.config.MAX_LINK_CHECK_TIMEOUT)
            if response.status == 200:
                return "OK"
            return f"HTTP_{response.status}"
        except HTTPError as e:
            return f"HTTP_{e.code}"
        except URLError as e:
            return f"ERROR_{e.reason!s}"
        except Exception as e:
            return f"UNKNOWN_{e!s}"

    def _optimize_file_content(self, content: str, file_path: str) -> str:
        """Optimize content of a single file."""
        optimized = content

        # Add table of contents for long documents (if not present)
        if len(content.splitlines()) > 50 and "## Table of Contents" not in content:
            toc = self._generate_table_of_contents(content)
            if toc:
                # Insert after title
                lines = content.splitlines()
                insert_pos = 1
                for i, line in enumerate(lines[1:], 1):
                    if line.strip() and not line.startswith("#"):
                        insert_pos = i
                        break

                lines.insert(insert_pos, "")
                lines.insert(insert_pos + 1, "## Table of Contents")
                lines.insert(insert_pos + 2, "")
                toc_lines = toc.splitlines()
                for i, toc_line in enumerate(toc_lines):
                    lines.insert(insert_pos + 3 + i, toc_line)
                lines.insert(insert_pos + 3 + len(toc_lines), "")

                optimized = "\n".join(lines)

        # Fix common formatting issues
        # Remove trailing whitespace
        optimized = re.sub(r"[ \t]+$", "", optimized, flags=re.MULTILINE)

        # Ensure consistent list formatting
        return re.sub(
            r"^([ \t]*)-([ \t])(.+)$", r"\1- \3", optimized, flags=re.MULTILINE
        )

    def _generate_table_of_contents(self, content: str) -> str:
        """Generate table of contents for a document."""
        toc_lines = []
        headings = re.findall(r"^(#{2,4})\s+(.+)$", content, re.MULTILINE)

        for level_marker, title in headings:
            level = len(level_marker)
            indent = "  " * (level - 2)
            # Create anchor link
            anchor = re.sub(r"[^\w\s-]", "", title.lower()).replace(" ", "-")
            toc_lines.append(f"{indent}- [{title}](#{anchor})")

        return "\n".join(toc_lines) if toc_lines else ""

    def _generate_recommendations(
        self, audit_results: dict, validation_results: dict, sync_results: dict
    ) -> list[dict]:
        """Generate recommendations based on analysis."""
        recommendations = []

        # Content quality recommendations
        if audit_results.get("aging_analysis"):
            stale_count = len(audit_results["aging_analysis"])
            recommendations.append({
                "priority": "HIGH",
                "category": "CONTENT_FRESHNESS",
                "message": f"Update {stale_count} stale documents (older than {self.config.MAX_DAYS_SINCE_UPDATE} days)",
                "action_items": [
                    "Review and update outdated content",
                    "Verify technical accuracy",
                ],
            })

        # Link validation recommendations
        if validation_results.get("broken_links"):
            broken_count = len(validation_results["broken_links"])
            recommendations.append({
                "priority": "CRITICAL",
                "category": "LINK_VALIDATION",
                "message": f"Fix {broken_count} broken external links",
                "action_items": [
                    "Update or remove broken links",
                    "Verify link destinations",
                ],
            })

        # Synchronization recommendations
        if sync_results.get("doc_updates_needed"):
            missing_count = len(sync_results["doc_updates_needed"])
            recommendations.append({
                "priority": "MEDIUM",
                "category": "CONTENT_COMPLETENESS",
                "message": f"Add documentation for {missing_count} undocumented modules",
                "action_items": [
                    "Create missing module documentation",
                    "Add API documentation",
                ],
            })

        # Quality improvement recommendations
        quality_issues = sum(
            len(issues) for issues in audit_results.get("quality_issues", {}).values()
        )
        if quality_issues > 0:
            recommendations.append({
                "priority": "MEDIUM",
                "category": "CONTENT_QUALITY",
                "message": f"Address {quality_issues} content quality issues",
                "action_items": [
                    "Fix formatting issues",
                    "Improve content structure",
                    "Add missing sections",
                ],
            })

        return recommendations

    def save_report(self, report: dict, filename: str | None = None) -> Path:
        """Save quality report to file."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"documentation_audit_{timestamp}.json"

        # Handle absolute paths vs relative filenames
        if Path(filename).is_absolute() or filename.startswith("docs/"):
            report_path = Path(filename)
        else:
            report_path = self.reports_dir / filename

        # Ensure parent directory exists
        report_path.parent.mkdir(parents=True, exist_ok=True)

        with Path(report_path).open("w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"📄 Report saved to: {report_path}")
        return report_path

    def generate_html_report(self, report: dict) -> str:
        """Generate HTML report from quality analysis."""
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Documentation Quality Report - {datetime.now().strftime("%Y-%m-%d")}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            text-align: center;
        }}
        .score-card {{
            background: white;
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .metric-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .metric {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
        }}
        .metric-value {{
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }}
        .metric-label {{
            color: #666;
            font-size: 0.9em;
        }}
        .issues-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        .issues-table th, .issues-table td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        .issues-table th {{
            background: #f8f9fa;
            font-weight: 600;
        }}
        .severity-critical {{ color: #dc3545; font-weight: bold; }}
        .severity-high {{ color: #fd7e14; font-weight: bold; }}
        .severity-medium {{ color: #ffc107; }}
        .severity-low {{ color: #28a745; }}
        .recommendations {{
            background: #e3f2fd;
            border-left: 4px solid #2196f3;
            padding: 15px;
            margin: 20px 0;
        }}
        .priority-high {{ border-left-color: #ff9800; background: #fff3e0; }}
        .priority-critical {{ border-left-color: #f44336; background: #ffebee; }}
        .file-list {{
            background: white;
            border-radius: 8px;
            padding: 15px;
            margin: 10px 0;
        }}
        .file-item {{
            padding: 8px 0;
            border-bottom: 1px solid #eee;
        }}
        .file-item:last-child {{
            border-bottom: none;
        }}
        .status-good {{ color: #28a745; }}
        .status-warning {{ color: #ffc107; }}
        .status-error {{ color: #dc3545; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 Documentation Quality Report</h1>
        <p>Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        <p>Project: gruponos-meltano-native</p>
    </div>

    <div class="score-card">
        <h2>📈 Quality Overview</h2>
        <div class="metric-grid">
            <div class="metric">
                <div class="metric-value">{report["summary"]["quality_score"]}%</div>
                <div class="metric-label">Quality Score</div>
            </div>
            <div class="metric">
                <div class="metric-value">{report["summary"]["total_files"]}</div>
                <div class="metric-label">Files Processed</div>
            </div>
            <div class="metric">
                <div class="metric-value">{report["summary"]["critical_issues"]}</div>
                <div class="metric-label">Critical Issues</div>
            </div>
            <div class="metric">
                <div class="metric-value">{report["summary"]["warning_issues"]}</div>
                <div class="metric-label">Warning Issues</div>
            </div>
        </div>
    </div>

    <div class="score-card">
        <h2>🔧 Maintenance Statistics</h2>
        <div class="metric-grid">
            <div class="metric">
                <div class="metric-value">{self.stats.get("links_checked", 0)}</div>
                <div class="metric-label">Links Checked</div>
            </div>
            <div class="metric">
                <div class="metric-value">{len(report["detailed_results"].get("validation", {}).get("broken_links", []))}</div>
                <div class="metric-label">Broken Links</div>
            </div>
            <div class="metric">
                <div class="metric-value">{self.stats.get("files_updated", 0)}</div>
                <div class="metric-label">Files Updated</div>
            </div>
            <div class="metric">
                <div class="metric-value">{len(report["detailed_results"].get("audit", {}).get("aging_analysis", {}))}</div>
                <div class="metric-label">Stale Documents</div>
            </div>
        </div>
    </div>

    {self._generate_html_recommendations(report["recommendations"])}

    {self._generate_html_issues_table(report)}

    {self._generate_html_file_status(report)}

    <div class="score-card">
        <h2>📋 Report Details</h2>
        <p><strong>Report Generated:</strong> {report["timestamp"]}</p>
        <p><strong>Analysis Duration:</strong> {(datetime.now() - datetime.fromisoformat(report["timestamp"])).total_seconds():.2f} seconds</p>
        <p><strong>Maintenance System Version:</strong> 1.0.0</p>
    </div>
</body>
</html>
"""

    def _generate_html_recommendations(self, recommendations: list[dict]) -> str:
        """Generate HTML for recommendations section."""
        if not recommendations:
            return ""

        html = '<div class="score-card"><h2>🎯 Recommendations</h2>'

        for rec in recommendations:
            priority_class = f"recommendations priority-{rec['priority'].lower()}"
            html += f"""
    <div class="{priority_class}">
        <h4>{rec["priority"]}: {rec["message"]}</h4>
        <ul>
"""
            for action in rec.get("action_items", []):
                html += f"<li>{action}</li>"
            html += "</ul></div>"

        html += "</div>"
        return html

    def _generate_html_issues_table(self, report: dict) -> str:
        """Generate HTML for issues table."""
        issues = []
        for file_path, file_issues in (
            report["detailed_results"]
            .get("audit", {})
            .get("quality_issues", {})
            .items()
        ):
            issues.extend(
                {
                    "file": file_path,
                    "type": issue["type"],
                    "message": issue["message"],
                    "severity": issue["severity"],
                }
                for issue in file_issues
            )

        if not issues:
            return ""

        html = """
    <div class="score-card">
        <h2>⚠️ Quality Issues</h2>
        <table class="issues-table">
            <thead>
                <tr>
                    <th>File</th>
                    <th>Type</th>
                    <th>Issue</th>
                    <th>Severity</th>
                </tr>
            </thead>
            <tbody>
"""

        for issue in issues[:20]:  # Limit to first 20 issues
            severity_class = f"severity-{issue['severity'].lower()}"
            html += f"""
                <tr>
                    <td>{issue["file"]}</td>
                    <td>{issue["type"]}</td>
                    <td>{issue["message"]}</td>
                    <td class="{severity_class}">{issue["severity"]}</td>
                </tr>
"""

        html += "</tbody></table></div>"
        return html

    def _generate_html_file_status(self, report: dict) -> str:
        """Generate HTML for file status section."""
        aging = report["detailed_results"].get("audit", {}).get("aging_analysis", {})

        if not aging:
            return ""

        html = '<div class="score-card"><h2>📅 Document Aging Analysis</h2>'

        for file_path, info in aging.items():
            status_class = (
                "status-error" if info["status"] == "STALE" else "status-warning"
            )
            html += f"""
    <div class="file-list">
        <div class="file-item">
            <strong>{file_path}</strong> -
            <span class="{status_class}">{info["days_old"]} days old ({info["status"]})</span>
        </div>
    </div>
"""

        html += "</div>"
        return html

    def run_maintenance_cycle(self, args):
        """Run complete maintenance cycle."""
        print("🚀 Starting Documentation Maintenance Cycle")
        print("=" * 50)

        # Find all documentation files
        files = self.find_docs_files()
        print(f"📁 Found {len(files)} documentation files")

        # Run all maintenance tasks
        audit_results = self.audit_content_quality(files)
        validation_results = self.validate_links_and_references(files)
        optimization_results = self.optimize_content(files)
        sync_results = self.synchronize_with_codebase(files)

        # Generate comprehensive report
        report = self.generate_quality_report(
            audit_results, validation_results, optimization_results, sync_results
        )

        # Save report
        report_file = self.save_report(report)

        # Print summary
        print("\n" + "=" * 50)
        print("📊 MAINTENANCE CYCLE SUMMARY")
        print("=" * 50)
        print(f"Files Processed: {report['summary']['total_files']}")
        print(f"Quality Score: {report['summary']['quality_score']}%")
        print(f"Critical Issues: {report['summary']['critical_issues']}")
        print(f"Warning Issues: {report['summary']['warning_issues']}")
        print(f"Info Issues: {report['summary']['info_issues']}")
        print(f"Files Updated: {self.stats['files_updated']}")
        print(f"Links Checked: {self.stats['links_checked']}")
        print(f"Broken Links: {len(validation_results.get('broken_links', []))}")
        print(f"Report Saved: {report_file}")

        if report["recommendations"]:
            print("\n🔧 TOP RECOMMENDATIONS:")
            for i, rec in enumerate(report["recommendations"][:3], 1):
                print(f"{i}. [{rec['priority']}] {rec['message']}")

        print("\n✅ Documentation maintenance cycle completed!")
        return report


def main() -> None:
    """Main entry point for documentation maintenance system."""
    parser = argparse.ArgumentParser(
        description="Documentation Maintenance & Quality Assurance System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/docs_maintenance.py audit
  python scripts/docs_maintenance.py validate
  python scripts/docs_maintenance.py optimize
  python scripts/docs_maintenance.py maintenance
  python scripts/docs_maintenance.py report --format html
        """,
    )

    parser.add_argument(
        "command",
        choices=["audit", "validate", "optimize", "sync", "report", "maintenance"],
        help="Maintenance command to execute",
    )

    parser.add_argument("--config", type=str, help="Path to configuration file")

    parser.add_argument("--output", type=str, help="Output file for reports")

    parser.add_argument(
        "--format",
        choices=["json", "html", "md"],
        default="json",
        help="Report output format",
    )

    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output"
    )

    args = parser.parse_args()

    # Initialize maintainer
    maintainer = DocsMaintainer()

    try:
        if args.command == "maintenance":
            # Run full maintenance cycle
            maintainer.run_maintenance_cycle(args)

        elif args.command == "audit":
            files = maintainer.find_docs_files()
            results = maintainer.audit_content_quality(files)
            report = maintainer.generate_quality_report(results, {}, {}, {})
            maintainer.save_report(report, args.output)

        elif args.command == "validate":
            files = maintainer.find_docs_files()
            results = maintainer.validate_links_and_references(files)
            report = maintainer.generate_quality_report({}, results, {}, {})
            maintainer.save_report(report, args.output)

        elif args.command == "optimize":
            files = maintainer.find_docs_files()
            results = maintainer.optimize_content(files)
            report = maintainer.generate_quality_report({}, {}, results, {})
            maintainer.save_report(report, args.output)

        elif args.command == "sync":
            files = maintainer.find_docs_files()
            results = maintainer.synchronize_with_codebase(files)
            report = maintainer.generate_quality_report({}, {}, {}, results)
            maintainer.save_report(report, args.output)

        elif args.command == "report":
            # Generate comprehensive report from existing data
            print("📊 Generating comprehensive quality report...")

            files = maintainer.find_docs_files()
            audit_results = maintainer.audit_content_quality(files)
            validation_results = maintainer.validate_links_and_references(files)
            sync_results = maintainer.synchronize_with_codebase(files)

            report = maintainer.generate_quality_report(
                audit_results, validation_results, {}, sync_results
            )

            if args.format == "html":
                # Generate HTML report
                html_report = maintainer.generate_html_report(report)
                output_file = (
                    args.output
                    or f"documentation_report_{datetime.now().strftime('%Y%m%d')}.html"
                )
                Path(output_file).write_text(html_report, encoding="utf-8")
                print(f"📄 HTML report saved to: {output_file}")
            else:
                maintainer.save_report(report, args.output)

    except KeyboardInterrupt:
        print("\n⚠️  Maintenance interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error during maintenance: {e!s}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
