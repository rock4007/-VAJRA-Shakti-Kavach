
# VAJRA — Shakti Kavach

VAJRA (Shakti Kavach) is a defensive cybersecurity framework designed to support critical infrastructure protection, incident response readiness, and secure operations for government and public-sector deployments.

## Recent Changes (2026-02-03)
- Backend: added `/heart_status` consolidated monitoring endpoint and improved SSE publishing for real-time heart-rate and admin events.
- Frontend: improved `app.html` to prefer SSE (`/heartrate/stream`) with a polling fallback and added auto-show of the heart monitor UI.
- Admin UI: fixed `admin_test_dashboard.html` to avoid overwriting loaded alerts (`alertsData` seeded only when empty) and added SSE-driven SOS alert display with quick action endpoints (`/admin/alerts/<case_id>/ack`, `/admin/alerts/<case_id>/case`).
- Tests & scripts: added smoke-test scripts for SSE verification and health-checks under `scripts/`.

If you maintain a fork or mirror, please pull these changes and run the smoke tests described in `VajraBackend/README.md` before deploying to any shared environment.

Executive Summary
- Purpose: Provide a hardened, audit-ready codebase and operational playbooks to support detection, containment, recovery, and sustained secure operations.
- Audience: Government security teams, SOC operators, system integrators, and authorized maintainers.

Key Objectives
- Deliver repeatable deployment artifacts and configuration templates for controlled environments.
- Enforce secure defaults and documented procedures for testing and production rollouts.
- Maintain an auditable change history and compliance posture suitable for regulated environments.

Repository Structure (high level)
- `VajraBackend/` — Backend services and API code.
- `VajraLightWeb/`, `VajraKavachApp_template/` — Frontend and integration templates.
- `CloudServer/` — Cloud deployment artifacts and container definitions.
- `docs/` (recommended) — Policies, playbooks, and audit artefacts (create and maintain).

Getting Started (recommended minimal steps)
1. Review this README and any component-level READMEs before any execution.
2. Validate in an isolated test environment (VM or air-gapped network) with limited privileges.
3. Ensure all credentials, secrets, and environment-specific configs are managed via secret stores and not checked into source control.

Security Controls and Best Practices
- Access: Restrict repository access to organization-approved accounts using org-level controls and MFA.
- Secrets: Use a secret management solution (Vault, cloud KMS). Do not store secrets in this repo.
- Testing: Run static analysis, dependency scanning, and container image scans before deployment.
- Change Management: All changes must be reviewed and approved through PR with required approvers.

Compliance and Governance
- This repository is maintained to support compliance with applicable government standards and organizational policies.
- Maintain an audit trail for all configuration and policy changes; use signed commits and tagged releases for production artifacts.

Support and Reporting
- For operational issues or incident reporting, follow the organizational incident response procedure and notify the project custodian listed in internal documentation.

Contributing
- Contributions must follow the project's contribution policy and pass code review and security checks. Contact the project custodian for contributor onboarding.
# VAJRA — Shakti Kavach

VAJRA — Shakti Kavach is a prototype platform for secure incident capture, evidence integrity, and emergency response. This repository contains the backend, deployment artifacts, and supporting tools used for development and pilot deployments.

## Purpose
- Provide a consolidated, auditable, and deployable codebase for controlled pilot and evaluation environments.
- Maintain production-minded defaults for deployment, security, and observability.

## Single canonical README
This file is the canonical top-level README. Extended, component-specific, and deployment documents have been moved to `docs/` to keep this page concise. See `docs/` for the full moved documents:

- `docs/README_DEPLOY.md` — Local & Kubernetes quick-start and deploy notes
- `docs/README_DEPLOY_CLOUD.md` — Cloud deployment (GCP/Terraform) details
- `docs/README_DEPLOYMENT.md` — Deployment status, CI/CD and observability notes
- `docs/README_GOVERNMENT.md` — Government-compliance and certification notes

## Quick Start (developer)
1. Create and activate a Python virtual environment, then install dependencies:

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

2. Start locally (development):

```powershell
docker-compose up -d
# Backend available at http://localhost:8008
```

3. For Kubernetes deploys, see `k8s/` and `docs/README_DEPLOY.md`.

## Deployment Overview
- Local development: `docker-compose.yml` (quick start)
- Kubernetes: manifests in `k8s/` (Deployment, Service, Ingress, HPA)
- Cloud: CI workflows and Terraform under `.github/workflows/` and `terraform/` (see `docs/README_DEPLOY_CLOUD.md`)

## Security highlights
- Do not commit secrets; use a secret manager (Vault, cloud KMS).
- Enforce TLS for all network endpoints in production.
- Use a persistent, auditable store for evidence and rotate keys regularly.

## Contributing
- Work in topic branches and submit pull requests for review.
- Include tests and a security review for production-impacting changes.

## Where to find more
- Component READMEs: e.g., `VajraBackend/README.md`
- Deployment docs and provider-specific instructions: `docs/`
- CI/CD workflows: `.github/workflows/`

## License
See `LICENSE` in the repository root.

---
This repository is maintained for controlled pilot and evaluation use. For production deployments follow the governance and compliance workflows documented in `docs/README_GOVERNMENT.md`.
