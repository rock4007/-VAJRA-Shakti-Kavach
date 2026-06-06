from internal.graph.attack_chain import Alert, AttackEdge, AttackPath, PotentialChain
from internal.graph.attack_graph import AttackGraph
from internal.graph.proactive_disruption import disrupt_attack_chain


def test_disrupt_attack_chain():
    graph = AttackGraph()
    graph.add_node("svc:gateway", "service", 0.7)
    graph.add_node("db:ledger", "database", 0.9)
    graph.add_edge("svc:gateway", "db:ledger", "T1190", "Exploit Public-Facing Application", weight=0.9, impact=0.8)

    path = AttackPath(
        nodes=["svc:gateway", "db:ledger"],
        edges=[AttackEdge(source="svc:gateway", target="db:ledger", technique_id="T1190", weight=0.9, impact=0.8)],
    )
    chain = PotentialChain(path=path, probability=0.85, impact=0.78, recommended_action="isolate")

    disrupt_attack_chain(chain, "ISOLATION", attack_graph=graph)
    assert graph.edges[("svc:gateway", "db:ledger")].blocked is True
