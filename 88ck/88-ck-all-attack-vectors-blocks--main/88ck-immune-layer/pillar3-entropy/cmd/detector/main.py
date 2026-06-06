from internal.baseline.baseline import BaselineEstimator
from internal.embedding.embed import EmbeddingModel
from internal.graph.attack_chain import Alert, AttackEdge, detect_attack_chains
from internal.graph.attack_graph import AttackGraph
from internal.graph.proactive_disruption import disrupt_attack_chain
from internal.graph.wl_scorer import WeisfeilerLehmanScorer
from internal.explainability.shap_explainer import ShapExplainer


def main() -> None:
    baseline = BaselineEstimator(window=128)
    embedder = EmbeddingModel(dim=64)
    scorer = WeisfeilerLehmanScorer(depth=2)
    explainer = ShapExplainer()

    event = {"actor": "nhi:svc-gateway", "target": "db:ledger", "action": "query"}
    vector = embedder.encode(event)
    baseline_score = baseline.score(vector)
    graph_score = scorer.score(event)
    explanation = explainer.explain(event, baseline_score + graph_score)

    print(
        {
            "baseline": round(baseline_score, 6),
            "graph": round(graph_score, 6),
            "total": round(baseline_score + graph_score, 6),
            "explanation": explanation,
        }
    )

    attack_graph = AttackGraph()
    attack_graph.add_node("nhi:svc-gateway", "service", 0.7)
    attack_graph.add_node("svc:auth", "service", 0.8)
    attack_graph.add_node("db:ledger", "database", 0.9)
    attack_graph.add_node("critical:identity", "critical", 1.0)
    attack_graph.add_node("critical:financials", "critical", 1.0)

    attack_graph.add_edge(
        "nhi:svc-gateway",
        "svc:auth",
        "T1059",
        "Command Execution",
        weight=0.7,
        impact=0.5,
    )
    attack_graph.add_edge(
        "nhi:svc-gateway",
        "db:ledger",
        "T1190",
        "Exploit Public-Facing Application",
        weight=0.9,
        impact=0.8,
    )
    attack_graph.add_edge(
        "svc:auth",
        "critical:identity",
        "T1078",
        "Valid Accounts",
        weight=0.8,
        impact=0.9,
    )
    attack_graph.add_edge(
        "db:ledger",
        "critical:financials",
        "T1499",
        "Endpoint Denial of Service",
        weight=0.6,
        impact=0.7,
    )

    attack_graph.set_mitigation("T1059", "harden process execution and privilege separation")
    attack_graph.set_mitigation("T1190", "enforce web application firewall and input validation")
    attack_graph.set_mitigation("T1078", "rotate credentials and enforce MFA")
    attack_graph.set_mitigation("T1499", "apply rate limiting and traffic shaping")

    current_alerts = [
        Alert(
            id="alert-001",
            source="nhi:svc-gateway",
            severity=0.92,
            description="Suspicious query pattern detected with possible replay and command execution",
            metadata={"technique_id": "T1059"},
        )
    ]

    graph_data = {}
    for (src, tgt), edge in attack_graph.edges.items():
        graph_data.setdefault(src, []).append(
            AttackEdge(
                source=src,
                target=tgt,
                technique_id=edge.technique_id,
                weight=edge.weight,
                impact=edge.impact,
            )
        )

    chains = detect_attack_chains(graph_data, current_alerts)
    print({"attack_chains": [chain.__dict__ for chain in chains]})

    if chains:
        disrupt_attack_chain(chains[0], "ISOLATION", attack_graph=attack_graph)
        print({"attack_graph_after_disruption": attack_graph.summarize()})
    else:
        print({"attack_graph": attack_graph.summarize()})


if __name__ == "__main__":
    main()
