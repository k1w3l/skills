# Kartrack — Sequência de Instalação Completa no k3s

Execute os comandos abaixo **em ordem**, no nó Proxmox que será o master k3s.

---

## 1. k3s

```bash
# Instalar k3s desabilitando Traefik e ServiceLB (usaremos Nginx Ingress + MetalLB)
curl -sfL https://get.k3s.io | sh -s - --disable traefik --disable servicelb

# Configurar kubeconfig para o usuário atual
mkdir -p ~/.kube
sudo cp /etc/rancher/k3s/k3s.yaml ~/.kube/config
sudo chown $(id -u):$(id -g) ~/.kube/config

# Verificar que o nó está Ready
kubectl get nodes
```

---

## 2. MetalLB

```bash
# Aplicar manifest do MetalLB
kubectl apply -f https://raw.githubusercontent.com/metallb/metallb/v0.14.5/config/manifests/metallb-native.yaml

# Aguardar pods do MetalLB ficarem prontos
kubectl wait --namespace metallb-system \
  --for=condition=ready pod \
  --selector=app=metallb \
  --timeout=120s

# Aplicar pool de IPs e L2Advertisement
kubectl apply -f k8s/addons/metallb-pool.yaml

# Verificar
kubectl get ipaddresspool -n metallb-system
kubectl get l2advertisement -n metallb-system
```

---

## 3. Nginx Ingress Controller

```bash
# Adicionar repo Helm
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update

# Instalar ingress-nginx (MetalLB alocará um IP do pool)
helm upgrade --install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace \
  --values k8s/addons/nginx-ingress-values.yaml \
  --wait

# Verificar IP externo alocado pelo MetalLB
kubectl get svc -n ingress-nginx ingress-nginx-controller
# EXTERNAL-IP deve ser um IP do range 192.168.1.241-192.168.1.254
```

---

## 4. NFS Subdir External Provisioner

```bash
# Adicionar repo Helm
helm repo add nfs-subdir-external-provisioner \
  https://kubernetes-sigs.github.io/nfs-subdir-external-provisioner/
helm repo update

# Instalar provisioner apontando para o TrueNAS
helm upgrade --install nfs-subdir-external-provisioner \
  nfs-subdir-external-provisioner/nfs-subdir-external-provisioner \
  --values k8s/addons/nfs-provisioner-values.yaml \
  --namespace nfs-provisioner \
  --create-namespace \
  --wait

# Verificar StorageClass criada
kubectl get storageclass nfs-client
```

---

## 5. Pré-flight: verificar acesso ao MySQL externo

```bash
# Instalar cliente MySQL no nó (se não tiver)
# apt install -y mysql-client  (Debian/Ubuntu)

# Testar conectividade antes de subir o app
mysql -h 192.168.1.50 -P 3306 -u kartrack -p kartrack -e "SELECT 1;"
# Deve retornar: 1
```

---

## 6. App Kartrack

```bash
# IMPORTANTE: editar secret.yaml ANTES de aplicar
# grep -r '<' k8s/app/secret.yaml  -- listar placeholders
# Substituir todos os <CHANGE_ME> pelos valores reais

# Aplicar todos os manifests da app
kubectl apply -f k8s/app/

# Acompanhar rollout
kubectl rollout status deployment/kartrack -n kartrack

# Verificar todos os recursos
kubectl get all -n kartrack
kubectl get pvc -n kartrack
kubectl get ingress -n kartrack
```

---

## 7. Configurar Pangolin / Newt (TLS externo)

1. Descobrir o IP alocado pelo MetalLB para o Ingress:
   ```bash
   kubectl get svc -n ingress-nginx ingress-nginx-controller \
     -o jsonpath='{.status.loadBalancer.ingress[0].ip}'
   ```
2. No painel do Pangolin, criar um tunnel/route apontando:
   - Domínio: `kartrack.kiwel.dev`
   - Target: `http://<IP-METALB>:80`
3. TLS é terminado pelo Cloudflare/Pangolin — o tráfego dentro do cluster é HTTP puro (correto e intencional).

---

## Verificação final

```bash
# Todos os pods devem estar Running
kubectl get pods -n kartrack

# Logs do app
kubectl logs -n kartrack deployment/kartrack --tail=50

# Teste HTTP direto no IP MetalLB (sem TLS)
INGRESS_IP=$(kubectl get svc -n ingress-nginx ingress-nginx-controller \
  -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
curl -H "Host: kartrack.kiwel.dev" http://${INGRESS_IP}/api/health
```
