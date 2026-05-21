# Walkthrough Notes

Video link: ADD_VIDEO_LINK_HERE

Planned walkthrough:

1. Start LocalStack with Docker.
2. Run `terraform init`, `terraform validate`, and `terraform apply -auto-approve`.
3. Run `python janitor.py --dry-run` and show the generated `report.json`.
4. Explain the known unattached EBS volume finding.
5. Point out the protected-delete guard in `janitor/janitor.py`.
6. Mention one thing I would improve next: scan history and approval workflow before production delete mode.

Short transcript outline:

This project is a local-only cost hygiene workflow for NimbusKart. Terraform creates a small staging stack in LocalStack, including one intentionally unattached EBS volume. The Python Janitor scans the same LocalStack endpoint and reports unattached volumes, old stopped instances, unused Elastic IPs, and missing required tags. The part I am most careful about is delete mode: every finding carries tags into the report, and anything tagged `Protected=true` is skipped before a destructive API call is made.
