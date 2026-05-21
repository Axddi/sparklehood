# Cost Janitor Report

Total orphans found: 4
Estimated monthly waste: $5.25

## Findings

- `vol-123abc` (ebs_volume) -> unattached
- `eipalloc-456xyz` (elastic_ip) -> unassociated
- `i-0abc123` (ec2_instance) -> stopped_too_long
- `untagged-bucket` (s3_bucket) -> missing_tags: Project,Environment,Owner
