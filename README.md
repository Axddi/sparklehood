# NimbusKart Cost Hygiene & Automation

## Overview

This project was built as part of the DevOps Engineer practical assignment for Code & Conscience.

The goal was to simulate a small cloud cost hygiene system for a fictional e-commerce startup called NimbusKart. The startup was facing increasing AWS costs because of orphaned infrastructure resources like unattached EBS volumes, unused Elastic IPs, stopped EC2 instances, and inconsistent tagging.

The repository contains:
- Terraform code for a small AWS-style staging setup
- A Python-based "Cost Janitor" tool to detect wasteful resources
- GitHub Actions workflow for automated checks
- A short design document describing how the solution could scale into a real multi-cloud setup

The implementation focuses more on safety, maintainability, and reproducibility than adding unnecessary complexity.

---

## How to run locally

### Clone the repository

```bash
git clone <your-repo-url>
cd nimbuskart-cost-hygiene
```

---

### Create a virtual environment

```bash
python -m venv .venv
```

---

### Activate the environment

#### Git Bash

```bash
source .venv/Scripts/activate
```

#### PowerShell

```powershell
.venv\Scripts\Activate.ps1
```

---

### Install dependencies

```bash
pip install -r janitor/requirements.txt
```

---

### Validate Terraform

```bash
cd terraform

terraform init

terraform fmt -check -recursive

terraform validate
```

---

### Run tests

```bash
cd ../janitor

python -m pytest tests/test_janitor.py -v
```

---

### Run the Cost Janitor

```bash
python janitor.py
```

The script generates:
- `report.json`
- `summary.md`

---

## Architecture

```text
                Terraform Infrastructure
                           │
                           ▼
                Simulated AWS Environment
                     (Moto Mocking)
                           │
                           ▼
                    Cost Janitor
                  Detection Engine
                           │
        ┌──────────────────┴──────────────────┐
        ▼                                     ▼
   report.json                           summary.md
                           │
                           ▼
                  GitHub Actions CI
```

---

## Decisions & deviations

- Kept SSH CIDR configurable because exposing port 22 to `0.0.0.0/0` would not be a safe production default.
- Used Moto for testing instead of fully relying on LocalStack because Docker networking was unstable on my Windows setup, and the assignment explicitly allowed SDK-level mocking.
- Pinned specific boto3/moto versions after running into Python 3.12 compatibility issues during testing.
- Kept cost estimation logic intentionally simple using static pricing constants because the focus of the assignment was detection and automation flow.
- Lifecycle configuration for S3 was simplified slightly during local testing due to LocalStack compatibility inconsistencies.

---

## Trade-offs

If I had more time, I would probably extend this in a few areas:
- Add support for additional AWS resources like snapshots, NAT gateways, and load balancers
- Store scan history in a database for trend analysis
- Add Slack or Teams notifications for new findings
- Build a cleaner provider abstraction layer for future GCP/Azure support
- Add approval workflows before destructive actions
- Improve automated test coverage around delete operations

I intentionally avoided overengineering the project and focused on keeping the workflow understandable and reproducible.

---

## AI usage disclosure

AI tools used:
- ChatGPT for debugging Terraform/provider issues, reviewing architecture decisions, and refining parts of the CI workflow
- GitHub Copilot for repetitive boilerplate code

One issue caused by AI-generated suggestions:
- An earlier recommendation used newer Moto versions that behaved inconsistently on Python 3.12 Windows environments. I debugged the issue manually and switched to stable pinned versions inside a virtual environment.

One section I intentionally worked through manually:
- The orphan detection/reporting flow and delete safeguards. I wanted to fully understand the detection logic and make sure the generated report matched the required schema exactly.