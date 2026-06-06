package gamma

import "testing"

func TestCouplerApplyClampsInput(t *testing.T) {
	c := NewCoupler(0.5)

	if got := c.Apply(-1); got != 0 {
		t.Fatalf("expected clamp to 0, got %v", got)
	}
	if got := c.Apply(2); got != 0.5 {
		t.Fatalf("expected clamp to 1 then scale, got %v", got)
	}
}

func TestNewCouplerClampsCoefficient(t *testing.T) {
	if got := NewCoupler(-2).Apply(1); got != 0 {
		t.Fatalf("expected negative coefficient to clamp to 0, got %v", got)
	}
	if got := NewCoupler(2).Apply(1); got != 1 {
		t.Fatalf("expected coefficient >1 to clamp to 1, got %v", got)
	}
}
