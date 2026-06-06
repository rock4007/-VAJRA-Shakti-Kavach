package observability

import (
	"github.com/prometheus/client_golang/prometheus"
)

type Metrics struct {
	Registry                     *prometheus.Registry
	MorphCyclesTotal             prometheus.Counter
	MorphCycleCompletedTotal     prometheus.Counter
	MorphCycleDurationSeconds    prometheus.Histogram
	MTValue                      prometheus.Gauge
	GammaLeadTimeMS              prometheus.Gauge
	GammaFaultsTotal             prometheus.Counter
	EndpointRotationEventsTotal  prometheus.Counter
}

func NewMetrics() *Metrics {
	registry := prometheus.NewRegistry()
	metrics := &Metrics{
		Registry: registry,
		MorphCyclesTotal: prometheus.NewCounter(prometheus.CounterOpts{
			Name: "morph_cycles_total",
			Help: "Total number of morph cycles started.",
		}),
		MorphCycleCompletedTotal: prometheus.NewCounter(prometheus.CounterOpts{
			Name: "morph_cycle_completed_total",
			Help: "Total number of morph cycles completed with an Envoy acknowledgement.",
		}),
		MorphCycleDurationSeconds: prometheus.NewHistogram(prometheus.HistogramOpts{
			Name:    "morph_cycle_duration_seconds",
			Help:    "Duration of completed morph cycles in seconds.",
			Buckets: prometheus.DefBuckets,
		}),
		MTValue: prometheus.NewGauge(prometheus.GaugeOpts{
			Name: "m_t_value",
			Help: "Morphomorphic pressure M(t), clamped to the [0,1] range.",
		}),
		GammaLeadTimeMS: prometheus.NewGauge(prometheus.GaugeOpts{
			Name: "gamma_lead_time_ms",
			Help: "Configured gamma baseline lead time in milliseconds.",
		}),
		GammaFaultsTotal: prometheus.NewCounter(prometheus.CounterOpts{
			Name: "gamma_faults_total",
			Help: "Total number of gamma coupling faults.",
		}),
		EndpointRotationEventsTotal: prometheus.NewCounter(prometheus.CounterOpts{
			Name: "endpoint_rotation_events_total",
			Help: "Total number of endpoint rotation events.",
		}),
	}

	registry.MustRegister(
		metrics.MorphCyclesTotal,
		metrics.MorphCycleCompletedTotal,
		metrics.MorphCycleDurationSeconds,
		metrics.MTValue,
		metrics.GammaLeadTimeMS,
		metrics.GammaFaultsTotal,
		metrics.EndpointRotationEventsTotal,
	)

	return metrics
}
