# Patterns & Techniques — Kubernetes Up & Running, 3rd Edition

## Sidecar Pattern
**When to use**: Two containers are tightly coupled (share localhost/volumes), but have different resource needs, restart policies, or concerns (e.g., nginx + git-sync).  
**How**: Add both containers to the same Pod spec. They share network namespace and can declare separate volumeMounts.  
**Trade-offs**: Couples lifecycle of both containers. If either crashes, Pod restarts. Use only for genuine co-location needs.

---

## Multistage Docker Build
**When to use**: Compiled languages (Go, Java, .NET, Rust) or any case where build tooling must not ship in the final image.  
**How**: `FROM <build-image> AS build` → build artifact → `FROM <runtime-image>` + `COPY --from=build`.  
**Trade-offs**: Slightly more complex Dockerfile; dramatically smaller, more secure final images.

---

## Reconciliation Loop (Controller Pattern)
**When to use**: Building any Kubernetes controller or operator; understanding why Kubernetes behaves as it does.  
**How**: 1) List desired state. 2) List observed state. 3) Compute diff. 4) Take action. 5) Repeat.  
**Trade-offs**: Eventually consistent — actions may lag slightly; don't design for exactly-once semantics without careful thought.

---

## Label Selector Wiring
**When to use**: Connecting Services, ReplicaSets, DaemonSets to their Pods.  
**How**: Set labels on Pod template; set matching selector on controller/service. Label selector is the ONLY relationship.  
**Trade-offs**: Loose coupling (good for flexibility) means misconfigured selectors silently result in no targets.

---

## Rolling Deployment with Health Gate
**When to use**: Zero-downtime updates for stateless services.  
**How**: Set `strategy.type: RollingUpdate`, configure `maxSurge`/`maxUnavailable`, set `minReadySeconds` to at least 30s.  
**Trade-offs**: Slower rollout than Recreate; both versions run simultaneously (ensure backward compatibility).

---

## Pause/Resume Canary with Deployment
**When to use**: Manual canary deployment without a service mesh.  
**How**: Begin rolling update → `kubectl rollout pause` (10% new version running) → observe → `kubectl rollout resume` or `kubectl rollout undo`.  
**Trade-offs**: Binary traffic split (can't send 5% to new version); requires coordination; service mesh is better for precise traffic shaping.

---

## Pod Quarantine Debugging
**When to use**: A Pod is misbehaving but you need it running for interactive debugging.  
**How**: Remove or change the Pod's labels that match the ReplicaSet selector. RS creates replacement; sick Pod stays alive for debugging.  
**Trade-offs**: Temporary workaround; must clean up manually; ReplicaSet creates a new Pod immediately.

---

## Headless Service for StatefulSets
**When to use**: StatefulSet members need to discover each other (databases, caches forming clusters).  
**How**: Create a Service with `clusterIP: None` and the same selector. DNS resolves `pod-0.service.namespace` to that Pod's IP.  
**Trade-offs**: No load balancing; clients must handle connection to individual members.

---

## ConfigMap/Secret Live Reload
**When to use**: Application supports config reload without restart (NGINX, Prometheus, etc.).  
**How**: Mount ConfigMap/Secret as a volume. K8s auto-updates files when CM/Secret changes. App watches for changes and reloads.  
**Trade-offs**: Small delay (~10s) before update propagates. Env vars require Pod restart. Application must support reload.

---

## RBAC Aggregation Pattern
**When to use**: Building layered permission sets (e.g., edit role extends view role).  
**How**: Use `aggregationRule.clusterRoleSelectors` with label selectors. Add label to sub-roles to include them.  
**Trade-offs**: Dynamic aggregation means adding a label to any ClusterRole adds it to the aggregate — label your roles carefully.

---

## Operator Pattern (CRD + Controller + Health Management)
**When to use**: Complex stateful software (databases, message queues) that needs lifecycle management (backup, restore, upgrade, health remediation).  
**How**: Define CRD for your resource type → implement controller that watches and acts → add health monitoring/remediation logic.  
**Trade-offs**: Significant implementation investment; excellent user experience once built. Use Kubebuilder to bootstrap.

---

## Job Work Queue Pattern
**When to use**: Processing items from a queue with multiple parallel workers.  
**How**: Set `parallelism` (N workers) but leave `completions` unset. Job ends when one Pod exits zero (the queue is empty signal).  
**Trade-offs**: Requires an external queue service; workers must signal "queue empty" by exiting 0.

---

## Parameterized Environments with Helm
**When to use**: Same application deployed to multiple environments (dev/staging/prod) with minor differences.  
**How**: Helm templates with `{{ .Values.* }}` placeholders + per-environment `values.yaml` files.  
**Trade-offs**: Adds Helm as a dependency; templates can become complex; Helm chart versioning requires discipline.

---

## NetworkPolicy Default-Deny
**When to use**: Production clusters requiring network isolation between services.  
**How**: Create a NetworkPolicy with `podSelector: {}` (all pods) and `policyTypes: [Ingress]` (no rules = deny all). Then add explicit allow rules per service.  
**Trade-offs**: Requires CNI plugin support (Calico, Cilium, etc.); start in audit mode to understand current traffic before enforcing.

---

## Replicated Silos (Multicluster)
**When to use**: Starting point for multicluster deployments; application with mostly stateless services.  
**How**: Deploy identical application to each region. Add global load balancer (GeoDNS or anycast) at top. Replicate state (or use strong consistency storage).  
**Trade-offs**: Simple to implement; over-provisioned in small regions; not flexible for per-service scaling.
