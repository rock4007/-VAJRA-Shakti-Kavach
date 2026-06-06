package scheduler

import (
	"crypto/rand"
	"encoding/hex"
	"time"
)

// Decision is a single scheduling output used by the gateway tick handler.
type Decision struct {
	Policy string
	Score  float64
}

// Scheduler produces lightweight policy/score decisions for each tick.
type Scheduler struct {
	period time.Duration
}

func New(period time.Duration) *Scheduler {
	if period <= 0 {
		period = 750 * time.Millisecond
	}
	return &Scheduler{period: period}
}

func (s *Scheduler) NextDecision(policyID string) Decision {
	if policyID == "" {
		policyID = randomID(8)
	}

	var b [1]byte
	_, _ = rand.Read(b[:])

	// Keep score bounded to [0,1] so downstream coupling stays stable.
	score := float64(b[0]) / 255.0
	return Decision{
		Policy: policyID,
		Score:  score,
	}
}

func randomID(n int) string {
	buf := make([]byte, n)
	_, _ = rand.Read(buf)
	return hex.EncodeToString(buf)
}
