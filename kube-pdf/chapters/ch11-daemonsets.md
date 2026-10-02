# Chapter 11: DaemonSets

## Core Idea
A DaemonSet ensures exactly one Pod runs on every (or a subset of) node(s) — the right primitive for node-level agents like log collectors, monitoring daemons, and network plugins.

## Frameworks Introduced
- **Node Selector for Targeting**: use node labels to restrict DaemonSet Pods to a subset of nodes.
  - When to use: Specialized hardware (GPUs, SSD), edge network nodes, compliance scanning.
- **RollingUpdate for DaemonSets**: same strategy as Deployments — controlled by `spec.updateStrategy`.

## Key Concepts
- **DaemonSet vs ReplicaSet decision**: ReplicaSet = N copies, don't care which node. DaemonSet = one copy per node.
- **DaemonSet Scheduler bypass**: DaemonSet controller sets `nodeName` directly; ignores the default scheduler.
- **minReadySeconds**: Pod must be healthy this long before rolling update proceeds to next node.
- **maxUnavailable**: how many nodes can have old/unavailable DaemonSet Pod simultaneously during rollout.
- **Node label add/remove**: DaemonSet Pods follow node labels — adding a required label → Pod deployed; removing → Pod deleted.

## Code Examples
```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: fluentd
spec:
  selector:
    matchLabels:
      app: fluentd
  updateStrategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1
  template:
    metadata:
      labels:
        app: fluentd
    spec:
      nodeSelector:            # optional: restrict to labeled nodes
        ssd: "true"
      containers:
      - name: fluentd
        image: fluent/fluentd:v0.14.10
        volumeMounts:
        - name: varlog
          mountPath: /var/log
      volumes:
      - name: varlog
        hostPath:
          path: /var/log
```

```bash
# Label a node for targeting
kubectl label nodes <node-name> ssd=true
kubectl get nodes --selector ssd=true

# DaemonSet status
kubectl describe daemonset fluentd
kubectl get pods -l app=fluentd -o wide         # shows node assignment

# Rolling update status
kubectl rollout status daemonSets fluentd
```

## Mental Models
- DaemonSets automatically handle cluster autoscaling: new node → DaemonSet detects missing Pod → deploys it.
- Use `spec.minReadySeconds: 30` + `maxUnavailable: 1` for safe rolling updates on DaemonSets.
- `hostPath` volumes let DaemonSet agents read node-level logs and metrics.

## Anti-patterns
- **Forcing one-per-node with ReplicaSet + scheduling constraints**: fragile. Use DaemonSet.
- **Rolling update without minReadySeconds**: daemon starts but isn't healthy; rollout proceeds to next node too fast.
- **Deleting DaemonSet without `--cascade=false`**: removes all Pods. Set flag if you want to preserve them.

## Key Takeaways
1. DaemonSets are the correct primitive for: log agents, metric collectors, network plugins, security scanners.
2. Node labels drive DaemonSet targeting — dynamic: add label → Pod appears; remove → Pod deleted.
3. Set `spec.updateStrategy.type: RollingUpdate` with `maxUnavailable: 1` for safe upgrades.
4. DaemonSet Pods bypass the scheduler — they go directly to the node via `nodeName`.
5. DaemonSets + cluster autoscaler = self-managing node agents.

## Connects To
- **Ch 6**: Node labels target DaemonSet subsets.
- **Ch 3**: kube-proxy runs as a DaemonSet in every cluster.
- **Ch 10**: Same rolling update semantics as Deployments.
