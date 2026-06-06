# 88/CK Architecture

The immune layer is split into three pillars and one stability supervisor:

- Pillar 1 Morphic: control-plane policy adaptation and xDS emission.
- Pillar 2 Consensus: Byzantine-tolerant agreement with multi-factor cryptographic admission.
- Pillar 3 Entropy: anomaly scoring across embeddings and graph structure.
- Stability Engine: Lyapunov-anchored guardrails and incident orchestration.

Data flows from detection and consensus into a shared control state. Γ coupling captures cross-pillar feedback and is constrained to preserve S(t) monotonic recovery after perturbations.

Consensus admission now enforces three checks before proposal progression:
- PQ-safe attestation prefix and format validation.
- Non-interactive proof-of-possession verification (NIZK-style transcript over statement + nonce).
- Nonce replay blocking to reject duplicated proofs.

Gateway ingress hardening now enforces:
- SQL injection pattern blocking across query, headers, and request body.
- Malware payload blocking for command/script delivery indicators.
- Payload defusion in logs to avoid replaying dangerous material during incident response.
