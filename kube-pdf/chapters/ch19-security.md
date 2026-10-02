# Chapter 19: Securing Applications in Kubernetes

## Core Idea
Kubernetes provides layered security APIs (SecurityContext, Pod Security Admission, network policies) that implement defense-in-depth and least-privilege at the Pod and container level.

## Frameworks Introduced
- **Defense in Depth**: multiple overlapping security controls; no single point of failure. Apply at every layer.
- **Principle of Least Privilege**: workloads access only what they need. Start locked down; add only necessary permissions.
- **SecurityContext Hierarchy**: Pod-level + container-level; container settings override Pod settings.

## Key Concepts
- **SecurityContext**: aggregated security fields at Pod and container level.
  - `runAsNonRoot: true` — refuse to run as root.
  - `runAsUser/runAsGroup` — set UID/GID.
  - `readOnlyRootFilesystem: true` — prevent writes to container filesystem.
  - `allowPrivilegeEscalation: false` — prevent `sudo`-like privilege gain.
  - `capabilities.drop: [ALL]` + `capabilities.add: [NET_BIND_SERVICE]` — minimize Linux capabilities.
- **Pod Security Admission (PSA)**: built-in admission controller enforcing security profiles.
  - Three profiles: `privileged` (no restrictions), `baseline` (prevent known privilege escalations), `restricted` (hardened).
  - Three modes: `enforce` (block), `audit` (log), `warn` (warn but allow).
- **seccomp**: system call filter; `RuntimeDefault` is a safe starting profile.
- **AppArmor**: Linux kernel security module; profile per container.
- **SELinux**: label-based mandatory access control.
- **Network Policy**: whitelist-based firewall for Pod-to-Pod traffic (requires a CNI plugin that supports it).

## Code Examples
```yaml
# Hardened Pod SecurityContext
apiVersion: v1
kind: Pod
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    runAsGroup: 3000
    fsGroup: 2000
    seccompProfile:
      type: RuntimeDefault
  containers:
  - name: app
    image: myapp
    securityContext:
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      capabilities:
        drop: [ALL]
```

```yaml
# NetworkPolicy: default deny all ingress
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-ingress
spec:
  podSelector: {}       # select all pods
  policyTypes: [Ingress]
```

```yaml
# Pod Security Admission namespace label
apiVersion: v1
kind: Namespace
metadata:
  name: my-app
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/warn: restricted
```

## Mental Models
- Start with `restricted` PSA profile; relax only when you understand why it's needed.
- Network policies are additive whitelists; the default is "allow all." Start with deny-all, add rules.
- `readOnlyRootFilesystem: true` forces you to declare all needed writable paths as volumes — good practice.

## Anti-patterns
- **Running containers as root**: any container escape gives the attacker root on the node.
- **No resource limits + privileged containers**: containers can starve neighbors or break out.
- **NetworkPolicy without a supporting CNI**: policy YAML is accepted but not enforced (Calico, Cilium, Weave required).
- **Ignoring PSA warnings**: warnings become errors in future versions; fix now.

## Key Takeaways
1. Always set `runAsNonRoot: true` and `allowPrivilegeEscalation: false` in production Pods.
2. Enable `readOnlyRootFilesystem: true` + explicit writable volume mounts for defense.
3. Drop ALL capabilities; add back only what's strictly needed.
4. Use Pod Security Admission with `enforce: restricted` for production namespaces.
5. NetworkPolicy default-deny-ingress is the right baseline; add ingress rules as needed.

## Connects To
- **Ch 14**: RBAC for API access control; SecurityContext for runtime control.
- **Ch 13**: Secrets encryption at rest.
- **Ch 17**: Admission controllers enforce security policies.
