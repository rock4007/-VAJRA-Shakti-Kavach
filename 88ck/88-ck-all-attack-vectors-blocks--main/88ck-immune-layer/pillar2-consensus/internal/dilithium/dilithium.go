package dilithium

import (
	"crypto/sha256"
	"encoding/hex"
)

type Signer struct{}

func NewSigner() *Signer {
	return &Signer{}
}

func (s *Signer) Sign(message string) string {
	sum := sha256.Sum256([]byte("dilithium-sim:" + message))
	return "pqsig:" + hex.EncodeToString(sum[:])
}
