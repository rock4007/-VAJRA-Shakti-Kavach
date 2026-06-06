# 88/CK All Attack Vectors Blocks

Security-focused distributed systems platform that combines preventive controls, admission hardening, anomaly analytics, and rollout safety governance.

## Executive Summary

88/CK is a multi-service reference architecture for modern security engineering. It demonstrates how to enforce controls across the full request lifecycle:

- ingress filtering and payload defusing
- replay-safe consensus admission
- anomaly detection with explainability
- stability-aware rollout decisioning

This repository is designed for engineering validation, portfolio credibility, and deployment-oriented experimentation.

## Current Status

- Readiness: deployment-ready for local and pre-production environments
- Runtime verification: docker compose build and stack startup validated
- Container hardening: healthchecks, restart policies, resource limits, and log rotation configured
- Frontend dependency posture: npm audit clean

## What Is New (April 2026)

- Added container healthchecks to gateway, stability engine, and frontend runtime images.
- Hardened Compose profile with restart policies, constrained resources, and bounded container logging.
- Introduced service-level dockerignore coverage to reduce image context and prevent leakage of non-runtime files.
- Added repository-level gitignore for generated artifacts and local environment noise.
- Upgraded frontend toolchain dependencies and verified clean audit output.

## Architecture Domains

Primary implementation lives in [88ck-immune-layer/README.md](88ck-immune-layer/README.md).

1. Pillar 1 Morphic: ingress gateway and adaptive threat filtering
2. Pillar 2 Consensus: replay resistance and proof-oriented admission
3. Pillar 3 Entropy: anomaly detection and explainability pipeline
4. Stability Engine: Lyapunov-inspired rollout guardrail and orchestration logic

## Security Control Coverage

| Layer | Control Objective | Representative Implementation |
|---|---|---|
| Ingress | Block high-confidence malicious input | SQLi and payload signature filtering in Morphic |
| Admission | Reject replay and unverifiable proposals | Staged nonce and proof checks in Consensus |
| Detection | Surface anomalous behavior patterns | Baseline plus graph and embedding analytics in Entropy |
| Governance | Prevent destabilizing change rollout | Stability scoring and action plans in Stability Engine |

## Operational Readiness

- Containerization: multi-service Docker builds with distroless runtime where applicable
- Local orchestration: [88ck-immune-layer/infra/docker-compose.yml](88ck-immune-layer/infra/docker-compose.yml)
- Kubernetes path: [88ck-immune-layer/infra/helm/88ck](88ck-immune-layer/infra/helm/88ck)
- Security automation: root workflows in [.github/workflows](.github/workflows)
- Documentation set: architecture, theory, API, and coupling analysis in [88ck-immune-layer/docs](88ck-immune-layer/docs)

## Quick Start

### Prerequisites

- Go 1.25 or newer
- Python 3.11 or newer
- Node.js 20 or newer
- Docker and Docker Compose

### Bootstrap

```bash
git clone https://github.com/rock4007/88-ck-all-attack-vectors-blocks-.git
cd 88-ck-all-attack-vectors-blocks-/88ck-immune-layer
./scripts/bootstrap.sh
```

### Run Full Stack

```bash
cd infra
docker compose up --build
```

## Validation Runbook

Execute from 88ck-immune-layer unless noted.

```bash
cd pillar1-morphic && go test ./...
cd ../pillar2-consensus && go test ./...
cd ../stability-engine && go test ./...
cd ../adversarial-harness && python runner.py --strict
cd ../frontend && npm run build
```

## Repository Structure

```text
88-ck-all-attack-vectors-blocks-/
├── README.md
└── 88ck-immune-layer/
    ├── go.work
    ├── adversarial-harness/
    ├── docs/
    ├── frontend/
    ├── infra/
    ├── pillar1-morphic/
    ├── pillar2-consensus/
    ├── pillar3-entropy/
    ├── scripts/
    └── stability-engine/
```

## Engineering Portfolio Value

This codebase maps directly to roles that require practical security depth:

- Security Engineer
- Application Security Engineer
- Platform Security Engineer
- Detection Engineer or SOC Engineer
- Cloud Security Engineer

## Governance

This repository is owner-controlled. Approval and branch policy are documented in [AUTHORITY_POLICY.md](AUTHORITY_POLICY.md).

## License

MIT. See [88ck-immune-layer/LICENSE](88ck-immune-layer/LICENSE).
