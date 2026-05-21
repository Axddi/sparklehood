import argparse
import boto3
import sys

from detectors.ebs import detect_unattached_ebs
from detectors.eip import detect_unused_eips
from detectors.tags import is_protected
from detectors.ec2 import detect_stopped_instances
from utils.report import (
    build_report,
    save_json_report,
    save_markdown_summary
)

def handle_deletions(findings, ec2_client):

    for finding in findings:

        tags = finding.get("tags", {})

        if is_protected([
            {"Key": k, "Value": v}
            for k, v in tags.items()
        ]):
            continue

        resource_type = finding["resource_type"]

        resource_id = finding["resource_id"]

        if resource_type == "ebs_volume":

            ec2_client.delete_volume(
                VolumeId=resource_id
            )

            print(f"Deleted volume {resource_id}")

        elif resource_type == "elastic_ip":

            ec2_client.release_address(
                AllocationId=resource_id
            )

            print(f"Released EIP {resource_id}")
            
def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--delete",
        action="store_true"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run without deleting resources"
    )

    args = parser.parse_args()

    ec2_client = boto3.client(
        "ec2",
        region_name="us-east-1"
    )

    findings = []

    findings.extend(
        detect_unattached_ebs(ec2_client)
    )
    
    findings.extend(
        detect_stopped_instances(ec2_client)
    )

    findings.extend(
        detect_unused_eips(ec2_client)
    )

    report = build_report(findings)

    save_json_report(report)

    save_markdown_summary(report)

    print("Report generated.")
    
    if args.delete:
        handle_deletions(findings, ec2_client)

    if findings and not args.delete:
        sys.exit(1)


if __name__ == "__main__":
    main()