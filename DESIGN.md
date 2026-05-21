# DESIGN.md

## Multi-cloud approach

Right now the project only scans AWS-style resources, but if NimbusKart wanted to add GCP or Azure later, I would avoid tightly coupling the detection logic to AWS APIs.

The cleaner approach would be to separate the project into:
- provider layer
- detection engine
- reporting layer

Something like this:

```text
providers/
  aws/
  gcp/
  azure/

detectors/
reporting/
core/
```

Each provider module would expose a common interface:

```python
list_instances()
list_volumes()
list_unused_ips()
list_tags()
```

The detection engine would stay cloud-agnostic and only work with normalized resource objects.

That way, adding GCP support would mostly involve implementing a new provider adapter instead of rewriting the core detection logic.

I would also avoid cloud-specific assumptions in the reporting schema so the same report format could work across providers.

---

## Permissions

The Janitor should operate in two modes:
- read-only (`--dry-run`)
- cleanup (`--delete`)

In dry-run mode, the tool only needs permissions to describe/list resources.

In delete mode, it additionally needs permissions to:
- delete volumes
- release Elastic IPs
- terminate instances
- remove snapshots (if implemented later)

For production, I would strongly separate these roles instead of giving one role permanent delete access.

### Minimal read-only IAM policy

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:DescribeInstances",
        "ec2:DescribeVolumes",
        "ec2:DescribeAddresses",
        "ec2:DescribeTags",
        "s3:ListAllMyBuckets",
        "s3:GetBucketTagging"
      ],
      "Resource": "*"
    }
  ]
}
```

In a real environment, I would also scope access down to specific accounts, regions, or environments wherever possible.

---

## Safety considerations

One obvious risk with automated cleanup systems is deleting something that looks unused but is actually still important.

### Example 1 — Detached disaster recovery volume

An unattached EBS volume might still contain:
- database backups
- forensic data
- rollback snapshots

Automatically deleting it could permanently remove recovery data.

Guardrails I would add:
- delayed deletion windows
- quarantine tags
- approval workflows
- notifications before deletion

---

### Example 2 — Stopped instances used for deployments

A stopped EC2 instance might belong to:
- a blue/green deployment setup
- temporary rollback infrastructure
- scheduled batch systems

Naively terminating it could break deployments or remove fallback infrastructure.

Guardrails:
- minimum inactivity thresholds
- owner approval
- exclusion tags like `Protected=true`
- environment-aware rules (production vs staging)

For production systems, I would strongly prefer recommendations + approval instead of immediate deletion.

---

## Observability

To understand whether the Janitor is actually helping reduce waste, I would publish a few operational metrics.

| Metric | Purpose | Alert Threshold |
|---|---|---|
| `orphan_resources_total` | Total detected waste | Sudden spike |
| `estimated_monthly_waste_usd` | Approximate monthly waste | > predefined budget |
| `janitor_scan_duration_seconds` | Scan performance | unusually high runtime |
| `deletion_attempts_total` | Cleanup activity tracking | abnormal spikes |
| `protected_resources_skipped_total` | Governance visibility | unusual increase |

I would probably send these metrics to:
- CloudWatch
- Prometheus/Grafana
- Datadog

depending on the company’s existing stack.

---

## What I intentionally did not build

There are a few things I intentionally kept out of scope for this assignment.

I did not build:
- historical storage for scan results
- Slack/Teams integrations
- real cloud account integration
- approval dashboards
- multi-account orchestration
- snapshot analysis
- advanced cost estimation logic

Most of those features are useful in production, but they would have added complexity without improving the core goal of the assignment, which was mainly around safe automation, infrastructure structure, and CI/CD integration.

I focused more on building something understandable, testable, and reproducible rather than trying to simulate a full enterprise FinOps platform.