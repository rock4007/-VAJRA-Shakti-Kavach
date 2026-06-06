package zkp

import (
	"crypto/ed25519"
	"crypto/rand"
	"crypto/sha256"
	"crypto/subtle"
	"encoding/base64"
	"encoding/hex"
)

const (
	ed25519PublicKeySize = ed25519.PublicKeySize
	ed25519SignatureSize = ed25519.SignatureSize
	sha256HexSize        = sha256.Size * 2
)

// Proof is a non-interactive proof-of-possession transcript.
// The prover demonstrates knowledge of a private key without revealing it.
type Proof struct {
	IdentityID    string `json:"identity_id"`
	Nonce         string `json:"nonce"`
	StatementHash string `json:"statement_hash"`
	Signature     string `json:"signature"`
}

type Prover struct {
	identityID string
	privateKey ed25519.PrivateKey
	publicKey  ed25519.PublicKey
}

func NewProver(identityID string) (*Prover, error) {
	publicKey, privateKey, err := ed25519.GenerateKey(rand.Reader)
	if err != nil {
		return nil, err
	}
	return &Prover{identityID: identityID, privateKey: privateKey, publicKey: publicKey}, nil
}

func (p *Prover) PublicKey() ed25519.PublicKey {
	return p.publicKey
}

func (p *Prover) BuildProof(statement string, nonce string) Proof {
	// Bind signature to the statement hash plus nonce so proofs cannot be replayed
	// for a different proposal payload.
	statementHash := hashHex(statement)
	msg := transcriptMessage(statementHash, nonce)
	sig := ed25519.Sign(p.privateKey, msg)
	return Proof{
		IdentityID:    p.identityID,
		Nonce:         nonce,
		StatementHash: statementHash,
		Signature:     base64.StdEncoding.EncodeToString(sig),
	}
}

type Verifier struct {
	keys map[string]ed25519.PublicKey
}

func NewVerifier() *Verifier {
	return &Verifier{keys: make(map[string]ed25519.PublicKey)}
}

func (v *Verifier) RegisterIdentity(identityID string, key ed25519.PublicKey) {
	if len(key) != ed25519PublicKeySize {
		return
	}
	copied := make(ed25519.PublicKey, ed25519PublicKeySize)
	copy(copied, key)
	v.keys[identityID] = copied
}

func (v *Verifier) Verify(statement string, proof Proof) bool {
	pub, ok := v.keys[proof.IdentityID]
	pubKey, identityOK := normalizePublicKey(pub, ok)

	expectedHash := hashHex(statement)
	hashOK := constantTimeStringEqualFixed(proof.StatementHash, expectedHash, sha256HexSize)

	sig, sigOK := decodeSignature(proof.Signature)

	// Always reach signature verification with normalized inputs so malformed
	// proofs do not skip the expensive cryptographic check based on attacker-
	// controlled hash or signature shape.
	msg := transcriptMessage(expectedHash, proof.Nonce)
	signatureOK := ed25519.Verify(pubKey[:], msg, sig[:])

	return identityOK == 1 && hashOK == 1 && sigOK == 1 && signatureOK
}

func hashHex(s string) string {
	sum := sha256.Sum256([]byte(s))
	return hex.EncodeToString(sum[:])
}

func transcriptMessage(statementHash string, nonce string) []byte {
	// Keep transcript compact and deterministic for reproducible verification.
	sum := sha256.Sum256([]byte(statementHash + "|" + nonce))
	return sum[:]
}

func normalizePublicKey(pub ed25519.PublicKey, found bool) ([ed25519PublicKeySize]byte, int) {
	var normalized [ed25519PublicKeySize]byte
	if !found || len(pub) != ed25519PublicKeySize {
		return normalized, 0
	}
	copy(normalized[:], pub)
	return normalized, 1
}

func decodeSignature(encoded string) ([ed25519SignatureSize]byte, int) {
	var normalized [ed25519SignatureSize]byte
	decoded, err := base64.StdEncoding.DecodeString(encoded)
	if err != nil || len(decoded) != ed25519SignatureSize {
		return normalized, 0
	}
	copy(normalized[:], decoded)
	return normalized, 1
}

func constantTimeStringEqualFixed(candidate string, expected string, expectedLen int) int {
	var candidateFixed [sha256HexSize]byte
	var expectedFixed [sha256HexSize]byte

	candidateLenOK := subtle.ConstantTimeEq(int32(len(candidate)), int32(expectedLen))
	expectedLenOK := subtle.ConstantTimeEq(int32(len(expected)), int32(expectedLen))

	copy(candidateFixed[:], candidate)
	copy(expectedFixed[:], expected)

	equal := subtle.ConstantTimeCompare(candidateFixed[:], expectedFixed[:])
	return candidateLenOK & expectedLenOK & equal
}
