package gamma

import (
	"context"
	"encoding/json"
	"errors"
	"sync"
	"time"

	"github.com/88ck/immune-layer/internal/observability"
	"github.com/rs/zerolog"
)

const (
	DefaultLeadTime = 200 * time.Millisecond
	DefaultTauEmb   = 38 * time.Millisecond
	BaselineStream  = "88ck:gamma:baseline-update"
)

var ErrCouplingFault = errors.New("gamma lead time is below tau_emb")

type StreamPublisher interface {
	Publish(ctx context.Context, stream string, values map[string]any) error
}

type Signal struct {
	MutationID  string    `json:"mutation_id"`
	ScheduledAt time.Time `json:"scheduled_at"`
	DeltaTMS    int64     `json:"delta_t_ms"`
	Seed        string    `json:"seed"`
}

type State struct {
	LeadTimeMS         int64     `json:"lead_time_ms"`
	TauEmbMS           int64     `json:"tau_emb_ms"`
	LastMutationID     string    `json:"last_mutation_id"`
	LastScheduledAt    time.Time `json:"last_scheduled_at"`
	LastPublishedAt    time.Time `json:"last_published_at"`
	LastSignal         Signal    `json:"last_signal"`
	Faulted            bool      `json:"faulted"`
	FaultReason        string    `json:"fault_reason,omitempty"`
	StreamKey          string    `json:"stream_key"`
	BaselineClockState string    `json:"baseline_clock_state"`
}

type Protocol struct {
	publisher StreamPublisher
	metrics   *observability.Metrics
	log       zerolog.Logger
	now       func() time.Time
	leadTime  time.Duration
	tauEmb    time.Duration

	mu    sync.RWMutex
	state State
}

func New(publisher StreamPublisher, leadTime time.Duration, tauEmb time.Duration, metrics *observability.Metrics, log zerolog.Logger) *Protocol {
	if leadTime <= 0 {
		leadTime = DefaultLeadTime
	}
	if tauEmb <= 0 {
		tauEmb = DefaultTauEmb
	}
	protocol := &Protocol{
		publisher: publisher,
		metrics:   metrics,
		log:       log,
		now:       time.Now,
		leadTime:  leadTime,
		tauEmb:    tauEmb,
		state: State{
			LeadTimeMS:         leadTime.Milliseconds(),
			TauEmbMS:           tauEmb.Milliseconds(),
			StreamKey:          BaselineStream,
			BaselineClockState: "idle",
		},
	}
	if metrics != nil {
		metrics.GammaLeadTimeMS.Set(float64(leadTime.Milliseconds()))
	}
	return protocol
}

func (p *Protocol) SetNow(now func() time.Time) {
	if now != nil {
		p.mu.Lock()
		p.now = now
		p.mu.Unlock()
	}
}

func (p *Protocol) LeadTime() time.Duration {
	return p.leadTime
}

func (p *Protocol) State() State {
	p.mu.RLock()
	defer p.mu.RUnlock()
	return p.state
}

func (p *Protocol) PrepareBaselineUpdate(ctx context.Context, mutationID string, mutationTime time.Time, seed string) (Signal, error) {
	p.mu.Lock()
	defer p.mu.Unlock()

	if p.leadTime < p.tauEmb {
		p.state.Faulted = true
		p.state.FaultReason = ErrCouplingFault.Error()
		p.state.BaselineClockState = "fault"
		if p.metrics != nil {
			p.metrics.GammaFaultsTotal.Inc()
		}
		p.log.Error().
			Dur("delta_t", p.leadTime).
			Dur("tau_emb", p.tauEmb).
			Msg("gamma coupling fault detected")
		return Signal{}, ErrCouplingFault
	}

	scheduledAt := mutationTime.Add(-p.leadTime)
	publishedAt := p.now()
	signal := Signal{
		MutationID:  mutationID,
		ScheduledAt: scheduledAt,
		DeltaTMS:    p.leadTime.Milliseconds(),
		Seed:        seed,
	}
	values := map[string]any{
		"mutation_id": mutationID,
		"scheduled_at": scheduledAt.UTC().Format(time.RFC3339Nano),
		"delta_t_ms":   p.leadTime.Milliseconds(),
		"seed":         seed,
	}
	if p.publisher != nil {
		if err := p.publisher.Publish(ctx, BaselineStream, values); err != nil {
			return Signal{}, err
		}
	}

	p.state = State{
		LeadTimeMS:         p.leadTime.Milliseconds(),
		TauEmbMS:           p.tauEmb.Milliseconds(),
		LastMutationID:     mutationID,
		LastScheduledAt:    scheduledAt,
		LastPublishedAt:    publishedAt,
		LastSignal:         signal,
		Faulted:            false,
		StreamKey:          BaselineStream,
		BaselineClockState: "scheduled",
	}

	p.log.Info().
		Str("mutation_id", mutationID).
		Time("scheduled_at", scheduledAt).
		Int64("delta_t_ms", p.leadTime.Milliseconds()).
		Msg("gamma baseline update scheduled")

	return signal, nil
}

func (s Signal) MarshalJSON() ([]byte, error) {
	type alias Signal
	return json.Marshal(alias(s))
}
