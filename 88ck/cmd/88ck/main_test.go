package main

import (
	"testing"
	"time"
)

func TestParseEndpoints(t *testing.T) {
	endpoints, err := parseEndpoints("127.0.0.1:8081,127.0.0.1:8082")
	if err != nil {
		t.Fatalf("unexpected parse error: %v", err)
	}
	if len(endpoints) != 2 {
		t.Fatalf("expected 2 endpoints, got %d", len(endpoints))
	}
}

func TestParseEndpointsRejectsInvalidPort(t *testing.T) {
	if _, err := parseEndpoints("127.0.0.1:not-a-port"); err == nil {
		t.Fatalf("expected invalid port error")
	}
}

func TestDurationFromEnvFallback(t *testing.T) {
	if got := durationFromEnv("MISSING_DURATION_ENV", 3*time.Second); got != 3*time.Second {
		t.Fatalf("expected fallback duration, got %v", got)
	}
}