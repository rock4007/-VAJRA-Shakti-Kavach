from internal.graph.attack_chain import Alert, AttackEdge, detect_attack_chains


def test_detect_attack_chain_allows_follow_on_techniques():
    graph = {
        "svc:gateway": [
            AttackEdge(
                source="svc:gateway",
                target="svc:auth",
                technique_id="T1190",
                weight=0.9,
                impact=0.7,
            )
        ],
        "svc:auth": [
            AttackEdge(
                source="svc:auth",
                target="critical:identity",
                technique_id="T1078",
                weight=0.8,
                impact=0.9,
            )
        ],
    }
    alerts = [
        Alert(
            id="alert-001",
            source="svc:gateway",
            severity=0.9,
            description="SQL injection against gateway",
            metadata={},
        )
    ]

    chains = detect_attack_chains(graph, alerts)

    assert len(chains) == 1
    assert chains[0].path.nodes == ["svc:gateway", "svc:auth", "critical:identity"]
