package guardrail

import (
	"math"

	"github.com/88ck/stability-engine/internal/lyapunov"
)

type EvaluateRequest struct {
	ProposalID       string  `json:"proposal_id"`
	CurrentStability float64 `json:"current_stability"`
	GammaDelta       float64 `json:"gamma_delta"`
	Disturbance      float64 `json:"disturbance"`
}

type Decision struct {
	ProposalID         string  `json:"proposal_id"`
	Approved           bool    `json:"approved"`
	Action             string  `json:"action"`
	Reason             string  `json:"reason"`
	PredictedStability float64 `json:"predicted_stability"`
	Risk               string  `json:"risk"`
	CouplingImpact     float64 `json:"coupling_impact"`
}

type Guardrail struct {
	constraint        *lyapunov.Constraint
	minStability      float64
	maxGammaStep      float64
	gammaWeight       float64
	disturbanceWeight float64
}

func New(constraint *lyapunov.Constraint, minStability float64, maxGammaStep float64) *Guardrail {
	if minStability < 0 {
		minStability = 0
	}
	if minStability > 1 {
		minStability = 1
	}
	if maxGammaStep < 0 {
		maxGammaStep = 0
	}

	return &Guardrail{
		constraint:        constraint,
		minStability:      minStability,
		maxGammaStep:      maxGammaStep,
		gammaWeight:       0.4,
		disturbanceWeight: 0.3,
	}
}

func (g *Guardrail) Evaluate(req EvaluateRequest) Decision {
	impact := math.Abs(req.GammaDelta)
	disturbance := math.Abs(req.Disturbance)
	currentStability := clamp01(req.CurrentStability)
	// Lightweight predictor: current stability minus coupling and disturbance pressure.
	predicted := currentStability - (impact * g.gammaWeight) - (disturbance * g.disturbanceWeight)
	predicted = clamp01(predicted)

	// Hard policy guard: reject abrupt coupling jumps even if current state is healthy.
	if impact > g.maxGammaStep {
		return Decision{
			ProposalID:         req.ProposalID,
			Approved:           false,
			Action:             "block-and-isolate",
			Reason:             "gamma_step_exceeds_policy",
			PredictedStability: predicted,
			Risk:               classifyRisk(predicted, g.minStability),
			CouplingImpact:     impact,
		}
	}

	stable := predicted >= g.minStability && g.constraint.IsStable(predicted)
	if !stable {
		// Soft guard: reject proposals that push predicted state below Lyapunov floor.
		return Decision{
			ProposalID:         req.ProposalID,
			Approved:           false,
			Action:             "block-and-isolate",
			Reason:             "predicted_stability_below_floor",
			PredictedStability: predicted,
			Risk:               classifyRisk(predicted, g.minStability),
			CouplingImpact:     impact,
		}
	}

	return Decision{
		ProposalID:         req.ProposalID,
		Approved:           true,
		Action:             "allow-rollout",
		Reason:             "within_lyapunov_guardrails",
		PredictedStability: predicted,
		Risk:               classifyRisk(predicted, g.minStability),
		CouplingImpact:     impact,
	}
}

func classifyRisk(predicted float64, minStability float64) string {
	// Keep thresholds explicit so on-call engineers can map them to alert severities.
	if predicted < minStability {
		return "critical"
	}
	if predicted < minStability+0.05 {
		return "high"
	}
	if predicted < minStability+0.12 {
		return "medium"
	}
	return "low"
}

func clamp01(v float64) float64 {
	if v < 0 {
		return 0
	}
	if v > 1 {
		return 1
	}
	return v
}
