from datetime import datetime, timezone

from constants import STOPPED_INSTANCE_ESTIMATED_MONTHLY
from detectors.tags import missing_tag_finding, report_tags


def stopped_at_from_reason(reason):
    if not reason or "(" not in reason or ")" not in reason:
        return None

    raw_timestamp = reason.split("(", 1)[1].split(")", 1)[0]

    for pattern in ("%Y-%m-%d %H:%M:%S %Z", "%Y-%m-%d %H:%M:%S GMT"):
        try:
            stopped_at = datetime.strptime(raw_timestamp, pattern)
            return stopped_at.replace(tzinfo=timezone.utc)
        except ValueError:
            continue

    return None


def detect_stopped_instances(
    ec2_client,
    threshold_days=14,
    now=None
):
    findings = []
    now = now or datetime.now(timezone.utc)

    response = ec2_client.describe_instances()

    reservations = response.get("Reservations", [])

    for reservation in reservations:

        for instance in reservation["Instances"]:
            tags = instance.get("Tags", [])
            tag_finding = missing_tag_finding(
                instance["InstanceId"],
                "ec2_instance",
                tags
            )

            if tag_finding:
                findings.append(tag_finding)

            state = instance["State"]["Name"]

            if state == "stopped":
                stopped_at = stopped_at_from_reason(
                    instance.get("StateTransitionReason")
                )

                if not stopped_at:
                    continue

                age_days = max((now - stopped_at).days, 0)

                if age_days >= threshold_days:

                    findings.append({
                        "resource_id": instance["InstanceId"],
                        "resource_type": "ec2_instance",
                        "reason": "stopped_too_long",
                        "age_days": age_days,
                        "estimated_monthly_cost_usd":
                            STOPPED_INSTANCE_ESTIMATED_MONTHLY,
                        "tags": report_tags(tags),
                        "suggested_action": "terminate",
                        "safe_to_auto_delete": False
                    })

    return findings
