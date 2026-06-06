package app

import (
	"context"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"
	"time"

	"github.com/88ck/immune-layer/internal/gamma"
	"github.com/88ck/immune-layer/internal/observability"
	"github.com/88ck/immune-layer/internal/scheduler"
	"github.com/88ck/immune-layer/internal/xds"
	"github.com/rs/zerolog"
)

type stubGamma struct {
	lead time.Duration
	state gamma.State
}

func (s *stubGamma) LeadTime() time.Duration {
	return s.lead
}

func (s *stubGamma) PrepareBaselineUpdate(_ context.Context, mutationID string, mutationTime time.Time, seed string) (gamma.Signal, error) {
	s.state = gamma.State{
		LeadTimeMS:      s.lead.Milliseconds(),
		LastMutationID:  mutationID,
		LastScheduledAt: mutationTime.Add(-s.lead),
		LastSignal: gamma.Signal{
			MutationID:  mutationID,
			ScheduledAt: mutationTime.Add(-s.lead),
			DeltaTMS:    s.lead.Milliseconds(),
			Seed:        seed,
		},
	}
	return s.state.LastSignal, nil
}

func (s *stubGamma) State() gamma.State {
	return s.state
}

type stubXDS struct {
	state xds.State
	ackDelay time.Duration
}

func (s *stubXDS) PushTopology(_ context.Context, endpoints []scheduler.Endpoint) (string, error) {
	s.state.CurrentVersion = "1"
	s.state.Endpoints = append([]scheduler.Endpoint(nil), endpoints...)
	return "1", nil
}

func (s *stubXDS) WaitForAck(ctx context.Context, _ string) error {
	if s.ackDelay == 0 {
		return nil
	}
	timer := time.NewTimer(s.ackDelay)
	defer timer.Stop()
	select {
	case <-ctx.Done():
		return ctx.Err()
	case <-timer.C:
		return nil
	}
}

func (s *stubXDS) State() xds.State {
	return s.state
}

func TestMorphRateNominal(t *testing.T) {
	metrics := observability.NewMetrics()
	clock := time.Date(2026, time.March, 15, 0, 0, 0, 0, time.UTC)
	schedulerInstance, err := scheduler.New("seed", []scheduler.Endpoint{{Address: "10.0.0.1", Port: 8080}}, scheduler.Config{
		MaxSustainableRate: 4,
		RotationPeriod:     2 * time.Minute,
		Now:                func() time.Time { return clock },
	})
	if err != nil {
		t.Fatalf("unexpected scheduler error: %v", err)
	}

	service, err := New(Config{Seed: "seed", XDSAckTimeout: 500 * time.Millisecond}, metrics, schedulerInstance, &stubGamma{lead: 200 * time.Millisecond}, &stubXDS{}, zerolog.Nop())
	if err != nil {
		t.Fatalf("unexpected service error: %v", err)
	}
	service.SetNow(func() time.Time {
		clock = clock.Add(20 * time.Second)
		return clock
	})

	for i := 0; i < 4; i++ {
		if err := service.TriggerMorph(context.Background()); err != nil {
			t.Fatalf("trigger morph error: %v", err)
		}
		status := service.Status()
		if status.MTValue < 0 || status.MTValue > 1 {
			t.Fatalf("expected M(t) to stay within [0,1], got %v", status.MTValue)
		}
	}
}

func TestMorphTriggerRequiresAdminToken(t *testing.T) {
	metrics := observability.NewMetrics()
	schedulerInstance, err := scheduler.New("seed", []scheduler.Endpoint{{Address: "10.0.0.1", Port: 8080}}, scheduler.Config{
		MaxSustainableRate: 4,
	})
	if err != nil {
		t.Fatalf("unexpected scheduler error: %v", err)
	}

	service, err := New(Config{Seed: "seed", AdminToken: "secret"}, metrics, schedulerInstance, &stubGamma{lead: 0}, &stubXDS{}, zerolog.Nop())
	if err != nil {
		t.Fatalf("unexpected service error: %v", err)
	}

	req := httptest.NewRequest(http.MethodPost, "/api/v1/morph/trigger", nil)
	resp := httptest.NewRecorder()
	service.Handler().ServeHTTP(resp, req)
	if resp.Code != http.StatusUnauthorized {
		t.Fatalf("expected unauthorized, got %d", resp.Code)
	}
}

func TestMorphStatusEndpoint(t *testing.T) {
	metrics := observability.NewMetrics()
	schedulerInstance, err := scheduler.New("seed", []scheduler.Endpoint{{Address: "10.0.0.1", Port: 8080}}, scheduler.Config{
		MaxSustainableRate: 4,
	})
	if err != nil {
		t.Fatalf("unexpected scheduler error: %v", err)
	}

	service, err := New(Config{Seed: "seed"}, metrics, schedulerInstance, &stubGamma{lead: 0}, &stubXDS{}, zerolog.Nop())
	if err != nil {
		t.Fatalf("unexpected service error: %v", err)
	}

	req := httptest.NewRequest(http.MethodGet, "/api/v1/morph/status", nil)
	resp := httptest.NewRecorder()
	service.Handler().ServeHTTP(resp, req)
	if resp.Code != http.StatusOK {
		t.Fatalf("expected 200, got %d", resp.Code)
	}

	var payload MorphStatus
	if err := json.Unmarshal(resp.Body.Bytes(), &payload); err != nil {
		t.Fatalf("unmarshal error: %v", err)
	}
	if payload.CurrentCycle != 0 {
		t.Fatalf("expected initial cycle 0, got %d", payload.CurrentCycle)
	}
}
