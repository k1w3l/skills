# Chapter 14: Role-Based Access Control for Kubernetes

## Core Idea
RBAC restricts who can perform which actions on which Kubernetes resources — defense against accidental (and malicious) cluster damage via least-privilege identity-to-capability binding.

## Frameworks Introduced
- **Identity → Role → RoleBinding chain**: identity (user/group/service account) + role (capabilities) + binding (assignment).
  - When to use: Always. Set up RBAC before your cluster is production-ready, not after.
- **Namespaced vs Cluster-scoped**: Role/RoleBinding = namespace scope; ClusterRole/ClusterRoleBinding = cluster-wide.
- **Aggregating ClusterRoles**: combine fine-grained roles into broader ones via label-based selectors.
  - When to use: Building role hierarchies without copy-pasting rules.
- **Group Bindings over Individual Bindings**: bind roles to groups, not individual users.
  - When to use: Any organization with more than a few people.

## Key Concepts
- **Service Account**: machine identity for Pods/components running inside the cluster.
- **User Account**: human identity; Kubernetes has no built-in user store (delegated to auth providers).
- **Authentication**: proving identity (x509 certs, tokens, OIDC, cloud IAM).
- **Authorization**: checking if the identity can perform the requested verb on the resource.
- **Verbs**: create, delete, get, list, patch, update, watch, proxy.
- **Built-in ClusterRoles**: cluster-admin (all), admin (namespace all), edit (namespace modify), view (namespace read-only).
- **`rbac.authorization.kubernetes.io/autoupdate: "false"`**: prevent API server from overwriting customized ClusterRoles on restart.
- **JIT access**: just-in-time group membership for emergency access; provides auditability.

## Code Examples
```yaml
# Namespaced Role
kind: Role
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  namespace: default
  name: pod-and-services
rules:
- apiGroups: [""]
  resources: ["pods", "services"]
  verbs: ["create", "delete", "get", "list", "patch", "update", "watch"]

# RoleBinding (user + group)
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  namespace: default
  name: pods-and-services
subjects:
- apiGroup: rbac.authorization.k8s.io
  kind: User
  name: alice
- apiGroup: rbac.authorization.k8s.io
  kind: Group
  name: mydevs
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: pod-and-services
```

```bash
# Test permissions
kubectl auth can-i create pods
kubectl auth can-i get pods --subresource=logs
kubectl auth can-i create pods --as=alice            # impersonate

# Reconcile RBAC from file
kubectl auth reconcile -f some-rbac-config.yaml
kubectl auth reconcile -f some-rbac-config.yaml --dry-run

# View built-in roles
kubectl get clusterroles
kubectl get clusterrolebindings
```

## Mental Models
- Least privilege: start with minimum access; add only what's needed.
- Roles describe capabilities; RoleBindings assign them. Roles are reusable; bindings are assignments.
- Groups simplify: when someone joins/leaves, update the group, not N individual bindings.

## Anti-patterns
- **Granting cluster-admin to all users**: single compromised identity → full cluster access.
- **Modifying built-in ClusterRoles directly**: overwritten on API server restart. Use `autoupdate: false` annotation first.
- **Allowing anonymous API discovery on public clusters**: disable with `--anonymous-auth=false`.
- **Individual user bindings at scale**: messy, inconsistent, hard to audit. Use groups.

## Key Takeaways
1. Set up RBAC from day one; retrofitting is expensive.
2. Use ClusterRole + RoleBinding (not ClusterRoleBinding) to grant namespace-scoped cluster roles.
3. Always prefer group bindings over individual bindings for scalability.
4. `kubectl auth can-i` is your RBAC debugging tool.
5. Service accounts: use different identities for different applications; never share service accounts.

## Connects To
- **Ch 17**: CRDs + admission controllers require RBAC to restrict who can create them.
- **Ch 19**: Security hardening builds on RBAC foundation.
- **Ch 21**: Multicluster: use central identity providers + RBAC for consistency across clusters.
