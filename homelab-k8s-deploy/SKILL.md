---
name: homelab-k8s-deploy
description: >
  Plans and generates Kubernetes deployment artifacts for homelab applications on k3s (Proxmox).
  Use this skill when the user wants to deploy an app to a local/homelab Kubernetes cluster,
  plan a k3s infrastructure stack, or generate K8s manifests. Trigger when the user mentions
  k3s, homelab K8s, deploying to Proxmox, MetalLB, NFS storage for K8s, Nginx Ingress on
  homelab, or says things like "subir no kubernetes", "deploy no k3s", "gerar manifests",
  "quero rodar no cluster", or similar. Also trigger when the user has a Dockerized app and
  asks how to run it on Kubernetes — even if they don't say "homelab" explicitly.
---

# Homelab K8s Deploy

Two-phase skill: **plan** the infrastructure, then **generate** all artifacts.

- **Phase 1 (Planning)** — interviews the user, maps dependencies, produces structured design with trade-offs and final decision table.
- **Phase 2 (Generation)** — takes the validated design and writes all files to `k8s/` in the project root.

If the user already has a completed design or says "pula para geração" / "skip to generation", go straight to Phase 2.

---

## Phase 1: Planning

### What to gather

**Inspect the codebase first** before asking anything. Check `docker-compose.yml`, `Dockerfile`, `.env.example` to extract:
- App image name and tag
- Container port
- Volumes (host path → container path)
- Required environment variables

Only ask about what you couldn't find. Then ask about infrastructure:

| Topic | What to ask |
|---|---|
| MetalLB | IP range available on the local network (e.g., `192.168.1.241-254`) |
| NFS | Server IP + export path |
| External DB | Host IP/hostname, port |
| Ingress | Hostname for the app (e.g., `app.domain.com`) |
| TLS | Terminated externally (Cloudflare, Pangolin, Nginx outside cluster) or in-cluster (cert-manager)? |
| Registry | Docker Hub public/private, or local registry? |
| Scale | Single node or multi-node cluster? |

Ask at most 2 questions per turn. Prioritize blockers.

**Check whether the cluster infra already exists first.** A very common case is a
homelab that already runs k3s + MetalLB + Nginx Ingress + an NFS StorageClass
(deployed for a previous app). If so, you only generate `k8s/app/` and the
install doc covers **only** the app deploy + DNS — skip the `addons/` and the
k3s/MetalLB/ingress/provisioner install steps entirely. Ask: *"O cluster já tem
ingress-nginx + MetalLB + StorageClass, ou gero os add-ons do zero?"* When infra
is reused, the app's ingress points to the **same MetalLB IP** as every other app
(one shared ingress controller IP); routing to the right namespace is by `Host`
header, not by IP. Confirm that shared IP with
`kubectl get svc -n ingress-nginx ingress-nginx-controller`.

### Output structure for Phase 1

**1. Dependency stack (ASCII diagram)**

```
External access (Cloudflare / Pangolin / DNS)
  │
Nginx Ingress ←── MetalLB IP
  │
Service (ClusterIP)
  │
Deployment ──── Secret (env vars)
  │
PVC (NFS RWX) ──── NFS server
  │
External dependencies (DB, etc.)
```

**2. Trade-offs table**

| Decision | Choice | Justification |
|---|---|---|
| K8s distribution | k3s | ... |
| Storage | NFS Subdir Provisioner (RWX) | ... |
| Ingress | Nginx + MetalLB L2 | ... |
| TLS | External / cert-manager | ... |

**3. Risks** — list 3-5 non-obvious risks with mitigations.

**4. Installation order** — numbered, sequential (each step depends on the previous).

**5. Final design table**

| Decision | Choice | Justification |
|---|---|---|

End with: "Design finalizado — posso gerar os manifests?"  
Wait for explicit confirmation before proceeding to Phase 2.

### Opinionated defaults for homelab

These are the right choices for single-node homelab; only deviate if the user has a specific reason:

- **k3s** with `--disable traefik --disable servicelb`
- **MetalLB** in L2 mode (no BGP needed for homelab)
- **NFS Subdir External Provisioner** as StorageClass for *shared, app-generated* data; access mode `ReadWriteMany`. **But two big exceptions (both hit in practice):**
  - **File-based DB (SQLite, or anything using file locks) → NEVER on NFS.** NFS file-locking is unreliable and corrupts the DB. Put it on a `local-path` PVC (`ReadWriteOnce`) — local node disk. For a reconstructible cache DB, being pinned to one node is a non-issue. Pair with `replicas: 1` + `strategy: Recreate` (single-writer).
  - **Pre-existing data already on the NAS → static NFS volume, NOT the subdir provisioner.** The provisioner creates a *new empty subdir*; it won't surface files that already live at a known export path. Use a direct `nfs:` volume (or a static PV with `storageClassName: ""`) pointing at the exact `server:` + `path:`. Mount it at the **exact container path the app's config expects** so first-boot config/seed works unmodified.
- **`imagePullPolicy: IfNotPresent`** for Docker Hub public images (avoids rate limits)
- **No cert-manager** when TLS is terminated externally; HTTP-only Ingress is correct and intentional
- **MySQL/Postgres outside the cluster** (dedicated VM) — stateful workloads in homelab K8s add operational complexity for no real benefit
- **MySQL VM RAM**: MySQL 8 needs at least 1GB; flag anything below that

### Known gotchas (learned in production)

**k3s on Proxmox LXC (not VM)**

If the user is running k3s inside an LXC container (detectable by `-pve` in the kernel name), three fixes are required:

1. On the **Proxmox HOST** — load the missing kernel modules:
```bash
modprobe br_netfilter overlay
echo -e "br_netfilter\noverlay" > /etc/modules-load.d/k3s.conf
```

2. On the **Proxmox HOST** — enable nesting and keyctl for the LXC container (replace `100` with the CT ID):
```bash
pct stop 100
pct set 100 --features nesting=1,keyctl=1
pct start 100
```

3. Inside the **LXC** — fix the missing `/dev/kmsg` device:
```bash
echo 'L /dev/kmsg - - - - /dev/console' > /etc/tmpfiles.d/kmsg.conf
systemd-tmpfiles --create /etc/tmpfiles.d/kmsg.conf
```

> Note: VM is simpler than LXC for k3s. If the user is creating the environment from scratch, recommend a full VM (Ubuntu 22.04).

**NFS client missing on k3s node**

k3s nodes need `nfs-common` installed or NFS mounts will fail with `bad option; for several filesystems`. Install on the k3s VM/LXC before applying the NFS provisioner:
```bash
sudo apt update && sudo apt install -y nfs-common
```

**`.local` TLD conflicts with mDNS**

Never use `.local` as the TLD for homelab ingress hostnames. On Linux and macOS, `.local` is intercepted by Avahi/mDNS before reaching Pi-hole or any DNS server. Recommend `.home` or `.lan` instead.

**NFS path is case-sensitive**

Linux NFS exports are case-sensitive. Always confirm the exact case of the export path with `showmount -e <NFS_IP>` before writing manifests.

**KUBECONFIG tilde expansion in fish shell**

In fish shell, `~` is not expanded inside `set -x KUBECONFIG ~/.kube/file.yaml`. Use the absolute path instead:
```fish
set -x KUBECONFIG /home/<user>/.kube/kartrack.yaml
```

**00-install.md must label where each command runs**

Users operating from their local machine get confused about which commands run on the VM vs their computer. Each section header in `00-install.md` must explicitly state `(na VM via SSH)` or `(no seu computador)`. The kubeconfig copy step must include the `sed` to replace `127.0.0.1` with the VM IP, and note that fish shell requires absolute paths.

**`kubectl apply -f <dir>` applies files alphabetically → namespace must sort first**

`kubectl apply -f k8s/app/` processes files in alphabetical order and does **not**
reorder by dependency. With plain names, `deployment.yaml` and `ingress.yaml` sort
*before* `namespace.yaml` → first apply fails with `namespaces "<ns>" not found`
(re-running "fixes" it because the ns now exists — confusing). **Always prefix app
manifests with numbers** so order is guaranteed: `00-namespace`, `01-secret`,
`02-pvc`, `03-deployment`, `04-service`, `05-ingress`.

**Never let the real Secret get committed**

Users *will* fill `secret.yaml` with the real API key/password and it's trivially
leaked if committed (Docker Hub/GitHub are often public). Pattern: commit a
template `NN-secret.yaml.example` (placeholders) and **gitignore the real
`NN-secret.yaml`**. Crucially, name the template with a non-manifest extension
(`.yaml.example`) so `kubectl apply -f <dir>` ignores it (kubectl only reads
`.yaml`/`.yml`/`.json`). Add the real filename to `.gitignore` and verify with
`git check-ignore` and `git add -n` before any commit. If a key was already pushed
anywhere, tell the user to rotate it.

**Non-root image + volume = `unable to open database file` / permission denied**

Images that run as a non-root UID (e.g. `1000`) can't write to a freshly
provisioned volume owned by root. Symptom: app crashes on startup writing to its
data dir (SQLite: `sqlite3.OperationalError: unable to open database file`). Fix
with a pod `securityContext`: `runAsUser`/`runAsGroup` + **`fsGroup: <uid>`** —
fsGroup makes the mounted volume group-writable by that gid. Works with the
already-published image; no rebuild needed. (`fsGroup` reliably fixes `local-path`
PVCs; for NFS it depends on the export — see next.)

**NFS `root_squash` blocks pods that write/move files**

If the app *writes or moves* files on an NFS export (not just reads), the export
must allow writes by the pod's uid/gid. With default `root_squash` and no
mapping, runtime file operations fail even though the mount succeeds. Confirm the
export maps/permits the container uid (TrueNAS: maproot/mapall or dataset perms),
and test before deploy: `sudo -u '#1000' touch /mnt/test/.w && rm /mnt/test/.w`.
Flag this as the #1 runtime risk whenever the app writes to NFS.

**Debugging a 404 from the Nginx Ingress**

A 404 almost always means DNS isn't pointing at the ingress IP, or the request
arrived without the matching `Host` header, or the Ingress object wasn't created
(e.g. the apply-ordering bug above). Isolate routing from DNS by hitting the
MetalLB IP directly with the Host header:
`curl -H "Host: app.domain.home" http://<METALLB_IP>/`. A 200/302/303 there proves
the cluster is fine and it's purely a DNS record to create
(`app.domain.home → A → <METALLB_IP>`). Also check `kubectl get ingress -n <ns>`
shows an `ADDRESS`.

---

## Phase 2: Generation

Write all files to `k8s/` in the project root. **Prefix app manifests with
numbers** so `kubectl apply -f k8s/app/` runs them in dependency order (see the
alphabetical-ordering gotcha). The real secret is gitignored; only its
`.example` template is versioned.

```
k8s/
├── 00-install.md              # Full install sequence (copy-paste commands)
├── addons/                    # OMIT this whole dir when reusing existing infra
│   ├── metallb-pool.yaml
│   ├── nginx-ingress-values.yaml
│   └── nfs-provisioner-values.yaml
└── app/
    ├── 00-namespace.yaml
    ├── 01-secret.yaml.example  # template (committed); real 01-secret.yaml is gitignored
    ├── 02-pvc.yaml
    ├── 03-deployment.yaml
    ├── 04-service.yaml
    └── 05-ingress.yaml
```

After generating, also append the real secret filename to `.gitignore`:
```
k8s/app/01-secret.yaml
```

### 00-install.md

Start with a table showing where each component is installed — this is critical to avoid confusion:

```markdown
| Componente | Onde instalar |
|---|---|
| k3s | Na VM do Proxmox (via SSH) |
| kubectl | No seu computador |
| helm | No seu computador |
| MetalLB | Aplicado via kubectl do seu computador |
| Nginx Ingress | Aplicado via helm do seu computador |
| NFS Provisioner | Aplicado via helm do seu computador |
| Manifests da app | Aplicados via kubectl do seu computador |
```

Each section header must state where the command runs: `(na VM via SSH)` or `(no seu computador)`.

> **When reusing existing cluster infra**, drop sections 1, 3, 5, 6, 7, 8 — keep
> only the NFS pre-check (`nfs-common` + `showmount` + write test), the kubeconfig
> context, fill-secret, `kubectl apply -f k8s/app/`, and DNS. Don't make the user
> reinstall k3s/MetalLB/ingress they already have.

Sections (full from-scratch install):

1. k3s install **(na VM)**
2. Configure remote access + copy kubeconfig **(no seu computador)** — include `sed` to replace `127.0.0.1` with VM IP; warn fish users to use absolute path, not `~`
3. kubectl + helm install **(no seu computador)**
4. Install `nfs-common` **(na VM)** — must come before NFS provisioner or mounts will fail
5. MetalLB **(no seu computador)**
6. Nginx Ingress **(no seu computador)**
7. NFS Subdir Provisioner **(no seu computador)**
8. MySQL setup **(na VM MySQL)**
9. App deploy: fill secrets + `kubectl apply -f k8s/app/` **(no seu computador)**
10. DNS config

```bash
# === NA VM (via SSH) ===

# 1. k3s
curl -sfL https://get.k3s.io | sh -s - --disable traefik --disable servicelb
sudo kubectl get nodes  # aguarde Ready

# 4. NFS client (obrigatório antes do NFS provisioner)
sudo apt update && sudo apt install -y nfs-common

# === NO SEU COMPUTADOR ===

# 2. Copiar kubeconfig
scp usuario@<IP_DA_VM>:/etc/rancher/k3s/k3s.yaml ~/.kube/<app>.yaml
sed -i 's/127.0.0.1/<IP_DA_VM>/g' ~/.kube/<app>.yaml
# fish shell: use caminho absoluto, não ~
set -x KUBECONFIG /home/<user>/.kube/<app>.yaml
kubectl get nodes

# 5. MetalLB
kubectl apply -f https://raw.githubusercontent.com/metallb/metallb/v0.14.5/config/manifests/metallb-native.yaml
kubectl wait --namespace metallb-system --for=condition=ready pod --selector=app=metallb --timeout=120s
kubectl apply -f k8s/addons/metallb-pool.yaml

# 6. Nginx Ingress
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx && helm repo update
helm upgrade --install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx --create-namespace \
  --values k8s/addons/nginx-ingress-values.yaml \
  --wait

# 7. NFS Subdir Provisioner
helm repo add nfs-subdir-external-provisioner \
  https://kubernetes-sigs.github.io/nfs-subdir-external-provisioner/ && helm repo update
helm upgrade --install nfs-subdir-external-provisioner \
  nfs-subdir-external-provisioner/nfs-subdir-external-provisioner \
  --namespace nfs-provisioner --create-namespace \
  --values k8s/addons/nfs-provisioner-values.yaml \
  --wait

# 9. App
kubectl apply -f k8s/app/
kubectl rollout status deployment/<app-name> -n <namespace>
kubectl get all -n <namespace>
```

### metallb-pool.yaml

```yaml
apiVersion: metallb.io/v1beta1
kind: IPAddressPool
metadata:
  name: homelab-pool
  namespace: metallb-system
spec:
  addresses:
    - <METALLB_RANGE>          # e.g., 192.168.1.241-192.168.1.254
---
apiVersion: metallb.io/v1beta1
kind: L2Advertisement
metadata:
  name: homelab-l2
  namespace: metallb-system
spec:
  ipAddressPools:
    - homelab-pool
```

### App manifests — key rules

**secret**: write the template as `NN-secret.yaml.example` with `stringData` +
`<CHANGE_ME>` placeholders (committed). The real `NN-secret.yaml` is created by
the user (`cp` the example) and **gitignored**. Never write real values into a
versioned file. Comment the `cp` step and the `token_hex(32)` generation.

**pvc.yaml**: pick storage by data type, not a blanket default:
- App-generated *shared* data → `ReadWriteMany`, NFS StorageClass.
- File-based DB / SQLite → `ReadWriteOnce`, `storageClassName: local-path` (avoids NFS lock corruption).
- Pre-existing files on the NAS → **not a PVC against the provisioner**; a direct `nfs:` volume in the Deployment (or a static PV) at the exact export path.

**deployment.yaml**:
- `imagePullPolicy: IfNotPresent` for public Docker Hub
- Mount the data PVC at the exact container path from docker-compose; mount NFS volumes at the **exact path the app config expects** (so first-boot seed works)
- Add a pod `securityContext` (`runAsUser`/`runAsGroup`/`fsGroup`) matching the image's UID whenever it runs non-root and writes to a volume
- For a single-writer/file-DB app: `replicas: 1` + `strategy: { type: Recreate }` (never two pods on the same file during a rollout)
- Add `livenessProbe`/`readinessProbe` on the app's health endpoint
- Use `envFrom.secretRef` for all secret env vars; use plain `env` only for non-secret vars (e.g., `TZ`)
- No resource limits by default for homelab (adds complexity without benefit at this scale)

**ingress.yaml**:
- `ingressClassName: nginx`
- No `tls:` block when TLS is external
- Add `nginx.ingress.kubernetes.io/proxy-body-size` annotation if the app handles file uploads (match the limit from docker-compose or nginx config if present)

### After generating files

Tell the user:
1. How to find all placeholders: `grep -r '<' k8s/`
2. Copy and fill the secret: `cp k8s/app/NN-secret.yaml.example k8s/app/NN-secret.yaml`, then edit. Confirm it's gitignored (`git check-ignore`) and not staged (`git add -n`) before committing.
3. Apply order: addons first (if any), then `kubectl apply -f k8s/app/` (numeric prefixes keep it ordered)
4. How to verify: `kubectl get all -n <namespace>`; pod `Running 1/1` and ingress has an `ADDRESS`
5. DNS: create `A <hostname> → <MetalLB ingress IP>` (the shared ingress IP, same for all apps). If 404, debug with `curl -H "Host: <hostname>" http://<MetalLB_IP>/` to isolate DNS from routing.
6. If Newt/Pangolin is in use: configure it to point to the MetalLB IP on port 80
