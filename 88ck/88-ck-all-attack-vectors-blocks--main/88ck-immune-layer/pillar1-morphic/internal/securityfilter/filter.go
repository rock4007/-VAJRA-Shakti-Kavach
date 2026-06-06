package securityfilter

import (
	"io"
	"net/http"
	"regexp"
	"strings"
)

type Verdict struct {
	Allowed  bool
	Reason   string
	Evidence string
}

type Filter struct {
	sqlPatterns     []*regexp.Regexp
	malwarePatterns []*regexp.Regexp
	maxInspectBytes int64
}

// New returns a heuristic ingress filter for common SQLi and payload-delivery patterns.
// Rules are intentionally conservative and can be tuned as false positives are observed.
func New() *Filter {
	return &Filter{
		sqlPatterns: []*regexp.Regexp{
			regexp.MustCompile(`(?i)union\s+select`),
			regexp.MustCompile(`(?i)or\s+1\s*=\s*1`),
			regexp.MustCompile(`(?i)sleep\s*\(`),
			regexp.MustCompile(`(?i)benchmark\s*\(`),
			regexp.MustCompile(`(?i)drop\s+table`),
			regexp.MustCompile(`(?i)information_schema`),
			regexp.MustCompile(`(?i)xp_cmdshell`),
			regexp.MustCompile(`(?i)(--|/\*|\*/)`)},
		malwarePatterns: []*regexp.Regexp{
			regexp.MustCompile(`(?i)powershell\s+-enc`),
			regexp.MustCompile(`(?i)cmd\.exe`),
			regexp.MustCompile(`(?i)/bin/sh`),
			regexp.MustCompile(`(?i)wget\s+https?://`),
			regexp.MustCompile(`(?i)curl\s+https?://`),
			regexp.MustCompile(`(?i)base64\s+-d`),
			regexp.MustCompile(`(?i)<script`),
			regexp.MustCompile(`(?i)javascript:`),
			regexp.MustCompile(`(?i)mshta`),
			regexp.MustCompile(`(?i)rundll32`),
			regexp.MustCompile(`(?i)nc\s+-e`)},
		maxInspectBytes: 32 * 1024,
	}
}

func (f *Filter) InspectRequest(r *http.Request) Verdict {
	// Build one probe string from path/query/headers/body so every rule sees the same view.
	parts := []string{r.URL.RawQuery, r.URL.Path}
	for key, vals := range r.URL.Query() {
		parts = append(parts, key)
		parts = append(parts, vals...)
	}
	if ua := r.Header.Get("User-Agent"); ua != "" {
		parts = append(parts, ua)
	}
	if ct := r.Header.Get("Content-Type"); ct != "" {
		parts = append(parts, ct)
	}

	if r.Body != nil && shouldInspectBody(r.Method) {
		bodyBytes, _ := io.ReadAll(io.LimitReader(r.Body, f.maxInspectBytes))
		// Replace body so downstream handlers still receive request payload.
		r.Body = io.NopCloser(strings.NewReader(string(bodyBytes)))
		parts = append(parts, string(bodyBytes))
	}

	probe := strings.Join(parts, "\n")
	probe = strings.ReplaceAll(probe, "+", " ")
	if reason, evidence := matchAny(f.sqlPatterns, probe); reason != "" {
		return Verdict{Allowed: false, Reason: "sql_injection_blocked", Evidence: evidence}
	}
	if reason, evidence := matchAny(f.malwarePatterns, probe); reason != "" {
		return Verdict{Allowed: false, Reason: "malware_payload_blocked", Evidence: evidence}
	}

	return Verdict{Allowed: true, Reason: "allowed"}
}

func shouldInspectBody(method string) bool {
	switch method {
	case http.MethodPost, http.MethodPut, http.MethodPatch:
		return true
	default:
		return false
	}
}

func matchAny(patterns []*regexp.Regexp, input string) (string, string) {
	for _, p := range patterns {
		if loc := p.FindStringIndex(input); loc != nil {
			// Return exact evidence fragment for forensics and deterministic tests.
			return p.String(), input[loc[0]:loc[1]]
		}
	}
	return "", ""
}

