# Kartrack — Plano de Deploy no k3s (Phase 1)

## Análise do Codebase

Extraído de `docker-compose.yml`, `Dockerfile` e `backend/app/config.py`:

| Campo | Valor |
|---|---|
| Imagem | `kiwel/kartrack:v1` |
| Porta do container | `8000` (uvicorn) |
| Volume | `./uploads/vehicles` → `/app/uploads/vehicles` |
| Env vars obrigatórias | `SECRET_KEY`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `DB_NAME` |
| Upload máximo (nginx.conf.example) | `20M` |
| TZ | `America/Sao_Paulo` |

O container é monolítico: serve o frontend React (dist embutido no build) e a API FastAPI na mesma porta 8000. O frontend é servido como arquivos estáticos pelo próprio uvicorn/FastAPI.

---

## 1. Diagrama de Dependências

```
Internet (Cloudflare / Pangolin)
  │  TLS termina externamente — HTTP puro dentro do cluster
  │
Nginx Ingress Controller ←── MetalLB L2 (IP pool 192.168.1.241-192.168.1.254)
  │  kartrack.kiwel.dev → ClusterIP:8000
  │
Service (ClusterIP) kartrack:8000
  │
Deployment kartrack
  │  imagePullPolicy: IfNotPresent (Docker Hub público)
  ├── Secret (SECRET_KEY, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME)
  ├── env TZ: America/Sao_Paulo (não-secret)
  │
  └── PVC kartrack-uploads (ReadWriteMany, StorageClass nfs-client)
        │
        NFS TrueNAS: 192.168.1.10:/mnt/pool/kartrack-uploads
          (montado em /app/uploads/vehicles no container)

Dependências externas:
  MySQL 8 VM: 192.168.1.50:3306 (db: kartrack, user: kartrack)
  FIPE API: https://fipe.parallelum.com.br/api/v2 (chamada outbound)
```

---

## 2. Tabela de Trade-offs

| Decisão | Escolha | Justificativa |
|---|---|---|
| Distribuição K8s | k3s `--disable traefik --disable servicelb` | Leve, sem conflito com MetalLB nem Traefik |
| Load Balancer | MetalLB L2 mode | Sem necessidade de BGP em homelab; L2 é suficiente |
| Ingress Controller | ingress-nginx via Helm | Padrão de fato; suporta annotations de proxy-body-size |
| Storage | NFS Subdir External Provisioner (StorageClass `nfs-client`, RWX) | TrueNAS já disponível; RWX facilita escala futura sem recriar PVC |
| Banco de dados | MySQL externo (VM 192.168.1.50) | Stateful workload fora do cluster = operação mais simples, backup independente |
| TLS | Externo (Cloudflare/Pangolin) | TLS termina antes do cluster; Ingress serve HTTP puro — correto e intencional |
| cert-manager | Não instalado | Desnecessário quando TLS é externo |
| Registry | Docker Hub público | `imagePullPolicy: IfNotPresent` evita rate limits |
| Replicas | 1 (single-node k3s) | Single-node não ganha nada com mais réplicas sem anti-affinity |

---

## 3. Riscos e Mitigações

| # | Risco | Mitigação |
|---|---|---|
| 1 | **NFS indisponível** causa CrashLoopBackOff no pod (volume não monta) | Monitorar TrueNAS uptime; o PVC usa `Retain` — dados não são perdidos se o pod reiniciar |
| 2 | **MySQL VM fora do ar** — app sobe mas todas as requisições falham com 500 | Configurar `livenessProbe`/`readinessProbe` no deployment; app só recebe tráfego quando DB responder |
| 3 | **Rate limit Docker Hub** em pulls frequentes | `imagePullPolicy: IfNotPresent` garante que o pull só ocorre na primeira vez por nó |
| 4 | **Upload de foto > 20M bloqueado pelo Ingress** | Annotation `nginx.ingress.kubernetes.io/proxy-body-size: 20m` espelha o `client_max_body_size` do nginx.conf.example |
| 5 | **FIPE API outbound** pode falhar em redes com firewall egress restritivo | A falha é silenciosa (try/except no código) — não impacta o funcionamento geral, mas o valor FIPE não atualiza |
| 6 | **Secret.yaml em git** com valores reais | O arquivo gerado usa placeholders `<CHANGE_ME>`; nunca commitar com valores reais; usar `.gitignore` ou external-secrets em produção |

---

## 4. Ordem de Instalação

1. **Provisionar k3s** no nó Proxmox com `--disable traefik --disable servicelb`
2. **Instalar MetalLB** (manifest) e aplicar `metallb-pool.yaml` com o range `192.168.1.241-192.168.1.254`
3. **Instalar ingress-nginx** via Helm — MetalLB alocará um IP do pool para o Service `LoadBalancer` do controller
4. **Instalar NFS Subdir External Provisioner** via Helm apontando para `192.168.1.10:/mnt/pool/kartrack-uploads`
5. **Verificar MySQL VM** — garantir que `192.168.1.50:3306` está acessível a partir do nó k3s (`mysql -h 192.168.1.50 -u kartrack -p`)
6. **Preencher `k8s/app/secret.yaml`** com os valores reais (substituir todos os `<CHANGE_ME>`)
7. **Aplicar manifests da app**: `kubectl apply -f k8s/app/`
8. **Verificar rollout**: `kubectl rollout status deployment/kartrack -n kartrack`
9. **Configurar Pangolin/Newt** para apontar `kartrack.kiwel.dev` → IP MetalLB alocado na porta 80

---

## 5. Tabela de Design Final

| Componente | Valor |
|---|---|
| Namespace | `kartrack` |
| Imagem | `kiwel/kartrack:v1` |
| ImagePullPolicy | `IfNotPresent` |
| Porta | `8000` |
| Service type | `ClusterIP` |
| Ingress class | `nginx` |
| Hostname | `kartrack.kiwel.dev` |
| TLS no Ingress | Não (externo) |
| proxy-body-size | `20m` |
| PVC access mode | `ReadWriteMany` |
| StorageClass | `nfs-client` |
| NFS server | `192.168.1.10` |
| NFS path | `/mnt/pool/kartrack-uploads` |
| Volume mount | `/app/uploads/vehicles` |
| DB host | `192.168.1.50` |
| DB port | `3306` |
| MetalLB pool | `192.168.1.241-192.168.1.254` |

---

## Próximos Passos

Todos os manifests foram gerados em `k8s/`. Antes de aplicar:

1. Localizar todos os placeholders: `grep -r '<' k8s/`
2. Editar **obrigatoriamente** `k8s/app/secret.yaml` com os valores reais
3. Aplicar na ordem: addons primeiro, depois app:
   ```bash
   kubectl apply -f k8s/addons/metallb-pool.yaml
   # (ingress-nginx e nfs-provisioner via Helm — ver 00-install.md)
   kubectl apply -f k8s/app/
   kubectl rollout status deployment/kartrack -n kartrack
   ```
4. Verificar: `kubectl get all -n kartrack`
5. Configurar Pangolin/Newt para apontar `kartrack.kiwel.dev` → IP MetalLB na porta 80
