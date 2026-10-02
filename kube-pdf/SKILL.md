---
name: kube-pdf
description: "Knowledge base from \"Kubernetes Up & Running, 3rd Edition\" by Kelsey Hightower, Brendan Burns & Joe Beda. Use when applying Kubernetes frameworks for container orchestration, cluster management, workload controllers (Pods, Deployments, StatefulSets, DaemonSets, Jobs), networking (Services, Ingress), RBAC, storage, security, extending Kubernetes, or organizing cloud native applications."
allowed-tools:
  - Read
  - Grep
argument-hint: [topic, chapter number, or concept name]
---

# Kubernetes Up & Running, 3rd Edition
**Authors**: Kelsey Hightower, Brendan Burns & Joe Beda | **Pages**: ~329 | **Chapters**: 22 | **Generated**: 2026-05-28

## How to Use This Skill

- **Without arguments** — load core frameworks for reference
- **With a topic** — ask about `deployments`, `rbac`, `storage`, or any indexed topic; I find and read the relevant chapter
- **With chapter** — ask for `ch05` or `chapter 5`; I load that chapter
- **Browse** — ask "what chapters do you have?" to see the full index

When you ask about a topic not in the Core Frameworks below, I read the relevant chapter file first.

---

## Core Frameworks & Mental Models

### The Five Benefits of Kubernetes (Ch 1)
Use Kubernetes for: **velocity** (immutability + self-healing), **scaling** (declarative replicas + HPA), **infrastructure abstraction** (portable APIs), **efficiency** (bin-packing + shared clusters), **cloud native ecosystem** (CNCF).

### Immutable Infrastructure + Declarative Configuration (Ch 1)
- **Immutability**: build new container images instead of modifying running containers. Old images remain for rollback.
- **Declarative**: describe desired state in YAML; Kubernetes reconciles actual → desired continuously.
- **GitOps**: git is the source of truth; cluster is read-only; all changes via reviewed PRs.
- Anti-pattern: `kubectl edit` in production without updating source control.

### Reconciliation Loop (Ch 9)
Every controller: observe desired state → observe actual state → take action → repeat. Goal-driven, self-healing. This is how ReplicaSets, Deployments, DaemonSets, and all operators work.

### Workload Controller Selection
| Use case | Controller |
|---|---|
| Stateless service, rolling updates | **Deployment** (Ch 10) |
| One copy per node (agents, daemons) | **DaemonSet** (Ch 11) |
| Stable identity, ordered scaling (DB) | **StatefulSet** (Ch 16) |
| Finite batch task | **Job** (Ch 12) |
| Scheduled recurring task | **CronJob** (Ch 12) |

### Pods: The Fundamental Unit (Ch 5)
- Always set **liveness + readiness probes** — no probes means K8s can't detect broken pods.
- Always set **resource requests** (scheduling) **and limits** (isolation). No requests = bad scheduling. No limits = noisy neighbor.
- **Sidecar pattern**: tight co-location on localhost; different resource/restart needs (nginx + git-sync).

### Services & Service Discovery (Ch 7)
- **ClusterIP** (default): stable virtual IP + DNS for internal communication.
- **Service DNS**: `<service>.<namespace>.svc.cluster.local` — memorize this format.
- **Ingress** (Ch 8): HTTP virtual hosting — one IP serves multiple services via hostname/path routing. Requires a separately installed controller (NGINX, Contour, Traefik).

### Labels: The Kubernetes Nervous System (Ch 6)
Labels wire everything together: Services → Pods, ReplicaSets → Pods, DaemonSets → Nodes.
- Rule: if you'll ever filter/select by it → **label**. Otherwise → **annotation**.
- Annotations: build metadata, rollout tracking, tool configuration.

### Deployments & Rolling Updates (Ch 10)
```yaml
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxSurge: 1          # extra pods above desired
    maxUnavailable: 0    # zero downtime
minReadySeconds: 60      # health gate
```
- `kubectl rollout pause` → deploy 10% → observe → `kubectl rollout resume` = manual canary.
- `kubectl rollout undo` = instant rollback to previous ReplicaSet.

### RBAC: Identity → Role → Binding (Ch 14)
- **Least privilege**: set up RBAC from day one. Retrofitting is expensive.
- `Role`/`RoleBinding` = namespace scope. `ClusterRole`/`ClusterRoleBinding` = cluster-wide.
- Use **group bindings** over individual user bindings for scalability.
- Test with: `kubectl auth can-i create pods`.

### ConfigMaps & Secrets (Ch 13)
- Volume-mounted: **auto-updated** in pods (~10s delay). Env vars: **require pod restart**.
- Never commit Secret YAML to git — base64 is not encryption. Use Sealed Secrets, Vault, or cloud KMS.
- `imagePullSecrets` on the default ServiceAccount = credentials for all pods in the namespace.

### Security Hardening (Ch 19)
Minimum secure Pod settings:
```yaml
securityContext:
  runAsNonRoot: true
  allowPrivilegeEscalation: false
  readOnlyRootFilesystem: true
  capabilities:
    drop: [ALL]
  seccompProfile:
    type: RuntimeDefault
```
NetworkPolicy default-deny + explicit allow = correct baseline.

### Extending Kubernetes: Three CRD Patterns (Ch 17)
1. **Just Data**: store config in API; no controller. Simplest.
2. **Compiler**: CRD compiled to lower-level K8s objects by a controller.
3. **Operator**: CRD + controller + active lifecycle management (health, backup, upgrade). Most powerful.

### Application Organization (Ch 22)
Three principles:
1. **Filesystem = source of truth**: git is authoritative; cluster is a projection.
2. **Code review all config changes**: most outages come from config mistakes.
3. **Feature flags**: new features off by default; activation via config change.

Release progression: HEAD → development → staging → canary → release.

### Multicluster Architectures (Ch 21)
Fix single-cluster foundations first (automation, identity, RBAC, policy). Then choose:
- **Replicated silos**: simplest, over-provisioned in small regions.
- **Regional sharding**: efficient, adds routing complexity.
- **Microservice routing**: most flexible, highest operational cost.

---

## Chapter Index

| # | Title | Key Frameworks |
|---|---|---|
| [ch01](chapters/ch01-introduction.md) | Introduction | immutability, declarative config, GitOps, five benefits |
| [ch02](chapters/ch02-containers.md) | Creating and Running Containers | container layering, multistage builds, image security |
| [ch03](chapters/ch03-cluster-setup.md) | Deploying a Kubernetes Cluster | GKE/EKS/AKS, kind, minikube, control plane components |
| [ch04](chapters/ch04-kubectl.md) | Common kubectl Commands | namespaces, contexts, apply/delete, debugging |
| [ch05](chapters/ch05-pods.md) | Pods | liveness/readiness probes, resources, sidecars, init containers |
| [ch06](chapters/ch06-labels.md) | Labels and Annotations | label selectors, operator syntax, annotations vs labels |
| [ch07](chapters/ch07-service-discovery.md) | Service Discovery | ClusterIP, NodePort, LoadBalancer, DNS, headless services |
| [ch08](chapters/ch08-ingress.md) | HTTP Load Balancing with Ingress | virtual hosting, path routing, TLS, cert-manager, Gateway API |
| [ch09](chapters/ch09-replicasets.md) | ReplicaSets | reconciliation loop, HPA, quarantine debugging |
| [ch10](chapters/ch10-deployments.md) | Deployments | rolling updates, canary, rollback, maxSurge/maxUnavailable |
| [ch11](chapters/ch11-daemonsets.md) | DaemonSets | node agents, node selectors, rolling updates |
| [ch12](chapters/ch12-jobs.md) | Jobs | one-shot, parallel, work queue, CronJobs |
| [ch13](chapters/ch13-configmaps-secrets.md) | ConfigMaps and Secrets | injection methods, live updates, security |
| [ch14](chapters/ch14-rbac.md) | RBAC | identity, roles, bindings, group-based access, least privilege |
| [ch15](chapters/ch15-service-meshes.md) | Service Meshes | mTLS, traffic shaping, observability, when NOT to use |
| [ch16](chapters/ch16-storage.md) | Integrating Storage | PV/PVC, StatefulSets, StorageClass, dynamic provisioning |
| [ch17](chapters/ch17-extending-kubernetes.md) | Extending Kubernetes | CRDs, admission controllers, operators, Kubebuilder |
| [ch18](chapters/ch18-programming-api.md) | Accessing Kubernetes from Code | Python/Java/.NET clients, watch API, exec, port-forward |
| [ch19](chapters/ch19-security.md) | Securing Applications | SecurityContext, Pod Security Admission, NetworkPolicy |
| [ch20](chapters/ch20-policy-governance.md) | Policy and Governance | OPA/Gatekeeper, Kyverno, policy-as-code |
| [ch21](chapters/ch21-multicluster.md) | Multicluster Deployments | replicated silos, sharding, microservice routing, GeoDNS |
| [ch22](chapters/ch22-organizing-application.md) | Organizing Your Application | filesystem source of truth, Helm, feature flags, release stages |

## Topic Index

- **admission controller** → ch17, ch19, ch20
- **annotations** → ch06
- **anycast** → ch21
- **canary deployment** → ch10, ch15
- **cert-manager** → ch08
- **ClusterIP / Service** → ch07
- **ConfigMap** → ch13
- **CronJob** → ch12
- **CRD / CustomResourceDefinition** → ch17
- **DaemonSet** → ch11
- **Deployment** → ch10
- **feature flags** → ch22
- **Gatekeeper / OPA** → ch20
- **GitOps** → ch01, ch22
- **Helm** → ch22
- **HPA / Horizontal Pod Autoscaling** → ch09
- **Ingress** → ch08
- **Jobs** → ch12
- **kubectl** → ch04
- **labels / selectors** → ch06
- **liveness probe / readiness probe** → ch05
- **multicluster** → ch21
- **mTLS** → ch15
- **NetworkPolicy** → ch19
- **operator pattern** → ch17
- **PersistentVolume / PVC** → ch16
- **Pods** → ch05
- **RBAC** → ch14
- **reconciliation loop** → ch09
- **ReplicaSet** → ch09
- **resource requests / limits** → ch05
- **rolling update** → ch10
- **Secrets** → ch13
- **SecurityContext** → ch19
- **service discovery** → ch07
- **service mesh** → ch15
- **sidecar** → ch05, ch15
- **StatefulSet** → ch16
- **StorageClass** → ch16

## Supporting Files

- [glossary.md](glossary.md) — all key terms with definitions
- [patterns.md](patterns.md) — all techniques and design patterns
- [cheatsheet.md](cheatsheet.md) — quick reference tables and decision guides

---

## Scope & Limits

This skill covers the book content only. For hands-on implementation in your codebase, combine with project-specific tools. For topics beyond this book (specific Helm charts, cloud-provider specifics, very recent Kubernetes versions), verify against current documentation.
