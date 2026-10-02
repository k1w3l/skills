# Chapter 2: Creating and Running Containers

## Core Idea
Container images bundle programs and dependencies into immutable artifacts, solving dependency management and enabling reliable, repeatable deployments.

## Frameworks Introduced
- **Container Layering**: images are stacks of filesystem layers; each layer adds/removes/modifies files from the layer below.
  - When to use: Understand to optimize image size and build cache.
  - How: Order layers from least-likely to most-likely to change; dependencies before source code.
- **Multistage Builds**: separate build environment from deployment image in a single Dockerfile.
  - When to use: Any compiled language (Go, Java, .NET) or when build tooling is not needed at runtime.
  - How: `FROM ... AS build` → build artifact → `FROM alpine` + `COPY --from=build`.

## Key Concepts
- **OCI Image Format**: Open Container Initiative standard; Docker format is the de facto standard.
- **System Container vs Application Container**: system containers run full OS boot; application containers run a single program. Prefer application containers.
- **Container Runtime Interface (CRI)**: standard API between Kubernetes and container runtimes (containerd, cri-o).
- **Overlay Filesystem**: aufs, overlay, overlay2 — enables copy-on-write layer semantics at runtime.
- **Image Registry**: remote store for container images; public (Docker Hub) or private (GCR, ECR, ACR).

## Mental Models
- Think of a container image as a shipping container: standardized, self-contained, portable.
- Deleted files in later layers are not truly deleted — they still exist in earlier layers and count toward image size.
- Ordering layers = ordering cache invalidation: change a layer → rebuild all layers above it.

## Anti-patterns
- **Secrets baked into layers**: passwords in any layer (even deleted ones) are accessible. Never mix secrets and images.
- **Build tools in production image**: leaves dev tools in final image; use multistage builds.
- **Wrong layer ordering**: putting source code before dependencies causes full dependency reinstall on every code change.

## Code Examples
```dockerfile
# STAGE 1: Build
FROM golang:1.17-alpine AS build
WORKDIR /go/src/app
COPY . .
RUN go build -o /app

# STAGE 2: Deployment  
FROM alpine
USER nobody:nobody
COPY --from=build /app /app
CMD ["/app"]
```
- **What it demonstrates**: Multistage build — build image ~500MB, final image ~20MB.

## Key Takeaways
1. Order Dockerfile layers from least → most likely to change to maximize build cache reuse.
2. Never put secrets, passwords, or private keys in any image layer.
3. Use multistage builds for compiled languages to dramatically reduce image size.
4. Tag images with semantically meaningful tags; avoid relying only on `latest`.
5. `docker system prune` for cleanup; consider a cron job for automated garbage collection.

## Connects To
- **Ch 1**: Immutability principle — container images are the implementation.
- **Ch 5**: Pods run containers; resource limits set here via cgroups.
- **Ch 13**: Secrets — how to inject credentials without baking them into images.
