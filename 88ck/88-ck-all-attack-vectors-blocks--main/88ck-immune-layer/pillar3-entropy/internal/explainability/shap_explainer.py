from __future__ import annotations

from typing import Dict


class ShapExplainer:
    def explain(self, event: Dict[str, str], score: float) -> Dict[str, float]:
        action_weight = 0.5 if event.get("action") in {"exec", "write", "admin"} else 0.2
        actor_weight = 0.3 if event.get("actor", "").startswith("nhi:") else 0.1
        target_weight = max(0.0, 1.0 - action_weight - actor_weight)
        return {
            "action": round(action_weight * score, 6),
            "actor": round(actor_weight * score, 6),
            "target": round(target_weight * score, 6),
        }
