package securityfilter

import (
	"strings"
	"unicode"
)

var dangerousReplacer = strings.NewReplacer(
	"<", "[lt]",
	">", "[gt]",
	"'", "[sq]",
	"\"", "[dq]",
	";", "[semi]",
	"--", "[dashdash]",
)

// Defuse strips control characters and neutralizes high-risk symbols before logging.
// The output is diagnostic-only and must never be reused as executable input.
func Defuse(input string) string {
	clean := strings.Map(func(r rune) rune {
		if unicode.IsPrint(r) || unicode.IsSpace(r) {
			return r
		}
		return -1
	}, input)
	clean = dangerousReplacer.Replace(clean)
	clean = strings.TrimSpace(clean)
	if len(clean) > 240 {
		return clean[:240] + "..."
	}
	return clean
}
