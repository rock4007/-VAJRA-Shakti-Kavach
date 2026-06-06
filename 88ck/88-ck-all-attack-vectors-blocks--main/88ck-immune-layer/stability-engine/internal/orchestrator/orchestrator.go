package orchestrator

import (
	"github.com/88ck/stability-engine/internal/guardrail"
	"github.com/88ck/stability-engine/internal/stability"
)

type Plan struct {
	Action string
	Reason string
}

type Controller struct{}

func NewController() *Controller {
	return &Controller{}
}

func (c *Controller) Plan(state stability.State) Plan {
	if state.Status == "stable" {
		return Plan{Action: "hold", Reason: "state_stable"}
	}
	return Plan{Action: "isolate-and-recover", Reason: "state_unstable"}
}

func (c *Controller) PlanFromGuardrail(state stability.State, decision guardrail.Decision) Plan {
	if decision.Approved {
		return Plan{Action: "stage-rollout", Reason: decision.Reason}
	}
	if state.Status == "stable" {
		return Plan{Action: "freeze-change-and-monitor", Reason: decision.Reason}
	}
	return Plan{Action: "isolate-and-recover", Reason: decision.Reason}
}
