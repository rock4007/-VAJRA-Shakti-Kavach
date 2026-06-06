package scheduler

import (
	"reflect"
	"testing"
	"time"
)

func TestDeterministicRotation(t *testing.T) {
	endpoints := []Endpoint{
		{Address: "10.0.0.1", Port: 8080},
		{Address: "10.0.0.2", Port: 8080},
		{Address: "10.0.0.3", Port: 8080},
		{Address: "10.0.0.4", Port: 8080},
	}

	now := time.Date(2026, time.March, 15, 0, 0, 0, 0, time.UTC)
	first, err := New("shared-seed", endpoints, Config{MaxSustainableRate: 10, Now: func() time.Time { return now }})
	if err != nil {
		t.Fatalf("unexpected new scheduler error: %v", err)
	}
	second, err := New("shared-seed", endpoints, Config{MaxSustainableRate: 10, Now: func() time.Time { return now }})
	if err != nil {
		t.Fatalf("unexpected new scheduler error: %v", err)
	}

	for cycle := uint64(0); cycle < 8; cycle++ {
		firstSequence := first.SequenceForCycle(cycle)
		secondSequence := second.SequenceForCycle(cycle)
		if !reflect.DeepEqual(firstSequence, secondSequence) {
			t.Fatalf("cycle %d produced different deterministic sequences", cycle)
		}
	}
}

func TestRotateClampsMTValue(t *testing.T) {
	now := time.Date(2026, time.March, 15, 0, 0, 0, 0, time.UTC)
	instance, err := New("seed", []Endpoint{{Address: "10.0.0.1", Port: 8080}}, Config{
		MaxSustainableRate: 1,
		RotationPeriod:     time.Minute,
		Now:                func() time.Time { return now },
	})
	if err != nil {
		t.Fatalf("unexpected new scheduler error: %v", err)
	}

	rotation := instance.Rotate(now)
	if rotation.MTValue != 1 {
		t.Fatalf("expected M(t) to clamp to 1, got %v", rotation.MTValue)
	}
	status := instance.Status()
	if status.CurrentCycle != 1 {
		t.Fatalf("expected current cycle to advance to 1, got %d", status.CurrentCycle)
	}
	if !status.NextScheduledMorph.Equal(now.Add(time.Minute)) {
		t.Fatalf("unexpected next scheduled morph: %v", status.NextScheduledMorph)
	}
}
