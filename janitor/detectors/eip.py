from constants import ELASTIC_IP_MONTHLY
from detectors.tags import missing_tag_finding, report_tags


def detect_unused_eips(ec2_client):
    findings = []

    response = ec2_client.describe_addresses()

    for address in response["Addresses"]:
        tags = address.get("Tags", [])
        resource_id = address.get("AllocationId") or address.get("PublicIp")
        tag_finding = missing_tag_finding(
            resource_id,
            "elastic_ip",
            tags
        )

        if tag_finding:
            findings.append(tag_finding)

        if "AssociationId" not in address:

            findings.append({
                "resource_id": resource_id,
                "resource_type": "elastic_ip",
                "reason": "unassociated",
                "age_days": 0,
                "estimated_monthly_cost_usd": round(ELASTIC_IP_MONTHLY, 2),
                "tags": report_tags(tags),
                "suggested_action": "release",
                "safe_to_auto_delete": False
            })

    return findings
