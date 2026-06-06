from __future__ import annotations

from typing import Any, Dict, Iterable, Optional

from internal.graph.attack_chain import AttackEdge, PotentialChain
from internal.graph.attack_graph import AttackGraph


def isolate_component(target: str) -> None:
    # In an enterprise deployment, this would sever network access to the target.
    print(f"[DISRUPTION] isolating component: {target}")


def deploy_decoy(target: str) -> None:
    # Deploy a decoy or honeypot to divert attacker activity.
    print(f"[DISRUPTION] deploying decoy for: {target}")


def trigger_morphic_rotation(target: str) -> None:
    # Trigger morphological hardening routines around the target.
    print(f"[DISRUPTION] morphic rotation triggered for: {target}")


def require_consensus_verification(target: str) -> None:
    # Enforce additional consensus checks before the target can be used.
    print(f"[DISRUPTION] consensus verification required for: {target}")


def update_attack_graph(attack_graph: AttackGraph, source: str, target: str, blocked: bool = True) -> None:
    if blocked:
        attack_graph.block_edge(source, target)
    if target in attack_graph.nodes:
        attack_graph.update_exposure(target, {"blocked": blocked})


def normalize_edge(edge: Any) -> AttackEdge:
    if isinstance(edge, AttackEdge):
        return edge
    return AttackEdge(
        source=edge.get("source", ""),
        target=edge.get("target", ""),
        technique_id=edge.get("technique_id", ""),
        weight=edge.get("weight", 0.0),
        impact=edge.get("impact", 0.0),
    )


def disrupt_attack_chain(
    chain: Any,
    disruption_method: str,
    attack_graph: Optional[AttackGraph] = None,
) -> None:
    path = getattr(chain, "path", None)
    if path is None and isinstance(chain, dict):
        path = chain.get("path", [])

    edges = path if isinstance(path, list) else getattr(path, "edges", [])
    if not isinstance(edges, list) and hasattr(edges, "__iter__"):
        edges = list(edges)

    for raw_edge in edges:
        edge = normalize_edge(raw_edge)
        target = edge.target

        if disruption_method == "ISOLATION":
            isolate_component(target)
        elif disruption_method == "DECEPTION":
            deploy_decoy(target)
        elif disruption_method == "MORPHIC":
            trigger_morphic_rotation(target)
        elif disruption_method == "CONSENSUS":
            require_consensus_verification(target)
        else:
            print(f"[DISRUPTION] unknown method {disruption_method}, defaulting to isolation for {target}")
            isolate_component(target)

        if attack_graph is not None:
            update_attack_graph(attack_graph, edge.source, target, blocked=True)
