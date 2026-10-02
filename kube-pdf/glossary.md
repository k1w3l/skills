# Glossary — Kubernetes Up & Running, 3rd Edition

**admission controller** — component that intercepts API requests before persistence; can reject or modify objects (Ch 17)

**anycast** — network routing where a single IP is advertised from multiple locations; routes to nearest endpoint (Ch 21)

**AppArmor** — Linux kernel security module; per-container security profiles (Ch 19)

**ClusterIP** — default Service type; virtual IP stable within the cluster (Ch 7)

**ClusterRole** — cluster-scoped RBAC role (vs namespace-scoped Role) (Ch 14)

**ClusterRoleBinding** — cluster-scoped RBAC role assignment (Ch 14)

**ConfigMap** — Kubernetes object storing non-sensitive configuration key/value pairs (Ch 13)

**Container Runtime Interface (CRI)** — standard API between Kubernetes and container runtimes (Ch 2)

**ConstraintTemplate** — Gatekeeper CRD defining a policy; instances called Constraints (Ch 20)

**containerd** — standard container runtime; used by Docker and Kubernetes (Ch 2)

**control plane** — Kubernetes components managing the cluster: API server, scheduler, controller-manager, etcd (Ch 3)

**CoreDNS** — DNS server running as a Kubernetes deployment; provides service name resolution (Ch 3)

**CronJob** — Kubernetes object scheduling Jobs at a cron interval (Ch 12)

**CustomResourceDefinition (CRD)** — meta-resource defining a new Kubernetes API type (Ch 17)

**DaemonSet** — ensures exactly one Pod runs on every (or a subset of) node(s) (Ch 11)

**declarative configuration** — describing desired state; Kubernetes reconciles actual → desired (Ch 1)

**defense in depth** — multiple overlapping security controls; no single point of failure (Ch 19)

**Deployment** — manages rolling updates of ReplicaSets; the standard primitive for stateless services (Ch 10)

**emptyDir** — ephemeral Pod volume; survives container restarts, deleted with Pod (Ch 5)

**Endpoints** — Kubernetes-managed list of Pod IP:ports backing a Service (Ch 7)

**etcd** — distributed key-value store; stores all cluster state (Ch 3)

**eventual consistency** — writes always succeed; replication happens later; lower cost but stale reads possible (Ch 21)

**ExternalDNS** — cluster add-on that syncs Service IPs with external DNS providers (Ch 7)

**ExternalName** — Service type that creates a DNS alias for an external service (Ch 7)

**feature flag / feature gate** — code path hidden behind a boolean; activation via config change (Ch 22)

**Gatekeeper** — Kubernetes-native OPA integration using CRDs for policy enforcement (Ch 20)

**GeoDNS** — routing based on client geography via different DNS responses (Ch 21)

**GitOps** — production changes via git push only; cluster is read-only (Ch 1)

**headless Service** — Service with `clusterIP: None`; DNS returns individual Pod IPs (Ch 16)

**Helm** — package manager for Kubernetes; mustache template + values files (Ch 22)

**Horizontal Pod Autoscaler (HPA)** — automatically adjusts replica count based on metrics (Ch 9)

**hostPath** — volume mounting a directory from the node's filesystem into a Pod (Ch 5)

**imagePullSecrets** — Pod field referencing docker-registry Secrets for private registries (Ch 13)

**immutable infrastructure** — artifacts never modified after creation; changes produce new artifacts (Ch 1)

**init container** — container running to completion before app containers start; used for setup (Ch 5)

**Ingress** — HTTP load-balancing schema; routes traffic via host/path rules to Services (Ch 8)

**IngressClass** — specifies which Ingress controller implementation handles an Ingress object (Ch 8)

**Job** — manages batch workloads running to successful completion (Ch 12)

**Kubebuilder** — framework for building Kubernetes API extensions and operators (Ch 17)

**kubectl** — official CLI for the Kubernetes API (Ch 4)

**kubeconfig** — file storing cluster connection and auth info; default at `~/.kube/config` (Ch 4, 18)

**kube-proxy** — DaemonSet on every node routing traffic to Service endpoints (Ch 3)

**label** — key/value pair for identifying information; used in selectors (Ch 6)

**label selector** — Boolean expression filtering objects by labels (Ch 6)

**liveness probe** — health check to determine if a container is alive; triggers restart if failed (Ch 5)

**LoadBalancer** — Service type provisioning a cloud load balancer (Ch 7)

**matchExpressions** — rich selector syntax supporting In, NotIn, Exists operators (Ch 6)

**matchLabels** — simple equality selector in spec (Ch 6)

**maxSurge** — max Pods above desired count during a rolling update (Ch 10)

**maxUnavailable** — max Pods below desired count during a rolling update (Ch 10)

**minReadySeconds** — time a new Pod must be healthy before rollout proceeds (Ch 10)

**mTLS (Mutual TLS)** — encrypts Pod-to-Pod traffic and authenticates both endpoints (Ch 15)

**namespace** — logical folder organizing objects in a cluster (Ch 4)

**NetworkPolicy** — whitelist-based firewall for Pod-to-Pod traffic (Ch 19)

**NodePort** — Service type exposing a static port on every cluster node (Ch 7)

**OCI (Open Container Initiative)** — image format standard (Ch 2)

**operator** — CRD + controller with active lifecycle management (backups, health, upgrades) (Ch 17)

**OPA (Open Policy Agent)** — general-purpose policy engine; policies in Rego (Ch 20)

**ownerReferences** — metadata field on Pods set by controllers; enables reverse lookup (Ch 9)

**PersistentVolume (PV)** — cluster-level storage resource (Ch 16)

**PersistentVolumeClaim (PVC)** — namespace-level storage request by a workload (Ch 16)

**Pod** — smallest deployable unit; one or more containers sharing network and storage (Ch 5)

**Pod Security Admission (PSA)** — built-in admission controller enforcing `privileged`/`baseline`/`restricted` profiles (Ch 19)

**readiness probe** — health check determining if a container is ready to serve traffic (Ch 5)

**reconciliation loop** — continuously observe desired state → take action to match actual state (Ch 9)

**ReplicaSet** — cluster-wide Pod manager; maintains desired replica count via label selectors (Ch 9)

**Role** — namespace-scoped RBAC capabilities object (Ch 14)

**RoleBinding** — assigns a Role to identities within a namespace (Ch 14)

**seccomp** — Linux system call filter; `RuntimeDefault` is a safe profile (Ch 19)

**Secret** — Kubernetes object storing sensitive data (base64-encoded); stored on tmpfs (Ch 13)

**SecurityContext** — aggregated security fields at Pod and container level (Ch 19)

**service account** — machine identity for Pods/components inside the cluster (Ch 14)

**service mesh** — infrastructure layer adding mTLS, traffic shaping, and observability (Ch 15)

**sidecar** — secondary container in the same Pod augmenting the primary (Ch 5, 15)

**StatefulSet** — manages Pods with stable network identity and ordered deployment (Ch 16)

**StorageClass** — defines a storage provisioner; enables dynamic PV provisioning (Ch 16)

**strong consistency** — writes don't succeed until replicated; higher cost, fewer TPS (Ch 21)

**two-pizza team** — ~6–8 person team size; ideal for microservice ownership (Ch 1)

**ValidatingWebhookConfiguration** — registers an HTTP endpoint as a validating admission controller (Ch 17)

**volumeClaimTemplates** — StatefulSet field that auto-creates a PVC per Pod replica (Ch 16)

**worker node** — cluster node where user Pods run (Ch 3)
