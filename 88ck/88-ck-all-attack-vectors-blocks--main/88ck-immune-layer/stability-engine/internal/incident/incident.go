package incident

import (
	"log"

	"github.com/88ck/stability-engine/internal/orchestrator"
)

type Sink struct{}

func NewSink() *Sink {
	return &Sink{}
}

func (s *Sink) Emit(plan orchestrator.Plan) {
	log.Printf("incident action=%s reason=%s", plan.Action, plan.Reason)
}
