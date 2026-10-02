# Quick Reference Cheatsheet — Kubernetes Up & Running

## Workload Controller Decision Table

| Use case | Controller |
|---|---|
| Long-running stateless service | Deployment |
| Long-running stateful service (DB, cache) | StatefulSet |
| One copy per node (logging, monitoring) | DaemonSet |
| Finite batch task | Job |
| Scheduled recurring task | CronJob |
| Single Pod (rare, non-HA) | Pod (raw) |

---

## Service Type Decision Table

| Need | Service type |
|---|---|
| Internal cluster communication | ClusterIP (default) |
| Expose on node IP for dev/testing | NodePort |
| External-facing with cloud LB | LoadBalancer |
| HTTP multi-host external routing | ClusterIP + Ingress |
| DNS alias for external service | ExternalName |
| StatefulSet peer discovery | Headless (`clusterIP: None`) |

---

## Health Probe Decision Guide

| Probe | Purpose | When it fails |
|---|---|---|
| liveness | Is the container alive? | Restart the container |
| readiness | Is it ready to serve traffic? | Remove from Service endpoints |
| startup | Allow slow-starting containers time | Enable liveness/readiness only after startup completes |

**Rule**: Always set both `liveness` and `readiness`. Use `startup` for slow-initializing apps.

---

## Resource Requests vs Limits

| Field | Effect |
|---|---|
| `resources.requests.cpu` | Scheduler guarantee; bin-packing |
| `resources.requests.memory` | Scheduler guarantee |
| `resources.limits.cpu` | Throttled if exceeded (not killed) |
| `resources.limits.memory` | OOM killed if exceeded |

**Rule**: Always set both requests and limits. QoS class = Guaranteed (req=limit), Burstable (req<limit), BestEffort (none).

---

## Rolling Update Configuration

```yaml
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxSurge: 1          # extra pods above desired (or %)
    maxUnavailable: 1    # pods below desired (or %)
minReadySeconds: 60      # health gate before continuing
```

**Safe defaults**: maxSurge=1, maxUnavailable=0 for zero downtime. minReadySeconds=30–60.

---

## RBAC Built-in Roles (ClusterRoles)

| Role | Scope | Access |
|---|---|---|
| cluster-admin | Cluster | Full access to everything |
| admin | Namespace | Full access within namespace |
| edit | Namespace | Read/write most objects |
| view | Namespace | Read-only |

---

## Label Selector Operators

| Operator | Example | Meaning |
|---|---|---|
| Equality | `app=nginx` | app equals nginx |
| Inequality | `app!=nginx` | app not nginx |
| Set-in | `app in (a,b)` | app is a or b |
| Set-notin | `app notin (a,b)` | app not a or b |
| Exists | `app` | app label is set |
| Not exists | `!app` | app label not set |

---

## Pod Security Quick Reference

| Field | Hardened value |
|---|---|
| `runAsNonRoot` | `true` |
| `allowPrivilegeEscalation` | `false` |
| `readOnlyRootFilesystem` | `true` |
| `capabilities.drop` | `[ALL]` |
| `seccompProfile.type` | `RuntimeDefault` |
| PSA label | `pod-security.kubernetes.io/enforce: restricted` |

---

## ConfigMap/Secret Injection Methods

| Method | Live-reload on update? | Use for |
|---|---|---|
| Volume mount | ✅ Yes (~10s delay) | Config files, certificates |
| Environment variable | ❌ No (restart needed) | Simple key/value |
| CLI argument via env var | ❌ No (restart needed) | App command-line flags |

---

## Common kubectl Debugging Commands

```bash
kubectl describe pod <pod>          # events, conditions, resource info
kubectl logs <pod> -f               # stream logs
kubectl exec -it <pod> -- bash      # shell into container
kubectl get events --watch          # real-time cluster events
kubectl top pods                    # CPU/memory usage
kubectl auth can-i create pods      # test RBAC permission
kubectl rollout status deploy/<n>   # watch rollout progress
kubectl rollout undo deploy/<n>     # rollback to previous version
```

---

## Multicluster Architecture Trade-offs

| Pattern | Simplicity | Efficiency | Flexibility |
|---|---|---|---|
| Replicated silos | ⭐⭐⭐ | ⭐ | ⭐⭐ |
| Regional data sharding | ⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| Microservice routing | ⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
