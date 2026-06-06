# API Surface

## Consensus Admission (internal flow)
- Proposal admission requires:
	- PQ-safe attestation (`pqsig:*`).
	- NIZK-style proof-of-possession transcript bound to proposal statement hash.
	- Fresh nonce accepted once only (replay-protected).
- Admission decision outputs:
	- `allowed` boolean.
	- `reason` in `{admitted, nonce_required, replay_detected, pq_attestation_failed, zk_proof_invalid}`.

## Morphic Gateway
- `GET /healthz` -> liveness status.
- `GET /tick` -> produce one policy scheduling cycle.

## Stability Engine
- `GET /healthz` -> liveness status.
- `POST /evaluate` -> evaluate candidate coupling update and return a guardrail decision.

Request body:

```json
{
	"proposal_id": "rollout-2026-03-15-a",
	"current_stability": 0.91,
	"gamma_delta": 0.04,
	"disturbance": 0.03
}
```

Response body:

```json
{
	"state": {
		"Status": "stable",
		"Value": 0.91
	},
	"decision": {
		"proposal_id": "rollout-2026-03-15-a",
		"approved": true,
		"action": "allow-rollout",
		"reason": "within_lyapunov_guardrails",
		"predicted_stability": 0.885,
		"risk": "low",
		"coupling_impact": 0.04
	},
	"plan": {
		"Action": "stage-rollout",
		"Reason": "within_lyapunov_guardrails"
	}
}
```

## Entropy Detector (planned)
- `POST /score` -> return baseline + graph anomaly decomposition.
