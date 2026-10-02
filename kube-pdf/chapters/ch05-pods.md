# Chapter 5: Pods

## Core Idea
A Pod is the smallest deployable unit in Kubernetes — one or more containers sharing network namespace, storage volumes, and lifecycle, co-scheduled on the same node.

## Frameworks Introduced
- **Sidecar Pattern**: secondary container in the same Pod augmenting the primary (e.g., git-sync alongside nginx).
  - When to use: Tight coupling needed (shared localhost), but containers have different resource needs or restart policies.
- **Health Check Trifecta**: liveness + readiness + startup probes guard pod reliability.
  - Liveness: is the container alive? Restart if not.
  - Readiness: is the container ready to serve traffic? Remove from Service endpoints if not.
  - Startup: allow slow-starting containers extra time before liveness kicks in.
- **Resource Requests vs Limits**: requests = scheduling guarantee; limits = enforcement ceiling.
  - When to use: Always set both. Requests for bin-packing; limits for noisy-neighbor protection.

## Key Concepts
- **Pod Manifest**: YAML/JSON specification submitted to the API server; immutable after creation (except some fields).
- **Init Containers**: run to completion before app containers start; sequential; used for setup/initialization.
- **Volume**: storage associated with Pod lifetime (not container); survives container restarts.
- **emptyDir**: ephemeral volume; lives as long as the Pod.
- **hostPath**: mounts a directory from the node's filesystem (use with caution).
- **nodeName**: field that pins a Pod to a specific node (set by scheduler).
- **QoS Classes**: Guaranteed (req=limit), Burstable (req<limit), BestEffort (no req/limit).

## Code Examples
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: kuard
spec:
  containers:
  - name: kuard
    image: gcr.io/kuar-demo/kuard-amd64:blue
    resources:
      requests:
        cpu: "500m"
        memory: "128Mi"
      limits:
        cpu: "1000m"
        memory: "256Mi"
    livenessProbe:
      httpGet:
        path: /healthy
        port: 8080
      initialDelaySeconds: 5
      timeoutSeconds: 1
      periodSeconds: 10
      failureThreshold: 3
    readinessProbe:
      httpGet:
        path: /ready
        port: 8080
      initialDelaySeconds: 30
      timeoutSeconds: 5
```

## Mental Models
- Use the same Pod manifest for readiness and liveness probes, but with different endpoints.
- Think of resource requests as the Pod's "reservation" and limits as the "ceiling."
- If a Pod has multiple containers, ALL containers share the same IP and localhost.

## Anti-patterns
- **No health probes**: Kubernetes doesn't know when your app is broken; traffic goes to broken pods.
- **No resource requests**: scheduler can't make good placement decisions; noisy neighbors steal resources.
- **Too many containers in one Pod**: if they don't need shared localhost or volumes, use separate Pods.
- **Limits without requests**: setting only limits causes inefficient scheduling.

## Key Takeaways
1. Always define both liveness and readiness probes for production workloads.
2. Always set resource requests (for scheduling) and limits (for isolation).
3. Sidecars share network namespace — they communicate over localhost.
4. Init containers run sequentially to completion before app containers start.
5. Prefer Deployments over raw Pods for any long-running workload.

## Connects To
- **Ch 9**: ReplicaSets manage sets of identical Pods.
- **Ch 10**: Deployments manage rollouts of ReplicaSets.
- **Ch 13**: ConfigMaps/Secrets mounted as volumes or environment variables.
