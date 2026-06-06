# Coupling Problem

Cross-pillar coupling can destabilize recovery loops if policy updates, consensus finality, and detector confidence are tuned independently.

Mitigations:
- Cap Γ at deployment-time and enforce runtime drift alarms.
- Use staged rollouts with stability index gates.
- Require incident orchestration hooks for every new feedback edge.
