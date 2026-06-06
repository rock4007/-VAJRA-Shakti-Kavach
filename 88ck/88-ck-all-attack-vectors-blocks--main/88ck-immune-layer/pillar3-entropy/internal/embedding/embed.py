from __future__ import annotations

import hashlib
from typing import Dict, List


class EmbeddingModel:
    def __init__(self, dim: int = 64) -> None:
        self.dim = dim

    def encode(self, event: Dict[str, str]) -> List[float]:
        text = "|".join([event.get("actor", ""), event.get("target", ""), event.get("action", "")])
        digest = hashlib.sha256(text.encode("utf-8")).digest()
        values = [b / 255.0 for b in digest]
        if self.dim <= len(values):
            return values[: self.dim]
        padding = [0.0] * (self.dim - len(values))
        return values + padding
