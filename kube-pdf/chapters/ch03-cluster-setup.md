# Chapter 3: Deploying a Kubernetes Cluster

## Core Idea
Getting a cluster running is prerequisite to everything else; cloud-managed options (GKE, EKS, AKS) are recommended for learning and production; local options (minikube, kind) for development.

## Frameworks Introduced
- **Cluster Options Spectrum**: managed KaaS → kind/Docker-in-Docker → minikube → bare metal (kubeadm).
  - When to use: Production → managed KaaS; local dev → kind (multinode) or minikube (single-node).

## Key Concepts
- **Control Plane Nodes**: run API server, scheduler, controller-manager, etcd. Kubernetes won't schedule user workloads here.
- **Worker Nodes**: where your Pods run.
- **etcd**: distributed key-value store; the source of truth for all cluster objects.
- **controller-manager**: runs reconciliation loops for ReplicaSets, Deployments, etc.
- **scheduler**: decides which node a Pod runs on.
- **kube-proxy**: DaemonSet on every node; routes network traffic to load-balanced services.
- **CoreDNS**: cluster DNS; provides DNS-based service discovery.
- **Kubernetes Proxy (kube-proxy)**: deployed as a DaemonSet; present on every node.
- **kubectl**: official CLI for the Kubernetes API.

## Commands & APIs
```bash
# GKE
gcloud container clusters create kuar-cluster --num-nodes=3
gcloud container clusters get-credentials kuar-cluster

# EKS
eksctl create cluster

# AKS
az group create --name=kuar --location=westus
az aks create --resource-group=kuar --name=kuar-cluster

# kind (local multinode)
kind create cluster --wait 5m

# Check cluster health
kubectl version
kubectl get componentstatuses
kubectl get nodes
kubectl describe nodes <node-name>
```

## Key Takeaways
1. Use managed KaaS for production; reduces operational burden significantly.
2. `kind` is preferred over `minikube` for local dev when you need multinode behavior.
3. The kube-system namespace contains cluster-internal components (DNS, proxy, etc.).
4. `kubectl describe nodes` shows resource capacity and current pod allocation.
5. Version skew: kubectl and server must be within 3 minor versions of each other.

## Connects To
- **Ch 4**: kubectl commands for managing objects in the cluster.
- **Ch 11**: DaemonSets — how kube-proxy and logging agents run on every node.
