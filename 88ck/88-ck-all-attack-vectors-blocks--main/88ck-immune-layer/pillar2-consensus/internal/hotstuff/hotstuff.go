package hotstuff

import (
	"crypto/rand"
	"encoding/hex"
)

type Engine struct {
	validators int
}

func NewEngine(validators int) *Engine {
	if validators < 4 {
		validators = 4
	}
	return &Engine{validators: validators}
}

func (e *Engine) Propose(prefix string) string {
	b := make([]byte, 6)
	if _, err := rand.Read(b); err != nil {
		return prefix + "-fallback"
	}
	return prefix + "-" + hex.EncodeToString(b)
}

func (e *Engine) Quorum() int {
	return (2*e.validators)/3 + 1
}
