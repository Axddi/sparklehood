HOURS_PER_MONTH = 730

# Source: AWS EBS pricing, General Purpose SSD gp3 storage in us-east-1:
# https://aws.amazon.com/ebs/pricing/
EBS_GP3_PER_GB_MONTH = 0.08

# Source: AWS VPC/EC2 public IPv4 pricing is 0.005 USD per IP-hour:
# https://aws.amazon.com/vpc/pricing/
ELASTIC_IP_PER_HOUR = 0.005
ELASTIC_IP_MONTHLY = ELASTIC_IP_PER_HOUR * HOURS_PER_MONTH

# Stopped EC2 instances do not accrue compute instance-hours. The waste signal is
# still useful because attached disks, IPs, and stale inventory often hide there.
STOPPED_INSTANCE_ESTIMATED_MONTHLY = 0.0

REQUIRED_TAGS = [
    "Project",
    "Environment",
    "Owner"
]
