# Cost Janitor Report

## Summary

- Total orphaned resources: 3
- Estimated monthly waste: $20.10

---

## Findings

| Resource ID | Type | Reason | Suggested Action |
|---|---|---|---|
| vol-123abc | EBS Volume | Unattached volume | Delete |
| eipalloc-456xyz | Elastic IP | Unassociated Elastic IP | Release |
| i-0abc123 | EC2 Instance | Missing required tags | Add tags |

---

## Notes

- Resources tagged with `Protected=true` are skipped during delete operations.
- Cost estimates are static approximations for demonstration purposes.