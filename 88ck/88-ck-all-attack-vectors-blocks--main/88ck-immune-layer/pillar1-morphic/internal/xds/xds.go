package xds

import (
	"context"
	"sync"
	"time"

	"github.com/88ck/pillar1-morphic/internal/metrics"
)

// Publisher is a lightweight in-process xDS publisher stub.
// It keeps the latest publish event and updates xDS metrics.
type Publisher struct {
	nodeID  string
	mu      sync.RWMutex
	policy  string
	coupled float64
	at      time.Time
	metrics *metrics.Metrics
}

func NewPublisher(nodeID string) *Publisher {
	if nodeID == "" {
		nodeID = "morphic-gateway"
	}
	return &Publisher{
		nodeID:  nodeID,
		metrics: metrics.NewMetrics(context.Background()),
	}
}

func (p *Publisher) Publish(policy string, coupled float64) {
	start := time.Now()
	p.mu.Lock()
	p.policy = policy
	p.coupled = coupled
	p.at = time.Now().UTC()
	p.mu.Unlock()

	metrics.XDSHotReloadTotal.Inc()
	metrics.XDSAckLatencyMs.Observe(float64(time.Since(start).Milliseconds()))
}

func (p *Publisher) Snapshot() (policy string, coupled float64, at time.Time) {
	p.mu.RLock()
	defer p.mu.RUnlock()
	return p.policy, p.coupled, p.at
}
