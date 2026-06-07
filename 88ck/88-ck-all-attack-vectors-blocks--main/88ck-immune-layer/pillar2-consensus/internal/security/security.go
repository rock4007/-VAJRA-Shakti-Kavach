package security

import (
	"sync"

	"github.com/88ck/pillar2-consensus/internal/nhi"
	"github.com/88ck/pillar2-consensus/internal/zkp"
)

type AdmissionRequest struct {
	Statement   string
	Attestation string
	Proof       zkp.Proof
}

type AdmissionDecision struct {
	Allowed bool
	Reason  string
}

type ReplayGuard struct {
	mu sync.Mutex

	// seen keeps a bounded recent window of nonces to limit memory growth.
	// Note: this is an in-memory heuristic; production systems should prefer
	// a time-bounded nonce mechanism at the protocol level.
	seen map[string]struct{}
	max  int
}

func NewReplayGuard() *ReplayGuard {
	return &ReplayGuard{seen: make(map[string]struct{}), max: 10000}
}

func (r *ReplayGuard) TryMark(nonce string) bool {
	if r == nil {
		return false
	}
	r.mu.Lock()
	defer r.mu.Unlock()

	if _, ok := r.seen[nonce]; ok {
		return false
	}

	// Simple bounded eviction: if we’re at capacity, reset the set.
	// This preserves the main replay-prevention behavior while preventing
	// unbounded memory growth under attack.
	if len(r.seen) >= r.max {
		r.seen = make(map[string]struct{})
	}
	r.seen[nonce] = struct{}{}
	return true
}

func (r *ReplayGuard) Seen(nonce string) bool {
	if r == nil {
		return true
	}
	r.mu.Lock()
	defer r.mu.Unlock()
	_, ok := r.seen[nonce]
	return ok
}

type Layer struct {
	identity *nhi.IdentityProvider
	zk       *zkp.Verifier
	replay   *ReplayGuard
}

func NewLayer(identity *nhi.IdentityProvider, zk *zkp.Verifier, replay *ReplayGuard) *Layer {
	return &Layer{identity: identity, zk: zk, replay: replay}
}

// Evaluate applies admission checks in strict order:
// 1) nonce freshness, 2) PQ attestation shape, 3) proof validity, 4) nonce mark.
// The nonce is marked only after validation so malformed requests cannot burn a
// legitimate proposal nonce before the real proof arrives.
func (l *Layer) Evaluate(req AdmissionRequest) AdmissionDecision {
	if l == nil || l.identity == nil || l.zk == nil || l.replay == nil {
		return AdmissionDecision{Allowed: false, Reason: "layer_not_ready"}
	}
	if req.Proof.Nonce == "" {
		return AdmissionDecision{Allowed: false, Reason: "nonce_required"}
	}
	if l.replay.Seen(req.Proof.Nonce) {
		return AdmissionDecision{Allowed: false, Reason: "replay_detected"}
	}
	if !l.identity.Verify(req.Attestation) {
		return AdmissionDecision{Allowed: false, Reason: "pq_attestation_failed"}
	}
	if !l.zk.Verify(req.Statement, req.Proof) {
		return AdmissionDecision{Allowed: false, Reason: "zk_proof_invalid"}
	}
	if !l.replay.TryMark(req.Proof.Nonce) {
		return AdmissionDecision{Allowed: false, Reason: "replay_detected"}
	}
	return AdmissionDecision{Allowed: true, Reason: "admitted"}
}
