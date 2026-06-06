package security

import (
	"testing"

	"github.com/88ck/pillar2-consensus/internal/nhi"
	"github.com/88ck/pillar2-consensus/internal/zkp"
)

func TestLayerAllowsValidAdmission(t *testing.T) {
	identity := nhi.NewIdentityProvider()
	prover, err := zkp.NewProver("svc-consensus")
	if err != nil {
		t.Fatalf("new prover: %v", err)
	}
	verifier := zkp.NewVerifier()
	verifier.RegisterIdentity("svc-consensus", prover.PublicKey())

	layer := NewLayer(identity, verifier, NewReplayGuard())
	proof := prover.BuildProof("proposal-1", "n-1")

	decision := layer.Evaluate(AdmissionRequest{
		Statement:   "proposal-1",
		Attestation: "pqsig:abc",
		Proof:       proof,
	})
	if !decision.Allowed {
		t.Fatalf("expected allowed decision")
	}
}

func TestLayerBlocksReplay(t *testing.T) {
	identity := nhi.NewIdentityProvider()
	prover, err := zkp.NewProver("svc-consensus")
	if err != nil {
		t.Fatalf("new prover: %v", err)
	}
	verifier := zkp.NewVerifier()
	verifier.RegisterIdentity("svc-consensus", prover.PublicKey())

	layer := NewLayer(identity, verifier, NewReplayGuard())
	proof := prover.BuildProof("proposal-1", "n-1")
	_ = layer.Evaluate(AdmissionRequest{Statement: "proposal-1", Attestation: "pqsig:abc", Proof: proof})

	replayDecision := layer.Evaluate(AdmissionRequest{Statement: "proposal-1", Attestation: "pqsig:abc", Proof: proof})
	if replayDecision.Allowed {
		t.Fatalf("expected replay to be blocked")
	}
	if replayDecision.Reason != "replay_detected" {
		t.Fatalf("unexpected reason: %s", replayDecision.Reason)
	}
}

func TestLayerDoesNotBurnNonceOnInvalidProof(t *testing.T) {
	identity := nhi.NewIdentityProvider()
	prover, err := zkp.NewProver("svc-consensus")
	if err != nil {
		t.Fatalf("new prover: %v", err)
	}
	verifier := zkp.NewVerifier()
	verifier.RegisterIdentity("svc-consensus", prover.PublicKey())

	layer := NewLayer(identity, verifier, NewReplayGuard())
	proof := prover.BuildProof("proposal-1", "n-1")
	invalidProof := proof
	invalidProof.Signature = "not base64"

	invalidDecision := layer.Evaluate(AdmissionRequest{
		Statement:   "proposal-1",
		Attestation: "pqsig:abc",
		Proof:       invalidProof,
	})
	if invalidDecision.Allowed {
		t.Fatalf("expected invalid proof to be rejected")
	}
	if invalidDecision.Reason != "zk_proof_invalid" {
		t.Fatalf("unexpected invalid reason: %s", invalidDecision.Reason)
	}

	validDecision := layer.Evaluate(AdmissionRequest{
		Statement:   "proposal-1",
		Attestation: "pqsig:abc",
		Proof:       proof,
	})
	if !validDecision.Allowed {
		t.Fatalf("expected valid proof to be admitted after invalid attempt, got %s", validDecision.Reason)
	}
}
