from datetime import datetime, timezone

from constants import STOPPED_T3_MICRO_ESTIMATED_MONTHLY


def detect_stopped_instances(
    ec2_client,
    threshold_days=14
):
    findings = []

    response = ec2_client.describe_instances()

    reservations = response.get("Reservations", [])

    for reservation in reservations:

        for instance in reservation["Instances"]:

            state = instance["State"]["Name"]

            if state == "stopped":

                launch_time = instance["LaunchTime"]

                age_days = (
                    datetime.now(timezone.utc) - launch_time
                ).days

                if age_days >= threshold_days:

                    findings.append({
                        "resource_id": instance["InstanceId"],
                        "resource_type": "ec2_instance",
                        "reason": "stopped_too_long",
                        "age_days": age_days,
                        "estimated_monthly_cost_usd":
                            STOPPED_T3_MICRO_ESTIMATED_MONTHLY,
                        "tags": {},
                        "suggested_action": "terminate",
                        "safe_to_auto_delete": False
                    })

    return findings