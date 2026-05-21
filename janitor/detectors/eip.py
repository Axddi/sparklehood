from constants import ELASTIC_IP_MONTHLY


def detect_unused_eips(ec2_client):
    findings = []

    response = ec2_client.describe_addresses()

    for address in response["Addresses"]:

        if "AssociationId" not in address:

            findings.append({
                "resource_id": address["AllocationId"],
                "resource_type": "elastic_ip",
                "reason": "unassociated",
                "age_days": 0,
                "estimated_monthly_cost_usd": ELASTIC_IP_MONTHLY,
                "tags": {},
                "suggested_action": "release",
                "safe_to_auto_delete": False
            })

    return findings