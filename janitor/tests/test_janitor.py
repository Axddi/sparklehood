from moto import mock_ec2
import boto3

from detectors.ebs import detect_unattached_ebs
from detectors.eip import detect_unused_eips


@mock_ec2
def test_mock_resources():

    ec2 = boto3.client(
        "ec2",
        region_name="us-east-1"
    )
    ec2.create_volume(
        AvailabilityZone="us-east-1a",
        Size=20
    )
    ec2.allocate_address(
        Domain="vpc"
    )

    ebs_findings = detect_unattached_ebs(ec2)

    eip_findings = detect_unused_eips(ec2)

    assert len(ebs_findings) == 1
    assert len(eip_findings) == 1