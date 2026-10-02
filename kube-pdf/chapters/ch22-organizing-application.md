# Chapter 22: Organizing Your Application

## Core Idea
Treat the filesystem of YAML files as the source of truth for your cluster; use code review, feature flags, versioned directories, and templating (Helm) to manage application configurations reliably.

## Frameworks Introduced
- **Three Organizing Principles**:
  1. **Filesystem as Source of Truth**: YAML in git IS the cluster; kubectl output is just a reflection.
  2. **Code Review for Configuration**: all YAML changes reviewed before merging, same as application code.
  3. **Feature Flags**: new features land behind a flag (off by default); activation is a config change, not a deploy.
- **Release Progression**: HEAD → development → staging → canary → release.
  - `development` tag: auto-moved to HEAD after integration tests pass.
  - `canary`: first real-user exposure; validate before broad rollout.
- **Versioning Strategies**: source-control tags/branches vs filesystem directories.
- **Parameterization with Helm**: templates + values files enable environment-specific configs from shared templates.

## Key Concepts
- **Filesystem Layout**: organize by component/service (`frontend/`, `service-1/`) not by object type.
- **One object per file**: avoid multi-object YAML unless objects are conceptually inseparable.
- **Naming convention**: `<service>-<type>.yaml` (e.g., `frontend-deployment.yaml`, `frontend-service.yaml`).
- **Cherry-pick workflow**: fix in HEAD → create release branch → cherry-pick fix → tag new point release.
- **Symbolic links for stage mapping**: `canary/ -> v2/`, `release/ -> v1/`.
- **Helm mustache syntax**: `{{ .Release.Name }}` replaced with values from `values.yaml`.
- **Parameterized environments**: 90% shared template + 10% environment-specific values = consistent environments.

## Code Examples
```
# Recommended filesystem layout
frontend/
  v1/
    frontend-deployment.yaml
    frontend-service.yaml
    frontend-ingress.yaml
  v2/
    ...
  staging/
    templates -> ../v2
    staging-parameters.yaml
  production/
    templates -> ../v1
    production-parameters.yaml
service-1/
  service-1-deployment.yaml
  service-1-service.yaml
  service-1-configmap.yaml
```

```yaml
# Helm template
metadata:
  name: {{ .Release.Name }}-deployment
  labels:
    app: {{ .Values.appName }}
    env: {{ .Values.environment }}
```

## Mental Models
- "The cluster is read-only" — all changes go through git, not `kubectl edit`.
- Feature flags decouple code merge from feature activation; rollback is a config change, not a binary rollback.
- Parameterization minimizes environment drift: same template, different values.

## Anti-patterns
- **`kubectl edit` in production without updating source**: cluster drifts from git truth.
- **Multi-object YAML files**: hard to diff, review, and manage individually.
- **No staging/canary before production**: no chance to catch config errors before full rollout.
- **Separate repos for each microservice config**: makes cross-service deployments harder to coordinate.

## Key Takeaways
1. Git is the source of truth; cluster state is a projection of git.
2. Enforce code review on all YAML changes — most outages come from config mistakes.
3. Feature flags enable zero-risk code merges; activation via config review.
4. Use Helm (or equivalent) to parameterize configs; avoid copy-pasting with minor edits.
5. Release stages: development (auto-moves) → staging → canary → release; each gate adds confidence.

## Connects To
- **Ch 1**: Declarative configuration and GitOps — this chapter operationalizes those principles.
- **Ch 10**: Deployment rollout stages map to the release progression here.
- **Ch 21**: Multicluster deployment follows the same filesystem organization principles.
