# Rede — topologia, IPs, MACs e firewall

**Verificado em:** 2026-09-23 para o mapa de IPs dos guests (guest agent + `pct config`). Topologia da bridge continua a de 2026-08-05.

## Topologia

Configuração **plana e simples**: uma única bridge, sem VLANs, sem bonding, sem SDN.

Nomes de NIC **fixados por MAC** via systemd `.link` (prep. remoção da Quadro K600):

| Nome estável | MAC | Hardware | Papel |
|---|---|---|---|
| **`lan0`** | `90:de:80:b7:7e:12` | RTL8125 2.5GbE (`10-lan0.link`) | bridge `vmbr0` |
| **`lan1`** | `d8:43:ae:a0:8a:5a` | RTL8111 1GbE (`11-lan1.link`) | sem cabo; `pve-power-tune` mantém down |

> Até o próximo reboot o kernel ainda mostra `enp6s0`/`enp4s0`. Depois do reboot de
> validação (K600 ainda instalada) devem aparecer `lan0`/`lan1`.

```
                    ┌─ lan1 (RTL8111 1GbE) — DOWN, ociosa
Internet ─ router ──┤
   192.168.1.1      └─ lan0 (RTL8125 2.5GbE) ── vmbr0 ── 192.168.1.5/24
                                                     │
      ┌──────────────────────────────────────────────┴──────────────────────┐
      │                                                                     │
   tap100i0 tap101i0 tap116i0 tap124i0 tap126i0        veth102..123 (14 LXC)
   (VMs sem firewall na NIC)                            (todos em vmbr0)
      │
   fwbr103i0 / fwbr109i0 / fwbr114i0  ← bridges de firewall (VMs 103, 109, 114)
```

### `/etc/network/interfaces`

```ini
auto lo
iface lo inet loopback

iface lan0 inet manual

auto vmbr0
iface vmbr0 inet static
    address 192.168.1.5/24
    gateway 192.168.1.1
    bridge-ports lan0
    bridge-stp off
    bridge-fd 0

iface lan1 inet manual
    # sem cabo; pve-power-tune mantém down

source /etc/network/interfaces.d/*
```

- Rota padrão: `default via 192.168.1.1 dev vmbr0`
- IPv6: apenas link-local (`fe80::92de:80ff:feb7:7e12/64`), sem endereçamento global
- STP desabilitado · MAC da bridge `90:de:80:b7:7e:12`
- `lan1` (1 GbE) livre — disponível para bond LACP ou rede de storage dedicada
- Arquivos: `/etc/systemd/network/10-lan0.link`, `11-lan1.link`

## Mapa de endereçamento

| IP | Guest | Tipo | Serviço |
|---|---|---|---|
| 192.168.1.1 | — | router | gateway + DNS upstream |
| **192.168.1.5** | **proxmox** | host | Proxmox VE (8006) |
| 192.168.1.6 | VM 116 | VM | Jarvis (agente IA) |
| 192.168.1.9 | CT 121 | LXC | Pi-hole (DNS) |
| 192.168.1.10 | CT 112 | LXC | Web |
| 192.168.1.11 | VM 100 | VM | TrueNAS SCALE (NFS/SMB) |
| 192.168.1.12 | CT 113 | LXC | Nexterm (`:6989`) |
| 192.168.1.13 | CT 102 | LXC | Stalwart (mail) |
| 192.168.1.14 | CT 107 | LXC | OpenBao (`:8200`) |
| 192.168.1.16 | CT 104 | LXC | karakeep |
| 192.168.1.17 | CT 105 | LXC | Vaultwarden |
| 192.168.1.18 | CT 108 | LXC | MariaDB (Alpine) |
| 192.168.1.19 | CT 125 | LXC | Vikunja (`:3456`) |
| 192.168.1.20 | CT 123 | LXC | PostgreSQL |
| 192.168.1.21 | CT 106 | LXC | Gotify (notificações) |
| 192.168.1.22 | CT 122 | LXC | Authentik (SSO) |
| 192.168.1.23 | CT 117 | LXC | Nginx Proxy Manager |
| 192.168.1.24 | VM 124 | VM | Immich |
| 192.168.1.25 | CT 110 | LXC | Uptime-Kuma (`:3001`) |
| 192.168.1.26 | CT 118 | LXC | Filebrowser |
| 192.168.1.28 | CT 120 | LXC | Pangolin (túnel) |
| 192.168.1.34 | CT 111 | LXC | Gitea (SSH em `:222`) |
| 192.168.1.40 | VM 101 | VM | Docker host |
| 192.168.1.42 | VM 103 | VM | Proxmox Backup Server |
| 192.168.1.46 | VM 114 | VM | Windows 11 (Plex / GoodSync) |
| 192.168.1.47 | VM 109 | VM | Home Assistant OS |
| 192.168.1.241 | VM 126 | VM | k3s (API `:6443`) |

Fora dos guests, já ocupados: `.1` MikroTik, `.2` X60, `.4` switch 2.5G, `.7` PCL. O `.29` aparece só como alvo velho do Uptime Kuma, não como guest. Faixas ainda sem dono conhecido no Proxmox: .8, .15, .27, .30–.33, .35–.39, .41, .43–.45, .48+.

### Redes internas dos guests

| Rede | Onde |
|---|---|
| `172.16.0.1` | docker0 dentro do TrueNAS (VM 100) |
| `192.168.128.1` | VM 101 (Docker) |
| `172.30.32.1` | supervisor do Home Assistant (VM 109) |
| `172.18.0.1` | docker da Immich (VM 124) |
| `10.42.0.0/16` | pods do k3s (VM 126, flannel) |

## Endereços MAC

| Guest | MAC | Guest | MAC |
|---|---|---|---|
| 100 TrueNAS | `66:A0:BA:7B:79:51` | 108 alpine-mariadb | `BC:24:11:9B:41:8F` |
| 101 Docker | `BC:24:11:BC:28:90` | 110 Uptime-Kuma | `BC:24:11:3A:31:6B` |
| 103 BackupServer | `EA:A2:EA:42:EB:8B` | 111 Gitea | `BC:24:11:ED:55:D5` |
| 109 Hassio | `5E:CF:EE:75:07:82` | 112 Web | `BC:24:11:82:16:06` |
| 114 W11 | `E6:7E:44:5D:C1:3B` | 117 nginx | `BC:24:11:3C:A7:19` |
| 116 Jarvis | `BC:24:11:DC:49:4D` | 118 Filebrowser | `BC:24:11:04:70:B9` |
| 124 Immich | `BC:24:11:85:FA:5F` | 120 Pangolin | `BC:24:11:E3:3C:EA` |
| 126 K3s | `BC:24:11:89:06:8F` | 121 Pihole | `BC:24:11:0C:F3:ED` |
| 102 Stalwart | `BC:24:11:62:8D:F0` | 122 Authentik | `BC:24:11:68:C5:E8` |
| 104 karakeep | `BC:24:11:9F:56:E9` | 123 Postgres | `BC:24:11:84:D9:D9` |
| 105 vaultwarden | `BC:24:11:6F:36:A3` | 107 Ubuntu (tpl) | `BC:24:11:8E:6D:D2` |
| 106 gotify | `BC:24:11:9D:B5:3C` | 1000 rockyt (tpl) | `BC:24:11:F1:36:BE` |
| — | — | 2000 ubuntu (tpl) | `BC:24:11:23:2E:1F` |

## Firewall

Serviço `pve-firewall` **ativo**, mas **sem nenhuma regra**:

- `/etc/pve/firewall/cluster.fw` — vazio/ausente
- `/etc/pve/nodes/proxmox/host.fw` — vazio/ausente
- Nenhum `<vmid>.fw`

Três VMs têm `firewall=1` na NIC — **103, 109, 114** — o que cria as bridges `fwbr103i0`,
`fwbr109i0`, `fwbr114i0`, mas sem ruleset nenhum aplicado. **Na prática o firewall não filtra
nada em lugar nenhum.** Ver `issues.md` #16.

## Portas em escuta no host

| Porta | Serviço | Bind |
|---|---|---|
| 22 | sshd | `0.0.0.0` + `[::]` |
| **111** | rpcbind | `0.0.0.0` + `[::]` — sem uso aparente, ver `issues.md` #18 |
| **3493** | `upsd` (NUT) | `0.0.0.0` |
| 3128 | spiceproxy | `*` |
| **8006** | pveproxy (interface web) | `*` |
| 85 | pvedaemon | `127.0.0.1` (local) |
| 25 | postfix | `127.0.0.1` + `[::1]` (local) |

## Exposição externa

- **Pangolin** (CT 120) — túnel reverso, alto tráfego (19,5 GB in / 21,1 GB out)
- **Nginx Proxy Manager** (CT 117) — reverse proxy com `/dev/net/tun`
- **Gotify** publicado em `https://push.kiwel.uk`
- Instância remota de Pulse (`pulse-kiwel-uk`) consome a API

## Tráfego acumulado notável

| Guest | In | Out |
|---|---|---|
| **VM 114 (W11)** | **2,64 TB** | **2,65 TB** |
| VM 109 (Hassio) | 127 GB | 64,7 GB |
| VM 101 (Docker) | 12,8 GB | 46,7 GB |
| CT 120 (Pangolin) | 19,5 GB | 21,1 GB |
| CT 118 (Filebrowser) | 537 MB | 17,5 GB |
| CT 102 (Stalwart) | 7,0 GB | 217 MB |

O volume da VM 114 é desproporcional e não foi investigado.
