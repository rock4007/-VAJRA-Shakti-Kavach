package securityfilter

import (
	"regexp"
	"strings"
)

// PromptShield detects LLM prompt injection, jailbreak, and indirect injection
// patterns before requests reach AI-backed services. This threat class is distinct
// from SQLi and malware delivery -- the payload is valid text that hijacks model
// context rather than executing code.
//
// Three attack families are modelled:
//   - Direct injection: user-supplied text that overrides system instructions
//   - Jailbreak: framing prompts that try to escape alignment constraints
//   - Indirect/data-plane injection: payloads embedded in external content
//     (PDFs, web pages, tool outputs) that re-route the model's next action
type PromptShield struct {
	directInjection  []*regexp.Regexp
	jailbreakFraming []*regexp.Regexp
	dataPlaneInject  []*regexp.Regexp
}

// multiSpaceRe collapses repeated whitespace -- pre-compiled once, used in the hot path.
var multiSpaceRe = regexp.MustCompile(`\s{2,}`)

func NewPromptShield() *PromptShield {
	return &PromptShield{
		// Direct injection: explicit instruction-override markers.
		directInjection: []*regexp.Regexp{
			regexp.MustCompile(`(?i)ignore\s+(all\s+)?(previous|prior|above|earlier)\s+(instructions?|prompts?|context|rules?|constraints?)`),
			regexp.MustCompile(`(?i)disregard\s+(all\s+)?(previous|prior|above|earlier)\s+(instructions?|prompts?|context|rules?)`),
			regexp.MustCompile(`(?i)forget\s+(everything|all|your\s+instructions?|your\s+context)`),
			regexp.MustCompile(`(?i)new\s+instructions?:\s`),
			regexp.MustCompile(`(?i)system\s*:\s*(you\s+are|act\s+as|your\s+new|from\s+now)`),
			regexp.MustCompile(`(?i)\[system\]|<system>|###\s*system`),
			regexp.MustCompile(`(?i)override\s+(system|safety|content)\s*(policy|filter|prompt|instructions?|rules?)`),
			regexp.MustCompile(`(?i)your\s+(real\s+|true\s+|actual\s+)?(instructions?|rules?|purpose|goal|directive)\s+(is|are)\s+(to|now)`),
		},
		// Jailbreak framing: role-play and hypothetical escapes.
		jailbreakFraming: []*regexp.Regexp{
			regexp.MustCompile(`(?i)(act|pretend|roleplay|imagine|simulate|behave)\s+as\s+(if\s+you\s+(are|were)|a[n]?\s+AI\s+(without|with\s+no)|an?\s+unrestricted|dan\b|jailbreak)`),
			regexp.MustCompile(`(?i)\bDAN\b.{0,60}\bdo\s+anything\s+now\b`),
			regexp.MustCompile(`(?i)developer\s+mode|jailbreak\s+mode|no\s+restrictions?\s+mode`),
			regexp.MustCompile(`(?i)(you\s+are|you're)\s+(now\s+)?(free\s+from|not\s+bound\s+by|unshackled\s+from)\s+(your\s+)?(guidelines?|rules?|restrictions?|alignment|training|filters?)`),
			regexp.MustCompile(`(?i)hypothetically\s+speaking.{0,60}(how\s+(would|do|can)|what\s+steps|instructions?)`),
			regexp.MustCompile(`(?i)in\s+(a\s+)?fictional\s+(world|story|scenario).{0,80}(how\s+(to|would)|instructions?|steps?)`),
			regexp.MustCompile(`(?i)token\s+(budget|limit).{0,40}(bypass|ignore|remove)`),
		},
		// Indirect / data-plane injection: payloads hidden in retrieved content.
		dataPlaneInject: []*regexp.Regexp{
			regexp.MustCompile(`(?i)\[INST\]|\[/INST\]|<\|im_start\|>|<\|im_end\|>`),
			regexp.MustCompile(`(?i)<\|endoftext\|>|<\|beginoftext\|>|<\|start_header_id\|>`),
			regexp.MustCompile(`(?i)human\s*:\s*.{0,200}assistant\s*:`),
			regexp.MustCompile(`(?i)###\s*(instruction|human|assistant|system|user)\b`),
			regexp.MustCompile(`(?i)(exfiltrate|leak|send|transmit|upload)\s+(all\s+)?(user\s+)?(data|messages?|history|context|conversation|credentials?|api\s+keys?)`),
			regexp.MustCompile(`(?i)execute\s+(the\s+following|this)\s+(command|code|script|tool\s+call)`),
			regexp.MustCompile(`(?i)tool_call\s*\[|<tool_call>|function_call\s*\{`),
		},
	}
}

// InspectPrompt evaluates a text payload for LLM injection signals.
func (ps *PromptShield) InspectPrompt(probe string) Verdict {
	normalized := normalizePromptProbe(probe)

	if reason, evidence := matchAny(ps.directInjection, normalized); reason != "" {
		return Verdict{Allowed: false, Reason: "prompt_injection_direct", Evidence: evidence}
	}
	if reason, evidence := matchAny(ps.jailbreakFraming, normalized); reason != "" {
		return Verdict{Allowed: false, Reason: "prompt_jailbreak_blocked", Evidence: evidence}
	}
	if reason, evidence := matchAny(ps.dataPlaneInject, normalized); reason != "" {
		return Verdict{Allowed: false, Reason: "prompt_injection_dataplane", Evidence: evidence}
	}

	return Verdict{Allowed: true, Reason: "allowed"}
}
// normalizePromptProbe strips invisible Unicode codepoints used to split keywords
// across regex word boundaries, then collapses repeated whitespace.
func normalizePromptProbe(input string) string {
	stripped := strings.Map(func(r rune) rune {
		switch r {
		case '\u200B', '\u200C', '\u200D', '\u200E', '\u200F',
			'\u202A', '\u202B', '\u202C', '\u202D', '\u202E',
			'\uFEFF':
			return -1
		}
		return r
	}, input)
	return multiSpaceRe.ReplaceAllString(stripped, " ")
}
