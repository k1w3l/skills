# Chapter 7: Service Discovery

## Core Idea
Kubernetes Services provide stable virtual IPs and DNS names for groups of Pods, solving the dynamic IP problem in a distributed system.

## Frameworks Introduced
- **Service as Virtual IP (ClusterIP)**: a stable virtual IP that load-balances to healthy Pods matching the selector.
  - When to use: Default for internal cluster communication.
- **Service Types Spectrum**: ClusterIP → NodePort → LoadBalancer → ExternalName.
  - How: Choose based on how you need to expose the service.
- **Endpoints Object**: Kubernetes-managed list of Pod IP:port pairs that back a Service; auto-updated as Pods come/go.

## Key Concepts
- **ClusterIP**: virtual IP stable within the cluster; DNS resolves to it.
- **NodePort**: exposes service on a static port on every cluster node; builds on ClusterIP.
- **LoadBalancer**: provisions a cloud load balancer; builds on NodePort; costs cloud resources.
- **ExternalName**: DNS alias for external services; no proxying, just CNAME.
- **Service DNS**: `<service-name>.<namespace>.svc.cluster.local` — full DNS name; short form works within same namespace.
- **kube-dns / CoreDNS**: cluster DNS service; resolves service names for Pods.
- **Headless Service** (`clusterIP: None`): DNS returns individual Pod IPs instead of virtual IP; used for stateful apps.
- **NodePort range**: default 30000–32767.
- **ExternalDNS**: cluster add-on that synchronizes Service IPs with external DNS providers.

## Code Examples
```yaml
apiVersion: v1
kind: Service
metadata:
  name: alpaca-prod
spec:
  selector:
    app: alpaca
    env: prod
  ports:
  - port: 8080
    targetPort: 8080
  type: ClusterIP    # or NodePort, LoadBalancer
```

```bash
# Inspect a service
kubectl get services -o wide
kubectl describe service alpaca-prod

# Manual service endpoint inspection
kubectl get endpoints alpaca-prod

# DNS lookup inside a pod
kubectl exec -it <pod> -- nslookup alpaca-prod.default.svc.cluster.local
```

## Mental Models
- A Service is a stable address for an unstable group of Pods.
- DNS name `<service>.<namespace>` works cluster-wide; just `<service>` works within the same namespace.
- `kube-proxy` on each node rewrites iptables/ipvs rules to forward traffic to actual Pod IPs.

## Anti-patterns
- **port-forwarding to a Service expecting load-balance**: `kubectl port-forward svc/...` routes to ONE pod only.
- **Using Pod IPs directly**: Pod IPs change on restart; always use Service DNS names.
- **LoadBalancer for every internal service**: wastes cloud resources; use ClusterIP + Ingress instead.

## Key Takeaways
1. ClusterIP is the default and correct choice for most internal services.
2. Service DNS format: `<name>.<namespace>.svc.cluster.local` — memorize this.
3. Endpoints object reflects actual healthy Pods; if a Service has no endpoints, check Pod labels.
4. NodePort exposes every cluster node at the same port — fine for dev, not ideal for production.
5. Use LoadBalancer for external-facing production services; pair with Ingress for HTTP.

## Connects To
- **Ch 6**: Labels — selectors are how Services find their Pods.
- **Ch 8**: Ingress — HTTP load balancing built on top of Services.
- **Ch 15**: Service Meshes — advanced networking capabilities beyond basic Services.
