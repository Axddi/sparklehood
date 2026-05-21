# Submission — DevOps Engineer Assignment

**Candidate name:** Aaditya Saxena  
**Email:** aaditya.saxena.1357@gmail.com
**Date submitted:** 2026-05-21  
**Hours spent (approximate):** Around 8–10 hours  

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

Link (Loom / YouTube unlisted / Google Drive):  
ADD_VIDEO_LINK_HERE

Length: under 5 minutes

---

## Sample report

Path to a sample report.json produced by the script:

```text
samples/report.example.json
```

---

## Known limitations

- Cost estimates are static approximations and not connected to live cloud pricing APIs
- Detection currently focuses only on a small set of AWS resources
- Moto was used for testing because it was more stable than LocalStack on my Windows setup
- Historical scan storage and dashboards were intentionally left out to keep the scope manageable
- Delete mode currently supports only selected resource types

---

## AI usage disclosure

- Used ChatGPT mainly for debugging Terraform/provider issues, reviewing architecture ideas, and improving parts of the CI workflow
- Used GitHub Copilot occasionally for repetitive boilerplate code
- One AI suggestion around Moto versions caused compatibility problems on Python 3.12 Windows environments, which I debugged and fixed by pinning stable versions inside a virtual environment
- The detection flow, reporting logic, and delete safeguards were manually adjusted to make sure the behavior matched the assignment requirements properly