# Chapter 6: Labels and Annotations

## Core Idea
Labels are the glue that connects Kubernetes objects — selectors route traffic, group pods into ReplicaSets, and bind services to workloads; annotations store non-identifying metadata for tools.

## Frameworks Introduced
- **Label Selector Pattern**: ReplicaSets, Services, DaemonSets all find their Pods via label selectors.
  - When to use: Whenever one K8s object must refer to a group of other objects.
  - How: Set matching labels on Pods; define selector in controller spec.
- **Labels vs Annotations Decision Rule**: If you'll ever want to filter/select by it → label. Otherwise → annotation.

## Key Concepts
- **Label**: key/value pair for identifying information; max 63-char value; used in selectors.
- **Annotation**: key/value pair for non-identifying metadata; free-form string value; tool metadata.
- **Label Selector**: Boolean expression filtering objects by labels (`app=alpaca`, `ver in (1,2)`, `!canary`).
- **matchLabels**: simple equality selector (older controllers like Services).
- **matchExpressions**: richer selector with In, NotIn, Exists operators (Deployments, ReplicaSets).
- **Label Prefix**: DNS subdomain prefix for organization-specific labels (e.g., `acme.com/app-version`).

## Reference Tables
| Operator | Syntax | Description |
|---|---|---|
| Equality | `key=value` | key equals value |
| Inequality | `key!=value` | key not equal |
| Set-in | `key in (v1,v2)` | key is one of values |
| Set-notin | `key notin (v1,v2)` | key is not in values |
| Exists | `key` | key is set |
| Not exists | `!key` | key is not set |

## Code Examples
```bash
# Apply labels
kubectl label pods bar color=red
kubectl label pods bar color=red --overwrite
kubectl label pods bar color-                  # remove

# Select with labels
kubectl get pods --selector="ver=2"
kubectl get pods --selector="app=alpaca,ver=2" # AND
kubectl get pods --selector="app in (alpaca,bandicoot)"
kubectl get pods -l 'ver=2,!canary'
kubectl get deployments -L canary              # show label as column
```

```yaml
# matchExpressions in a ReplicaSet
selector:
  matchLabels:
    app: alpaca
  matchExpressions:
    - {key: ver, operator: In, values: [1, 2]}
```

## Mental Models
- Labels are the nervous system of Kubernetes — they wire objects together.
- When in doubt, add as annotation first; promote to label when you need to select by it.
- Avoid using the API server as a general database via annotations — keep annotation data small and associated with the object.

## Anti-patterns
- **Labels on Deployment but not Pod template**: `kubectl label deployment` only labels the Deployment object, not the Pods it creates. Change the template to label Pods.
- **Conflicting selectors**: two controllers with overlapping selectors will fight over the same Pods.
- **Unbounded annotation values**: annotations have no size validation by default; large values degrade API server performance.

## Key Takeaways
1. Labels are how Kubernetes wires objects together — they are not optional metadata.
2. The label selector is the only relationship between a Service and its Pods — no ownership.
3. Use `kubernetes.io/` prefix for system labels; use your domain prefix for custom labels.
4. Annotations are the right place for rollout tracking, build metadata, icon URLs, external tool config.
5. `kubectl get -L <label>` shows label value as a column — useful for visual inspection.

## Connects To
- **Ch 9**: ReplicaSets use label selectors to manage Pods.
- **Ch 7**: Services use label selectors to route traffic to Pods.
- **Ch 11**: DaemonSets use node labels to target specific nodes.
