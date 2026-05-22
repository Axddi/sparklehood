# Submission - DevOps Engineer Assignment

**Candidate name:** Aaditya Saxena  
**Email:** aaditya.saxena.1357@gmail.com  
**Date submitted:** 2026-05-22  
**Hours spent (approximate):** Around 8-10 hours  

## Deliverables checklist

- [x] Part A: Terraform code under /terraform applies cleanly on LocalStack
- [x] Part A: `terraform validate` and `terraform fmt -check` both pass
- [x] Part B: Janitor script runs in --dry-run mode and produces report.json
- [x] Part B: GitHub Actions workflow runs green on a fresh PR
- [x] Part B: --delete mode respects Protected=true tag
- [x] Part C: DESIGN.md is present and within 2 pages
- [ ] Walkthrough video link below is accessible (unlisted is fine)

---

## Walkthrough video

Link:
https://www.loom.com/share/de9ba22ab89943eab6bd7f6ed1c295f6

Length: 6 minutes (can watch in 1.25x)

---

## Sample report

Path to a sample report.json produced by the script:

```text
samples/report.example.json
```

---

## Known limitations

- Cost estimates are intentionally conservative and static.
- Stopped EC2 instances are reported as stale resources, but compute waste is shown as `$0.00` because stopped instances do not accrue compute instance-hours.
- Delete mode supports EBS volumes, Elastic IPs, and stopped EC2 instances; tag-only findings remain recommendations.
- The Janitor currently scans one configured LocalStack/AWS-compatible endpoint at a time.
- The walkthrough video is still pending and should be recorded after the final local verification pass.

---

## AI usage disclosure

- Used ChatGPT for debugging the LocalStack/Terraform flow, reviewing safety edge cases, and tightening documentation.
- Used GitHub Copilot lightly for repetitive Python/YAML scaffolding.
- One AI suggestion treated stopped EC2 instances as active compute waste; I corrected that because stopped EC2 compute is not billed the same way running compute is.
- I manually focused on the protected-delete path and report shape because those are the parts I expect an interviewer to ask me to explain.
