package gamma

import (
	"context"
	"errors"
	"testing"
	"time"

	"github.com/88ck/immune-layer/internal/observability"
	"github.com/prometheus/client_golang/prometheus/testutil"
	"github.com/rs/zerolog"
)

type stubPublisher struct {
	stream string
	values map[string]any
	err    error
}

func (s *stubPublisher) Publish(_ context.Context, stream string, values map[string]any) error {
	s.stream = stream
	s.values = values
	return s.err
}

func TestGammaLeadTime(t *testing.T) {
	metrics := observability.NewMetrics()
	publisher := &stubPublisher{}
	protocol := New(publisher, 200*time.Millisecond, 38*time.Millisecond, metrics, zerolog.Nop())
	base := time.Date(2026, time.March, 15, 0, 0, 0, 0, time.UTC)
	protocol.SetNow(func() time.Time { return base })

	mutationTime := base.Add(protocol.LeadTime())
	_, err := protocol.PrepareBaselineUpdate(context.Background(), "mutation-1", mutationTime, "seed")
	if err != nil {
		t.Fatalf("expected no error, got %v", err)
	}
	if protocol.State().LeadTimeMS <= 38 {
		t.Fatalf("expected lead time above tau_emb, got %d", protocol.State().LeadTimeMS)
	}
	if publisher.stream != BaselineStream {
		t.Fatalf("expected stream %q, got %q", BaselineStream, publisher.stream)
	}
}

func TestCouplingFaultAlert(t *testing.T) {
	metrics := observability.NewMetrics()
	protocol := New(&stubPublisher{}, 20*time.Millisecond, 38*time.Millisecond, metrics, zerolog.Nop())
	_, err := protocol.PrepareBaselineUpdate(context.Background(), "mutation-2", time.Now(), "seed")
	if !errors.Is(err, ErrCouplingFault) {
		t.Fatalf("expected ErrCouplingFault, got %v", err)
	}
	if got := testutil.ToFloat64(metrics.GammaFaultsTotal); got != 1 {
		t.Fatalf("expected gamma fault counter to be 1, got %v", got)
	}
	if !protocol.State().Faulted {
		t.Fatalf("expected protocol to be faulted")
	}
}

func TestPublisherErrorPropagates(t *testing.T) {
	metrics := observability.NewMetrics()
	publisher := &stubPublisher{err: errors.New("redis unavailable")}
	protocol := New(publisher, 200*time.Millisecond, 38*time.Millisecond, metrics, zerolog.Nop())
	_, err := protocol.PrepareBaselineUpdate(context.Background(), "mutation-3", time.Now().Add(200*time.Millisecond), "seed")
	if err == nil || err.Error() != "redis unavailable" {
		t.Fatalf("expected publisher error to propagate, got %v", err)
	}
}
