package app

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"net"
	"net/http"
	"sync"
	"time"

	"github.com/88ck/immune-layer/internal/gamma"
	"github.com/88ck/immune-layer/internal/observability"
	"github.com/88ck/immune-layer/internal/scheduler"
	"github.com/88ck/immune-layer/internal/xds"
	"github.com/prometheus/client_golang/prometheus/promhttp"
	"github.com/rs/zerolog"
	"go.opentelemetry.io/otel"
	"go.opentelemetry.io/otel/trace"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"
)

type gammaCoordinator interface {
	LeadTime() time.Duration
	PrepareBaselineUpdate(ctx context.Context, mutationID string, mutationTime time.Time, seed string) (gamma.Signal, error)
	State() gamma.State
}

type xdsCoordinator interface {
	PushTopology(ctx context.Context, endpoints []scheduler.Endpoint) (string, error)
	WaitForAck(ctx context.Context, version string) error
	State() xds.State
}

type Config struct {
	Seed               string
	RotationPeriod     time.Duration
	MaxSustainableRate float64
	AdminToken         string
	HTTPAddress        string
	Endpoints          []scheduler.Endpoint
	XDSAckTimeout      time.Duration
}

type MorphStatus struct {
	MTValue            float64              `json:"m_t_value"`
	NextScheduledMorph time.Time            `json:"next_scheduled_morph"`
	CurrentCycle       uint64               `json:"current_cycle"`
	EventsPerMinute    float64              `json:"events_per_minute"`
	CurrentVersion     string               `json:"current_version"`
	Topology           []scheduler.Endpoint `json:"topology"`
}

type Service struct {
	config    Config
	log       zerolog.Logger
	metrics   *observability.Metrics
	tracer    trace.Tracer
	scheduler *scheduler.Scheduler
	gamma     gammaCoordinator
	xds       xdsCoordinator
	now       func() time.Time

	mu         sync.RWMutex
	running    bool
	lastStatus MorphStatus
	lastError  string
}

func New(config Config, metrics *observability.Metrics, schedulerInstance *scheduler.Scheduler, gammaProtocol gammaCoordinator, xdsControlPlane xdsCoordinator, logger zerolog.Logger) (*Service, error) {
	if metrics == nil {
		metrics = observability.NewMetrics()
	}
	if schedulerInstance == nil {
		return nil, errors.New("scheduler is required")
	}
	if gammaProtocol == nil {
		return nil, errors.New("gamma protocol is required")
	}
	if xdsControlPlane == nil {
		return nil, errors.New("xds control plane is required")
	}
	if config.HTTPAddress == "" {
		config.HTTPAddress = ":8080"
	}
	if config.XDSAckTimeout <= 0 {
		config.XDSAckTimeout = 500 * time.Millisecond
	}
	service := &Service{
		config:    config,
		log:       logger,
		metrics:   metrics,
		tracer:    otel.Tracer("88ck/app"),
		scheduler: schedulerInstance,
		gamma:     gammaProtocol,
		xds:       xdsControlPlane,
		now:       time.Now,
	}
	service.refreshStatus(schedulerInstance.Status(), xdsControlPlane.State())
	return service, nil
}

func (s *Service) SetNow(now func() time.Time) {
	if now != nil {
		s.now = now
	}
}

func (s *Service) Start(ctx context.Context) {
	s.mu.Lock()
	if s.running {
		s.mu.Unlock()
		return
	}
	s.running = true
	s.mu.Unlock()

	go s.runScheduler(ctx)
}

func (s *Service) runScheduler(ctx context.Context) {
	ticker := time.NewTicker(s.scheduler.RotationPeriod())
	defer ticker.Stop()

	for {
		select {
		case <-ctx.Done():
			return
		case <-ticker.C:
			if err := s.TriggerMorph(ctx); err != nil {
				s.log.Error().Err(err).Msg("scheduled morph cycle failed")
			}
		}
	}
}

func (s *Service) TriggerMorph(ctx context.Context) error {
	ctx, span := s.tracer.Start(ctx, "morph.cycle")
	defer span.End()

	startedAt := s.now()
	s.metrics.MorphCyclesTotal.Inc()

	rotation := s.scheduler.Rotate(startedAt)
	s.metrics.EndpointRotationEventsTotal.Inc()
	s.metrics.MTValue.Set(rotation.MTValue)

	mutationTime := startedAt.Add(s.gamma.LeadTime())
	if _, err := s.gamma.PrepareBaselineUpdate(ctx, rotation.MutationID, mutationTime, s.config.Seed); err != nil {
		s.setLastError(err)
		return err
	}

	if delay := mutationTime.Sub(startedAt); delay > 0 {
		timer := time.NewTimer(delay)
		defer timer.Stop()
		select {
		case <-ctx.Done():
			return ctx.Err()
		case <-timer.C:
		}
	}

	version, err := s.xds.PushTopology(ctx, rotation.Endpoints)
	if err != nil {
		s.setLastError(err)
		return err
	}

	ackCtx, cancel := context.WithTimeout(ctx, s.config.XDSAckTimeout)
	defer cancel()
	if err := s.xds.WaitForAck(ackCtx, version); err != nil {
		s.setLastError(err)
		return err
	}

	s.metrics.MorphCycleCompletedTotal.Inc()
	s.metrics.MorphCycleDurationSeconds.Observe(time.Since(startedAt).Seconds())
	s.refreshStatus(s.scheduler.Status(), s.xds.State())
	s.clearLastError()

	s.log.Info().
		Str("mutation_id", rotation.MutationID).
		Str("version", version).
		Float64("m_t_value", rotation.MTValue).
		Time("next_scheduled_morph", rotation.NextScheduledMorph).
		Msg("morph cycle completed")

	return nil
}

func (s *Service) Handler() http.Handler {
	mux := http.NewServeMux()
	mux.Handle("/metrics", promhttp.HandlerFor(s.metrics.Registry, promhttp.HandlerOpts{}))
	mux.HandleFunc("/health", s.handleHealth)
	mux.HandleFunc("/morph-status", s.handleMorphStatus)
	mux.HandleFunc("/api/v1/morph/status", s.handleMorphStatus)
	mux.HandleFunc("/api/v1/gamma/status", s.handleGammaStatus)
	mux.HandleFunc("/api/v1/morph/trigger", s.handleMorphTrigger)
	return mux
}

func (s *Service) ListenAndServe(ctx context.Context) error {
	server := &http.Server{
		Addr:              s.config.HTTPAddress,
		Handler:           s.Handler(),
		ReadHeaderTimeout: 5 * time.Second,
	}

	errCh := make(chan error, 1)
	go func() {
		<-ctx.Done()
		shutdownCtx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
		defer cancel()
		errCh <- server.Shutdown(shutdownCtx)
	}()

	s.log.Info().Str("addr", s.config.HTTPAddress).Msg("starting http server")
	serveErr := server.ListenAndServe()
	if serveErr != nil && !errors.Is(serveErr, http.ErrServerClosed) {
		return serveErr
	}
	shutdownErr := <-errCh
	if shutdownErr != nil && !errors.Is(shutdownErr, net.ErrClosed) {
		return shutdownErr
	}
	return nil
}

func (s *Service) handleHealth(w http.ResponseWriter, _ *http.Request) {
	status := map[string]any{
		"status": "ok",
		"error":  s.errorString(),
	}
	writeJSON(w, http.StatusOK, status)
}

func (s *Service) handleMorphStatus(w http.ResponseWriter, _ *http.Request) {
	writeJSON(w, http.StatusOK, s.Status())
}

func (s *Service) handleGammaStatus(w http.ResponseWriter, _ *http.Request) {
	writeJSON(w, http.StatusOK, s.gamma.State())
}

func (s *Service) handleMorphTrigger(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		w.WriteHeader(http.StatusMethodNotAllowed)
		return
	}
	if s.config.AdminToken != "" && r.Header.Get("X-Admin-Token") != s.config.AdminToken {
		writeJSON(w, http.StatusUnauthorized, map[string]string{"error": "admin token required"})
		return
	}
	if err := s.TriggerMorph(r.Context()); err != nil {
		code := http.StatusInternalServerError
		if status.Code(err) == codes.DeadlineExceeded {
			code = http.StatusGatewayTimeout
		}
		writeJSON(w, code, map[string]string{"error": err.Error()})
		return
	}
	writeJSON(w, http.StatusAccepted, map[string]string{"status": "triggered"})
}

func (s *Service) Status() MorphStatus {
	s.mu.RLock()
	defer s.mu.RUnlock()
	return s.lastStatus
}

func (s *Service) refreshStatus(schedulerStatus scheduler.Status, xdsState xds.State) {
	s.mu.Lock()
	defer s.mu.Unlock()
	s.lastStatus = MorphStatus{
		MTValue:            schedulerStatus.CurrentMTValue,
		NextScheduledMorph: schedulerStatus.NextScheduledMorph,
		CurrentCycle:       schedulerStatus.CurrentCycle,
		EventsPerMinute:    schedulerStatus.EventsPerMinute,
		CurrentVersion:     xdsState.CurrentVersion,
		Topology:           xdsState.Endpoints,
	}
}

func (s *Service) errorString() string {
	s.mu.RLock()
	defer s.mu.RUnlock()
	return s.lastError
}

func (s *Service) setLastError(err error) {
	s.mu.Lock()
	defer s.mu.Unlock()
	s.lastError = err.Error()
}

func (s *Service) clearLastError() {
	s.mu.Lock()
	defer s.mu.Unlock()
	s.lastError = ""
}

func writeJSON(w http.ResponseWriter, statusCode int, payload any) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(statusCode)
	_ = json.NewEncoder(w).Encode(payload)
}

func (s *Service) DebugString() string {
	status := s.Status()
	return fmt.Sprintf("cycle=%d m_t=%.4f next=%s", status.CurrentCycle, status.MTValue, status.NextScheduledMorph.Format(time.RFC3339Nano))
}
