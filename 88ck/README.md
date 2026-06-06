# 88/CK Immune Layer - Pillar I

Pillar I implements **Morphomorphic Logic** (the **M(t)** component) for the 88/CK immune layer.

Stack:
- Go 1.22
- Envoy 1.29 (xDS ADS control plane)
- Redis Streams
- Prometheus

## What This Service Does

On each morph cycle, the service:
1. Computes a deterministic ChaCha20-seeded endpoint topology rotation.
2. Emits a gamma baseline update signal at `t_mutation - delta_t`.
3. Pushes new config over xDS ADS.
4. Waits for Envoy acknowledgement.
5. Records cycle metrics and traces.

This gives reproducible behavior for tests while remaining unpredictable to adversaries without the seed.

## Project Layout

- `cmd/88ck` - service bootstrap and runtime wiring
- `internal/scheduler` - deterministic rotation scheduler and M(t)
- `internal/gamma` - gamma synchronization protocol and Redis Stream publish
- `internal/xds` - Envoy ADS control plane and snapshot push/ack tracking
- `internal/app` - morph orchestration, HTTP API, health/status handlers
- `internal/observability` - Prometheus metric registry and definitions

## M(t) Definition

`m_t_value = current_rotation_events_per_min / max_sustainable_rate`

The implementation clamps M(t) to `[0,1]`.

## Gamma Protocol

- Default `delta_t = 200ms`
- Embedding latency threshold `tau_emb = 38ms`
- Coupling fault if `delta_t < tau_emb`
- Redis Stream key: `88ck:gamma:baseline-update`

Payload fields:
- `mutation_id`
- `scheduled_at`
- `delta_t_ms`
- `seed`

## API Endpoints

- `POST /api/v1/morph/trigger` - manual morph (admin-only if `ADMIN_TOKEN` is set)
- `GET /api/v1/morph/status` - current M(t), cycle, topology, next morph
- `GET /api/v1/gamma/status` - gamma protocol state
- `GET /morph-status` - alias for morph status
- `GET /health` - liveness/health status
- `GET /metrics` - Prometheus scrape endpoint

Admin trigger authentication:
- Header: `X-Admin-Token: <ADMIN_TOKEN>`

## Prometheus Metrics

- `morph_cycles_total` (counter)
- `morph_cycle_completed_total` (counter)
- `morph_cycle_duration_seconds` (histogram)
- `m_t_value` (gauge, clamped 0.0-1.0)
- `gamma_lead_time_ms` (gauge)
- `gamma_faults_total` (counter)
- `endpoint_rotation_events_total` (counter)

## Configuration

Environment variables:

- `MORPH_SEED` (default: `88ck-default-seed`)
- `ROTATION_PERIOD` (default: `2m`)
- `MAX_SUSTAINABLE_RATE` (default: `30`)
- `UPSTREAM_ENDPOINTS` (default: `127.0.0.1:8081,127.0.0.1:8082`)
- `REDIS_ADDRESS` (default: `127.0.0.1:6379`)
- `GAMMA_LEAD_TIME` (default: `200ms`)
- `TAU_EMB` (default: `38ms`)
- `HTTP_ADDRESS` (default: `:8080`)
- `XDS_ADDRESS` (default: `:18000`)
- `XDS_ACK_TIMEOUT` (default: `500ms`)
- `ENVOY_NODE_ID` (default: `88ck-node`)
- `ENVOY_LISTEN_ADDRESS` (default: `0.0.0.0`)
- `ENVOY_LISTEN_PORT` (default: `10000`)
- `ADMIN_TOKEN` (optional)

## Run Locally

1. Start Redis:

```powershell
docker run --rm -p 6379:6379 redis:7
```

2. Install dependencies and run service:

```powershell
go mod tidy
go run ./cmd/88ck
```

3. Check health and metrics:

```powershell
curl http://localhost:8080/health
curl http://localhost:8080/metrics
```

4. Trigger a manual morph:

```powershell
curl -X POST http://localhost:8080/api/v1/morph/trigger
```

With admin token:

```powershell
curl -X POST http://localhost:8080/api/v1/morph/trigger -H "X-Admin-Token: your-token"
```

## Tests

Implemented tests cover the requested behaviors:
- deterministic rotation sequence for same seed
- gamma lead time above embedding threshold
- gamma coupling fault alert when violated
- xDS hot-reload acknowledgement within 500ms (unit-level ack path)
- nominal M(t) bounded in `[0,1]`

Run:

```powershell
go test ./... -cover
```

## Observability

- Structured logging with `zerolog`
- OpenTelemetry spans around each morph cycle and xDS push
- Prometheus metrics for morph, gamma, and rotation pressure

## Notes

- xDS is implemented in ADS mode via go-control-plane snapshots.
- For full integration validation, run this service with a live Envoy 1.29 configured to connect to `XDS_ADDRESS`.