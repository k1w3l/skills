# Kartrack — Plano de Deploy no k3s

## Visão Geral da Arquitetura

O Kartrack é uma aplicação monolítica: frontend React (servido como arquivos estáticos pelo FastAPI via `StaticFiles`) e backend FastAPI no mesmo container, imagem `kiwel/kartrack:v1` no Docker Hub público. O banco MySQL já existe numa VM dedicada, e os uploads de veículos precisam ser persistidos num volume NFS do TrueNAS.

```
Internet → Cloudflare/Pangolin (TLS) → kartrack.kiwel.dev
              ↓ HTTP (plain, confiando no X-Forwarded-Proto)
         k3s Node → MetalLB LoadBalancer (192.168.1.241-254)
              ↓
         Service (ClusterIP) → Deployment (kiwel/kartrack:v1)
              ↓                        ↓
         NFS PVC (uploads)     MySQL 192.168.1.50:3306
```

---

## Estrutura dos Manifests

```
k8s/
├── base/
│   └── namespace.yaml
├── storage/
│   ├── nfs-pv.yaml
│   └── nfs-pvc.yaml
└── app/
    ├── secret.yaml
    ├── deployment.yaml
    ├── service.yaml
    └── ingress.yaml
```

---

## Decisões de Design

### Por que sem Ingress Controller?
Com TLS terminando externamente no Cloudflare/Pangolin, o cluster só precisa expor HTTP. Optei por um `Service` do tipo `LoadBalancer` (MetalLB) que recebe tráfego na porta 80. Isso é suficiente e evita a camada extra de um Ingress Controller. Um `Ingress` com `ingressClassName: traefik` (padrão do k3s) também é fornecido como opção.

### Variáveis de Ambiente Sensíveis
Todas as credenciais ficam num `Secret` em Base64. Em produção, considere usar `sealed-secrets` ou External Secrets Operator para não comitar o secret com valores reais no git.

### NFS para Uploads
O volume NFS aponta para `192.168.1.10:/mnt/pool/kartrack-uploads`. O container monta este volume em `/app/uploads`, que é exatamente o `UPLOAD_ROOT` do código (`Path("uploads")`). O código cria os subdiretórios `vehicles/` em runtime via `VEHICLE_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)`.

### Health Check
O FastAPI expõe `GET /health` que retorna `{"status": "ok"}`. Usado como liveness e readiness probe.

### Single Replica
k3s single node, portanto `replicas: 1`. Para upgrade sem downtime use `RollingUpdate` com `maxUnavailable: 0` (já configurado).

---

## Checklist de Deploy

1. **Criar namespace:**
   ```bash
   kubectl apply -f k8s/base/namespace.yaml
   ```

2. **Configurar NFS no k3s node** (se necessário):
   ```bash
   # No node k3s
   sudo apt install nfs-common   # ou dnf/pacman conforme distro
   ```

3. **Criar PV e PVC:**
   ```bash
   kubectl apply -f k8s/storage/nfs-pv.yaml
   kubectl apply -f k8s/storage/nfs-pvc.yaml
   ```

4. **Verificar binding do PVC:**
   ```bash
   kubectl get pvc -n kartrack
   # STATUS deve ser Bound
   ```

5. **Editar secret com valores reais** (os valores já estão corretos conforme o enunciado):
   ```bash
   kubectl apply -f k8s/app/secret.yaml
   ```

6. **Deploy da aplicação:**
   ```bash
   kubectl apply -f k8s/app/deployment.yaml
   kubectl apply -f k8s/app/service.yaml
   ```

7. **Aguardar pod Ready:**
   ```bash
   kubectl rollout status deployment/kartrack -n kartrack
   kubectl get pods -n kartrack
   ```

8. **Verificar IP do LoadBalancer (MetalLB):**
   ```bash
   kubectl get svc kartrack -n kartrack
   # EXTERNAL-IP deve mostrar um IP do range 192.168.1.241-254
   ```

9. **Configurar DNS/Pangolin:**
   - Aponte `kartrack.kiwel.dev` para o IP externo obtido acima no seu Pangolin/Cloudflare Tunnel.

10. **Aplicar Ingress (opcional, se usar Traefik):**
    ```bash
    kubectl apply -f k8s/app/ingress.yaml
    ```

---

## Verificação Pós-Deploy

```bash
# Logs do pod
kubectl logs -n kartrack -l app=kartrack --tail=50 -f

# Teste de health direto no cluster
kubectl exec -n kartrack -it $(kubectl get pod -n kartrack -l app=kartrack -o jsonpath='{.items[0].metadata.name}') -- curl -s localhost:8000/health

# Teste externo (após DNS propagado)
curl https://kartrack.kiwel.dev/health
```

---

## Notas Importantes

- **SECRET_KEY**: O valor `change-me-in-production-use-openssl-rand-base64-32` deve ser substituído por um valor seguro gerado com `openssl rand -base64 32` antes do primeiro deploy.
- **Timezone**: A variável `TZ=America/Sao_Paulo` está configurada no Deployment para manter consistência com o Docker Compose original.
- **Branding estático**: Os arquivos `logo_light.png`, `logo_dark.png`, `favicon.ico` em `uploads/` estão no diretório raiz do volume NFS. Se não existirem no TrueNAS, você pode copiá-los de `backend/arquivos/` do repositório para o share NFS via `cp` ou `rsync`.
- **Primeiro acesso**: O primeiro usuário registrado em `/api/auth/register` automaticamente vira admin (`is_admin=True`).
- **Banco de dados**: O `init_db()` é chamado no startup e cria todas as tabelas via `Base.metadata.create_all`. Não há migrations — se o banco já tiver dados, nenhuma tabela existente será destruída.
