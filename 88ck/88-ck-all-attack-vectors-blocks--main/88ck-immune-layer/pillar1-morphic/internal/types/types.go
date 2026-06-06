package types

import "time"

type Endpoint struct {
	ID     string            `json:"id"`
	Addr   string            `json:"addr"`
	Weight uint32            `json:"weight"`
	Labels map[string]string `json:"labels,omitempty"`
}

type EndpointTopology struct {
	MutationID  string     `json:"mutation_id"`
	Endpoints   []Endpoint `json:"endpoints"`
	ScheduledAt time.Time  `json:"scheduled_at"`
	Seed        []byte     `json:"seed,omitempty"`
}

