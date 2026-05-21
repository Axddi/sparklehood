from constants import EBS_GP3_PER_GB_MONTH
from detectors.tags import missing_tag_finding, report_tags


def volume_age_days(volume, now):
    created_at = volume.get("CreateTime")

    if not created_at:
        return 0

    return max((now - created_at).days, 0)


def detect_unattached_ebs(ec2_client, now):
    findings = []

    response = ec2_client.describe_volumes()

    for volume in response.get("Volumes", []):
        tags = volume.get("Tags", [])
        tag_finding = missing_tag_finding(volume["VolumeId"], "ebs_volume", tags)

        if tag_finding:
            findings.append(tag_finding)

        if volume["State"] == "available":
            size = volume.get("Size", 0)

            findings.append(
                {
                    "resource_id": volume["VolumeId"],
                    "resource_type": "ebs_volume",
                    "reason": "unattached",
                    "age_days": volume_age_days(volume, now),
                    "estimated_monthly_cost_usd": round(size * EBS_GP3_PER_GB_MONTH, 2),
                    "tags": report_tags(tags),
                    "suggested_action": "delete",
                    "safe_to_auto_delete": False,
                }
            )

    return findings
