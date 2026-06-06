package scheduler

import "testing"

func TestNextDecisionUsesProvidedPolicy(t *testing.T) {
	s := New(0)
	d := s.NextDecision("policy-fixed")

	if d.Policy != "policy-fixed" {
		t.Fatalf("expected provided policy to be preserved, got %q", d.Policy)
	}
	if d.Score < 0 || d.Score > 1 {
		t.Fatalf("expected score in [0,1], got %v", d.Score)
	}
}

func TestNextDecisionGeneratesPolicyWhenEmpty(t *testing.T) {
	s := New(0)
	d := s.NextDecision("")

	if d.Policy == "" {
		t.Fatal("expected generated policy id, got empty")
	}
	if d.Score < 0 || d.Score > 1 {
		t.Fatalf("expected score in [0,1], got %v", d.Score)
	}
}
