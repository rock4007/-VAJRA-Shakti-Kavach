package metrics

import (
	"context"
	"fmt"

	"go.opentelemetry.io/otel"
	"go.opentelemetry.io/otel/attribute"
	"go.opentelemetry.io/otel/metric"
	"go.opentelemetry.io/otel/trace"

	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promauto"
)

var (
	// Prometheus metrics
	MorphCyclesTotal = promauto.NewCounter(prometheus.CounterOpts{
		Name: "morph_cycles_total",
		Help: "Total number of morph rotation cycles fired",
	})

	MorphCycleDuration = promauto.NewHistogram(prometheus.HistogramOpts{
		Name:    "morph_cycle_duration_seconds",
		Help:    "Morph cycle execution duration",
		Buckets: []float64{0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0},
	})

	MTValue = promauto.NewGauge(prometheus.GaugeOpts{
		Name: "m_t_value",
		Help: "Current morph rate M(t) clamped [0.0, 1.0]",
	})

	GammaLeadTimeMs = promauto.NewGauge(prometheus.GaugeOpts{
		Name: "gamma_lead_time_ms",
		Help: "Gamma baseline update lead time deltaT (ms)",
	})

	GammaFaultsTotal = promauto.NewCounter(prometheus.CounterOpts{
		Name: "gamma_faults_total",
		Help: "Number of gamma coupling faults (deltaT < tauEmb)",
	})

	GammaSafetyMarginMs = promauto.NewGauge(prometheus.GaugeOpts{
		Name: "gamma_safety_margin_ms",
		Help: "Gamma safety margin (deltaT - tauEmb)",
	})

	EndpointRotationEventsTotal = promauto.NewCounter(prometheus.CounterOpts{
		Name: "endpoint_rotation_events_total",
		Help: "Total endpoint rotation events published",
	})

	XDSHotReloadTotal = promauto.NewCounter(prometheus.CounterOpts{
		Name: "xds_hot_reload_total",
		Help: "Total successful xDS hot reloads to Envoy",
	})

	XDSAckLatencyMs = promauto.NewHistogram(prometheus.HistogramOpts{
		Name:    "xds_ack_latency_ms",
		Help:    "xDS config ACK latency from Envoy (ms)",
		Buckets: prometheus.ExponentialBuckets(50, 2, 5),
	})

	MorphicSecurityBlocksTotal = promauto.NewCounterVec(prometheus.CounterOpts{
		Name: "morphic_security_blocks_total",
		Help: "Total blocked gateway requests by security middleware",
	}, []string{"reason"})
)

type Metrics struct {
	meter  metric.Meter
	tracer trace.Tracer
}

// IncSecurityBlock is called by ingress middleware whenever a request is denied.
// The reason label makes it easy to separate SQLi bursts from malware probes.
func IncSecurityBlock(reason string) {
	if reason == "" {
		reason = "unknown"
	}
	MorphicSecurityBlocksTotal.WithLabelValues(reason).Inc()
}

func NewMetrics(ctx context.Context) *Metrics {
	meter := otel.Meter("pillar1-morphic")
	tracer := otel.Tracer("pillar1-morphic")
	return &Metrics{
		meter:  meter,
		tracer: tracer,
	}
}

func (m *Metrics) StartMorphCycle(ctx context.Context, seed []byte) (context.Context, trace.Span) {
	ctx, span := m.tracer.Start(ctx, "morph_cycle", trace.WithAttributes(
		attribute.String("seed.hex", fmt.Sprintf("%x", seed[0:8])),
	))
	return ctx, span
}

func (m *Metrics) StartXDSApply(ctx context.Context) (context.Context, trace.Span) {
	ctx, span := m.tracer.Start(ctx, "xds.apply_topology")
	return ctx, span
}
