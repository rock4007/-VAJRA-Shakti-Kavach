package stability

import "github.com/88ck/stability-engine/internal/lyapunov"

type State struct {
	Status string
	Value  float64
}

type Monitor struct {
	constraint *lyapunov.Constraint
}

func NewMonitor(c *lyapunov.Constraint) *Monitor {
	return &Monitor{constraint: c}
}

func (m *Monitor) Snapshot(v float64) State {
	if m.constraint.IsStable(v) {
		return State{Status: "stable", Value: v}
	}
	return State{Status: "unstable", Value: v}
}
