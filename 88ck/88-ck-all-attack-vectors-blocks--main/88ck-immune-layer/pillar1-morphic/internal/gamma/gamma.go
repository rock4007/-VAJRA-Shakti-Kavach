package gamma

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"

	"time"

	"github.com/redis/go-redis/v9"

	"github.com/88ck/pillar1-morphic/internal/metrics"
)

const (
	DefaultDeltaT = 200 * time.Millisecond
	TauEmb        = 38 * time.Millisecond
	SafetyMargin  = DefaultDeltaT - TauEmb
	RedisStream   = "88ck:gamma:baseline-update"
)

type GammaProtocol struct {
	deltaT      time.Duration
	tauEmb      time.Duration
	redisClient redis.Client
	metrics     *metrics.Metrics
}

// Coupler is a lightweight gamma coupling helper used by the gateway.
type Coupler struct {
	coefficient float64
}

func NewCoupler(coefficient float64) *Coupler {
	if coefficient < 0 {
		coefficient = 0
	}
	if coefficient > 1 {
		coefficient = 1
	}
	return &Coupler{coefficient: coefficient}
}

func (c *Coupler) Apply(score float64) float64 {
	if score < 0 {
		score = 0
	}
	if score > 1 {
		score = 1
	}
	return score * c.coefficient
}

func NewGammaProtocol(deltaT time.Duration, rdb redis.Client) *GammaProtocol {
	if deltaT <= 0 {
		deltaT = DefaultDeltaT
	}
	if deltaT < TauEmb {
		deltaT = TauEmb
	}
	safetyMargin := deltaT - TauEmb
	metrics.GammaLeadTimeMs.Set(float64(deltaT.Milliseconds()))
	metrics.GammaSafetyMarginMs.Set(float64(safetyMargin.Milliseconds()))

	return &GammaProtocol{
		deltaT:      deltaT,
		tauEmb:      TauEmb,
		redisClient: rdb,
		metrics:     metrics.NewMetrics(context.Background()),
	}
}

func (g *GammaProtocol) ValidateLeadTime(deltaT time.Duration) error {
	if deltaT < g.tauEmb {
		metrics.GammaFaultsTotal.Inc()
		return errors.New("lead time violation: deltaT < tauEmb")
	}
	return nil
}

func (g *GammaProtocol) ScheduleBaselineUpdate(mutationID string, mutationTime time.Time) error {
	scheduledAt := mutationTime.Add(-g.deltaT)
	if err := g.ValidateLeadTime(g.deltaT); err != nil {
		return err
	}

	payload := struct {
		MutationID   string `json:"mutation_id"`
		ScheduledAt  int64  `json:"scheduled_at"`
		DeltaTMs     int64  `json:"delta_t_ms"`
		SafetyMargin int64  `json:"safety_margin"`
		Seed         string `json:"seed"`
	}{
		MutationID:   mutationID,
		ScheduledAt:  scheduledAt.Unix(),
		DeltaTMs:     g.deltaT.Milliseconds(),
		SafetyMargin: (g.deltaT - g.tauEmb).Milliseconds(),
		Seed:         "", // Reserved for optional topology seed tracing.
	}
	data, err := json.Marshal(payload)
	if err != nil {
		return fmt.Errorf("marshal payload: %w", err)
	}

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()
	_, err = g.redisClient.XAdd(ctx, &redis.XAddArgs{
		Stream: RedisStream,
		Values: map[string]interface{}{"event": string(data)},
	}).Result()
	return err
}

