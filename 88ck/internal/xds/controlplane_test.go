package xds

import (
	"context"
	"net"
	"testing"
	"time"

	"github.com/88ck/immune-layer/internal/observability"
	"github.com/88ck/immune-layer/internal/scheduler"
	"github.com/rs/zerolog"
	"go.opentelemetry.io/otel/trace"
)

func TestXDSHotReload(t *testing.T) {
	metrics := observability.NewMetrics()
	controlPlane, err := New(context.Background(), Config{NodeID: "test-node", AckTimeout: 500 * time.Millisecond}, metrics, zerolog.Nop(), trace.NewNoopTracerProvider().Tracer("test"))
	if err != nil {
		t.Fatalf("unexpected control plane error: %v", err)
	}

	listener, err := net.Listen("tcp", "127.0.0.1:0")
	if err != nil {
		t.Fatalf("listen error: %v", err)
	}
	defer controlPlane.Stop()
	go func() {
		_ = controlPlane.Run(listener)
	}()

	version, err := controlPlane.PushTopology(context.Background(), []scheduler.Endpoint{{Address: "127.0.0.1", Port: 8080}})
	if err != nil {
		t.Fatalf("push topology error: %v", err)
	}

	go func() {
		time.Sleep(100 * time.Millisecond)
		controlPlane.Acknowledge(version)
	}()

	ackCtx, cancel := context.WithTimeout(context.Background(), 500*time.Millisecond)
	defer cancel()
	if err := controlPlane.WaitForAck(ackCtx, version); err != nil {
		t.Fatalf("expected ack within 500ms, got %v", err)
	}

	state := controlPlane.State()
	if state.CurrentVersion != version {
		t.Fatalf("expected current version %q, got %q", version, state.CurrentVersion)
	}
	if state.LastAckVersion != version {
		t.Fatalf("expected last ack version %q, got %q", version, state.LastAckVersion)
	}
}
