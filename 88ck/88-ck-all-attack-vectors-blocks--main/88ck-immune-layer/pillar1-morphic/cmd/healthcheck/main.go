package main

import (
	"net/http"
	"os"
)

// Healthcheck probe for the morphic gateway. Compiled into the distroless
// image so Docker / Kubernetes can use it as a liveness / readiness test.
func main() {
	resp, err := http.Get("http://127.0.0.1:8080/healthz") //nolint:noctx
	if err != nil || resp.StatusCode != http.StatusOK {
		os.Exit(1)
	}
}
