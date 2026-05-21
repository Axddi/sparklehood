# Design Note

## Multi-cloud Approach

The current Janitor talks directly to AWS-shaped APIs. Before adding GCP next quarter, I would split it into three layers:

```text
providers/
  aws.py      -> boto3 calls, AWS tag shape, AWS ids
  gcp.py      -> Google Cloud clients, labels, project ids
  azure.py    -> Azure SDK clients, resource groups, tags

core/
  models.py   -> normalized Resource and Finding objects
  rules.py    -> unattached disk, idle ip, missing owner, stale compute

reporting/
  json.py
  markdown.py
  notifications.py
```

Provider modules should return normalized resources such as `Volume`, `ComputeInstance`, `PublicIp`, and `Bucket`. The rule engine should not know whether a disk came from EBS, a GCP persistent disk, or an Azure managed disk. That is the boundary that keeps multi-cloud support from becoming three separate scripts with the same bugs copied around.

## Permissions

Dry-run mode should only list and describe resources. For this implementation, the AWS read-only policy would be:

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
        "s3:ListAllMyBuckets",
        "s3:GetBucketTagging"
      ],
      "Resource": "*"
    }
  ]
}
```

Delete mode should be a separate role, not the same role with more permissions left on all the time. It would add `ec2:DeleteVolume`, `ec2:ReleaseAddress`, and `ec2:TerminateInstances`, with tag conditions where AWS supports them. I would also require the automation role to deny deletion when `Protected=true` is present.

## Safety Net

Failure mode 1: an unattached EBS volume is actually a rollback or recovery volume. Deleting it immediately could remove the fastest path back from a bad deployment. Guardrails: quarantine first by tagging it, wait through a configurable grace period, notify the owner, and only delete after approval or a second scan confirms it is still orphaned.

Failure mode 2: a stopped EC2 instance is part of a blue/green deployment, a seasonal worker, or a manual recovery path. Terminating it because it is old could break a release or remove a fallback. Guardrails: require owner and environment tags, skip production unless explicitly enabled, keep `Protected=true` as a hard stop, and make terminate actions approval-based by default.

## Observability

| Metric | Source | Alert |
|---|---|---|
| `janitor_findings_total` | report summary | Spike above previous 7-day average by 50% |
| `janitor_estimated_waste_usd` | report summary | Above team budget threshold |
| `janitor_protected_skips_total` | delete handler | Any sudden increase after a deploy |
| `janitor_delete_attempts_total` | delete handler | Any production delete without approval |
| `janitor_scan_duration_seconds` | wrapper around scan run | Above 2x recent baseline |

I would publish these to the company's existing stack rather than introduce a new one just for this tool. In AWS-only environments that is CloudWatch; in mixed environments I would prefer Prometheus/Grafana or Datadog with cloud/account/resource labels.

## What I Did Not Build

I did not build historical storage, Slack approvals, multi-account fan-out, snapshot analysis, or real cloud credentials. Those are useful production features, but they would hide the core assignment behind extra plumbing. The important part here is the local, reproducible path: create resources, detect waste, produce a report, and prove delete mode has guardrails.
