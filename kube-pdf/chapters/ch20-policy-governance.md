# Chapter 20: Policy and Governance for Kubernetes Clusters

## Core Idea
Policy and governance tools (like OPA/Gatekeeper) enforce organizational rules on Kubernetes resources BEFORE they're created — filling the gap between what RBAC allows and what your organization requires.

## Frameworks Introduced
- **Admission-time Policy Enforcement**: validate and potentially mutate resource definitions at creation time against custom rules.
  - When to use: Enforcing labels, image registries, resource limits, naming conventions, security baselines.
- **Policy-as-Code**: store policies in version control; apply via CI/CD; audit compliance continuously.

## Key Concepts
- **OPA (Open Policy Agent)**: general-purpose policy engine; policies written in Rego language.
- **Gatekeeper**: Kubernetes-native OPA integration using CRDs (ConstraintTemplate + Constraint).
- **ConstraintTemplate**: defines a policy (schema + Rego logic).
- **Constraint**: instance of a ConstraintTemplate; specifies what it applies to and parameter values.
- **Audit mode**: check existing resources against policies without blocking (unlike enforce mode).
- **Policy vs RBAC**: RBAC = who can create/modify resources; Policy = what those resources must look like.
- **Kyverno**: alternative to Gatekeeper; policies written as YAML (no Rego needed).

## Code Examples
```yaml
# Gatekeeper ConstraintTemplate: require labels
apiVersion: templates.gatekeeper.sh/v1beta1
kind: ConstraintTemplate
metadata:
  name: k8srequiredlabels
spec:
  crd:
    spec:
      names:
        kind: K8sRequiredLabels
      validation:
        openAPIV3Schema:
          properties:
            labels:
              type: array
              items: string
  targets:
  - target: admission.k8s.gatekeeper.sh
    rego: |
      package k8srequiredlabels
      violation[{"msg": msg}] {
        provided := {label | input.review.object.metadata.labels[label]}
        required := {label | label := input.parameters.labels[_]}
        missing := required - provided
        count(missing) > 0
        msg := sprintf("Missing required labels: %v", [missing])
      }

# Constraint: all Pods must have "app" and "env" labels
apiVersion: constraints.gatekeeper.sh/v1beta1
kind: K8sRequiredLabels
metadata:
  name: pod-must-have-app-env
spec:
  match:
    kinds:
    - apiGroups: [""]
      kinds: ["Pod"]
  parameters:
    labels: ["app", "env"]
```

## Mental Models
- RBAC says "can Alice create Pods?" Policy says "must Pods have these labels?". Both are needed.
- Audit mode first → understand violations → switch to enforce → require fixes.
- Policies are the guardrails; RBAC is the gate.

## Anti-patterns
- **Starting with enforce mode**: blocks legitimate work without warning. Start with audit + warn.
- **Overly broad policies**: policies that catch everything will have many false positives.
- **Not storing policies in version control**: policy drift = security drift; treat policies like code.
- **Using only RBAC for governance**: RBAC can't check if labels are present or images come from approved registries.

## Key Takeaways
1. RBAC ≠ governance; RBAC controls access, governance controls content.
2. Use Gatekeeper or Kyverno; start with audit mode before enforcing.
3. Policy-as-code: store ConstraintTemplates in git, deploy via CI/CD.
4. Require: approved image registries, mandatory labels (app, env, owner), resource limit presence.
5. Audit existing violations before turning on enforcement to avoid surprise breakage.

## Connects To
- **Ch 14**: RBAC for access control; this chapter for content policy.
- **Ch 17**: Admission controllers — Gatekeeper is built on this mechanism.
- **Ch 19**: Security policies complement SecurityContext enforcement.
