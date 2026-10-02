# Chapter 18: Accessing Kubernetes from Programming Languages

## Core Idea
The Kubernetes API is an HTTP server; client libraries for Python, Java, and .NET wrap it into typed, idiomatic APIs for building operators, tools, and automation.

## Frameworks Introduced
- **kubeconfig vs in-cluster auth**: external programs use kubeconfig; in-cluster Pods use mounted service account tokens.
- **Watch/Event-based vs Polling**: watch API delivers changes as a stream; polling wastes resources and adds latency.
- **Patch Semantics**: three patch types — JSON Patch (RFC 6902), JSON Merge Patch, Strategic Merge Patch.

## Key Concepts
- **OpenAPI-generated clients**: all official clients are generated from the Kubernetes OpenAPI spec; don't edit generated code directly.
- **API groups**: resources are grouped (e.g., `apps/v1` for Deployments, `batch/v1` for Jobs); each group has its own client object.
- **Namespaced vs cluster-level resources**: different function signatures (`list_namespaced_pod` vs `list_namespaces`).
- **Watch API**: hanging GET; server writes events to open TCP connection; avoid polling for efficiency.
- **kubeconfig loading**: `~/.kube/config` or `$KUBECONFIG`; in-cluster from mounted service account.
- **WebSocket**: used for exec, port-forward, attach — not standard REST.

## Code Examples
```python
# Python: list pods + watch
from kubernetes import client, config, watch

config.load_kube_config()           # or load_incluster_config()
api = client.CoreV1Api()

# List
pods = api.list_namespaced_pod('default')

# Watch
w = watch.Watch()
for event in w.stream(api.list_namespaced_pod, 'default'):
    print(event['type'], event['object'].metadata.name)

# Create a pod
container = client.V1Container(name="myapp", image="myimage:v1")
pod = client.V1Pod(
    metadata=client.V1ObjectMeta(name="myapp"),
    spec=client.V1PodSpec(containers=[container])
)
api.create_namespaced_pod('default', pod)

# Exec in pod
from kubernetes.stream import stream
stream(api.connect_get_namespaced_pod_exec,
       "my-pod", "default",
       command=["ls", "/foo"],
       stdout=True, stderr=True, stdin=False, tty=False)
```

## Mental Models
- Use `--v=10` on kubectl to see the raw HTTP requests — reverse-engineer what API calls to make.
- Watch > Poll: watch delivers changes instantly with no load; polling is O(n) every interval.
- Exec and port-forward use WebSockets under the hood; the client libraries abstract this.

## Anti-patterns
- **Polling in a tight loop**: overloads the API server; use watch/informers.
- **Hand-editing generated client code**: gets overwritten on next code generation.
- **Forgetting cloud provider auth executable**: in CI/CD, the external auth binary must be available.
- **Default service account for operator Pods**: has minimal permissions; create a specific ServiceAccount with needed RBAC.

## Key Takeaways
1. Use `load_kube_config()` for out-of-cluster code; `load_incluster_config()` inside Pods.
2. Watch API is always preferred over polling for change detection.
3. `kubectl --v=10` reveals the HTTP API calls behind kubectl commands.
4. Three manipulation verbs: `create` (new), `replace` (full update), `patch` (partial update).
5. Python client at `kubernetes-client/client-python`; all clients follow the same patterns.

## Connects To
- **Ch 17**: Building operators requires API access from a running container.
- **Ch 14**: Service account RBAC governs what in-cluster code can do.
