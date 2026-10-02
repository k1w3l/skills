# Acesso — usuários, tokens, grupos, ACLs e roles

**Verificado em:** 2026-07-28

> ⚠️ **Leia isto antes de confiar em qualquer token:** os grupos `api-users` e `hass-users` têm
> ACL `Administrator` em `/`. As roles customizadas `horus` e `homarr` existem e são restritivas,
> mas o ACL de grupo as **sobrepõe**. Na prática, os tokens do Horus, do Homarr e do Home
> Assistant têm poder total sobre o Proxmox. Ver `issues.md` #6.

## Usuários

| Usuário | Realm | Habilitado | E-mail / Nome |
|---|---|---|---|
| `root@pam` | PAM | ✅ | kiwel.01@gmail.com |
| `pulse-monitor@pam` | PAM | ✅ | Pulse monitoring service |
| `kiwel@pve` | PVE | ✅ | — |
| `hass@pve` | PVE | ✅ | — |
| `homarr@pve` | PVE | ✅ | — |
| `horus@pve` | PVE | ✅ | — |
| **`kiwel@Authentik`** | **OpenID** | ✅ | Eduardo Kiwel — kiwel01@gmail.com |

SSO via OIDC contra o **Authentik (CT 122, 192.168.1.22)** configurado e funcional.

## Tokens de API

| Token | Dono | Finalidade |
|---|---|---|
| `hass@pve!hass` | hass@pve | Integração Home Assistant (VM 109) |
| `homarr@pve!homarr` | homarr@pve | Dashboard Homarr |
| `horus@pve!horus` | horus@pve | Projeto Horus (observabilidade, `~/git/horus`) |
| `pulse-monitor@pam!pulse-token` | pulse-monitor@pam | Pulse |
| `pulse-monitor@pam!pulse-192-168-1-202-1764594859` | pulse-monitor@pam | Pulse (instância local) |
| `pulse-monitor@pam!pulse-pulse-kiwel-uk-1768916247` | pulse-monitor@pam | Pulse (instância remota) |
| `root@pam!terraform` | root@pam | Provisionamento Terraform |

Os segredos ficam fora desta skill. O do Horus está em `~/git/horus/.env`.

> **Nota sobre o Horus:** o projeto foi desenhado com *privilege separation* — dois tokens, um
> `read` e um `control`. Hoje o `.env` usa **o mesmo token para os dois papéis**, e esse token é
> Administrator. A separação existe só no código.

## Grupos

```
group:api-users:   homarr@pve, horus@pve
group:hass-users:  hass@pve
group:root:        kiwel@Authentik, kiwel@pve, root@pam
```

## ACLs

```
acl:1:/         :@api-users, @hass-users, @root, hass@pve!hass, kiwel@Authentik, kiwel@pve
                 → Administrator
acl:1:/         :pulse-monitor@pam    → PVEAuditor, PulseMonitor
acl:1:/         :homarr@pve           → homarr
acl:1:/storage  :pulse-monitor@pam    → PVEDatastoreAdmin
```

## Roles customizadas

| Role | Privilégios |
|---|---|
| `PulseMonitor` | `Sys.Audit`, ~~`VM.Monitor`~~ |
| `homarr` | `Datastore.AllocateSpace`, `Datastore.Audit`, `Pool.Audit`, `Sys.Audit`, `VM.Audit`, ~~`VM.Monitor`~~ |
| `horus` | 40+ privilégios — `Datastore.Allocate`, `Datastore.AllocateSpace`, `Datastore.AllocateTemplate`, `Datastore.Audit`, `Group.Allocate`, `Mapping.Audit/Modify/Use`, `Permissions.Modify`, `Pool.Allocate/Audit`, `Realm.Allocate/AllocateUser`, `SDN.Allocate/Audit/Use`, `Sys.AccessNetwork`, `Sys.Audit`, `Sys.Console`, `Sys.Incoming`, `Sys.Modify`, `Sys.PowerMgmt`, `Sys.Syslog`, `User.Modify`, `VM.Allocate`, `VM.Audit`, `VM.Backup`, `VM.Clone`, `VM.Config.*`, `VM.Console`, `VM.Migrate`, `VM.PowerMgmt`, `VM.Snapshot`, `VM.Snapshot.Rollback`, ~~`VM.Monitor`~~ |

### O privilégio `VM.Monitor` não existe mais

**`VM.Monitor` foi removido no PVE 9.** As três roles ainda o referenciam, o que faz **toda**
invocação de `qm`, `pct`, `pvesm` e `pvesh` imprimir:

```
user config - ignore invalid privilege 'VM.Monitor'
```

Isso é **ruído conhecido, não é falha** — mas polui a saída de todo comando e pode ser confundido
com erro em diagnósticos. Editar as três roles para remover o privilégio elimina o ruído.
Ver `issues.md` #15.

### Sobre a role `horus`

Além de ser irrelevante hoje (o grupo dá Administrator), a role inclui `Permissions.Modify`,
`User.Modify` e `Realm.Allocate` — privilégios de **escalação** que não têm relação nenhuma com
observabilidade. Se a ACL for corrigida, a role também deve ser enxugada.

## Acesso SSH

Chave já configurada para `root@192.168.1.5` a partir do PCL (`~/.ssh/id_ed25519`).
Os templates de VM (1000, 2000) e as VMs cloud-init carregam duas chaves públicas:
uma FIDO/`sk-ecdsa` (Termius) e uma ECDSA.

`sshd` escuta em `0.0.0.0:22` e `[::]:22`.
