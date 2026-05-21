from moto import mock_ec2
import boto3


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

    print("Mock resources created successfully.")