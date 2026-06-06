from __future__ import annotations

from typing import Dict


class WeisfeilerLehmanScorer:
    def __init__(self, depth: int = 2) -> None:
        self.depth = depth

    def score(self, event: Dict[str, str]) -> float:
        entropy_like = len(set(event.values())) / max(len(event), 1)
        return min(1.0, entropy_like * (0.25 * self.depth))
