FROM golang:1.22-alpine AS builder
WORKDIR /src
COPY . .
RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -trimpath -ldflags="-s -w" -o /out/consensus ./cmd/consensus

FROM gcr.io/distroless/static-debian12:nonroot
WORKDIR /
COPY --from=builder /out/consensus /consensus
USER nonroot:nonroot
ENTRYPOINT ["/consensus"]
