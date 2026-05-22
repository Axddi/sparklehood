# NimbusKart Cost Hygiene & Automation

## Overview

NimbusKart is a fictional e-commerce company whose AWS bill has grown because old resources are not being cleaned up consistently. This repo builds a local-only version of a cost hygiene workflow: Terraform creates a small staging stack in LocalStack, and a Python Janitor scans that local AWS API for unattached EBS volumes, old stopped EC2 instances, unused Elastic IPs, and missing ownership tags. The goal is not to pretend this is a full FinOps platform; it is a safe, reproducible slice of the workflow I would want before allowing any cleanup automation near a real account.

## How to run locally

```bash
git clone <your-repo-url>
cd sparklehood
```

Start LocalStack:

```bash
docker run --rm -d \
  --name localstack \
  -p 4566:4566 \
  -e SERVICES=ec2,s3,iam \
  -e DEFAULT_REGION=us-east-1 \
  localstack/localstack:3.8.1
```

Create and activate a virtual environment:

**Linux / macOS:**

```bash
python -m venv .venv
source .venv/bin/activate
```

**Windows (Git Bash):**

```bash
source .venv/Scripts/activate
```

**Windows (PowerShell):**

```powershell
.\.venv\Scripts\Activate.ps1
```

Install Python dependencies:

```bash
pip install -r janitor/requirements.txt
```

Apply the Terraform stack against LocalStack:

```bash
cd terraform
terraform init
terraform fmt -check -recursive
terraform validate
terraform apply -auto-approve
```

Run the unit tests:

```bash
cd ../janitor
python -m pytest tests/test_janitor.py -v
```

Run the Cost Janitor in dry-run mode:

```bash
python janitor.py --dry-run
```

The dry run is expected to exit with code `2` when it finds the intentionally unattached EBS volume. It still writes:

- `janitor/report.json`
- `janitor/summary.md`

To inspect the report without your shell stopping on the non-zero exit:

```bash
python janitor.py --dry-run || true
```

Delete mode is intentionally explicit:

```bash
python janitor.py --delete
```

Resources tagged `Protected=true` are skipped even in delete mode.

## Architecture

```text
GitHub PR or local shell
        |
        v
Terraform -> LocalStack AWS APIs
        |       |
        |       +-- VPC, subnets, security group
        |       +-- EC2 web instances
        |       +-- S3 log bucket
        |       +-- known unattached EBS volume
        |
        v
Python Cost Janitor
        |
        +-- EC2/EBS/EIP detectors
        +-- S3 tag detector
        +-- protected-resource guard
        |
        v
report.json + summary.md + PR comment
```

## Decisions & deviations

- I kept the assignment's default SSH CIDR as `0.0.0.0/0`, but called it out because I would not use that default in production.
- I use LocalStack as the default runtime endpoint so the project does not need, or accidentally use, a real AWS account.
- I added S3 tag scanning even though the orphan examples focus mostly on EC2 resources, because the brief says any resource missing required tags should be reported.
- I estimate stopped EC2 compute waste as `$0.00` because stopped instances do not accrue EC2 compute hours; the finding is still useful because stopped instances often hide attached disks, IPs, and stale ownership.
- I left destructive cleanup limited to EBS, EIP, and old stopped EC2 findings. Tag-only findings are recommendations, not deletion candidates.
- I keep generated reports out of git and store stable examples under `samples/`, so running the tool does not dirty the repo.

## Trade-offs

With one more week, I would add snapshot and NAT gateway detectors, store scan history so trends are visible, and add a small approval queue before delete mode can run in production. I would also split provider access behind a clearer adapter interface before adding GCP or Azure. For this assignment I kept the implementation small enough that a reviewer can read the whole flow and see the safety checks directly.

## AI usage disclosure

I used ChatGPT while debugging the LocalStack/Terraform workflow, checking edge cases around protected delete behavior, and tightening the documentation. I also used GitHub Copilot lightly for repetitive Python and YAML scaffolding.

One AI suggestion I rejected was treating stopped EC2 instances as if they always had active compute cost. I checked that assumption and changed the report to show stopped instances as a cleanup signal with `$0.00` compute waste, because the real spend is usually attached storage or public IPs.

The part I worked through most deliberately was delete safety: the Janitor now carries tags into each finding and checks `Protected=true` at deletion time. I wanted that path to be boring and obvious, because a cleanup tool that is clever but unsafe is worse than no cleanup tool.
