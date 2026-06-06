package scheduler

import (
	"crypto/sha256"
	"encoding/binary"
	"errors"
	"fmt"
	"io"
	"math"
	"sync"
	"time"

	"golang.org/x/crypto/chacha20"
)

const DefaultRotationPeriod = 2 * time.Minute

var ErrNoEndpoints = errors.New("scheduler requires at least one endpoint")

type Endpoint struct {
	Address string `json:"address"`
	Port    uint32 `json:"port"`
}

type Config struct {
	RotationPeriod     time.Duration
	MaxSustainableRate float64
	Now                func() time.Time
}

type Rotation struct {
	Cycle               uint64     `json:"cycle"`
	MutationID          string     `json:"mutation_id"`
	Endpoints           []Endpoint `json:"endpoints"`
	EventsPerMinute     float64    `json:"events_per_minute"`
	MTValue             float64    `json:"m_t_value"`
	TriggeredAt         time.Time  `json:"triggered_at"`
	NextScheduledMorph  time.Time  `json:"next_scheduled_morph"`
}

type Status struct {
	CurrentCycle        uint64    `json:"current_cycle"`
	CurrentMTValue      float64   `json:"current_m_t_value"`
	NextScheduledMorph  time.Time `json:"next_scheduled_morph"`
	RotationPeriod      string    `json:"rotation_period"`
	MaxSustainableRate  float64   `json:"max_sustainable_rate"`
	EventsPerMinute     float64   `json:"events_per_minute"`
}

type Scheduler struct {
	key                [32]byte
	seed               string
	rotationPeriod     time.Duration
	maxSustainableRate float64
	now                func() time.Time

	mu           sync.RWMutex
	endpoints    []Endpoint
	cycle        uint64
	recentEvents []time.Time
	currentMT    float64
	nextMorph    time.Time
}

func New(seed string, endpoints []Endpoint, cfg Config) (*Scheduler, error) {
	if len(endpoints) == 0 {
		return nil, ErrNoEndpoints
	}
	if cfg.MaxSustainableRate <= 0 {
		return nil, fmt.Errorf("max sustainable rate must be positive")
	}
	rotationPeriod := cfg.RotationPeriod
	if rotationPeriod <= 0 {
		rotationPeriod = DefaultRotationPeriod
	}
	now := cfg.Now
	if now == nil {
		now = time.Now
	}

	s := &Scheduler{
		key:                sha256.Sum256([]byte(seed)),
		seed:               seed,
		rotationPeriod:     rotationPeriod,
		maxSustainableRate: cfg.MaxSustainableRate,
		now:                now,
		endpoints:          cloneEndpoints(endpoints),
	}
	s.nextMorph = s.now().Add(s.rotationPeriod)
	return s, nil
}

func (s *Scheduler) Seed() string {
	return s.seed
}

func (s *Scheduler) RotationPeriod() time.Duration {
	return s.rotationPeriod
}

func (s *Scheduler) LeadWindow(now time.Time) []time.Time {
	s.mu.RLock()
	defer s.mu.RUnlock()

	cutoff := now.Add(-time.Minute)
	filtered := make([]time.Time, 0, len(s.recentEvents))
	for _, eventTime := range s.recentEvents {
		if !eventTime.Before(cutoff) {
			filtered = append(filtered, eventTime)
		}
	}
	return filtered
}

func (s *Scheduler) SequenceForCycle(cycle uint64) []Endpoint {
	shuffled := cloneEndpoints(s.endpoints)
	if len(shuffled) <= 1 {
		return shuffled
	}

	reader, err := s.readerForCycle(cycle)
	if err != nil {
		return shuffled
	}

	for i := len(shuffled) - 1; i > 0; i-- {
		j := deterministicIndex(reader, i+1)
		shuffled[i], shuffled[j] = shuffled[j], shuffled[i]
	}
	return shuffled
}

func (s *Scheduler) Rotate(now time.Time) Rotation {
	s.mu.Lock()
	defer s.mu.Unlock()

	cycle := s.cycle
	sequence := s.SequenceForCycle(cycle)
	s.cycle++

	cutoff := now.Add(-time.Minute)
	filtered := s.recentEvents[:0]
	for _, eventTime := range s.recentEvents {
		if !eventTime.Before(cutoff) {
			filtered = append(filtered, eventTime)
		}
	}
	filtered = append(filtered, now)
	s.recentEvents = filtered

	eventsPerMinute := float64(len(s.recentEvents))
	mtValue := clamp(eventsPerMinute/s.maxSustainableRate, 0, 1)
	s.currentMT = mtValue
	s.nextMorph = now.Add(s.rotationPeriod)

	return Rotation{
		Cycle:              cycle,
		MutationID:         fmt.Sprintf("morph-%06d", cycle),
		Endpoints:          sequence,
		EventsPerMinute:    eventsPerMinute,
		MTValue:            mtValue,
		TriggeredAt:        now,
		NextScheduledMorph: s.nextMorph,
	}
}

func (s *Scheduler) Status() Status {
	now := s.now()
	s.mu.RLock()
	defer s.mu.RUnlock()

	cutoff := now.Add(-time.Minute)
	events := 0
	for _, eventTime := range s.recentEvents {
		if !eventTime.Before(cutoff) {
			events++
		}
	}

	return Status{
		CurrentCycle:       s.cycle,
		CurrentMTValue:     s.currentMT,
		NextScheduledMorph: s.nextMorph,
		RotationPeriod:     s.rotationPeriod.String(),
		MaxSustainableRate: s.maxSustainableRate,
		EventsPerMinute:    float64(events),
	}
}

func (s *Scheduler) readerForCycle(cycle uint64) (io.Reader, error) {
	nonce := make([]byte, chacha20.NonceSize)
	binary.BigEndian.PutUint64(nonce[chacha20.NonceSize-8:], cycle)
	stream, err := chacha20.NewUnauthenticatedCipher(s.key[:], nonce)
	if err != nil {
		return nil, err
	}
	return &cipherReader{cipher: stream}, nil
}

type cipherReader struct {
	cipher *chacha20.Cipher
}

func (r *cipherReader) Read(p []byte) (int, error) {
	zeros := make([]byte, len(p))
	r.cipher.XORKeyStream(p, zeros)
	return len(p), nil
}

func deterministicIndex(reader io.Reader, size int) int {
	if size <= 1 {
		return 0
	}
	var buf [8]byte
	if _, err := io.ReadFull(reader, buf[:]); err != nil {
		return 0
	}
	value := binary.BigEndian.Uint64(buf[:])
	return int(value % uint64(size))
}

func cloneEndpoints(endpoints []Endpoint) []Endpoint {
	cloned := make([]Endpoint, len(endpoints))
	copy(cloned, endpoints)
	return cloned
}

func clamp(value float64, min float64, max float64) float64 {
	return math.Max(min, math.Min(max, value))
}
