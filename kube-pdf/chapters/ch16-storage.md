# Chapter 16: Integrating Storage Solutions and Kubernetes

## Core Idea
Persistent storage in Kubernetes abstracts underlying infrastructure via PersistentVolumes and PersistentVolumeClaims; StatefulSets provide ordered, stable-identity Pod management for stateful applications.

## Frameworks Introduced
- **PV/PVC Abstraction Layer**: PersistentVolume (cluster resource) + PersistentVolumeClaim (namespace request) decouple storage from Pods.
  - When to use: Any workload needing storage that outlives a Pod.
- **StatefulSet**: manages Pods with stable network identity and ordered deployment/scaling.
  - When to use: Databases, distributed caches, any app requiring stable hostname or ordered startup.
- **StorageClass**: defines storage provisioner (type, IOPS, replication); enables dynamic provisioning.

## Key Concepts
- **PersistentVolume (PV)**: cluster-level storage resource; provisioned by admin or dynamically.
- **PersistentVolumeClaim (PVC)**: namespace-level storage request by a workload.
- **StorageClass**: defines how PVs are dynamically provisioned (`provisioner`, `reclaimPolicy`, `volumeBindingMode`).
- **Access Modes**: `ReadWriteOnce` (one node), `ReadOnlyMany` (many nodes read), `ReadWriteMany` (many nodes read/write).
- **Reclaim Policy**: `Delete` (PV deleted with PVC), `Retain` (PV kept for manual cleanup).
- **StatefulSet**: Pods get stable names (`pod-0`, `pod-1`), stable DNS (`pod-0.service.namespace`), ordered startup/shutdown.
- **Headless Service**: required for StatefulSet DNS; `clusterIP: None` returns individual Pod IPs.
- **volumeClaimTemplates**: StatefulSet field that auto-creates a PVC per Pod replica.
- **Data Gravity**: existing data migration complexity; often the hardest part of containerizing stateful apps.

## Code Examples
```yaml
# StatefulSet with volumeClaimTemplates
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: mongo
spec:
  serviceName: "mongo"
  replicas: 3
  selector:
    matchLabels:
      app: mongo
  template:
    spec:
      containers:
      - name: mongo
        image: mongo:4.4
        volumeMounts:
        - name: data
          mountPath: /data/db
  volumeClaimTemplates:
  - metadata:
      name: data
    spec:
      accessModes: [ReadWriteOnce]
      storageClassName: fast
      resources:
        requests:
          storage: 10Gi
```

```bash
# Storage operations
kubectl get pv                                   # list persistent volumes
kubectl get pvc                                  # list claims
kubectl get storageclass                         # list storage classes
kubectl describe pvc my-claim
```

## Mental Models
- PVC = a request for storage (like a job posting); PV = the actual storage that fulfills it (like a hire).
- StatefulSet Pod names are stable: `mongo-0`, `mongo-1`, `mongo-2`. DNS: `mongo-0.mongo.default.svc.cluster.local`.
- Ordered startup: StatefulSet starts Pods sequentially (0 then 1 then 2); important for leader election.

## Anti-patterns
- **Using Deployment for stateful apps**: no stable Pod names → databases can't form quorums.
- **ReadWriteMany for all storage**: most cloud providers only support ReadWriteOnce; RWX requires special NFS/EFS solutions.
- **Not setting a reclaim policy**: default `Delete` destroys data when PVC is deleted; set `Retain` for databases.
- **Skipping cloud-managed databases**: running your own DB in K8s is complex; consider managed services (RDS, CloudSQL, Cosmos DB).

## Key Takeaways
1. Use StatefulSet (not Deployment) for any app requiring stable hostname or ordered scaling.
2. Always set `reclaimPolicy: Retain` for production database PVs.
3. `volumeClaimTemplates` in StatefulSet auto-creates per-Pod PVCs.
4. StorageClass enables dynamic provisioning; use `volumeBindingMode: WaitForFirstConsumer` for zone-aware binding.
5. Strongly prefer managed cloud databases over self-operated databases in Kubernetes.

## Connects To
- **Ch 5**: Pods use volumes; PVCs are a type of volume.
- **Ch 19**: Security for storage — encryption at rest.
- **Ch 21**: Multicluster storage — replicated data for regional deployments.
