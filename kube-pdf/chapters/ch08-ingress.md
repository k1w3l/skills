# Chapter 8: HTTP Load Balancing with Ingress

## Core Idea
Ingress implements virtual hosting for HTTP/HTTPS — routing traffic to multiple services based on hostname and path from a single IP, avoiding the cost of per-service cloud load balancers.

## Frameworks Introduced
- **Virtual Hosting Pattern**: single IP/LB routes traffic to different upstream services based on HTTP Host header and URL path.
  - When to use: Multiple HTTP services that need to share an external IP/domain.
- **Ingress Controller Architecture**: Ingress proxy (load balancer) + Ingress reconciler (operator) watching the API.
  - Key: The controller is NOT built into Kubernetes — you install it separately (Contour, NGINX, Traefik, etc.).

## Key Concepts
- **Ingress object**: declarative routing rules (host, path → Service).
- **IngressClass**: specifies which Ingress controller handles the object; use `spec.ingressClassName`.
- **Default backend**: where unmatched traffic goes.
- **Longest prefix match**: when multiple paths match, the most specific one wins.
- **Path rewriting**: some controllers rewrite the path before proxying upstream (use carefully).
- **TLS termination**: Ingress can terminate TLS using a Secret with `tls.crt` and `tls.key`.
- **cert-manager**: CNCF project for automatic TLS certificate management via Let's Encrypt.
- **Gateway API**: future replacement for Ingress (still in development); more expressive routing.

## Code Examples
```yaml
# Host-based routing
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: host-ingress
spec:
  defaultBackend:
    service:
      name: be-default
      port:
        number: 8080
  rules:
  - host: alpaca.example.com
    http:
      paths:
      - pathType: Prefix
        path: /
        backend:
          service:
            name: alpaca
            port:
              number: 8080
```

```yaml
# TLS termination
spec:
  tls:
  - hosts:
    - alpaca.example.com
    secretName: tls-secret-name
  rules:
  - host: alpaca.example.com
    ...
```

## Mental Models
- Ingress is a schema + pluggable implementation. Installing Ingress CRDs without an Ingress controller does nothing.
- Longest prefix wins: `/a/` beats `/` for request `/a/foo`.
- Ingress can only reference Services in its own namespace.

## Anti-patterns
- **Multiple conflicting Ingress objects**: undefined behavior if same host+path in multiple objects.
- **Subpaths for complex apps**: apps linking with absolute paths break when served from a subpath; avoid unless you control the app.
- **Modifying built-in ClusterRole resources**: they'll be overwritten on API server restart.

## Key Takeaways
1. Ingress requires a separately installed controller — it's just a schema by itself.
2. Use `spec.ingressClassName` to target a specific controller when multiple exist.
3. Path routing uses longest-prefix matching; order rules from most to least specific.
4. TLS: create a `kubernetes.io/tls` Secret with cert and key, reference in Ingress spec.
5. cert-manager automates TLS certificate rotation; strongly recommended for production.

## Connects To
- **Ch 7**: Services are the upstream backends for Ingress rules.
- **Ch 15**: Service meshes provide more advanced HTTP routing within the cluster.
- **Ch 17**: Gateway API is the future of Ingress (CRD-based extensibility).
