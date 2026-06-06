package xds

import (
	"context"
	"fmt"
	"net"
	"sync"
	"sync/atomic"
	"time"

	"github.com/88ck/immune-layer/internal/observability"
	"github.com/88ck/immune-layer/internal/scheduler"
	cluster "github.com/envoyproxy/go-control-plane/envoy/config/cluster/v3"
	core "github.com/envoyproxy/go-control-plane/envoy/config/core/v3"
	endpoint "github.com/envoyproxy/go-control-plane/envoy/config/endpoint/v3"
	listener "github.com/envoyproxy/go-control-plane/envoy/config/listener/v3"
	route "github.com/envoyproxy/go-control-plane/envoy/config/route/v3"
	discoverygrpc "github.com/envoyproxy/go-control-plane/envoy/service/discovery/v3"
	clusterservice "github.com/envoyproxy/go-control-plane/envoy/service/cluster/v3"
	endpointservice "github.com/envoyproxy/go-control-plane/envoy/service/endpoint/v3"
	listenerservice "github.com/envoyproxy/go-control-plane/envoy/service/listener/v3"
	routeservice "github.com/envoyproxy/go-control-plane/envoy/service/route/v3"
	hcm "github.com/envoyproxy/go-control-plane/envoy/extensions/filters/network/http_connection_manager/v3"
	router "github.com/envoyproxy/go-control-plane/envoy/extensions/filters/http/router/v3"
	cachetypes "github.com/envoyproxy/go-control-plane/pkg/cache/types"
	cache "github.com/envoyproxy/go-control-plane/pkg/cache/v3"
	resource "github.com/envoyproxy/go-control-plane/pkg/resource/v3"
	server "github.com/envoyproxy/go-control-plane/pkg/server/v3"
	"github.com/rs/zerolog"
	"go.opentelemetry.io/otel/trace"
	"google.golang.org/grpc"
	"google.golang.org/protobuf/types/known/anypb"
	"google.golang.org/protobuf/types/known/durationpb"
)

type Config struct {
	NodeID          string
	ClusterName     string
	RouteName       string
	ListenerName    string
	ListenAddress   string
	ListenPort      uint32
	AckTimeout      time.Duration
	ManagementHost  string
}

type State struct {
	CurrentVersion string                `json:"current_version"`
	LastAckVersion string                `json:"last_ack_version"`
	NodeID         string                `json:"node_id"`
	Endpoints      []scheduler.Endpoint  `json:"endpoints"`
}

type ControlPlane struct {
	cache    cache.SnapshotCache
	server   server.Server
	grpc     *grpc.Server
	config   Config
	metrics  *observability.Metrics
	log      zerolog.Logger
	tracer   trace.Tracer

	versionCounter atomic.Uint64

	mu             sync.RWMutex
	ackWaiters     map[string]chan struct{}
	currentVersion string
	lastAckVersion string
	endpoints      []scheduler.Endpoint
	streamNodeID   string
	listener       net.Listener
}

func New(ctx context.Context, cfg Config, metrics *observability.Metrics, log zerolog.Logger, tracer trace.Tracer) (*ControlPlane, error) {
	if cfg.NodeID == "" {
		cfg.NodeID = "88ck-node"
	}
	if cfg.ClusterName == "" {
		cfg.ClusterName = "88ck-cluster"
	}
	if cfg.RouteName == "" {
		cfg.RouteName = "88ck-route"
	}
	if cfg.ListenerName == "" {
		cfg.ListenerName = "88ck-listener"
	}
	if cfg.ListenAddress == "" {
		cfg.ListenAddress = "0.0.0.0"
	}
	if cfg.ListenPort == 0 {
		cfg.ListenPort = 10000
	}
	if cfg.AckTimeout <= 0 {
		cfg.AckTimeout = 500 * time.Millisecond
	}
	if tracer == nil {
		tracer = trace.NewNoopTracerProvider().Tracer("88ck/xds")
	}

	cp := &ControlPlane{
		cache:      cache.NewSnapshotCache(true, cache.IDHash{}, nil),
		config:     cfg,
		metrics:    metrics,
		log:        log,
		tracer:     tracer,
		ackWaiters: make(map[string]chan struct{}),
	}
	cp.server = server.NewServer(ctx, cp.cache, cp)
	cp.grpc = grpc.NewServer()

	discoverygrpc.RegisterAggregatedDiscoveryServiceServer(cp.grpc, cp.server)
	clusterservice.RegisterClusterDiscoveryServiceServer(cp.grpc, cp.server)
	endpointservice.RegisterEndpointDiscoveryServiceServer(cp.grpc, cp.server)
	routeservice.RegisterRouteDiscoveryServiceServer(cp.grpc, cp.server)
	listenerservice.RegisterListenerDiscoveryServiceServer(cp.grpc, cp.server)

	return cp, nil
}

func (cp *ControlPlane) Run(listener net.Listener) error {
	cp.listener = listener
	cp.log.Info().Str("addr", listener.Addr().String()).Msg("starting xds control plane")
	return cp.grpc.Serve(listener)
}

func (cp *ControlPlane) Stop() {
	if cp.grpc != nil {
		cp.grpc.GracefulStop()
	}
	if cp.listener != nil {
		_ = cp.listener.Close()
	}
}

func (cp *ControlPlane) PushTopology(ctx context.Context, endpoints []scheduler.Endpoint) (string, error) {
	_, span := cp.tracer.Start(ctx, "xds.push_topology")
	defer span.End()

	version := fmt.Sprintf("%d", cp.versionCounter.Add(1))
	snapshot, err := cp.snapshot(version, endpoints)
	if err != nil {
		return "", err
	}
	if err := snapshot.Consistent(); err != nil {
		return "", err
	}
	if err := cp.cache.SetSnapshot(ctx, cp.config.NodeID, snapshot); err != nil {
		return "", err
	}

	cp.mu.Lock()
	cp.currentVersion = version
	cp.endpoints = cloneEndpoints(endpoints)
	if _, exists := cp.ackWaiters[version]; !exists {
		cp.ackWaiters[version] = make(chan struct{})
	}
	cp.mu.Unlock()

	cp.log.Info().Str("version", version).Int("endpoint_count", len(endpoints)).Msg("xds snapshot pushed")
	return version, nil
}

func (cp *ControlPlane) WaitForAck(ctx context.Context, version string) error {
	cp.mu.Lock()
	ack, exists := cp.ackWaiters[version]
	if !exists {
		ack = make(chan struct{})
		cp.ackWaiters[version] = ack
	}
	cp.mu.Unlock()

	select {
	case <-ctx.Done():
		return ctx.Err()
	case <-ack:
		return nil
	}
}

func (cp *ControlPlane) Acknowledge(version string) {
	cp.mu.Lock()
	defer cp.mu.Unlock()
	cp.lastAckVersion = version
	ack, exists := cp.ackWaiters[version]
	if !exists {
		ack = make(chan struct{})
		close(ack)
		cp.ackWaiters[version] = ack
		return
	}
	select {
	case <-ack:
	default:
		close(ack)
	}
	delete(cp.ackWaiters, version)
	cp.log.Info().Str("version", version).Msg("envoy configuration acknowledged")
}

func (cp *ControlPlane) State() State {
	cp.mu.RLock()
	defer cp.mu.RUnlock()
	return State{
		CurrentVersion: cp.currentVersion,
		LastAckVersion: cp.lastAckVersion,
		NodeID:         cp.config.NodeID,
		Endpoints:      cloneEndpoints(cp.endpoints),
	}
}

func (cp *ControlPlane) OnStreamOpen(_ context.Context, _ int64, _ string) error {
	return nil
}

func (cp *ControlPlane) OnStreamClosed(_ int64, node *core.Node) {
	if node != nil {
		cp.log.Info().Str("node_id", node.GetId()).Msg("xds stream closed")
	}
}

func (cp *ControlPlane) OnStreamRequest(_ int64, req *discoverygrpc.DiscoveryRequest) error {
	if req == nil {
		return nil
	}
	if req.GetVersionInfo() != "" && req.GetResponseNonce() != "" {
		cp.Acknowledge(req.GetVersionInfo())
	}
	return nil
}

func (cp *ControlPlane) OnStreamResponse(_ context.Context, _ int64, _ *discoverygrpc.DiscoveryRequest, _ *discoverygrpc.DiscoveryResponse) {
}

func (cp *ControlPlane) OnFetchRequest(_ context.Context, _ *discoverygrpc.DiscoveryRequest) error {
	return nil
}

func (cp *ControlPlane) OnFetchResponse(*discoverygrpc.DiscoveryRequest, *discoverygrpc.DiscoveryResponse) {
}

func (cp *ControlPlane) OnDeltaStreamOpen(_ context.Context, _ int64, _ string) error {
	return nil
}

func (cp *ControlPlane) OnDeltaStreamClosed(_ int64, _ *core.Node) {
}

func (cp *ControlPlane) OnStreamDeltaRequest(_ int64, _ *discoverygrpc.DeltaDiscoveryRequest) error {
	return nil
}

func (cp *ControlPlane) OnStreamDeltaResponse(_ int64, _ *discoverygrpc.DeltaDiscoveryRequest, _ *discoverygrpc.DeltaDiscoveryResponse) {
}

func (cp *ControlPlane) snapshot(version string, endpoints []scheduler.Endpoint) (*cache.Snapshot, error) {
	resources := make(map[resource.Type][]cachetypes.Resource)
	clusterLoadAssignment := &endpoint.ClusterLoadAssignment{
		ClusterName: cp.config.ClusterName,
		Endpoints: []*endpoint.LocalityLbEndpoints{{
			LbEndpoints: buildLbEndpoints(endpoints),
		}},
	}

	clusterResource := &cluster.Cluster{
		Name:           cp.config.ClusterName,
		ConnectTimeout: durationpb.New(2 * time.Second),
		ClusterDiscoveryType: &cluster.Cluster_Type{
			Type: cluster.Cluster_STATIC,
		},
		LbPolicy:       cluster.Cluster_ROUND_ROBIN,
		LoadAssignment: clusterLoadAssignment,
	}

	routeResource := &route.RouteConfiguration{
		Name: cp.config.RouteName,
		VirtualHosts: []*route.VirtualHost{{
			Name:    "88ck-vhost",
			Domains: []string{"*"},
			Routes: []*route.Route{{
				Match: &route.RouteMatch{
					PathSpecifier: &route.RouteMatch_Prefix{Prefix: "/"},
				},
				Action: &route.Route_Route{
					Route: &route.RouteAction{
						ClusterSpecifier: &route.RouteAction_Cluster{Cluster: cp.config.ClusterName},
					},
				},
			}},
		}},
	}

	routerFilter, err := anypb.New(&router.Router{})
	if err != nil {
		return nil, err
	}
	hcmConfig, err := anypb.New(&hcm.HttpConnectionManager{
		CodecType:  hcm.HttpConnectionManager_AUTO,
		StatPrefix: "88ck_ingress",
		RouteSpecifier: &hcm.HttpConnectionManager_RouteConfig{
			RouteConfig: routeResource,
		},
		HttpFilters: []*hcm.HttpFilter{{
			Name: "envoy.filters.http.router",
			ConfigType: &hcm.HttpFilter_TypedConfig{
				TypedConfig: routerFilter,
			},
		}},
	})
	if err != nil {
		return nil, err
	}

	listenerResource := &listener.Listener{
		Name: cp.config.ListenerName,
		Address: &core.Address{
			Address: &core.Address_SocketAddress{
				SocketAddress: &core.SocketAddress{
					Address: cp.config.ListenAddress,
					PortSpecifier: &core.SocketAddress_PortValue{PortValue: cp.config.ListenPort},
				},
			},
		},
		FilterChains: []*listener.FilterChain{{
			Filters: []*listener.Filter{{
				Name: "envoy.filters.network.http_connection_manager",
				ConfigType: &listener.Filter_TypedConfig{
					TypedConfig: hcmConfig,
				},
			}},
		}},
	}

	resources[resource.EndpointType] = []cachetypes.Resource{clusterLoadAssignment}
	resources[resource.ClusterType] = []cachetypes.Resource{clusterResource}
	resources[resource.RouteType] = []cachetypes.Resource{routeResource}
	resources[resource.ListenerType] = []cachetypes.Resource{listenerResource}

	snapshot, err := cache.NewSnapshot(version, resources)
	if err != nil {
		return nil, err
	}
	return snapshot, nil
}

func buildLbEndpoints(endpoints []scheduler.Endpoint) []*endpoint.LbEndpoint {
	lbEndpoints := make([]*endpoint.LbEndpoint, 0, len(endpoints))
	for _, ep := range endpoints {
		lbEndpoints = append(lbEndpoints, &endpoint.LbEndpoint{
			HostIdentifier: &endpoint.LbEndpoint_Endpoint{
				Endpoint: &endpoint.Endpoint{
					Address: &core.Address{
						Address: &core.Address_SocketAddress{
							SocketAddress: &core.SocketAddress{
								Address: ep.Address,
								PortSpecifier: &core.SocketAddress_PortValue{PortValue: ep.Port},
							},
						},
					},
				},
			},
		})
	}
	return lbEndpoints
}

func cloneEndpoints(endpoints []scheduler.Endpoint) []scheduler.Endpoint {
	cloned := make([]scheduler.Endpoint, len(endpoints))
	copy(cloned, endpoints)
	return cloned
}
