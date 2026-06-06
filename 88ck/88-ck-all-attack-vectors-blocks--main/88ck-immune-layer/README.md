<div align="center">

<img src="https://img.shields.io/badge/88%2FCK-Immune%20Layer-0d1117?style=for-the-badge&labelColor=0d1117&color=00d4ff" alt="88/CK Immune Layer"/>

# 88/CK Immune Layer

**A practical security and resilience stack for distributed systems.**

[![Build](https://img.shields.io/github/actions/workflow/status/rock4007/88-ck-all-attack-vectors-blocks-/ci.yml?branch=main&style=flat-square&label=CI)](https://github.com/rock4007/88-ck-all-attack-vectors-blocks-/actions)
[![Security Scan](https://img.shields.io/github/actions/workflow/status/rock4007/88-ck-all-attack-vectors-blocks-/security-scan.yml?branch=main&style=flat-square&label=Security%20Scan&color=green)](https://github.com/rock4007/88-ck-all-attack-vectors-blocks-/actions)
[![Go Version](https://img.shields.io/badge/Go-1.25%2B-00ADD8?style=flat-square&logo=go)](https://go.dev)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](./LICENSE)
[![Coverage](https://img.shields.io/badge/Coverage-Enforced-brightgreen?style=flat-square)](./github/workflows/ci.yml)

<br/>

> A hands-on reference implementation for secure ingress, resilient consensus, anomaly detection, and guarded rollouts.

</div>

---

## What is 88/CK Immune Layer?

88/CK Immune Layer is a multi-service project that explores how security controls can be combined across the request path, consensus path, and rollout path. It includes:

- Adaptive policy controls for ingress handling
- Zero-knowledge oriented admission checks for consensus traffic
- AI-supported anomaly detection with explainability components
- Lyapunov-inspired rollout guardrails for stability checks
- Ingress filtering and payload defusing for common attack classes

---

## For Cybersecurity Recruiters and Hiring Managers

This project is structured as a job-ready security engineering portfolio. It shows end-to-end ownership across architecture, implementation, testing, and operations.

### Role alignment

- Security Engineer: threat detection, secure middleware, abuse-case hardening
- Application Security Engineer: prevention controls for injection and payload-based attacks
- Cloud Security Engineer: observability, alerting, and containerized deployment patterns
- Detection Engineer / SOC Engineering: anomaly scoring, explainability, and incident routing
- Platform Security Engineer: policy-driven controls and safe rollout guardrails

### What this demonstrates to HR and interview panels

- Ability to build controls that are measurable and testable
- Systems thinking across Go, Python, infrastructure, and telemetry
- Security-focused coding practices including replay resistance and payload defusing
- Clear technical communication in architecture and API documentation

### Resume-friendly impact highlights

- Built a multi-service platform that blocks malicious ingress before service execution
- Implemented replay-safe admission checks in the consensus path
- Added anomaly detection and explainability hooks for incident triage
- Introduced a stability gate to reduce unsafe rollout risk

---

## Architecture at a Glance

```
                        ┌─────────────────────────────────────────────┐
                        │              88/CK Immune Layer              │
                        └──────────────────┬──────────────────────────┘
                                           │
            ┌──────────────────────────────┼──────────────────────────────┐
            │                             │                              │
    ┌───────▼────────┐           ┌────────▼───────┐            ┌────────▼───────┐
    │  Pillar 1      │           │  Pillar 2      │            │  Pillar 3      │
    │  Morphic       │           │  Consensus     │            │  Entropy       │
    │  ─────────     │           │  ─────────     │            │  ─────────     │
    │  Gateway       │           │  ZK Proofs     │            │  Graph Scorer  │
    │  SQLi Blocker  │           │  Replay Guard  │            │  Embedding     │
    │  xDS Policy    │           │  PQ Attest.    │            │  SHAP Explain  │
    │  Gamma Control │           │  3-Tier Gate   │            │  Anomaly Score │
    └───────┬────────┘           └────────┬───────┘            └────────┬───────┘
            │                             │                              │
            └──────────────────┬──────────┘──────────────────────────────
                               │
                    ┌──────────▼──────────┐
                    │   Stability Engine  │
                    │   ───────────────── │
                    │   Lyapunov Control  │
                    │   Guardrail API     │
                    │   Incident Sink     │
                    └─────────────────────┘
```

---

## Components

### Pillar 1: Morphic (Adaptive Gateway)
Ingress requests pass through a layered security filter before reaching downstream services.

| Capability | Detail |
|---|---|
| **SQLi Blocker** | 8 regex patterns covering UNION, DROP, comment injection, error-based exfiltration |
| **Malware Defuser** | 11 signature patterns; dangerous bytes stripped before logging |
| **xDS Publisher** | In-process publisher stub for policy snapshots |
| **Gamma Coupling** | Rate-limits cross-pillar influence to prevent destabilization cascades |
| **Prometheus Metrics** | Per-reason security block counter exposed at `/metrics` |

### Pillar 2: Consensus (Admission and Proof Path)
Consensus admission combines replay checks, attestation, and proof verification in a staged flow.

| Capability | Detail |
|---|---|
| **ZK Proof-of-Possession** | Ed25519 + SHA-256 transcript binding (NIZK-style) |
| **Replay Guard** | Mutex-protected nonce map prevents replay attacks |
| **PQ Attestation** | Post-quantum-safe attestation abstraction |
| **3-Tier Admission** | Nonce → PQ attestation → ZK proof, cheapest checks first |
| **Side-Channel Hygiene** | Constant-time proof-field validation notes in [docs/side-channel-validation.md](./docs/side-channel-validation.md) |

### Pillar 3: Entropy (Anomaly Detection)
Entropy focuses on structural and embedding-based anomaly detection with explainability support.

| Capability | Detail |
|---|---|
| **Graph Scoring** | Weisfeiler-Leman style structural comparison |
| **Attack Chain Detection** | Real-time mapping of correlated alerts into probable MITRE ATT&CK chains |
| **Attack Graph Representation** | Component/technique graph model for CoEB path analysis and hardening |
| **Embedding Detector** | ONNX-backed vector distance anomaly scoring |
| **Explainability** | SHAP value attribution for every anomaly decision |
| **Baseline Tracking** | Rolling normality windows with drift alerting |

### Stability Engine (Rollout Guardrail)
The stability engine evaluates rollout risk before a change is approved.

| Capability | Detail |
|---|---|
| **Predictive Evaluation** | `S(t+1) = S(t) - (γ·0.4) - (d·0.3)` |
| **Guardrail API** | POST `/evaluate` — approve or block a rollout proposal |
| **Risk Classification** | Critical / High / Medium / Low bands |
| **Orchestrator Plans** | `hold`, `stage-rollout`, `freeze-change-and-monitor`, `isolate-and-recover` |

### Enterprise Resilience and Observability
This stack is designed for enterprise deployment with live resilience telemetry, hardened policy enforcement, and service-level status visibility.

- **Enterprise stability monitoring** via the immune gateway and stability engine
- **Metrics-first architecture** exposing Prometheus-compatible `/metrics`
- **Real-time status streaming** over `/immune/ws` for dashboard and orchestration integration
- **Deterministic stability scoring** with `M(t)`, `C(t)`, `D(t)`, and `E(t)` components
- **Service identity digest** for trusted operational signing/health checks
- **Policy hardening response** triggers on stability threshold breach

---

## Security Stack

```
Request ──► SQLi/Malware Filter ──► ZK Admission Gate ──► Stability Guardrail ──► Service
              │                          │                        │
           Block + 403             Block + reason           Block + 409
           Defuse payload          Log nonce replay         Log risk band
           Increment metric        Verify ZK proof          Return rollout plan
```

For blocked requests, the system applies:
1. Defusing of control characters and dangerous symbols before logging
2. Trace identifier generation for deny responses
3. Prometheus metric updates via `morphic_security_blocks_total{reason="..."}`
4. Alerting through configured Prometheus rules

---

## Quick Start

**Prerequisites:** Go 1.25+, Python 3.11+, Docker, Node.js 20+

```bash
# Clone and bootstrap
git clone https://github.com/rock4007/88-ck-all-attack-vectors-blocks-
cd 88-ck-all-attack-vectors-blocks-/88ck-immune-layer
./scripts/bootstrap.sh
```

**Run all services with Docker Compose:**
```bash
cd infra
docker compose up --build
```

**Run the Stability Engine standalone:**
```bash
cd stability-engine
go run ./cmd/engine
# Listening on :8090
```

**Evaluate a rollout proposal:**
```bash
curl -sS -X POST http://localhost:8090/evaluate \
  -H 'Content-Type: application/json' \
  -d '{
    "proposal_id": "deploy-v2.1.0",
    "current_stability": 0.91,
    "gamma_delta": 0.04,
    "disturbance": 0.03
  }' | jq
```

**Test the security filter:**
```bash
# This should return 403
curl -i "http://localhost:8080/tick?q=1'+OR+'1'='1"

# This should return a 200
curl -i "http://localhost:8080/tick"
```

**Check enterprise status:**
```bash
curl -sS http://localhost:8080/immune/status | jq
```

**Stream live resilience updates:**
```bash
# Example websocket client; replace with enterprise dashboard or orchestration client
python - <<'PY'
import websocket
ws = websocket.create_connection('ws://localhost:8080/immune/ws')
print(ws.recv())
ws.close()
PY
```

**Health check:**
```bash
curl -i "http://localhost:8080/healthz"
```

---

## Guardrail API Reference

### `POST /evaluate`

**Request:**
```json
{
  "proposal_id": "string",
  "current_stability": 0.0–1.0,
  "gamma_delta": 0.0–1.0,
  "disturbance": 0.0–1.0
}
```

**Response (approved):** `200 OK`
```json
{
  "decision": {
    "approved": true,
    "reason": "stability nominal",
    "risk": "low",
    "predicted_stability": 0.88
  },
  "orchestrator": { "plan": "stage-rollout" }
}
```

**Response (blocked):** `409 Conflict`
```json
{
  "decision": {
    "approved": false,
    "reason": "predicted stability below minimum floor",
    "risk": "critical",
    "predicted_stability": 0.71
  },
  "orchestrator": { "plan": "freeze-change-and-monitor" }
}
```

### `GET /healthz`
Returns `200 ok` when the engine is live.

---

## Observability

**Prometheus metrics exposed:**

| Metric | Type | Description |
|---|---|---|
| `morphic_security_blocks_total` | Counter | Blocked requests by reason label |
| `morphic_security_block_rate_5m` | Recording Rule | 5-minute block rate |
| `morphic_security_block_rate_critical_5m` | Recording Rule | Critical payload rate |
| `stability_index` | Gauge | Current Lyapunov stability score |

**Active alerts:**

| Alert | Severity | Condition |
|---|---|---|
| `MorphicSecurityBlocksSpike` | warning | Block rate > 0.5/s for 5 minutes |
| `MorphicCriticalPayloadBlocks` | critical | Critical payload rate > 0.1/s for 3 minutes |
| `StabilityDegradation` | critical | `stability_index` < 0.80 for 2 minutes |

---

## Repository Layout

```
88ck-immune-layer/
├── pillar1-morphic/          # Gateway, SQLi/malware filter, gamma coupling, xDS
│   ├── cmd/gateway/          # HTTP entrypoint (port 8080)
│   └── internal/
│       ├── securityfilter/   # Ingress threat detection + defuser
│       ├── metrics/          # Prometheus + OTel declarations
│       ├── gamma/            # Lyapunov coupling controller
│       ├── scheduler/        # Bounded score scheduler
│       └── xds/              # In-process xDS publisher stub
│
├── pillar2-consensus/        # ZK agreement, replay guard, PQ attestation
│   ├── cmd/consensus/        # Consensus node entrypoint
│   └── internal/
│       ├── zkp/              # Ed25519 + SHA-256 proof-of-possession
│       └── security/         # 3-tier admission gate
│
├── pillar3-entropy/          # Python anomaly detection
│   ├── cmd/detector/         # Detector entrypoint
│   └── internal/
│       ├── baseline/         # Baseline tracker
│       ├── embedding/        # Embedding-based scoring
│       ├── explainability/   # SHAP layer
│       └── graph/            # WL-style graph scorer
│
├── stability-engine/         # Lyapunov guardrail + orchestrator
│   └── cmd/engine/           # HTTP API (port 8090)
│
├── frontend/                 # React + Vite + Tailwind ops UI
│
├── adversarial-harness/      # MITRE-style scenario runner
│
├── infra/
│   ├── docker-compose.yml
│   ├── helm/                 # Kubernetes Helm chart
│   └── prometheus/           # Alert + recording rules
│
├── docs/                     # Architecture, theory, API docs
└── scripts/                  # Bootstrap and validation utilities
```

---

## CI / CD Pipelines

| Workflow | Trigger | Purpose |
|---|---|---|
| `ci.yml` | Push / PR | Build, test, coverage enforce |
| `security-scan.yml` | Push / PR | Dependency and secrets scan |
| `adversarial-test.yml` | Schedule + PR | MITRE scenario regression |
| `release.yml` | Tag `v*` | Multi-arch image build + push |

---

## Validation Status

Latest industry-style validation report:
- [Industry Validation Report](./docs/industry-validation-report.md)

Validated gates include:
- Go static analysis + race tests
- Frontend production build
- Python compile and import smoke checks
- Security scans (`gosec`, `bandit`)
- Supply-chain SBOM generation (CycloneDX)
- Containerized integration and adversarial regression tests

---

## Current Scope Notes

- This is an engineering project and learning platform, not a turnkey commercial product.
- Some controls are simplified prototypes intended to show design approach and integration patterns.
- Use the docs and tests in each component to understand current behavior and limitations.

---

## Security Baseline

- **Distroless containers** — `gcr.io/distroless/static-debian12:nonroot` for all Go services
- **No `math/rand`** — all entropy sourced from `crypto/rand`
- **Post-quantum posture** — PQ-safe attestation abstraction in consensus path
- **Zero-knowledge proofs** — proposal content never exposed during agreement
- **Side-channel hygiene** — normalized proof verification path limits timing differences for malformed proof fields
- **Log injection prevention** — all logged payloads pass through the defuser before writing
- **Replay protection** — nonce map blocks duplicate proposal submissions

---

## Development

```bash
# Run all Go tests (pillar2 + stability-engine)
cd pillar2-consensus && go test ./...
cd stability-engine && go test ./...

# Run security filter tests
cd pillar1-morphic && go test ./internal/securityfilter/...

# Validate a coupling coefficient
./scripts/validate-coefficients.sh 0.42

# Run adversarial harness
cd adversarial-harness && python runner.py --strict

# Run live adversarial checks against the Compose services
cd infra && docker compose -f docker-compose.yml -f docker-compose.adversarial.yml up --build --abort-on-container-exit --exit-code-from adversarial-harness
```

---

MIT. See [LICENSE](./LICENSE).
