from datetime import datetime, timezone

from detectors.ebs import detect_unattached_ebs
from detectors.ec2 import detect_stopped_instances, stopped_at_from_reason
from detectors.eip import detect_unused_eips
from detectors.s3 import detect_untagged_buckets
from janitor import handle_deletions
from utils.report import build_report


REQUIRED_TAGS = [
    {"Key": "Project", "Value": "NimbusKart"},
    {"Key": "Environment", "Value": "staging"},
    {"Key": "Owner", "Value": "aaditya"},
]


class FakeEc2Client:
    def __init__(self):
        self.deleted_volumes = []
        self.released_addresses = []
        self.terminated_instances = []

    def describe_volumes(self):
        return {
            "Volumes": [
                {
                    "VolumeId": "vol-orphan",
                    "State": "available",
                    "Size": 20,
                    "CreateTime": datetime(2026, 5, 1, tzinfo=timezone.utc),
                    "Tags": REQUIRED_TAGS,
                },
                {
                    "VolumeId": "vol-missing-tags",
                    "State": "in-use",
                    "Size": 8,
                    "CreateTime": datetime(2026, 5, 1, tzinfo=timezone.utc),
                    "Tags": [{"Key": "Project", "Value": "NimbusKart"}],
                },
            ]
        }

    def describe_instances(self):
        return {
            "Reservations": [
                {
                    "Instances": [
                        {
                            "InstanceId": "i-stopped-old",
                            "State": {"Name": "stopped"},
                            "StateTransitionReason": "User initiated (2026-05-01 10:00:00 GMT)",
                            "Tags": REQUIRED_TAGS,
                        },
                        {
                            "InstanceId": "i-missing-tags",
                            "State": {"Name": "running"},
                            "Tags": [{"Key": "Project", "Value": "NimbusKart"}],
                        },
                    ]
                }
            ]
        }

    def describe_addresses(self):
        return {
            "Addresses": [
                {
                    "AllocationId": "eipalloc-unused",
                    "PublicIp": "203.0.113.10",
                    "Tags": REQUIRED_TAGS,
                },
                {
                    "AllocationId": "eipalloc-missing-tags",
                    "PublicIp": "203.0.113.11",
                    "AssociationId": "eipassoc-123",
                    "Tags": [],
                },
            ]
        }

    def delete_volume(self, VolumeId):
        self.deleted_volumes.append(VolumeId)

    def release_address(self, AllocationId=None, PublicIp=None):
        self.released_addresses.append(AllocationId or PublicIp)

    def terminate_instances(self, InstanceIds):
        self.terminated_instances.extend(InstanceIds)


class FakeS3Client:
    class exceptions:
        class NoSuchTagSet(Exception):
            pass

        class NoSuchBucket(Exception):
            pass

    def list_buckets(self):
        return {"Buckets": [{"Name": "tagged-bucket"}, {"Name": "untagged-bucket"}]}

    def get_bucket_tagging(self, Bucket):
        if Bucket == "tagged-bucket":
            return {"TagSet": REQUIRED_TAGS}

        raise self.exceptions.NoSuchTagSet()


def test_detects_required_orphan_patterns():
    ec2 = FakeEc2Client()
    s3 = FakeS3Client()
    now = datetime(2026, 5, 22, tzinfo=timezone.utc)

    findings = []
    findings.extend(detect_unattached_ebs(ec2, now))
    findings.extend(detect_stopped_instances(ec2, now=now))
    findings.extend(detect_unused_eips(ec2))
    findings.extend(detect_untagged_buckets(s3))

    reasons = {finding["reason"] for finding in findings}

    assert "unattached" in reasons
    assert "stopped_too_long" in reasons
    assert "unassociated" in reasons
    assert "missing_tags: Environment,Owner" in reasons


def test_stopped_instance_age_uses_state_transition_time():
    stopped_at = stopped_at_from_reason("User initiated (2026-05-01 10:00:00 GMT)")

    assert stopped_at == datetime(2026, 5, 1, 10, 0, tzinfo=timezone.utc)


def test_delete_mode_skips_protected_resources():
    ec2 = FakeEc2Client()
    findings = [
        {
            "resource_id": "vol-protected",
            "resource_type": "ebs_volume",
            "reason": "unattached",
            "age_days": 21,
            "estimated_monthly_cost_usd": 1.60,
            "tags": {"Protected": "true"},
            "suggested_action": "delete",
            "safe_to_auto_delete": False,
        },
        {
            "resource_id": "eipalloc-unused",
            "resource_type": "elastic_ip",
            "reason": "unassociated",
            "age_days": 0,
            "estimated_monthly_cost_usd": 3.65,
            "tags": {},
            "suggested_action": "release",
            "safe_to_auto_delete": False,
        },
    ]

    handle_deletions(findings, ec2)

    assert ec2.deleted_volumes == []
    assert ec2.released_addresses == ["eipalloc-unused"]


def test_report_schema_matches_assignment_shape():
    report = build_report(
        findings=[
            {
                "resource_id": "vol-orphan",
                "resource_type": "ebs_volume",
                "reason": "unattached",
                "age_days": 21,
                "estimated_monthly_cost_usd": 1.60,
                "tags": {"Project": "NimbusKart"},
                "suggested_action": "delete",
                "safe_to_auto_delete": False,
            }
        ],
        region="us-east-1",
    )

    assert set(report) == {
        "scan_timestamp",
        "account_id",
        "region",
        "summary",
        "findings",
    }
    assert report["summary"]["total_orphans"] == 1
    assert report["findings"][0]["resource_id"] == "vol-orphan"
