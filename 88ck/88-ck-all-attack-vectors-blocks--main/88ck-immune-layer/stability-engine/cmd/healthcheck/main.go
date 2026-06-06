package main

import (
	"net/http"
	"os"
)

// Healthcheck probe for the stability engine. Compiled into the distroless
// image so Docker / Kubernetes can use it as a liveness / readiness test.
func main() {
	resp, err := http.Get("http://127.0.0.1:8090/healthz") //nolint:noctx
	if err != nil || resp.StatusCode != http.StatusOK {
		os.Exit(1)
	}
}
