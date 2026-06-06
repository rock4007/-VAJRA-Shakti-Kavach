package main

import (
	"context"
	"crypto/rand"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/gorilla/websocket"
	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promhttp"

	"github.com/88ck/pillar1-morphic/internal/gamma"
	"github.com/88ck/pillar1-morphic/internal/immune"
	"github.com/88ck/pillar1-morphic/internal/scheduler"
	"github.com/88ck/pillar1-morphic/internal/securityfilter"
	"github.com/88ck/pillar1-morphic/internal/xds"
)

var (
	upgrader = websocket.Upgrader{
		ReadBufferSize:  1024,
		WriteBufferSize: 1024,
		CheckOrigin:     func(*http.Request) bool { return true },
	}

	statusGauge = prometheus.NewGaugeVec(prometheus.GaugeOpts{
		Name: "immune_service_status",
		Help: "Immune service stability and component gauge values",
	}, []string{"component"})
)

type statusMessage struct {
	ServerID        string  `json:"server_id"`
	Stability       float64 `json:"stability"`
	Morphological   float64 `json:"m_value"`
	Consensus       float64 `json:"c_value"`
	ChainProtection float64 `json:"d_value"`
	Entropy         float64 `json:"e_value"`
	GeneratedAt     string  `json:"generated_at"`
	ServiceDigest   string  `json:"service_digest"`
}

func main() {
	ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)
	defer stop()

	policyID := randomID(8)
	s := scheduler.New(750 * time.Millisecond)
	x := xds.NewPublisher("morphic-gateway")
	g := gamma.NewCoupler(0.42)
	securityFilter := securityfilter.New()
	immuneLayer := immune.NewImmuneLayer()
	serviceID := randomID(12)
	serviceDigest := fmt.Sprintf("%x", sha256.Sum256([]byte("88ck-immune:"+serviceID)))

	prometheus.MustRegister(statusGauge)

	mux := http.NewServeMux()
	mux.HandleFunc("/healthz", func(w http.ResponseWriter, _ *http.Request) {
		w.WriteHeader(http.StatusOK)
		_, _ = w.Write([]byte("ok"))
	})
	mux.HandleFunc("/tick", func(w http.ResponseWriter, _ *http.Request) {
		decision := s.NextDecision(policyID)
		coupled := g.Apply(decision.Score)
		x.Publish(decision.Policy, coupled)
		_, _ = w.Write([]byte("scheduled"))
	})
	mux.HandleFunc("/immune/status", func(w http.ResponseWriter, _ *http.Request) {
		immuneLayer.CalculateStability()
		writeJSON(w, http.StatusOK, immuneLayer.StabilityFunction)
	})
	mux.HandleFunc("/immune/ws", func(w http.ResponseWriter, r *http.Request) {
		wsStatusHandler(w, r, immuneLayer, serviceID, serviceDigest)
	})
	mux.Handle("/metrics", promhttp.Handler())

	protectedHandler := securityfilter.Middleware(securityFilter)(mux)

	srv := &http.Server{
		Addr:              ":8080",
		Handler:           protectedHandler,
		ReadHeaderTimeout: 3 * time.Second,
	}

	go func() {
		<-ctx.Done()
		shutdownCtx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
		defer cancel()
		_ = srv.Shutdown(shutdownCtx)
	}()

	log.Printf("morphic gateway listening on %s", srv.Addr)
	if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
		log.Fatalf("gateway failed: %v", err)
	}
}

func randomID(n int) string {
	b := make([]byte, n)
	if _, err := rand.Read(b); err != nil {
		return "fallback-policy"
	}
	return hex.EncodeToString(b)
}

func writeJSON(w http.ResponseWriter, status int, payload any) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	if err := json.NewEncoder(w).Encode(payload); err != nil {
		log.Printf("encode response: %v", err)
	}
}

func wsStatusHandler(w http.ResponseWriter, r *http.Request, immuneLayer *immune.ImmuneLayer, serviceID, serviceDigest string) {
	conn, err := upgrader.Upgrade(w, r, nil)
	if err != nil {
		log.Printf("websocket upgrade failed: %v", err)
		return
	}
	defer conn.Close()

	conn.SetReadLimit(512)
	conn.SetReadDeadline(time.Now().Add(30 * time.Second))
	conn.SetPongHandler(func(string) error {
		conn.SetReadDeadline(time.Now().Add(30 * time.Second))
		return nil
	})

	done := make(chan struct{})
	go func() {
		defer close(done)
		for {
			if _, _, err := conn.ReadMessage(); err != nil {
				return
			}
		}
	}()

	ticker := time.NewTicker(5 * time.Second)
	defer ticker.Stop()

	for {
		select {
		case <-done:
			return
		case <-ticker.C:
			immuneLayer.CalculateStability()
			msg := statusMessage{
				ServerID:        serviceID,
				Stability:       immuneLayer.StabilityFunction.SValue,
				Morphological:   immuneLayer.StabilityFunction.MValue,
				Consensus:       immuneLayer.StabilityFunction.CValue,
				ChainProtection: immuneLayer.StabilityFunction.DValue,
				Entropy:         immuneLayer.StabilityFunction.EValue,
				GeneratedAt:     time.Now().UTC().Format(time.RFC3339),
				ServiceDigest:   serviceDigest,
			}
			updateStatusMetrics(msg)
			if err := conn.WriteJSON(msg); err != nil {
				return
			}
		}
	}
}

func updateStatusMetrics(status statusMessage) {
	statusGauge.WithLabelValues("stability").Set(status.Stability)
	statusGauge.WithLabelValues("m_value").Set(status.Morphological)
	statusGauge.WithLabelValues("c_value").Set(status.Consensus)
	statusGauge.WithLabelValues("d_value").Set(status.ChainProtection)
	statusGauge.WithLabelValues("e_value").Set(status.Entropy)
}
