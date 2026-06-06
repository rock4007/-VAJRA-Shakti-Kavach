package main

import (
	"encoding/json"
	"log"
	"net/http"
	"time"

	"github.com/88ck/stability-engine/internal/guardrail"
	"github.com/88ck/stability-engine/internal/incident"
	"github.com/88ck/stability-engine/internal/lyapunov"
	"github.com/88ck/stability-engine/internal/orchestrator"
	"github.com/88ck/stability-engine/internal/stability"
)

func main() {
	constraint := lyapunov.NewConstraint(0.82)
	monitor := stability.NewMonitor(constraint)
	controller := orchestrator.NewController()
	sink := incident.NewSink()
	guard := guardrail.New(constraint, constraint.Threshold(), 0.20)

	mux := http.NewServeMux()
	mux.HandleFunc("/healthz", func(w http.ResponseWriter, _ *http.Request) {
		writeJSON(w, http.StatusOK, map[string]string{"status": "ok"})
	})
	mux.HandleFunc("/evaluate", func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodPost {
			writeJSON(w, http.StatusMethodNotAllowed, map[string]string{"error": "method_not_allowed"})
			return
		}

		var req guardrail.EvaluateRequest
		dec := json.NewDecoder(r.Body)
		dec.DisallowUnknownFields()
		if err := dec.Decode(&req); err != nil {
			writeJSON(w, http.StatusBadRequest, map[string]string{"error": "invalid_request", "detail": err.Error()})
			return
		}

		if req.ProposalID == "" {
			writeJSON(w, http.StatusBadRequest, map[string]string{"error": "proposal_id_required"})
			return
		}

		state := monitor.Snapshot(req.CurrentStability)
		decision := guard.Evaluate(req)
		plan := controller.PlanFromGuardrail(state, decision)
		sink.Emit(plan)

		status := http.StatusOK
		if !decision.Approved {
			status = http.StatusConflict
		}
		writeJSON(w, status, map[string]any{
			"state":    state,
			"decision": decision,
			"plan":     plan,
		})
	})

	srv := &http.Server{
		Addr:              ":8090",
		Handler:           mux,
		ReadHeaderTimeout: 3 * time.Second,
	}

	log.Printf("stability engine listening on %s", srv.Addr)
	if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
		log.Fatalf("stability engine failed: %v", err)
	}
}

func writeJSON(w http.ResponseWriter, status int, payload any) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	if err := json.NewEncoder(w).Encode(payload); err != nil {
		log.Printf("encode response: %v", err)
	}
}
