package immune

import (
	"testing"
	"time"
)

func TestCalculateStability(t *testing.T) {
	il := NewImmuneLayer()

	il.MorphologicalLogic.RotationSchedule["compA"] = &RotationConfig{
		ComponentID:  "compA",
		LastRotation: time.Now().Add(-2 * time.Minute),
	}

	il.ChainProtection.ActivePaths = []*SecurityPath{{
		ID:          "active-1",
		Probability: 0.8,
		Impact:      0.7,
		Status:      "active",
	}}
	il.ChainProtection.ProtectedPaths = []*SecurityPath{{
		ID:          "protected-1",
		Probability: 0.9,
		Impact:      0.9,
		Status:      "protected",
	}}
	il.SemanticEntropy.PotentialAnomalies = []*SecurityPath{{
		ID:          "anomaly-1",
		Probability: 0.4,
		Impact:      0.5,
		Status:      "suspected",
	}}

	il.CalculateStability()

	if il.StabilityFunction.SValue < 0.0 || il.StabilityFunction.SValue > 1.5 {
		t.Fatalf("unexpected stability value: got %.3f", il.StabilityFunction.SValue)
	}

	if il.StabilityFunction.LastCalculated.IsZero() {
		t.Fatal("expected stability function last calculated time to be set")
	}
}

func TestEnforceHardeningSecuresEdges(t *testing.T) {
	il := NewImmuneLayer()
	protection := "initial"
	il.AddEdge(&Edge{
		SourceID:      "nodeA",
		TargetID:      "nodeB",
		TechniqueID:   "T1059",
		TechniqueName: "command execution",
		Protection:    &protection,
		Secured:       false,
	})

	il.enforceHardening()

	edge := il.SystemTopology.Edges["nodeA->nodeB"]
	if edge == nil {
		t.Fatal("expected edge saved in topology")
	}
	if !edge.Secured {
		t.Fatal("expected edge to be secured after enforcement")
	}
	if edge.Protection == nil || *edge.Protection != "hardened" {
		t.Fatalf("unexpected edge protection: %v", edge.Protection)
	}
}
