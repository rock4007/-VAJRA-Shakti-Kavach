package guardrail

import (
	"testing"

	"github.com/88ck/stability-engine/internal/lyapunov"
)

func TestEvaluateBlocksLargeGammaStep(t *testing.T) {
	g := New(lyapunov.NewConstraint(0.82), 0.82, 0.15)

	decision := g.Evaluate(EvaluateRequest{
		ProposalID:       "p-large-step",
		CurrentStability: 0.91,
		GammaDelta:       0.40,
		Disturbance:      0.01,
	})

	if decision.Approved {
		t.Fatalf("expected proposal to be blocked")
	}
	if decision.Reason != "gamma_step_exceeds_policy" {
		t.Fatalf("unexpected reason: %s", decision.Reason)
	}
}

func TestEvaluateBlocksLowPredictedStability(t *testing.T) {
	g := New(lyapunov.NewConstraint(0.82), 0.82, 0.20)

	decision := g.Evaluate(EvaluateRequest{
		ProposalID:       "p-low-stability",
		CurrentStability: 0.84,
		GammaDelta:       0.05,
		Disturbance:      0.20,
	})

	if decision.Approved {
		t.Fatalf("expected proposal to be blocked")
	}
	if decision.Reason != "predicted_stability_below_floor" {
		t.Fatalf("unexpected reason: %s", decision.Reason)
	}
}

func TestEvaluateAllowsSafeProposal(t *testing.T) {
	g := New(lyapunov.NewConstraint(0.82), 0.82, 0.20)

	decision := g.Evaluate(EvaluateRequest{
		ProposalID:       "p-safe",
		CurrentStability: 0.94,
		GammaDelta:       0.03,
		Disturbance:      0.02,
	})

	if !decision.Approved {
		t.Fatalf("expected proposal to be approved")
	}
	if decision.Action != "allow-rollout" {
		t.Fatalf("unexpected action: %s", decision.Action)
	}
}

func TestEvaluateTreatsNegativeDisturbanceAsPressure(t *testing.T) {
	g := New(lyapunov.NewConstraint(0.82), 0.82, 0.20)

	decision := g.Evaluate(EvaluateRequest{
		ProposalID:       "p-negative-disturbance",
		CurrentStability: 0.84,
		GammaDelta:       0.05,
		Disturbance:      -0.20,
	})

	if decision.Approved {
		t.Fatalf("expected negative disturbance magnitude to be treated as pressure")
	}
	if decision.PredictedStability >= 0.84 {
		t.Fatalf("expected predicted stability to decrease, got %.3f", decision.PredictedStability)
	}
}

func TestEvaluateClampsCurrentStability(t *testing.T) {
	g := New(lyapunov.NewConstraint(0.82), 0.82, 0.20)

	decision := g.Evaluate(EvaluateRequest{
		ProposalID:       "p-clamped-current",
		CurrentStability: 1.20,
		GammaDelta:       0.00,
		Disturbance:      0.00,
	})

	if decision.PredictedStability != 1.0 {
		t.Fatalf("expected predicted stability to be clamped to 1.0, got %.3f", decision.PredictedStability)
	}
}
