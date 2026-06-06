package main

import (
	"crypto/rand"
	"encoding/hex"
	"log"

	"github.com/88ck/pillar2-consensus/internal/dilithium"
	"github.com/88ck/pillar2-consensus/internal/hotstuff"
	"github.com/88ck/pillar2-consensus/internal/nhi"
	"github.com/88ck/pillar2-consensus/internal/security"
	"github.com/88ck/pillar2-consensus/internal/zkp"
)

func main() {
	engine := hotstuff.NewEngine(4)
	identity := nhi.NewIdentityProvider()
	signer := dilithium.NewSigner()

	// Register one service identity for the sample run.
	prover, err := zkp.NewProver("svc-consensus")
	if err != nil {
		log.Fatalf("create zkp prover: %v", err)
	}
	verifier := zkp.NewVerifier()
	verifier.RegisterIdentity("svc-consensus", prover.PublicKey())
	layer := security.NewLayer(identity, verifier, security.NewReplayGuard())

	proposal := engine.Propose("checkpoint-epoch-001")
	attestation := signer.Sign(proposal)
	// Nonce ensures each proof is single-use in admission flow.
	nonce := secureNonce(12)
	proof := prover.BuildProof(proposal, nonce)
	decision := layer.Evaluate(security.AdmissionRequest{
		Statement:   proposal,
		Attestation: attestation,
		Proof:       proof,
	})

	log.Printf("proposal=%s allowed=%t reason=%s quorum=%d", proposal, decision.Allowed, decision.Reason, engine.Quorum())
}

func secureNonce(length int) string {
	b := make([]byte, length)
	if _, err := rand.Read(b); err != nil {
		return "nonce-fallback"
	}
	return hex.EncodeToString(b)
}
