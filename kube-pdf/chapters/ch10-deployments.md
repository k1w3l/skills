# Chapter 10: Deployments

## Core Idea
Deployments manage the release lifecycle of applications — they orchestrate rolling updates between versions by creating and managing ReplicaSets, with configurable rollout strategies, rollbacks, and health-gated progression.

## Frameworks Introduced
- **Rolling Update Strategy**: gradually replace Pods from old ReplicaSet with new, controlling pace via maxSurge and maxUnavailable.
  - When to use: Zero-downtime deployments for stateless services.
  - How: Update the container image in the Deployment spec; controller manages the ReplicaSet transition.
- **Recreate Strategy**: delete all old Pods, then create new ones. Brief downtime.
  - When to use: When old and new versions cannot run simultaneously (DB migrations, incompatible protocols).
- **Rollout Control**: `kubectl rollout` commands to pause, resume, check status, undo.

## Key Concepts
- **Deployment → ReplicaSet → Pod hierarchy**: Deployment creates and manages multiple ReplicaSets (one per version).
- **maxSurge**: max Pods above desired count during rollout (allows temporary overage).
- **maxUnavailable**: max Pods below desired count during rollout (limits downtime).
- **minReadySeconds**: time a new Pod must be healthy before rollout continues.
- **progressDeadlineSeconds**: how long before a stalled rollout is marked as failed.
- **Revision history**: Kubernetes keeps old ReplicaSets for rollback; controlled by `revisionHistoryLimit`.
- **rollout pause/resume**: hold a rollout mid-way (e.g., 10% canary) to observe before proceeding.

## Code Examples
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: kuard
spec:
  replicas: 3
  selector:
    matchLabels:
      run: kuard
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 1
  minReadySeconds: 60
  revisionHistoryLimit: 14
  template:
    metadata:
      labels:
        run: kuard
    spec:
      containers:
      - name: kuard
        image: gcr.io/kuar-demo/kuard-amd64:blue
```

```bash
# Rollout management
kubectl rollout status deployments kuard          # watch rollout progress
kubectl rollout history deployment kuard          # list revisions
kubectl rollout history deployment kuard --revision=2
kubectl rollout pause deployments kuard           # pause mid-rollout
kubectl rollout resume deployments kuard          # resume
kubectl rollout undo deployments kuard            # rollback to previous
kubectl rollout undo deployments kuard --to-revision=3  # rollback to specific
```

## Mental Models
- Deployment = Rollout Manager. ReplicaSet = Pod Manager. Don't skip to ReplicaSets unless you need low-level control.
- `kubectl rollout pause` enables canary deployments: deploy 10% new, pause, monitor, then resume.
- Old ReplicaSets are kept (scaled to 0) for rollback. They will accumulate unless you set `revisionHistoryLimit`.

## Anti-patterns
- **Setting image with `kubectl set image` without updating YAML**: drift between cluster state and source control.
- **maxUnavailable: 0 + maxSurge: 0**: invalid; rollout will never proceed.
- **No minReadySeconds**: pods appear healthy before they're actually serving traffic; bad pod promoted too fast.
- **No progressDeadlineSeconds**: stalled rollouts hang forever without alerting.

## Key Takeaways
1. Always use Deployments (not raw Pods or ReplicaSets) for stateless services.
2. `minReadySeconds` is your health gate; set it to at least 30–60 seconds for production.
3. Use `kubectl rollout pause` + `kubectl rollout resume` for canary deployments without a service mesh.
4. Keep `revisionHistoryLimit` at 10–14 for useful rollback history without unbounded RS accumulation.
5. `Recreate` strategy is appropriate when old and new versions share state that's incompatible.

## Connects To
- **Ch 9**: ReplicaSets — Deployments manage them.
- **Ch 5**: Pod spec lives in the Deployment template.
- **Ch 15**: Service meshes provide more sophisticated traffic shaping for canary releases.
