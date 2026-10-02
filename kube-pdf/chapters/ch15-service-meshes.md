# Chapter 15: Service Meshes

## Core Idea
Service meshes provide mTLS encryption, traffic shaping (canary/A-B testing), and distributed tracing for inter-Pod communication — but add operational complexity; use only when the benefits justify the cost.

## Frameworks Introduced
- **Three Service Mesh Capabilities**: encryption (mTLS), traffic shaping (experiments), introspection (request tracing).
  - When to use: Need any two of the three at cluster scale; not for small/simple apps.
- **Sidecar Proxy Pattern**: a proxy container injected into every Pod transparently intercepts all traffic.
  - How: Mutating admission controller auto-injects the sidecar; no app code changes needed.

## Key Concepts
- **mTLS (Mutual TLS)**: encrypts pod-to-pod traffic AND authenticates both endpoints using client certificates.
- **Traffic Shaping**: route X% of traffic to version A, Y% to version B — declarative canary/A-B testing.
- **Introspection**: distributed request tracing across services; single request view spanning multiple Pods.
- **Mutating Admission Controller**: auto-injects sidecar container into all Pods; requires cluster-admin.
- **Service Mesh Interface (SMI)**: CNCF effort to standardize service mesh APIs across implementations.
- **Popular Implementations**: Istio (most popular), Linkerd, Consul Connect, AWS App Mesh.
- **eBPF**: newer approach replacing iptables for sidecar traffic interception; less overhead.

## Mental Models
- Service mesh = infrastructure for infrastructure concerns: security, observability, experimentation.
- The sidecar IS the mesh for that Pod — when it fails, that Pod loses mesh capabilities (or worse, can't communicate).
- Best service mesh = the one your cloud provider manages. Avoid self-managing unless at large scale.

## Anti-patterns
- **Installing a service mesh "just in case"**: adds operational complexity, potential outage vector. Only add when benefits are clear.
- **Mixing service mesh with existing mTLS implementations**: double-encryption, confused certificate management.
- **Not monitoring service mesh software releases**: security patches need fast rollout; mesh is deep in your stack.

## Key Takeaways
1. A service mesh is optional and often unnecessary for small/simple applications.
2. Use a cloud-managed service mesh when available — operational burden is on the provider.
3. Service mesh adds a potential outage vector; only adopt when team can operate it reliably.
4. All major meshes add sidecars via mutating admission controllers — transparent to app code.
5. SMI (Service Mesh Interface) aims to standardize APIs; still evolving.

## Connects To
- **Ch 8**: Service meshes extend Ingress capabilities for within-cluster routing.
- **Ch 14**: Service mesh admission controllers require cluster-admin RBAC.
- **Ch 17**: Service mesh configs are CRDs — same extensibility mechanism.
