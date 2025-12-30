#!/usr/bin/env python3
"""Documentation Maintenance Dashboard.

Generates visual dashboards and metrics for documentation maintenance
and quality assurance for the gruponos-meltano-native project.

Usage:
    python scripts/docs_dashboard.py [command] [options]

Commands:
    generate    - Generate dashboard from latest reports
    metrics     - Show current documentation metrics
    trends      - Analyze trends over time
    alerts      - Check for issues requiring attention

Author: FLEXT Documentation Team
Version: 1.0.0
"""

import argparse
import json
import logging
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Configuration
DASHBOARD_DIR = Path("docs/dashboard")
REPORTS_DIR = Path("docs/reports")


class DocsDashboard:
    """Documentation maintenance dashboard generator."""

    def __init__(self) -> None:
        """Initialize the documentation dashboard generator."""
        self.dashboard_dir = DASHBOARD_DIR
        self.reports_dir = REPORTS_DIR
        self.dashboard_dir.mkdir(exist_ok=True)

        # Load latest reports
        self.latest_reports = self._find_latest_reports()

    def _find_latest_reports(self) -> dict[str, Path]:
        """Find the most recent reports for each type."""
        reports = {}

        if not self.reports_dir.exists():
            return reports

        # Find latest report of each type
        report_types = [
            "audit",
            "validation",
            "optimization",
            "sync",
            "maintenance",
            "report",
        ]

        for report_type in report_types:
            pattern = f"docs_{report_type}_*.json"
            matching_files = list(self.reports_dir.glob(pattern))

            if matching_files:
                # Sort by modification time, get latest
                latest = max(matching_files, key=lambda f: f.stat().st_mtime)
                reports[report_type] = latest

        return reports

    def generate_dashboard(self, output_format: str = "html") -> Path:
        """Generate comprehensive dashboard.

        Args:
            output_format: Output format for the dashboard (html, json, or markdown).

        Returns:
            Path to the generated dashboard file.

        """
        print("📊 Generating documentation dashboard...")

        # Collect data from all reports
        dashboard_data = {
            "timestamp": datetime.now(UTC).isoformat(),
            "metrics": self._collect_metrics(),
            "trends": self._analyze_trends(),
            "issues": self._collect_issues(),
            "recommendations": self._collect_recommendations(),
        }

        # Generate dashboard file
        if output_format == "html":
            dashboard_file = self._generate_html_dashboard(dashboard_data)
        elif output_format == "json":
            dashboard_file = self._generate_json_dashboard(dashboard_data)
        else:
            dashboard_file = self._generate_markdown_dashboard(dashboard_data)

        print(f"📄 Dashboard generated: {dashboard_file}")
        return dashboard_file

    def _collect_metrics(self) -> dict[str, Any]:
        """Collect current documentation metrics."""
        metrics = {
            "total_files": 0,
            "quality_score": 0.0,
            "critical_issues": 0,
            "warning_issues": 0,
            "info_issues": 0,
            "links_checked": 0,
            "broken_links": 0,
            "files_updated": 0,
            "stale_documents": 0,
        }

        # Aggregate metrics from latest reports
        for report_file in self.latest_reports.values():
            try:
                with Path(report_file).open(encoding="utf-8") as f:
                    data = json.load(f)

                if "summary" in data:
                    summary = data["summary"]
                    metrics["quality_score"] = max(
                        metrics["quality_score"], summary.get("quality_score", 0)
                    )
                    metrics["critical_issues"] += summary.get("critical_issues", 0)
                    metrics["warning_issues"] += summary.get("warning_issues", 0)
                    metrics["info_issues"] += summary.get("info_issues", 0)
                    metrics["total_files"] = max(
                        metrics["total_files"], summary.get("total_files", 0)
                    )

                if "detailed_results" in data:
                    results = data["detailed_results"]

                    # Count links checked
                    if "validation" in results:
                        validation = results["validation"]
                        metrics["links_checked"] += len(
                            validation.get("external_links", {})
                        )
                        metrics["broken_links"] += len(
                            validation.get("broken_links", [])
                        )

                    # Count stale documents
                    if "audit" in results:
                        audit = results["audit"]
                        aging = audit.get("aging_analysis", {})
                        metrics["stale_documents"] += len(aging)

            except Exception as e:
                print(f"Warning: Could not process report {report_file}: {e}")

        return metrics

    def _analyze_trends(self) -> dict[str, Any]:
        """Analyze trends over time."""
        trends = {
            "quality_score_trend": [],
            "issues_trend": [],
            "files_trend": [],
            "time_periods": [],
        }

        # Find all reports for trend analysis
        all_reports = []
        for pattern in ["docs_*.json"]:
            all_reports.extend(list(self.reports_dir.glob(pattern)))

        # Sort by date and analyze last 10 reports
        sorted_reports = sorted(
            all_reports, key=lambda f: f.stat().st_mtime, reverse=True
        )[:10]

        for report_file in reversed(sorted_reports):
            try:
                with Path(report_file).open(encoding="utf-8") as f:
                    data = json.load(f)

                if "summary" in data:
                    summary = data["summary"]
                    timestamp = data.get("timestamp", report_file.stat().st_mtime)

                    if isinstance(timestamp, (int, float)):
                        date_str = datetime.fromtimestamp(timestamp, tz=UTC).strftime(
                            "%m/%d"
                        )
                    else:
                        try:
                            date_str = datetime.fromisoformat(timestamp).strftime(
                                "%m/%d"
                            )
                        except (ValueError, TypeError) as e:
                            logger.debug(f"Error parsing timestamp {timestamp}: {e}")
                            date_str = "Unknown"

                    trends["time_periods"].append(date_str)
                    trends["quality_score_trend"].append(
                        summary.get("quality_score", 0)
                    )
                    total_issues = (
                        summary.get("critical_issues", 0)
                        + summary.get("warning_issues", 0)
                        + summary.get("info_issues", 0)
                    )
                    trends["issues_trend"].append(total_issues)
                    trends["files_trend"].append(summary.get("total_files", 0))

            except Exception as e:
                print(f"Warning: Could not analyze trend for {report_file}: {e}")

        return trends

    def _collect_issues(self) -> list[dict[str, Any]]:
        """Collect all current issues."""
        issues = []

        for report_file in self.latest_reports.values():
            try:
                with Path(report_file).open(encoding="utf-8") as f:
                    data = json.load(f)

                # Extract quality issues
                if "detailed_results" in data and "audit" in data["detailed_results"]:
                    audit = data["detailed_results"]["audit"]
                    for file_path, file_issues in audit.get(
                        "quality_issues", {}
                    ).items():
                        issues.extend(
                            {
                                "file": file_path,
                                "type": issue.get("type", "Unknown"),
                                "message": issue.get("message", ""),
                                "severity": issue.get("severity", "INFO"),
                                "source": "audit",
                            }
                            for issue in file_issues
                        )

                # Extract broken links
                if (
                    "detailed_results" in data
                    and "validation" in data["detailed_results"]
                ):
                    validation = data["detailed_results"]["validation"]
                    issues.extend(
                        {
                            "file": "Multiple files",
                            "type": "Broken Link",
                            "message": f"Broken link: {broken_link.get('url', '')}",
                            "severity": "HIGH",
                            "source": "validation",
                        }
                        for broken_link in validation.get("broken_links", [])
                    )

            except Exception as e:
                print(f"Warning: Could not collect issues from {report_file}: {e}")

        return issues

    def _collect_recommendations(self) -> list[dict[str, Any]]:
        """Collect all recommendations."""
        recommendations = []

        for report_file in self.latest_reports.values():
            try:
                with Path(report_file).open(encoding="utf-8") as f:
                    data = json.load(f)

                if "recommendations" in data:
                    recommendations.extend(data["recommendations"])

            except Exception as e:
                print(
                    f"Warning: Could not collect recommendations from {report_file}: {e}"
                )

        return recommendations

    def _generate_html_dashboard(self, data: dict[str, Any]) -> Path:
        """Generate HTML dashboard.

        Args:
            data: Dashboard data dictionary containing metrics, trends, issues, and recommendations.

        Returns:
            Path to the generated HTML file.

        """
        current_time = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Documentation Dashboard - gruponos-meltano-native</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
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
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .metric-card {{
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
        }}
        .metric-value {{
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
        }}
        .metric-label {{
            color: #666;
            font-size: 0.9em;
            margin-top: 5px;
        }}
        .chart-container {{
            background: white;
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
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
        }}
        .severity-CRITICAL {{ color: #dc3545; font-weight: bold; }}
        .severity-HIGH {{ color: #fd7e14; font-weight: bold; }}
        .severity-MEDIUM {{ color: #ffc107; }}
        .severity-LOW {{ color: #28a745; }}
        .recommendations {{
            background: #e3f2fd;
            border-left: 4px solid #2196f3;
            padding: 15px;
            margin: 20px 0;
        }}
        .status-good {{ color: #28a745; }}
        .status-warning {{ color: #ffc107; }}
        .status-error {{ color: #dc3545; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 Documentation Quality Dashboard</h1>
        <p>gruponos-meltano-native Project</p>
        <p>Last Updated: {current_time}</p>
    </div>

    <div class="metrics-grid">
        <div class="metric-card">
            <div class="metric-value">{data["metrics"]["quality_score"]}%</div>
            <div class="metric-label">Quality Score</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">{data["metrics"]["total_files"]}</div>
            <div class="metric-label">Total Files</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">{data["metrics"]["critical_issues"]}</div>
            <div class="metric-label">Critical Issues</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">{data["metrics"]["broken_links"]}</div>
            <div class="metric-label">Broken Links</div>
        </div>
    </div>

    <div class="chart-container">
        <h2>📈 Quality Trends</h2>
        <canvas id="qualityChart" width="400" height="200"></canvas>
    </div>

    <div class="chart-container">
        <h2>🔧 Maintenance Activity</h2>
        <canvas id="activityChart" width="400" height="200"></canvas>
    </div>

    {self._generate_recommendations_html(data["recommendations"])}

    <div class="chart-container">
        <h2>⚠️ Current Issues</h2>
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

        # Add issues rows
        for issue in data["issues"][:20]:  # Limit to 20 issues
            html_content += f"""
                <tr>
                    <td>{issue["file"]}</td>
                    <td>{issue["type"]}</td>
                    <td>{issue["message"]}</td>
                    <td class="severity-{issue["severity"]}">{issue["severity"]}</td>
                </tr>
"""

        html_content += (
            """
            </tbody>
        </table>
    </div>

    <script>
        // Quality Score Trend Chart
        const qualityCtx = document.getElementById('qualityChart').getContext('2d');
        new Chart(qualityCtx, {
            type: 'line',
            data: {
                labels: """
            + str(data["trends"]["time_periods"])
            + """,
                datasets: [{
                    label: 'Quality Score',
                    data: """
            + str(data["trends"]["quality_score_trend"])
            + """,
                    borderColor: '#667eea',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100
                    }
                }
            }
        });

        // Activity Chart
        const activityCtx = document.getElementById('activityChart').getContext('2d');
        new Chart(activityCtx, {
            type: 'bar',
            data: {
                labels: """
            + str(data["trends"]["time_periods"])
            + """,
                datasets: [{
                    label: 'Issues Found',
                    data: """
            + str(data["trends"]["issues_trend"])
            + """,
                    backgroundColor: '#ff9800'
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    </script>
</body>
</html>
"""
        )

        dashboard_date = datetime.now(UTC).strftime("%Y%m%d")
        dashboard_file = (
            self.dashboard_dir / f"documentation_dashboard_{dashboard_date}.html"
        )
        dashboard_file.write_text(html_content, encoding="utf-8")
        return dashboard_file

    def _generate_recommendations_html(
        self, recommendations: list[dict[str, Any]]
    ) -> str:
        """Generate HTML for recommendations."""
        if not recommendations:
            return ""

        html = '<div class="chart-container"><h2>🎯 Recommendations</h2>'

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

    def _generate_json_dashboard(self, data: dict[str, Any]) -> Path:
        """Generate JSON dashboard.

        Args:
            data: Dashboard data dictionary.

        Returns:
            Path to the generated JSON file.

        """
        dashboard_date = datetime.now(UTC).strftime("%Y%m%d")
        dashboard_file = (
            self.dashboard_dir / f"documentation_dashboard_{dashboard_date}.json"
        )
        with Path(dashboard_file).open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return dashboard_file

    def _generate_markdown_dashboard(self, data: dict[str, Any]) -> Path:
        """Generate Markdown dashboard.

        Args:
            data: Dashboard data dictionary.

        Returns:
            Path to the generated Markdown file.

        """
        current_time = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")
        md_content = f"""# 📊 Documentation Quality Dashboard

**Generated:** {current_time}
**Project:** gruponos-meltano-native

## 📈 Current Metrics

| Metric | Value | Status |
|--------|-------|--------|
| Quality Score | {data["metrics"]["quality_score"]}% | {"✅ Good" if data["metrics"]["quality_score"] >= 80 else "⚠️ Needs Attention"} |
| Total Files | {data["metrics"]["total_files"]} | - |
| Critical Issues | {data["metrics"]["critical_issues"]} | {"❌ Action Required" if data["metrics"]["critical_issues"] > 0 else "✅ OK"} |
| Warning Issues | {data["metrics"]["warning_issues"]} | {"⚠️ Monitor" if data["metrics"]["warning_issues"] > 0 else "✅ OK"} |
| Broken Links | {data["metrics"]["broken_links"]} | {"❌ Fix Required" if data["metrics"]["broken_links"] > 0 else "✅ OK"} |
| Stale Documents | {data["metrics"]["stale_documents"]} | {"⚠️ Update Needed" if data["metrics"]["stale_documents"] > 0 else "✅ OK"} |

## 🎯 Top Recommendations

"""

        for i, rec in enumerate(data["recommendations"][:5], 1):
            md_content += f"""### {i}. {rec["priority"]}: {rec["message"]}

"""

            for action in rec.get("action_items", []):
                md_content += f"""- {action}
"""

        md_content += """

## ⚠️ Current Issues

| File | Type | Issue | Severity |
|------|------|-------|----------|
"""

        for issue in data["issues"][:10]:  # Show first 10 issues
            md_content += f"""| {issue["file"]} | {issue["type"]} | {issue["message"][:50]}... | {issue["severity"]} |
"""

        md_content += (
            """

## 📈 Trends (Last 10 Reports)

- **Quality Score Trend:** """
            + ", ".join([
                f"{date}: {score}%"
                for date, score in zip(
                    data["trends"]["time_periods"],
                    data["trends"]["quality_score_trend"],
                    strict=False,
                )
            ])
            + """
- **Issues Trend:** """
            + ", ".join([
                f"{date}: {issues}"
                for date, issues in zip(
                    data["trends"]["time_periods"],
                    data["trends"]["issues_trend"],
                    strict=False,
                )
            ])
            + """

---
*Generated by Documentation Maintenance System*
"""
        )

        dashboard_date = datetime.now(UTC).strftime("%Y%m%d")
        dashboard_file = (
            self.dashboard_dir / f"documentation_dashboard_{dashboard_date}.md"
        )
        dashboard_file.write_text(md_content, encoding="utf-8")
        return dashboard_file

    def show_metrics(self) -> None:
        """Display current documentation metrics."""
        metrics = self._collect_metrics()

        print("📊 Current Documentation Metrics")
        print("=" * 40)
        print(f"Quality Score:     {metrics['quality_score']}%")
        print(f"Total Files:       {metrics['total_files']}")
        print(f"Critical Issues:   {metrics['critical_issues']}")
        print(f"Warning Issues:    {metrics['warning_issues']}")
        print(f"Info Issues:       {metrics['info_issues']}")
        print(f"Links Checked:     {metrics['links_checked']}")
        print(f"Broken Links:      {metrics['broken_links']}")
        print(f"Files Updated:     {metrics['files_updated']}")
        print(f"Stale Documents:   {metrics['stale_documents']}")

        # Status indicators
        if metrics["critical_issues"] > 0:
            print("❌ Status: CRITICAL - Immediate action required")
        elif metrics["quality_score"] < 80:
            print("⚠️  Status: WARNING - Quality improvements needed")
        else:
            print("✅ Status: GOOD - Documentation quality is acceptable")

    def analyze_trends(self) -> None:
        """Analyze and display trends."""
        trends = self._analyze_trends()

        print("📈 Documentation Quality Trends")
        print("=" * 40)

        if trends["time_periods"]:
            print("Quality Score Trend:")
            for date, score in zip(
                trends["time_periods"], trends["quality_score_trend"], strict=False
            ):
                print(f"  {date}: {score}%")

            print("\nIssues Trend:")
            for date, issues in zip(
                trends["time_periods"], trends["issues_trend"], strict=False
            ):
                print(f"  {date}: {issues} issues")
        else:
            print("No trend data available - run maintenance cycles first")

    def check_alerts(self) -> None:
        """Check for issues requiring immediate attention."""
        metrics = self._collect_metrics()
        self._collect_issues()

        alerts = []

        # Quality score alert
        if metrics["quality_score"] < 70:
            alerts.append({
                "level": "CRITICAL",
                "message": f"Quality score critically low: {metrics['quality_score']}%",
            })
        elif metrics["quality_score"] < 80:
            alerts.append({
                "level": "WARNING",
                "message": f"Quality score below threshold: {metrics['quality_score']}%",
            })

        # Critical issues alert
        if metrics["critical_issues"] > 0:
            alerts.append({
                "level": "CRITICAL",
                "message": f"{metrics['critical_issues']} critical issues found",
            })

        # Broken links alert
        if metrics["broken_links"] > 0:
            alerts.append({
                "level": "WARNING",
                "message": f"{metrics['broken_links']} broken links detected",
            })

        # Stale documents alert
        if metrics["stale_documents"] > 5:
            alerts.append({
                "level": "WARNING",
                "message": f"{metrics['stale_documents']} documents are stale (>90 days)",
            })

        print("🚨 Documentation Alerts")
        print("=" * 40)

        if alerts:
            for alert in alerts:
                level_emoji = {"CRITICAL": "🔴", "WARNING": "🟡", "INFO": "🔵"}.get(
                    alert["level"], "⚪"
                )
                print(f"{level_emoji} {alert['level']}: {alert['message']}")
        else:
            print("✅ No alerts - documentation quality is good")


def main() -> int:
    """Main entry point for dashboard."""
    parser = argparse.ArgumentParser(
        description="Documentation Maintenance Dashboard",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/docs_dashboard.py generate --format html
  python scripts/docs_dashboard.py metrics
  python scripts/docs_dashboard.py trends
  python scripts/docs_dashboard.py alerts
        """,
    )

    parser.add_argument(
        "command",
        choices=["generate", "metrics", "trends", "alerts"],
        help="Dashboard command to execute",
    )

    parser.add_argument(
        "--format",
        choices=["html", "json", "markdown"],
        default="html",
        help="Output format for generate command",
    )

    parser.add_argument("--output", type=str, help="Output file path")

    args = parser.parse_args()

    dashboard = DocsDashboard()

    try:
        if args.command == "generate":
            dashboard_file = dashboard.generate_dashboard(args.format)
            print(f"✅ Dashboard generated: {dashboard_file}")

        elif args.command == "metrics":
            dashboard.show_metrics()

        elif args.command == "trends":
            dashboard.analyze_trends()

        elif args.command == "alerts":
            dashboard.check_alerts()

    except Exception as e:
        print(f"❌ Error: {e!s}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
