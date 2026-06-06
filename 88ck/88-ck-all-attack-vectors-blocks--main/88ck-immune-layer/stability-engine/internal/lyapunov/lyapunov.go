package lyapunov

type Constraint struct {
	threshold float64
}

func NewConstraint(threshold float64) *Constraint {
	if threshold < 0 {
		threshold = 0
	}
	if threshold > 1 {
		threshold = 1
	}
	return &Constraint{threshold: threshold}
}

func (c *Constraint) IsStable(value float64) bool {
	return value >= c.threshold
}

func (c *Constraint) Threshold() float64 {
	return c.threshold
}
