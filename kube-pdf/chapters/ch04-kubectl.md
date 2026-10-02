# Chapter 4: Common kubectl Commands

## Core Idea
kubectl is the primary CLI for interacting with the Kubernetes API; mastering it means mastering namespaces, object CRUD, labels, debugging, and cluster management.

## Key Concepts
- **Namespace**: logical folder organizing objects in a cluster; default namespace for most operations.
- **Context**: saved combination of cluster + user + namespace in `~/.kube/config`.
- **RESTful Resources**: every Kubernetes object is a REST resource at a URL path.
- **JSONPath**: query language for extracting specific fields from Kubernetes objects.
- **Dry-run**: `--dry-run=client` prints what would happen without sending to server.

## Commands & APIs
```bash
# Namespaces & contexts
kubectl --namespace=mystuff get pods          # specific namespace
kubectl -n mystuff get pods                   # shorthand
kubectl --all-namespaces get pods             # all namespaces
kubectl config set-context my-context --namespace=mystuff
kubectl config use-context my-context

# Viewing objects
kubectl get <resource>                        # list all
kubectl get <resource> <name>                 # specific object
kubectl get pods -o wide                      # more columns
kubectl get pods -o yaml                      # full YAML output
kubectl get pods -o json                      # full JSON output
kubectl get pods -o jsonpath --template={.status.podIP}
kubectl get pods,services                     # multiple types
kubectl describe <resource> <name>            # rich details
kubectl explain pods                          # field docs

# CRUD
kubectl apply -f obj.yaml                     # create or update (idempotent)
kubectl apply -f obj.yaml --dry-run=client    # preview
kubectl delete -f obj.yaml                    # delete
kubectl delete <resource> <name>              # delete by name
kubectl edit <resource> <name>                # interactive edit

# Labels & annotations
kubectl label pods bar color=red
kubectl label pods bar color=red --overwrite
kubectl label pods bar color-                 # remove label
kubectl annotate pods bar key=value

# Debugging
kubectl logs <pod-name>
kubectl logs <pod-name> -c <container>        # multi-container pod
kubectl logs <pod-name> -f                    # follow/stream
kubectl exec -it <pod-name> -- bash           # interactive shell
kubectl attach -it <pod-name>                 # attach to process
kubectl cp <pod>:/remote/path /local/path     # copy files
kubectl port-forward <pod-name> 8080:80       # forward port
kubectl get events                            # cluster events
kubectl top nodes                             # resource usage
kubectl top pods

# Cluster management
kubectl cordon <node>                         # prevent scheduling
kubectl drain <node>                          # evict pods + cordon
kubectl uncordon <node>                       # re-enable scheduling
```

## Mental Models
- `apply` is idempotent; safe to run in loops. Prefer over `create` for declarative workflows.
- `describe` is for humans; `-o yaml` is for machines/scripting.
- Use `port-forward` to access pods that are not exposed publicly.

## Anti-patterns
- **`kubectl edit` in production**: makes imperative change without updating source control — causes drift.
- **`kubectl delete pod`**: temporary fix; the ReplicaSet recreates it. Delete the controller instead.
- **No `--namespace`**: accidentally operating on the wrong namespace.

## Key Takeaways
1. `kubectl apply -f` is the primary way to create and update objects; it's idempotent.
2. Always use `--dry-run=client` before destructive changes.
3. `kubectl describe` provides events and conditions — essential for debugging stuck pods.
4. Set up shell autocompletion: `source <(kubectl completion bash)`.
5. `kubectl get events --watch` is invaluable for real-time cluster observation.

## Connects To
- **Ch 6**: Labels — how selectors work with `kubectl get -l`.
- **Ch 14**: RBAC — `kubectl auth can-i` for testing permissions.
