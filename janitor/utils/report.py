import json
from datetime import datetime, timezone


def build_report(findings, region="us-east-1", account_id="000000000000"):
    total_waste = sum(
        finding["estimated_monthly_cost_usd"]
        for finding in findings
    )

    return {
        "scan_timestamp": datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z"),
        "account_id": account_id,
        "region": region,
        "summary": {
            "total_orphans": len(findings),
            "estimated_monthly_waste_usd": round(total_waste, 2)
        },
        "findings": findings
    }


def save_json_report(report, filename="report.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
        f.write("\n")


def save_markdown_summary(report, filename="summary.md"):
    lines = [
        "# Cost Janitor Report",
        "",
        f"Total orphans found: {report['summary']['total_orphans']}",
        f"Estimated monthly waste: ${report['summary']['estimated_monthly_waste_usd']}",
        "",
        "## Findings",
        ""
    ]

    if not report["findings"]:
        lines.append("- No orphaned resources found.")

    for finding in report["findings"]:
        lines.append(
            f"- `{finding['resource_id']}` "
            f"({finding['resource_type']}) -> "
            f"{finding['reason']}"
        )

    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
        f.write("\n")
