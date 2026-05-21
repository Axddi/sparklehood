import argparse
import boto3
import os
import sys
from datetime import datetime, timezone

from botocore.config import Config

from detectors.ebs import detect_unattached_ebs
from detectors.ec2 import detect_stopped_instances
from detectors.eip import detect_unused_eips
from detectors.s3 import detect_untagged_buckets
from detectors.tags import is_protected
from utils.report import build_report, save_json_report, save_markdown_summary


def handle_deletions(findings, ec2_client):
    for finding in findings:
        tags = finding.get("tags", {})
        resource_type = finding["resource_type"]
        resource_id = finding["resource_id"]
        action = finding["suggested_action"]

        if action not in ["delete", "release", "terminate"]:
            continue

        if is_protected(
            [{"Key": k, "Value": v} for k, v in tags.items() if v is not None]
        ):
            print(f"Skipped protected resource {resource_id}")
            continue

        if resource_type == "ebs_volume":
            ec2_client.delete_volume(VolumeId=resource_id)

            print(f"Deleted volume {resource_id}")

        elif resource_type == "elastic_ip":
            if resource_id.startswith("eipalloc-"):
                ec2_client.release_address(AllocationId=resource_id)
            else:
                ec2_client.release_address(PublicIp=resource_id)

            print(f"Released EIP {resource_id}")

        elif resource_type == "ec2_instance":
            ec2_client.terminate_instances(InstanceIds=[resource_id])

            print(f"Terminated instance {resource_id}")


def main():
    default_endpoint_url = os.getenv("AWS_ENDPOINT_URL", "http://localhost:4566")

    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group()

    mode.add_argument("--delete", action="store_true")
    mode.add_argument(
        "--dry-run", action="store_true", help="Scan only. This is the default."
    )

    parser.add_argument("--region", default=os.getenv("AWS_REGION", "us-east-1"))

    parser.add_argument(
        "--endpoint-url",
        default=default_endpoint_url,
        help="AWS-compatible endpoint. Defaults to LocalStack.",
    )

    parser.add_argument("--account-id", default="000000000000")

    parser.add_argument(
        "--stopped-days",
        type=int,
        default=14,
        help="Flag stopped EC2 instances older than this many days.",
    )

    args = parser.parse_args()

    client_kwargs = {
        "region_name": args.region,
        "endpoint_url": args.endpoint_url,
        "aws_access_key_id": os.getenv("AWS_ACCESS_KEY_ID", "test"),
        "aws_secret_access_key": os.getenv("AWS_SECRET_ACCESS_KEY", "test"),
        "config": Config(s3={"addressing_style": "path"}),
    }

    ec2_client = boto3.client("ec2", **client_kwargs)
    s3_client = boto3.client("s3", **client_kwargs)

    findings = []
    now = datetime.now(timezone.utc)

    findings.extend(detect_unattached_ebs(ec2_client, now))

    findings.extend(
        detect_stopped_instances(ec2_client, threshold_days=args.stopped_days, now=now)
    )

    findings.extend(detect_unused_eips(ec2_client))

    findings.extend(detect_untagged_buckets(s3_client))

    report = build_report(findings, region=args.region, account_id=args.account_id)

    save_json_report(report)
    save_markdown_summary(report)

    print("Report generated.")

    if args.delete:
        handle_deletions(findings, ec2_client)

    if findings and not args.delete:
        sys.exit(2)


if __name__ == "__main__":
    main()
