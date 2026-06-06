from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class NodeInfo:
    node_type: str
    security_level: float
    current_state: str = "secure"
    exposure_vector: Optional[Dict[str, Any]] = None


@dataclass
class EdgeInfo:
    technique_id: str
    technique_name: str
    weight: float = 0.0
    impact: float = 0.0
    mitigation: Optional[str] = None
    blocked: bool = False


class AttackGraph:
    def __init__(self) -> None:
        self.nodes: Dict[str, NodeInfo] = {}
        self.edges: Dict[Tuple[str, str], EdgeInfo] = {}
        self.mitigations: Dict[str, str] = {}

    def add_node(self, node_id: str, node_type: str, security_level: float) -> None:
        self.nodes[node_id] = NodeInfo(
            node_type=node_type,
            security_level=security_level,
        )

    def add_edge(
        self,
        source: str,
        target: str,
        technique_id: str,
        technique_name: str,
        weight: float = 0.0,
        impact: float = 0.0,
    ) -> None:
        self.edges[(source, target)] = EdgeInfo(
            technique_id=technique_id,
            technique_name=technique_name,
            weight=weight,
            impact=impact,
        )

    def set_mitigation(self, technique_id: str, mitigation: str) -> None:
        self.mitigations[technique_id] = mitigation
        for edge in self.edges.values():
            if edge.technique_id == technique_id:
                edge.mitigation = mitigation

    def block_edge(self, source: str, target: str) -> None:
        edge = self.edges.get((source, target))
        if edge:
            edge.blocked = True

    def update_exposure(self, node_id: str, exposure_vector: Dict[str, Any]) -> None:
        node = self.nodes.get(node_id)
        if node:
            node.exposure_vector = exposure_vector

    def mark_node_compromised(self, node_id: str) -> None:
        node = self.nodes.get(node_id)
        if node:
            node.current_state = "compromised"

    def get_paths(self, source: str, destination_prefix: str) -> List[List[str]]:
        results: List[List[str]] = []
        visited: List[str] = []

        def dfs(current: str, path: List[str]) -> None:
            if current.startswith(destination_prefix):
                results.append(path.copy())
                return
            for (src, tgt), edge in self.edges.items():
                if src != current or edge.blocked:
                    continue
                if tgt in path:
                    continue
                path.append(tgt)
                dfs(tgt, path)
                path.pop()

        dfs(source, [source])
        return results

    def summarize(self) -> Dict[str, Any]:
        return {
            "nodes": {node_id: node.__dict__ for node_id, node in self.nodes.items()},
            "edges": {
                f"{src}->{tgt}": edge.__dict__ for (src, tgt), edge in self.edges.items()
            },
            "mitigations": self.mitigations,
        }
