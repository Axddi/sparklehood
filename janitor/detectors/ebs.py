from constants import EBS_GP3_PER_GB_MONTH


def detect_unattached_ebs(ec2_client):
    findings = []

    response = ec2_client.describe_volumes()

    for volume in response["Volumes"]:

        if volume["State"] == "available":

            size = volume.get("Size", 0)

            findings.append({
                "resource_id": volume["VolumeId"],
                "resource_type": "ebs_volume",
                "reason": "unattached",
                "age_days": 0,
                "estimated_monthly_cost_usd": round(
                    size * EBS_GP3_PER_GB_MONTH,
                    2
                ),
                "tags": {},
                "suggested_action": "delete",
                "safe_to_auto_delete": False
            })

    return findings