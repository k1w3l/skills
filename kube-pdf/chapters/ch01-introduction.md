# Chapter 1: Introduction

## Core Idea
Kubernetes provides velocity, scaling, infrastructure abstraction, and efficiency by offering an application-oriented container API that decouples developers from underlying machines.

## Frameworks Introduced
- **The Five Benefits of Kubernetes**: velocity, scaling, infrastructure abstraction, efficiency, cloud native ecosystem.
  - When to use: Justifying Kubernetes adoption; communicating value to stakeholders.
- **Immutable Infrastructure**: artifacts are never modified after creation; changes produce new artifacts.
  - How: Build new container images instead of modifying running containers. Old images remain for rollback.
- **Declarative Configuration**: describe desired state, let the system reconcile.
  - When to use: Always prefer over imperative `kubectl run`; store YAML in version control (GitOps).
- **Self-Healing Systems**: Kubernetes continuously reconciles actual state with desired state.
  - How: controllers watch cluster state and act; no manual operator intervention required for pod failures.

## Key Concepts
- **Velocity**: speed of reliable feature delivery, not raw speed. Enabled by immutability, declarative config, self-healing.
- **Decoupling**: APIs + load balancers isolate components; enables independent scaling and team autonomy.
- **Two-Pizza Team**: ideal team size ~6–8 people; microservices + Kubernetes enable this at scale.
- **"Not My Monkey, Not My Circus" Line**: crisp boundary between app operators (use orchestration SLA) and cluster operators (deliver orchestration SLA).
- **KaaS (Kubernetes-as-a-Service)**: managed Kubernetes from cloud providers; offloads cluster management.
- **GitOps**: production changes via git pushes only; cluster is effectively read-only.
- **CNCF Maturity Levels**: sandbox → incubating → graduated. Prefer graduated/incubating for production.

## Mental Models
- Think of Kubernetes as a reconciliation engine: it continuously watches and acts, not a one-shot executor.
- Prefer declarative over imperative: "3 replicas" beats "run A, run B, run C."
- Immutability enables reliable rollback: the old image still exists, swap is atomic.

## Anti-patterns
- **Mutable containers in production**: SSH-ing into a container to hotfix breaks the immutability contract; record changes as declarative config after.
- **Imperative cluster management**: ad-hoc `kubectl` commands without corresponding YAML in source control cause drift.

## Key Takeaways
1. Kubernetes separates developers from specific machines, enabling horizontal scaling without redesign.
2. Immutable images + declarative config + self-healing = high velocity with high reliability.
3. Decoupled architectures via APIs + load balancers let small teams operate large systems independently.
4. GitOps: treat the cluster as read-only; all changes via version-controlled YAML.
5. The CNCF ecosystem provides solutions for nearly every cloud native need; prefer graduated projects.

## Connects To
- **Ch 22**: Organizing application configs (the filesystem as source of truth).
- **Ch 14**: RBAC — separating responsibilities for app vs. cluster operators.
