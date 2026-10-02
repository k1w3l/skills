# Chapter 17: Extending Kubernetes

## Core Idea
Kubernetes is extensible via CustomResourceDefinitions (new API objects) and admission controllers (request interception/modification) — the foundation for operators and the entire ecosystem of Kubernetes add-ons.

## Frameworks Introduced
- **Three CRD Patterns**:
  - Just Data: store config/state in the API server; no controller needed.
  - Compiler/Abstraction: CRD is compiled into lower-level K8s objects by a controller.
  - Operator: CRD + controller that actively manages health/lifecycle of the resource.
  - When to use: Complexity increases in this order; use the simplest pattern that fits.
- **Admission Controller Flow**: Authenticate → Authorize → Mutating Admission → Validating Admission → Persist.
  - Mutating: modifies requests (e.g., inject sidecar).
  - Validating: approves or rejects requests (e.g., validate schema).

## Key Concepts
- **CustomResourceDefinition (CRD)**: meta-resource defining a new API type. Name format: `<plural>.<api-group>`.
- **Custom Resource**: instance of a CRD (like a Pod is an instance of the Pod API).
- **Controller**: watches CRs and takes action to reconcile desired → actual state.
- **Operator**: CRD + controller + active lifecycle management (health checks, backups, upgrades).
- **Informer pattern**: efficient watch API using the client-go library; avoids polling.
- **ValidatingWebhookConfiguration**: registers an HTTP admission controller for validation.
- **MutatingWebhookConfiguration**: registers an HTTP admission controller for mutation.
- **Kubebuilder**: framework for building Kubernetes API extensions and operators.
- **OpenAPI spec**: optional schema for CRD validation; 4MB in size for full Kubernetes API.

## Code Examples
```yaml
# CustomResourceDefinition
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: loadtests.beta.kuar.com
spec:
  group: beta.kuar.com
  versions:
  - name: v1
    served: true
    storage: true
  scope: Namespaced
  names:
    plural: loadtests
    singular: loadtest
    kind: LoadTest
    shortNames: [lt]
```

```bash
# CRD lifecycle
kubectl create -f loadtest-crd.yaml
kubectl get loadtests                # now available
kubectl create -f loadtest.yaml      # create an instance
kubectl get lt                       # short name works
```

## Mental Models
- CRD = new noun in the Kubernetes vocabulary. Controller = the verb handler.
- Operator = a domain expert encoded as code: "if this DB is unhealthy, take snapshot, remediate, alert."
- Admission controllers run in the request path — a buggy one can block ALL object creation.

## Anti-patterns
- **Operator pattern for simple config storage**: overkill. Use "just data" CRD.
- **Using Kubernetes API server as app data store**: not designed for arbitrary data; use it for control objects only.
- **Running admission webhooks with self-signed certs improperly**: API server must trust the webhook's CA.
- **Not limiting admission controller scope**: register for only the resources/actions you need.

## Key Takeaways
1. CRDs add new API types; controllers make them meaningful.
2. Use the simplest pattern: Just Data → Compiler → Operator.
3. Admission controllers run synchronously in the API path — implement them defensively.
4. Kubebuilder is the recommended starting point for building operators.
5. Cluster-admin is required to install CRDs and admission controllers — treat with care.

## Connects To
- **Ch 8**: Ingress controllers are a specific application of the CRD + controller pattern.
- **Ch 15**: Service meshes use CRDs + admission controllers (sidecar injection).
- **Ch 14**: RBAC governs who can create/modify CRDs.
