package securityfilter

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"log"
	"net/http"

	"github.com/88ck/pillar1-morphic/internal/metrics"
)

type blockedResponse struct {
	Error   string `json:"error"`
	Reason  string `json:"reason"`
	TraceID string `json:"trace_id"`
}

func Middleware(filter *Filter) func(http.Handler) http.Handler {
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			verdict := filter.InspectRequest(r)
			if verdict.Allowed {
				next.ServeHTTP(w, r)
				return
			}

			// Stable trace id helps correlate blocks across logs and metrics without exposing raw payloads.
			traceID := hashTraceID(r.Method + "|" + r.URL.String() + "|" + verdict.Evidence)
			// #nosec G706 -- evidence is normalized via Defuse and trace id is hashed.
			log.Printf("security_block reason=%s trace_id=%s evidence=%s", verdict.Reason, traceID, Defuse(verdict.Evidence))
			metrics.IncSecurityBlock(verdict.Reason)

			// Return a consistent deny payload so clients and gateways can branch on reason.
			w.Header().Set("Content-Type", "application/json")
			w.WriteHeader(http.StatusForbidden)
			_ = json.NewEncoder(w).Encode(blockedResponse{
				Error:   "request_blocked",
				Reason:  verdict.Reason,
				TraceID: traceID,
			})
		})
	}
}

func hashTraceID(s string) string {
	sum := sha256.Sum256([]byte(s))
	return hex.EncodeToString(sum[:8])
}
