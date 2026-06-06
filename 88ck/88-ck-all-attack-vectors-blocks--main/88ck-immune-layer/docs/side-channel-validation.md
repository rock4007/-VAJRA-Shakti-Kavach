# Side-Channel Validation Notes

## Scope

Pillar 2 currently implements a proof-of-possession prototype with Ed25519 and
SHA-256 transcript binding. The `internal/dilithium` package is a simulation
stub and is not a production ML-DSA implementation.

This validation therefore focuses on constant-time hygiene in the consensus
proof verifier, especially around attacker-controlled proof fields:

- identity lookup
- claimed statement hash
- base64-encoded signature shape
- signature verification dispatch

## Hardened Validation Path

`zkp.Verifier.Verify` normalizes proof inputs before deciding whether the proof
is accepted:

1. Registered public keys are copied and length-checked at registration time.
2. Missing or malformed public keys are replaced with a fixed zero-value key for
   verification.
3. The claimed statement hash is compared against the expected hash using a
   fixed-size constant-time comparison.
4. Signatures are decoded into a fixed 64-byte buffer and malformed signatures
   are represented as an all-zero signature.
5. Ed25519 verification is reached for both valid and malformed proof shapes,
   avoiding early exits based on attacker-controlled hash/signature validity.
6. The final decision combines identity, hash, signature-shape, and
   cryptographic verification results only after the normalized verification
   path has run.

This reduces timing differences caused by malformed proof fields and prevents a
remote caller from trivially distinguishing rejection reasons through skipped
cryptographic work.

## Residual Risk

This is not a formal constant-time proof. Remaining timing variation can still
come from:

- Go runtime behavior and allocation/GC effects
- map lookup timing for identity IDs
- standard-library base64 decoding behavior
- platform and CPU microarchitecture effects
- Ed25519 implementation details outside this repository

For production ML-DSA, use a vetted implementation that documents constant-time
decapsulation/signature behavior, then repeat this validation with dudect-style
timing tests, CPU pinning, noise isolation, and compiler/version pinning.

## Validation Commands

Run from `88ck-immune-layer/pillar2-consensus`:

```bash
go test ./internal/zkp
go test -bench BenchmarkVerifyValidAndMalformed ./internal/zkp
```

The benchmark is a regression aid. It is not a side-channel proof by itself.
