package zkp

import "testing"

func TestZKProofRoundTrip(t *testing.T) {
	prover, err := NewProver("svc-consensus")
	if err != nil {
		t.Fatalf("new prover: %v", err)
	}

	verifier := NewVerifier()
	verifier.RegisterIdentity("svc-consensus", prover.PublicKey())

	proof := prover.BuildProof("checkpoint-epoch-777", "nonce-1")
	if !verifier.Verify("checkpoint-epoch-777", proof) {
		t.Fatalf("expected proof verification to pass")
	}
}

func TestZKProofRejectsTamper(t *testing.T) {
	prover, err := NewProver("svc-consensus")
	if err != nil {
		t.Fatalf("new prover: %v", err)
	}

	verifier := NewVerifier()
	verifier.RegisterIdentity("svc-consensus", prover.PublicKey())

	proof := prover.BuildProof("checkpoint-epoch-777", "nonce-1")
	if verifier.Verify("checkpoint-epoch-778", proof) {
		t.Fatalf("expected verification failure for tampered statement")
	}
}

func TestZKProofRejectsMalformedFields(t *testing.T) {
	prover, err := NewProver("svc-consensus")
	if err != nil {
		t.Fatalf("new prover: %v", err)
	}

	verifier := NewVerifier()
	verifier.RegisterIdentity("svc-consensus", prover.PublicKey())

	validProof := prover.BuildProof("checkpoint-epoch-777", "nonce-1")
	cases := map[string]Proof{
		"unknown_identity": {
			IdentityID:    "svc-unknown",
			Nonce:         validProof.Nonce,
			StatementHash: validProof.StatementHash,
			Signature:     validProof.Signature,
		},
		"short_statement_hash": {
			IdentityID:    validProof.IdentityID,
			Nonce:         validProof.Nonce,
			StatementHash: validProof.StatementHash[:8],
			Signature:     validProof.Signature,
		},
		"mismatched_statement_hash": {
			IdentityID:    validProof.IdentityID,
			Nonce:         validProof.Nonce,
			StatementHash: hashHex("different-statement"),
			Signature:     validProof.Signature,
		},
		"invalid_signature_base64": {
			IdentityID:    validProof.IdentityID,
			Nonce:         validProof.Nonce,
			StatementHash: validProof.StatementHash,
			Signature:     "not base64",
		},
		"short_signature": {
			IdentityID:    validProof.IdentityID,
			Nonce:         validProof.Nonce,
			StatementHash: validProof.StatementHash,
			Signature:     "c2hvcnQ=",
		},
	}

	for name, proof := range cases {
		t.Run(name, func(t *testing.T) {
			if verifier.Verify("checkpoint-epoch-777", proof) {
				t.Fatalf("expected malformed proof to fail")
			}
		})
	}
}

func TestRegisterIdentityRejectsInvalidPublicKey(t *testing.T) {
	verifier := NewVerifier()
	verifier.RegisterIdentity("svc-consensus", []byte("short"))

	proof := Proof{
		IdentityID:    "svc-consensus",
		Nonce:         "nonce-1",
		StatementHash: hashHex("checkpoint-epoch-777"),
		Signature:     "c2hvcnQ=",
	}
	if verifier.Verify("checkpoint-epoch-777", proof) {
		t.Fatalf("expected proof with invalid registered key to fail")
	}
}

func BenchmarkVerifyValidAndMalformed(b *testing.B) {
	prover, err := NewProver("svc-consensus")
	if err != nil {
		b.Fatalf("new prover: %v", err)
	}

	verifier := NewVerifier()
	verifier.RegisterIdentity("svc-consensus", prover.PublicKey())

	validProof := prover.BuildProof("checkpoint-epoch-777", "nonce-1")
	malformedProof := validProof
	malformedProof.StatementHash = validProof.StatementHash[:8]
	malformedProof.Signature = "not base64"

	b.Run("valid", func(b *testing.B) {
		for i := 0; i < b.N; i++ {
			_ = verifier.Verify("checkpoint-epoch-777", validProof)
		}
	})

	b.Run("malformed", func(b *testing.B) {
		for i := 0; i < b.N; i++ {
			_ = verifier.Verify("checkpoint-epoch-777", malformedProof)
		}
	})
}
