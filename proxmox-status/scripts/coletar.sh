#!/usr/bin/env bash
# Coleta o estado completo do Proxmox do Kiwel e grava um arquivo por área.
#
# Uso:  ./coletar.sh [diretorio-destino]
# Ex.:  ./coletar.sh /tmp/pve-2026-08-15
#
# Sem argumento, grava em ./coleta-<data>. Cada área vira um .txt, o que torna
# trivial comparar duas coletas com `diff -r` e enxergar exatamente o que mudou
# desde a última atualização do estado da skill.
#
# Não altera nada no host — só leitura.

set -uo pipefail

PVE_HOST="${PVE_HOST:-192.168.1.5}"
PVE_USER="${PVE_USER:-root}"
SSH="ssh -o ConnectTimeout=10 ${PVE_USER}@${PVE_HOST}"

DEST="${1:-./coleta-$(date +%Y-%m-%d)}"
mkdir -p "$DEST" || exit 1

echo "Coletando de ${PVE_USER}@${PVE_HOST} → ${DEST}"

if ! $SSH -o BatchMode=yes true 2>/dev/null; then
  echo "ERRO: sem acesso SSH por chave a ${PVE_USER}@${PVE_HOST}." >&2
  exit 1
fi

run() { # run <arquivo> <comando remoto>
  printf '  %-16s' "$1"
  $SSH "$2" > "${DEST}/$1.txt" 2>&1
  echo "ok ($(wc -l < "${DEST}/$1.txt") linhas)"
}

run versao '
  echo "### pveversion"; pveversion -v
  echo "### node status"; pvesh get /nodes/proxmox/status --output-format json
  echo "### uptime"; uptime; hostname -f; cat /etc/resolv.conf
  echo "### datacenter.cfg"; cat /etc/pve/datacenter.cfg
  echo "### subscription"; pvesubscription get
  echo "### repos"; grep -rh . /etc/apt/sources.list.d/ | grep -vE "^\s*#|^\s*$"
  echo "### cluster"; pvecm status 2>&1 | head -20
'

run hardware '
  echo "### lscpu"; lscpu
  echo "### memoria"; free -h
  echo "### dmidecode"; dmidecode -t system -t baseboard -t bios
  echo "### modulos ram"; dmidecode -t memory | grep -E "Size|Speed|Manufacturer|Part Number|Locator|Type:|Rank"
  echo "### sensores"; sensors
  echo "### pci"; lspci -nnk
  echo "### iommu"; for g in /sys/kernel/iommu_groups/*/devices/*; do n=${g%%/devices/*}; echo "grupo ${n##*/}: $(lspci -nns ${g##*/})"; done | sort -V
  echo "### cmdline"; cat /proc/cmdline
  echo "### modprobe"; grep -r . /etc/modprobe.d/ 2>/dev/null | grep -v "^Binary"
'

run discos '
  echo "### lsblk"; lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINT,MODEL,SERIAL,ROTA
  echo "### df"; df -hT
  echo "### disks/list"; pvesh get /nodes/proxmox/disks/list --output-format json
  echo "### smart"
  for d in $(lsblk -dn -o NAME | grep -E "^(sd|nvme)"); do
    echo "--- /dev/$d ---"
    smartctl -i -H /dev/$d 2>/dev/null | grep -Ei "Model|Serial|Capacity|Rotation|SMART overall|Firmware|Form Factor"
    smartctl -A /dev/$d 2>/dev/null | grep -Ei "Power_On_Hours|Reallocated|Temperature|Percentage Used|Data Units Written|Power On Hours"
  done
  echo "### zfs/md no host"; zpool list 2>&1 | head -5; cat /proc/mdstat
'

run storage '
  echo "### storage.cfg"; cat /etc/pve/storage.cfg
  echo "### pvesm status"; pvesm status
  echo "### uso por guest (Samsung)"; du -sh /mnt/pve/Samsung/images/* 2>/dev/null | sort -k1 -h
  echo "### templates"; ls /mnt/pve/Samsung/template/cache/ 2>/dev/null
  echo "### isos"; ls /mnt/pve/ISOS/template/iso/ 2>/dev/null
  echo "### fstab"; cat /etc/fstab
  echo "### mounts"; mount | grep -Ei "nfs|cifs"
'

run guests '
  echo "### qm list"; qm list
  echo "### pct list"; pct list
  echo "### cluster/resources"; pvesh get /cluster/resources --output-format json
  echo "### configs VM"
  for f in /etc/pve/qemu-server/*.conf; do echo "===== $f ====="; cat "$f"; done
  echo "### configs LXC"
  for f in /etc/pve/lxc/*.conf; do echo "===== $f ====="; cat "$f"; done
  echo "### pending"
  for f in /etc/pve/qemu-server/*.conf; do grep -l "\[PENDING\]" "$f" 2>/dev/null; done
'

run guests-runtime '
  echo "### IPs e SO das VMs (guest agent)"
  for i in $(qm list 2>/dev/null | awk "NR>1 && \$3==\"running\"{print \$1}"); do
    echo "--- VM $i ---"
    timeout 8 qm agent $i network-get-interfaces 2>/dev/null | grep "\"ip-address\"" | grep -v "127.0.0.1\|::1" | head -4
    timeout 8 qm agent $i get-osinfo 2>/dev/null | grep -E "pretty-name|kernel-release"
  done
  echo "### SO dos LXC"
  for i in $(pct list 2>/dev/null | awk "NR>1 && \$2==\"running\"{print \$1}"); do
    echo "$i: $(timeout 6 pct exec $i -- sh -c ". /etc/os-release 2>/dev/null; echo \$PRETTY_NAME" 2>/dev/null)"
  done
  echo "### snapshots"
  for i in $(qm list 2>/dev/null | awk "NR>1{print \$1}"); do s=$(qm listsnapshot $i 2>/dev/null | grep -v "no-parent\|^$"); [ -n "$s" ] && echo "VM $i: $s"; done
  for i in $(pct list 2>/dev/null | awk "NR>1{print \$1}"); do s=$(pct listsnapshot $i 2>/dev/null | grep -v "no-parent\|^$"); [ -n "$s" ] && echo "CT $i: $s"; done
'

run passthrough '
  echo "### hostpci nas VMs"; grep -H "hostpci" /etc/pve/qemu-server/*.conf
  echo "### discos fisicos passados"; grep -H "/dev/disk/by-id" /etc/pve/qemu-server/*.conf
  echo "### usb nas VMs"; grep -H "^usb" /etc/pve/qemu-server/*.conf
  echo "### devices/mounts nos LXC"; grep -HE "lxc\.(cgroup2\.devices|mount)|^mp[0-9]" /etc/pve/lxc/*.conf
  echo "### drivers vfio"; lspci -nnk | grep -B2 "vfio-pci"
  echo "### usb do host"; lsusb; lsusb -t
  echo "### hardware/usb (API)"; pvesh get /nodes/proxmox/hardware/usb --output-format json
'

run ups '
  echo "### estado"; for u in $(upsc -l 2>/dev/null); do echo "--- $u ---"; upsc $u 2>/dev/null; done
  echo "### configs"; for f in /etc/nut/nut.conf /etc/nut/ups.conf /etc/nut/upsd.conf /etc/nut/upsmon.conf /etc/nut/upssched.conf /etc/nut/upsd.users; do
    echo "--- $f ---"; grep -vE "^\s*#|^\s*$" $f 2>/dev/null
  done
  echo "### servicos"; systemctl is-active nut-server nut-monitor
  echo "### porta serial"; ls -l /dev/ttyACM* /dev/ttyUSB* 2>/dev/null
'

run rede '
  echo "### interfaces"; cat /etc/network/interfaces
  echo "### ip addr"; ip -br addr
  echo "### rotas"; ip route
  echo "### bridges"; brctl show 2>/dev/null || bridge link
  echo "### links fisicos"
  for i in $(ls /sys/class/net | grep -vE "lo|veth|tap|fw|vmbr|bonding_masters"); do
    echo "--- $i ---"; ethtool $i 2>/dev/null | grep -E "Speed|Duplex|Link detected"; ethtool -i $i 2>/dev/null | grep -E "driver|firmware|bus-info"
  done
  echo "### firewall"; cat /etc/pve/firewall/cluster.fw 2>/dev/null; cat /etc/pve/nodes/proxmox/host.fw 2>/dev/null; ls /etc/pve/firewall/ 2>/dev/null
  echo "### portas em escuta"; ss -tulpn 2>/dev/null | grep LISTEN
'

run backup '
  echo "### jobs.cfg"; cat /etc/pve/jobs.cfg
  echo "### mtime do jobs.cfg"; ls -la --time-style=full-iso /etc/pve/jobs.cfg
  echo "### estado dos jobs"; cat /var/lib/pve-manager/jobs/*.json 2>/dev/null
  echo "### vzdump.conf"; grep -vE "^\s*#|^\s*$" /etc/vzdump.conf 2>/dev/null
  echo "### backup mais recente por guest"
  pvesm list Bkp1tb 2>/dev/null | awk "NR>1{split(\$1,a,\"/\"); print a[3], a[4]}" | sort -k1,1n -k2,2 | awk "{last[\$1]=\$2} END {for (g in last) print g, last[g]}" | sort -n
  echo "### contagem de copias por guest"; pvesm list Bkp1tb 2>/dev/null | awk "NR>1{print \$5}" | sort -n | uniq -c
  echo "### outros storages de backup"; pvesm list Backup_VMs 2>/dev/null | tail -20
  echo "### tarefas vzdump recentes"; pvesh get /nodes/proxmox/tasks --typefilter vzdump --limit 10 --output-format json
  echo "### replicacao / HA"; cat /etc/pve/replication.cfg 2>/dev/null; ha-manager status 2>/dev/null
'

run acesso '
  echo "### user.cfg"; cat /etc/pve/user.cfg
  echo "### users (API)"; pvesh get /access/users --output-format json
  # a API devolve os realms em ordem não-determinística; ordenar evita falso positivo no diff
  echo "### realms"; pvesh get /access/domains --output-format json 2>/dev/null | \
    python3 -c "import sys,json; print(json.dumps(sorted(json.load(sys.stdin), key=lambda r: r[\"realm\"])))" 2>/dev/null
'

run servicos '
  echo "### estado dos daemons"
  for s in pvedaemon pveproxy pvestatd pve-cluster pve-firewall pvescheduler corosync ksmtuned nut-server nut-monitor smartd; do
    echo "$s: $(systemctl is-active $s 2>/dev/null)"
  done
  echo "### unidades falhadas"; systemctl --failed --no-pager
  echo "### cron"; crontab -l 2>/dev/null; grep -rh . /etc/cron.d/ 2>/dev/null | grep -vE "^\s*#|^\s*$"
  echo "### timers"; systemctl list-timers --all --no-pager | head -20
  echo "### notificacoes"; cat /etc/pve/notifications.cfg 2>/dev/null
  echo "### ksm"; for f in run pages_shared pages_sharing pages_unshared full_scans; do echo "$f: $(cat /sys/kernel/mm/ksm/$f)"; done
  grep -vE "^\s*#|^\s*$" /etc/ksmtuned.conf 2>/dev/null
  echo "### tarefas recentes"; pvesh get /nodes/proxmox/tasks --limit 20 --output-format json
'

echo
echo "Coleta concluída em ${DEST}"
echo "Para ver o que mudou desde a última: diff -r <coleta-anterior> ${DEST}"
