package main

import (
	"context"
	"errors"
	"fmt"
	"net"
	"os"
	"os/signal"
	"strconv"
	"strings"
	"syscall"
	"time"

	"github.com/88ck/immune-layer/internal/app"
	"github.com/88ck/immune-layer/internal/gamma"
	"github.com/88ck/immune-layer/internal/observability"
	"github.com/88ck/immune-layer/internal/scheduler"
	"github.com/88ck/immune-layer/internal/xds"
	"github.com/redis/go-redis/v9"
	"github.com/rs/zerolog"
	"github.com/rs/zerolog/log"
	"go.opentelemetry.io/otel"
	"go.opentelemetry.io/otel/sdk/trace"
	stdouttrace "go.opentelemetry.io/otel/sdk/trace/tracetest"
	"go.opentelemetry.io/otel/trace/noop"
)

func main() {
	zerolog.TimeFieldFormat = time.RFC3339Nano
	log.Logger = log.Output(zerolog.ConsoleWriter{Out: os.Stdout, TimeFormat: time.RFC3339})

	ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)
	defer stop()

	service, controlPlane, cleanup, err := bootstrap(ctx)
	if err != nil {
		log.Fatal().Err(err).Msg("bootstrap failed")
	}
	defer cleanup()

	xdsListener, err := net.Listen("tcp", envOrDefault("XDS_ADDRESS", ":18000"))
	if err != nil {
		log.Fatal().Err(err).Msg("failed to start xds listener")
	}
	go func() {
		if serveErr := controlPlane.Run(xdsListener); serveErr != nil {
			log.Error().Err(serveErr).Msg("xds server stopped")
		}
	}()

	service.Start(ctx)
	if err := service.ListenAndServe(ctx); err != nil && !errors.Is(err, context.Canceled) {
		log.Fatal().Err(err).Msg("http server stopped unexpectedly")
	}
}

func bootstrap(ctx context.Context) (*app.Service, *xds.ControlPlane, func(), error) {
	metrics := observability.NewMetrics()
	tracerProvider := initTracerProvider()
	otel.SetTracerProvider(tracerProvider)

	seed := envOrDefault("MORPH_SEED", "88ck-default-seed")
	rotationPeriod := durationFromEnv("ROTATION_PERIOD", scheduler.DefaultRotationPeriod)
	maxSustainableRate := floatFromEnv("MAX_SUSTAINABLE_RATE", 30)
	endpoints, err := parseEndpoints(envOrDefault("UPSTREAM_ENDPOINTS", "127.0.0.1:8081,127.0.0.1:8082"))
	if err != nil {
		return nil, nil, nil, err
	}

	schedulerInstance, err := scheduler.New(seed, endpoints, scheduler.Config{
		RotationPeriod:     rotationPeriod,
		MaxSustainableRate: maxSustainableRate,
	})
	if err != nil {
		return nil, nil, nil, err
	}

	redisClient := redis.NewClient(&redis.Options{Addr: envOrDefault("REDIS_ADDRESS", "127.0.0.1:6379")})
	publisher := gamma.NewRedisPublisher(redisClient)
	gammaProtocol := gamma.New(
		publisher,
		durationFromEnv("GAMMA_LEAD_TIME", gamma.DefaultLeadTime),
		durationFromEnv("TAU_EMB", gamma.DefaultTauEmb),
		metrics,
		log.With().Str("component", "gamma").Logger(),
	)

	tracer := otel.Tracer("88ck")
	controlPlane, err := xds.New(ctx, xds.Config{
		NodeID:        envOrDefault("ENVOY_NODE_ID", "88ck-node"),
		AckTimeout:    durationFromEnv("XDS_ACK_TIMEOUT", 500*time.Millisecond),
		ListenAddress: envOrDefault("ENVOY_LISTEN_ADDRESS", "0.0.0.0"),
		ListenPort:    uint32(intFromEnv("ENVOY_LISTEN_PORT", 10000)),
	}, metrics, log.With().Str("component", "xds").Logger(), tracer)
	if err != nil {
		return nil, nil, nil, err
	}

	service, err := app.New(app.Config{
		Seed:               seed,
		RotationPeriod:     rotationPeriod,
		MaxSustainableRate: maxSustainableRate,
		AdminToken:         os.Getenv("ADMIN_TOKEN"),
		HTTPAddress:        envOrDefault("HTTP_ADDRESS", ":8080"),
		Endpoints:          endpoints,
		XDSAckTimeout:      durationFromEnv("XDS_ACK_TIMEOUT", 500*time.Millisecond),
	}, metrics, schedulerInstance, gammaProtocol, controlPlane, log.With().Str("component", "app").Logger())
	if err != nil {
		return nil, nil, nil, err
	}

	cleanup := func() {
		controlPlane.Stop()
		_ = redisClient.Close()
		_ = tracerProvider.Shutdown(context.Background())
	}
	return service, controlPlane, cleanup, nil
}

func initTracerProvider() *trace.TracerProvider {
	provider := noop.NewTracerProvider()
	_ = provider
	return trace.NewTracerProvider(trace.WithSpanProcessor(stdouttrace.NewSpanRecorder()))
}

func envOrDefault(key string, fallback string) string {
	if value := strings.TrimSpace(os.Getenv(key)); value != "" {
		return value
	}
	return fallback
}

func durationFromEnv(key string, fallback time.Duration) time.Duration {
	value := strings.TrimSpace(os.Getenv(key))
	if value == "" {
		return fallback
	}
	parsed, err := time.ParseDuration(value)
	if err != nil {
		return fallback
	}
	return parsed
}

func floatFromEnv(key string, fallback float64) float64 {
	value := strings.TrimSpace(os.Getenv(key))
	if value == "" {
		return fallback
	}
	parsed, err := strconv.ParseFloat(value, 64)
	if err != nil {
		return fallback
	}
	return parsed
}

func intFromEnv(key string, fallback int) int {
	value := strings.TrimSpace(os.Getenv(key))
	if value == "" {
		return fallback
	}
	parsed, err := strconv.Atoi(value)
	if err != nil {
		return fallback
	}
	return parsed
}

func parseEndpoints(raw string) ([]scheduler.Endpoint, error) {
	parts := strings.Split(raw, ",")
	endpoints := make([]scheduler.Endpoint, 0, len(parts))
	for _, part := range parts {
		part = strings.TrimSpace(part)
		if part == "" {
			continue
		}
		host, portText, ok := strings.Cut(part, ":")
		if !ok {
			return nil, fmt.Errorf("endpoint %q must be host:port", part)
		}
		portValue, err := strconv.Atoi(portText)
		if err != nil {
			return nil, fmt.Errorf("endpoint %q has invalid port: %w", part, err)
		}
		endpoints = append(endpoints, scheduler.Endpoint{Address: host, Port: uint32(portValue)})
	}
	if len(endpoints) == 0 {
		return nil, errors.New("at least one upstream endpoint is required")
	}
	return endpoints, nil
}