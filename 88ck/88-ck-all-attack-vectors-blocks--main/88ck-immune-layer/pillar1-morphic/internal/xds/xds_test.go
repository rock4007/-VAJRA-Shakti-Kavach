package xds

import "testing"

func TestPublisherSnapshotReflectsLastPublish(t *testing.T) {
	p := NewPublisher("")
	p.Publish("policy-a", 0.42)

	policy, coupled, at := p.Snapshot()
	if policy != "policy-a" {
		t.Fatalf("expected policy-a, got %q", policy)
	}
	if coupled != 0.42 {
		t.Fatalf("expected 0.42, got %v", coupled)
	}
	if at.IsZero() {
		t.Fatal("expected non-zero publish timestamp")
	}
}
