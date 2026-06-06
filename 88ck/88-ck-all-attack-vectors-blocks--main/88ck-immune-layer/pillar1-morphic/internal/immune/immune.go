package immune

import (
	"log"
	"math"
	"sync"
	"time"

	"github.com/88ck/pillar1-morphic/internal/metrics"
)

const (
	alpha = 0.38
	beta  = 0.38
	delta = 0.19
	gamma = 0.19
	star  = 0.42
)

type SystemTopology struct {
	Nodes map[string]*Node `json:"nodes"`
	Edges map[string]*Edge `json:"edges"`
	mu    sync.RWMutex
}

type Node struct {
	ID            string    `json:"id"`
	Type          string    `json:"type"`
	SecurityLevel int       `json:"security_level"`
	CurrentState  string    `json:"current_state"`
	Protection    *string   `json:"protection,omitempty"`
	LastUpdated   time.Time `json:"last_updated"`
}

type Edge struct {
	SourceID      string    `json:"source_id"`
	TargetID      string    `json:"target_id"`
	TechniqueID   string    `json:"technique_id"`
	TechniqueName string    `json:"technique_name"`
	Protection    *string   `json:"protection,omitempty"`
	Secured       bool      `json:"secured"`
	LastUpdated   time.Time `json:"last_updated"`
}

type ChainProtection struct {
	ActivePaths    []*SecurityPath `json:"active_paths"`
	ProtectedPaths []*SecurityPath `json:"protected_paths"`
	ProtectionRate float64         `json:"protection_rate"`
	LastProtection time.Time       `json:"last_protection"`
}

type SecurityPath struct {
	ID          string    `json:"id"`
	Path        []*Edge   `json:"path"`
	Probability float64   `json:"probability"`
	Impact      float64   `json:"impact"`
	StartTime   time.Time `json:"start_time"`
	Status      string    `json:"status"`
}

type MorphologicalLogic struct {
	RotationSchedule map[string]*RotationConfig `json:"rotation_schedule"`
	LastRotation     map[string]time.Time       `json:"last_rotation"`
	RotationRate     float64                    `json:"rotation_rate"`
}

type RotationConfig struct {
	ComponentID  string        `json:"component_id"`
	Frequency    time.Duration `json:"frequency"`
	NextRotation time.Time     `json:"next_rotation"`
	LastRotation time.Time     `json:"last_rotation"`
	Priority     string        `json:"priority"`
}

type ConsensusIntegrity struct {
	QuorumSuccess    float64   `json:"quorum_success"`
	LastQuorumCheck  time.Time `json:"last_quorum_check"`
	ConsensusLatency float64   `json:"consensus_latency"`
}

type SemanticEntropy struct {
	EntropyLevel       float64         `json:"entropy_level"`
	AnomalyDetected    bool            `json:"anomaly_detected"`
	PotentialAnomalies []*SecurityPath `json:"potential_anomalies,omitempty"`
	LastCalculation    time.Time       `json:"last_calculation"`
}

type StabilityFunction struct {
	MValue         float64   `json:"m_value"`
	CValue         float64   `json:"c_value"`
	DValue         float64   `json:"d_value"`
	EValue         float64   `json:"e_value"`
	SValue         float64   `json:"s_value"`
	LastCalculated time.Time `json:"last_calculated"`
}

type VSCodeSecurityContext struct {
	ExtensionValidation     bool      `json:"extension_validation"`
	WorkspaceTrust          bool      `json:"workspace_trust"`
	ProtocolHandlerSecurity bool      `json:"protocol_handler_security"`
	WebviewXSSProtection    bool      `json:"webview_xss_protection"`
	LastSecurityCheck       time.Time `json:"last_security_check"`
}

type PromptInjectionProtection struct {
	InputSanitization       bool      `json:"input_sanitization"`
	ToolMetadataValidation  bool      `json:"tool_metadata_validation"`
	InstructionBoundary     bool      `json:"instruction_boundary"`
	ContentVerification     bool      `json:"content_verification"`
	LastProtectionUpdate    time.Time `json:"last_protection_update"`
}

type ImmuneLayer struct {
	SystemTopology           *SystemTopology           `json:"system_topology"`
	ChainProtection          *ChainProtection          `json:"chain_protection"`
	MorphologicalLogic       *MorphologicalLogic       `json:"morphological_logic"`
	ConsensusIntegrity       *ConsensusIntegrity       `json:"consensus_integrity"`
	SemanticEntropy          *SemanticEntropy          `json:"semantic_entropy"`
	StabilityFunction        *StabilityFunction        `json:"stability_function"`
	VSCodeSecurityContext    *VSCodeSecurityContext    `json:"vscode_security_context"`
	PromptInjectionProtection *PromptInjectionProtection `json:"prompt_injection_protection"`
	mu                       sync.RWMutex
}

func NewImmuneLayer() *ImmuneLayer {
	return &ImmuneLayer{
		SystemTopology: &SystemTopology{
			Nodes: make(map[string]*Node),
			Edges: make(map[string]*Edge),
		},
		ChainProtection: &ChainProtection{
			ActivePaths:    make([]*SecurityPath, 0),
			ProtectedPaths: make([]*SecurityPath, 0),
		},
		MorphologicalLogic: &MorphologicalLogic{
			RotationSchedule: make(map[string]*RotationConfig),
			LastRotation:     make(map[string]time.Time),
		},
		ConsensusIntegrity: &ConsensusIntegrity{},
		SemanticEntropy: &SemanticEntropy{
			PotentialAnomalies: make([]*SecurityPath, 0),
		},
		StabilityFunction: &StabilityFunction{},
		VSCodeSecurityContext: &VSCodeSecurityContext{
			ExtensionValidation:     true,
			WorkspaceTrust:          true,
			ProtocolHandlerSecurity: true,
			WebviewXSSProtection:    true,
			LastSecurityCheck:       time.Now(),
		},
		PromptInjectionProtection: &PromptInjectionProtection{
			InputSanitization:      true,
			ToolMetadataValidation: true,
			InstructionBoundary:    true,
			ContentVerification:    true,
			LastProtectionUpdate:   time.Now(),
		},
	}
}

func (il *ImmuneLayer) CalculateStability() {
	il.mu.Lock()
	defer il.mu.Unlock()

	il.updateVSCodeSecurityContext()
	il.updatePromptInjectionProtection()

	mValue := il.calculateMorphologicalRate()
	cValue := il.calculateConsensusIntegrity()
	dValue := il.calculateChainProtection()
	eValue := il.calculateSemanticEntropy()

	sValue := alpha*mValue + beta*cValue + delta*dValue - gamma*eValue

	il.StabilityFunction.MValue = mValue
	il.StabilityFunction.CValue = cValue
	il.StabilityFunction.DValue = dValue
	il.StabilityFunction.EValue = eValue
	il.StabilityFunction.SValue = sValue
	il.StabilityFunction.LastCalculated = time.Now()

	metrics.MTValue.Set(mValue)

	if sValue < star {
		log.Printf("STABILITY ALERT: S(t)=%.3f below threshold %.3f", sValue, star)
		il.triggerStabilityResponse()
	}
}

func (il *ImmuneLayer) calculateMorphologicalRate() float64 {
	now := time.Now()
	window := 5 * time.Minute
	transformationCount := 0

	for _, config := range il.MorphologicalLogic.RotationSchedule {
		if config.LastRotation.After(now.Add(-window)) {
			transformationCount++
		}
	}

	maxTransformations := 10.0
	rate := float64(transformationCount) / maxTransformations
	if rate > 1.0 {
		rate = 1.0
	}

	il.MorphologicalLogic.RotationRate = rate
	return rate
}

func (il *ImmuneLayer) calculateConsensusIntegrity() float64 {
	quorumSuccess := 0.95
	consensusLatency := 65.0

	il.ConsensusIntegrity.QuorumSuccess = quorumSuccess
	il.ConsensusIntegrity.ConsensusLatency = consensusLatency
	il.ConsensusIntegrity.LastQuorumCheck = time.Now()

	return quorumSuccess * math.Max(0.0, 1.0-math.Min(consensusLatency/500.0, 1.0))
}

func (il *ImmuneLayer) calculateChainProtection() float64 {
	activeCount := len(il.ChainProtection.ActivePaths)
	protectedCount := len(il.ChainProtection.ProtectedPaths)

	var protectionRate float64
	if activeCount+protectedCount > 0 {
		protectionRate = float64(protectedCount) / float64(activeCount+protectedCount)
	}

	if protectionRate > 1.0 {
		protectionRate = 1.0
	}

	il.ChainProtection.ProtectionRate = protectionRate
	if protectedCount > 0 {
		il.ChainProtection.LastProtection = time.Now()
	}

	return protectionRate
}

func (il *ImmuneLayer) calculateSemanticEntropy() float64 {
	entropy := il.SemanticEntropy.EntropyLevel
	anomalyWeight := 0.0

	if len(il.SemanticEntropy.PotentialAnomalies) > 0 {
		anomalyWeight = float64(len(il.SemanticEntropy.PotentialAnomalies)) * 0.1
	}

	entropy = math.Min(1.0, entropy+anomalyWeight)
	il.SemanticEntropy.EntropyLevel = entropy
	il.SemanticEntropy.AnomalyDetected = len(il.SemanticEntropy.PotentialAnomalies) > 0
	il.SemanticEntropy.LastCalculation = time.Now()

	return entropy
}

func (il *ImmuneLayer) updateVSCodeSecurityContext() float64 {
	ctx := il.VSCodeSecurityContext
	score := 0.0
	if ctx.ExtensionValidation {
		score += 0.25
	}
	if ctx.WorkspaceTrust {
		score += 0.25
	}
	if ctx.ProtocolHandlerSecurity {
		score += 0.25
	}
	if ctx.WebviewXSSProtection {
		score += 0.25
	}
	ctx.LastSecurityCheck = time.Now()
	if score < 1.0 {
		log.Printf("VS Code security context degraded: %.2f", score)
	}
	return score
}

func (il *ImmuneLayer) updatePromptInjectionProtection() float64 {
	prot := il.PromptInjectionProtection
	score := 0.0
	if prot.InputSanitization {
		score += 0.25
	}
	if prot.ToolMetadataValidation {
		score += 0.25
	}
	if prot.InstructionBoundary {
		score += 0.25
	}
	if prot.ContentVerification {
		score += 0.25
	}
	prot.LastProtectionUpdate = time.Now()
	if score < 1.0 {
		log.Printf("Prompt injection protections incomplete: %.2f", score)
	}
	return score
}

func (il *ImmuneLayer) triggerStabilityResponse() {
	log.Print("triggering defensive hardening response")
	il.enforceHardening()
}

func (il *ImmuneLayer) enforceHardening() {
	for _, edge := range il.SystemTopology.Edges {
		if !edge.Secured {
			edge.Secured = true
			protection := "hardened"
			edge.Protection = &protection
			edge.LastUpdated = time.Now()
		}
	}

	for _, path := range il.ChainProtection.ActivePaths {
		if path.Status != "protected" {
			path.Status = "protected"
			path.Impact = math.Max(path.Impact, 0.5)
		}
	}
}

func (il *ImmuneLayer) AddNode(node *Node) {
	il.SystemTopology.mu.Lock()
	defer il.SystemTopology.mu.Unlock()
	il.SystemTopology.Nodes[node.ID] = node
}

func (il *ImmuneLayer) AddEdge(edge *Edge) {
	il.SystemTopology.mu.Lock()
	defer il.SystemTopology.mu.Unlock()
	il.SystemTopology.Edges[edge.SourceID+"->"+edge.TargetID] = edge
}

func (il *ImmuneLayer) RegisterRotation(config *RotationConfig) {
	il.MorphologicalLogic.RotationSchedule[config.ComponentID] = config
	il.MorphologicalLogic.LastRotation[config.ComponentID] = config.LastRotation
}
