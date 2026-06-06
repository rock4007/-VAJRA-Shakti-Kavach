from __future__ import annotations

from collections import deque
from typing import Deque, List


class BaselineEstimator:
    def __init__(self, window: int = 128) -> None:
        self.window = window
        self.history: Deque[float] = deque(maxlen=window)

    def score(self, vector: List[float]) -> float:
        if not vector:
            return 0.0
        observed = sum(vector) / len(vector)
        baseline = (sum(self.history) / len(self.history)) if self.history else observed
        self.history.append(observed)
        delta = abs(observed - baseline)
        return min(1.0, delta * 4.0)
