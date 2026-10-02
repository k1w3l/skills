# Chapter 9: ReplicaSets

## Core Idea
A ReplicaSet is the cluster-wide Pod manager — it continuously reconciles desired replica count with actual, using label selectors to identify its Pods.

## Frameworks Introduced
- **Reconciliation Loop**: observe desired state → observe current state → take action to make them match. Repeat forever.
  - When to use: Foundational pattern for all controllers in Kubernetes.
- **Decoupled Ownership via Labels**: ReplicaSets don't own Pods; they find them via labels.
  - Benefit: Quarantine a misbehaving Pod by removing its label — it exits the ReplicaSet while remaining for debugging.
- **Horizontal Pod Autoscaling (HPA)**: automatically adjusts replica count based on CPU/memory/custom metrics.
  - When to use: Variable load services; combine with requests-based resource settings.

## Key Concepts
- **Desired State**: what you declare in spec.replicas.
- **Observed State**: current number of running Pods matching the selector.
- **Pod Template**: cookie-cutter for creating new Pods when count is below desired.
- **ownerReferences**: metadata field on Pods set by the ReplicaSet controller; enables reverse lookup.
- **metrics-server**: required for HPA to work; query with `kubectl top pods`.

## Code Examples
```yaml
apiVersion: apps/v1
kind: ReplicaSet
metadata:
  name: kuard
spec:
  replicas: 3
  selector:
    matchLabels:
      app: kuard
      version: "2"
  template:
    metadata:
      labels:
        app: kuard
        version: "2"
    spec:
      containers:
      - name: kuard
        image: gcr.io/kuar-demo/kuard-amd64:green
```

```bash
# Scaling
kubectl scale replicasets kuard --replicas=4          # imperative (update YAML too!)
kubectl apply -f kuard-rs.yaml                         # declarative (preferred)
kubectl autoscale rs kuard --min=2 --max=5 --cpu-percent=80

# Inspection
kubectl describe rs kuard
kubectl get pods -l app=kuard,version=2
kubectl get pods <pod-name> -o=jsonpath='{.metadata.ownerReferences[0].name}'
kubectl get hpa

# Delete without deleting pods
kubectl delete rs kuard --cascade=false
```

## Mental Models
- ReplicaSet = desired count + cookie cutter + label selector.
- Use quarantine debugging: change a pod's label → ReplicaSet creates replacement, sick pod stays for inspection.
- Don't combine HPA with manual replica scaling — they'll conflict.

## Anti-patterns
- **Imperative scaling without updating YAML**: Alice scales to 10 in an emergency; Bob's rollout reverts to 5. Use declarative changes to source control.
- **ReplicaSet directly in production**: use Deployments for rollout management. ReplicaSets are lower-level building blocks.
- **Mixing HPA and manual replicas**: undefined/conflicting behavior.

## Key Takeaways
1. The reconciliation loop is self-healing: it acts on node failures, not just desired-state changes.
2. Label selectors must be a subset of Pod template labels — otherwise the RS won't find its Pods.
3. Always prefer declarative scaling via `kubectl apply` over `kubectl scale`.
4. HPA requires metrics-server; scale based on CPU for request-processing services.
5. Delete with `--cascade=false` to preserve Pods when removing the RS.

## Connects To
- **Ch 10**: Deployments manage ReplicaSets for rolling updates.
- **Ch 6**: Labels — the selector is how RS finds and adopts Pods.
- **Ch 5**: Pod spec lives inside the RS template.
