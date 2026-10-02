# Proxmox Troubleshooting Reference

## Quick Lookup Table

| Problem | First Commands |
|---------|----------------|
| Service down | `systemctl status <svc>`, `journalctl -u <svc>` |
| Network unreachable | `ping`, `ip route`, `ss -tlnp` |
| Disk full | `df -h`, `du -sh /*`, `lsof +D /path` |
| High CPU | `top`, `ps aux --sort=-%cpu` |
| High memory | `free -h`, `ps aux --sort=-%mem` |
| VM issue | `qm status <id>`, `qm showcmd <id>` |
| Container issue | `pct status <id>`, `pct enter <id>` |
| Container logs empty / `dmesg` flooded | `journalctl -k \| grep DENIED`, `pct exec <id> -- ls -l /var/log/syslog` |

## System Diagnostics

### Resource Usage

```bash
# CPU and processes
top -bn1 | head -20
ps aux --sort=-%cpu | head -10
uptime
mpstat 1 5

# Memory
free -h
ps aux --sort=-%mem | head -10
cat /proc/meminfo

# Disk
df -h
du -sh /* 2>/dev/null | sort -h
lsblk
iostat -x 1 5

# Network
ss -tlnp           # listening ports
ss -s              # socket statistics
iftop              # real-time bandwidth
ip -s link         # interface statistics
```

### Log Locations

| Service | Log Location |
|---------|--------------|
| System | `/var/log/syslog`, `journalctl` |
| Auth | `/var/log/auth.log` |
| Kernel | `dmesg`, `/var/log/kern.log` |
| Proxmox | `/var/log/pve/`, `journalctl -u pve*` |
| Ceph | `/var/log/ceph/` |
| Cloud-init | `/var/log/cloud-init.log`, `/var/log/cloud-init-output.log` |

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| VM won't start | Lock, storage, resources | `qm unlock`, check storage, verify resources |
| Migration failed | No shared storage, resources | Verify shared storage, check target capacity |
| Cluster issues | Quorum, network, time | `pvecm status`, check NTP, network |
| Storage unavailable | Mount failed, network | Check mount, network access |
| High load | Resource contention | Identify bottleneck, rebalance VMs |
| VM RAM stuck at ~100% | `balloon: 0`, or reading `mem` from `/nodes/{node}/qemu` | Unset `balloon` + stop/start; read `mem` from `/cluster/resources` — see "VM Memory Reported at ~100%" |
| Network issues | Bridge, VLAN, firewall | `brctl show`, check tags, firewall rules |
| Backup failed | Disk space, VM state | Check space, storage access |
| Template not found | Not downloaded | Download from Proxmox repo |
| API errors | Auth, permissions | Check token, user permissions |

## Diagnostic Commands

### Cluster Health

```bash
pvecm status                     # Quorum and node status
pvecm nodes                      # List cluster members
systemctl status pve-cluster     # Cluster service
systemctl status corosync        # Corosync service
```

### Node Health

```bash
pveversion -v                    # Proxmox version info
uptime                           # Load and uptime
free -h                          # Memory usage
df -h                            # Disk space
top -bn1 | head -20              # Process overview
```

### VM Diagnostics

```bash
qm status <vmid>                 # VM state
qm config <vmid>                 # VM configuration
qm showcmd <vmid>                # QEMU command line
qm unlock <vmid>                 # Clear locks
qm monitor <vmid>                # QEMU monitor access
```

### Container Diagnostics

```bash
pct status <ctid>                # Container state
pct config <ctid>                # Container configuration
pct enter <ctid>                 # Enter container shell
pct unlock <ctid>                # Clear locks
```

### Storage Diagnostics

```bash
pvesm status                     # Storage status
df -h                            # Disk space
mount | grep -E 'nfs|ceph'       # Mounted storage
zpool status                     # ZFS pool status (if using ZFS)
ceph -s                          # Ceph status (if using Ceph)
```

### Network Diagnostics

```bash
brctl show                       # Bridge configuration
ip link                          # Network interfaces
ip addr                          # IP addresses
ip route                         # Routing table
bridge vlan show                 # VLAN configuration
```

### Log Files

```bash
# Cluster logs
journalctl -u pve-cluster
journalctl -u corosync

# VM/Container logs
journalctl | grep <vmid>
tail -f /var/log/pve/tasks/*

# Firewall logs
journalctl -u pve-firewall

# Web interface logs
journalctl -u pveproxy
```

## Troubleshooting Workflows

### VM Won't Start

1. Check for locks: `qm unlock <vmid>`
2. Verify storage: `pvesm status`
3. Check resources: `free -h`, `df -h`
4. Review config: `qm config <vmid>`
5. Check logs: `journalctl | grep <vmid>`
6. Try manual start: `qm start <vmid> --debug`

### Migration Failure

1. Verify shared storage: `pvesm status`
2. Check target resources: `pvesh get /nodes/<target>/status`
3. Verify network: `ping <target-node>`
4. Check version match: `pveversion` on both nodes
5. Review migration logs

### Cluster Quorum Lost

1. Check status: `pvecm status`
2. Identify online nodes
3. If majority lost, set expected: `pvecm expected <n>`
4. Recover remaining nodes
5. Rejoin lost nodes when available

### Storage Mount Failed

1. Check network: `ping <storage-server>`
2. Verify mount: `mount | grep <storage>`
3. Try manual mount
4. Check permissions on storage server
5. Review `/var/log/syslog`

### High CPU/Memory Usage

1. Identify culprit: `top`, `htop`
2. Check VM resources: `qm monitor <vmid>` → `info balloon`
3. Review resource allocation across cluster
4. Consider migration or resource limits

Before chasing a memory hog, confirm the number is real — see "VM Memory
Reported at ~100%" below. A VM pinned at 100% is more often a reporting
artifact than an actual shortage.

## VM Memory Reported at ~100%

A VM pinned near (or above) 100% RAM that never drops almost always has **two
independent causes**. Both need fixing, and the second stays invisible until the
first is resolved — which makes it easy to declare victory too early.

### Cause 1: `balloon: 0` disables the virtio-balloon device

Without the balloon device PVE has no channel to ask the guest how much RAM it
actually uses, so it falls back to `memhost` — the anonymous memory of the KVM
process on the host. That number only grows: a guest page touched once is never
returned to the host, and the guest's own page cache counts too. So it climbs to
the VM's full allocation and stays there.

```bash
# Diagnose: no freemem/ballooninfo in the output means no balloon device
qm status <vmid> --verbose | grep -E "^(mem|maxmem|memhost|freemem):"

# Ground truth from inside the guest (needs qemu-guest-agent)
qm guest exec <vmid> -- /usr/bin/free -m

# Host-side cross-check: mem == memhost == cgroup anon confirms the fallback
cat /sys/fs/cgroup/qemu.slice/<vmid>.scope/memory.current
```

The command is `qm guest exec`, not `qm agent exec` — the latter fails with
`400 too many arguments`.

**Fix:** leave `balloon` *unset* rather than setting it to a number. Unset means
the device is created at the full `memory` size, so min == max and the guest
never shrinks — accurate reporting with no dynamic resizing and no risk to the
workload.

```bash
qm set <vmid> --delete balloon
```

The change lands in the `[PENDING]` section of `/etc/pve/qemu-server/<vmid>.conf`
and needs a **full stop/start**. The device is created at VM startup, so
rebooting from inside the guest will not pick it up:

```bash
qm shutdown <vmid> --timeout 120 || qm stop <vmid>
qm start <vmid>
qm status <vmid> --verbose | grep freemem   # populated = balloon is live
```

Guest requirements: Linux needs `virtio_balloon`, built in or as a module on
essentially every distro (`modinfo virtio_balloon` to confirm). Windows needs
the virtio-win balloon driver **and** the `BalloonService` running — the driver
alone is not enough.

### Cause 2: `/nodes/{node}/qemu` reports `memhost` in the `mem` field

This is the trap for anything scraping the API. The per-node guest list returns
host memory in `mem`, ignoring the balloon entirely.

| Endpoint | `mem` value | Notes |
|---|---|---|
| `/nodes/{node}/qemu` | `memhost` — **wrong** | no separate `memhost` field to compare against |
| `/cluster/resources?type=vm` | balloon-derived — correct | also exposes `memhost` separately |
| `/nodes/{node}/qemu/{vmid}/status/current` | balloon-derived — correct | one call per VM |

Prefer `/cluster/resources?type=vm` for collectors: a single call covers qemu
**and** lxc across all nodes, carries every counter the per-node list has
(`cpu`, `maxmem`, `disk`, `maxdisk`, `netin`, `netout`, `diskread`, `diskwrite`,
`uptime`, `status`), and keys each row with `id` already formatted as `qemu/124`
/ `lxc/102`.

Without a balloon device `mem == memhost` on every endpoint, so all three agree
and this defect is undetectable. It only surfaces once cause 1 is fixed — which
is exactly why fixing the balloon alone can look like it changed nothing in an
external dashboard.

### Reading the corrected numbers

The balloon reports `mem = total_mem - free_mem`, and **guest page cache counts
as used**. That makes it an honest ceiling, not the `used` column of `free -m` —
expect it to sit above what the guest itself calls "used". For the real figure,
query the guest agent instead of the balloon.

Two guest types stay high after the fix, correctly:

- **ZFS guests** (TrueNAS and friends) — the ARC is not free memory. Check
  `grep ^size /proc/spl/kstat/zfs/arcstats` before assuming something is broken;
  an ARC filling most of RAM is working as designed, so expect ~90% and gain
  little from a disruptive restart.
- **Busy databases and file servers** — a large page cache is doing its job.

LXC containers are immune to all of this: their numbers come from cgroups and
are already accurate.

## LXC: Empty `/var/log/syslog` and an AppArmor Denial Flood

Unprivileged **Ubuntu** LXC containers that have `rsyslog` installed hit an
AppArmor defect where journald cannot forward to rsyslog. It costs you twice:
the container loses every rsyslog-based log file, and the host kernel ring
buffer fills with the same denial ~50 times a minute.

Host-side symptom (note it names the container's AppArmor namespace):

```
apparmor="DENIED" operation="sendmsg" class="file"
namespace="root//lxc-102_<-var-lib-lxc>" profile="rsyslogd"
name="/run/systemd/journal/dev-log" comm="systemd-journal"
requested_mask="r" denied_mask="r" fsuid=100000 ouid=100000
```

Container-side symptom: `/var/log/syslog` and `/var/log/mail.log` sit at **0
bytes** while `journalctl` still works. Anything that reads those files —
fail2ban, log shippers, mail troubleshooting — is silently blind.

The host cost is easy to miss: at that rate the container evicts real host
kernel messages from the ring buffer, so `dmesg` stops being useful for
diagnosing the node itself.

```bash
# Which containers are affected, and how hard
journalctl -k --since "-1 hour" | grep -c DENIED
journalctl -k --since "-1 hour" | grep DENIED \
  | grep -oE 'namespace="[^"]*" profile="[^"]*" name="[^"]*"' | sort | uniq -c

# Per-container check
for ct in $(pct list | awk '$2=="running"{print $1}'); do
  printf "%s %s\n" "$ct" \
    "$(pct exec $ct -- stat -c %s /var/log/syslog 2>/dev/null || echo n/a)"
done
```

### Root cause: AppArmor mediates by the socket's label, not the caller

The shipped `usr.sbin.rsyslogd` profile grants `/dev/log rwl`, but `/dev/log` is
a symlink to `/run/systemd/journal/dev-log` and AppArmor matches on the
**resolved** path, which has no rule. Adding the rule is only half the fix,
because that label is **pinned when the socket is created** — at container boot,
by PID 1, via `systemd-journald-dev-log.socket` and `syslog.socket`.

Confirm the mediation model when in doubt: have any unrelated process write to
the socket and watch the denial come back attributed to `profile="rsyslogd"`.

```bash
pct exec <ctid> -- python3 -c \
  'import socket;socket.socket(socket.AF_UNIX,socket.SOCK_DGRAM).sendto(b"<13>x\n","/run/systemd/journal/syslog")'
# -> apparmor="DENIED" ... profile="rsyslogd" ... comm="python3"
```

A `python3` process is obviously not rsyslogd. The profile in the record is the
socket's, which is why three plausible fixes all do nothing:

| Attempt | Why it fails |
|---|---|
| `apparmor_parser -r` after adding the rule | Reloading a profile does not relabel an already-created socket |
| `systemctl restart systemd-journald` | The sockets belong to PID 1 socket units, not to journald |
| Setting the profile to **complain** | Records still read `DENIED` — the pinned label wins, so complain mode is worthless as a diagnostic here |

That last row matters most: complain mode normally proves whether AppArmor is
responsible. Here it lies, and will talk you out of the correct diagnosis.

### Fix

All four steps, inside the container. Step 3 is the one everyone omits.

```bash
# 1. grant the resolved paths (profile already ends with #include <local/...>)
mkdir -p /etc/apparmor.d/local
cat >> /etc/apparmor.d/local/usr.sbin.rsyslogd <<'EOF'
/run/systemd/journal/dev-log rw,
/run/systemd/journal/syslog rw,
EOF

# 2. load the new policy
apparmor_parser -r /etc/apparmor.d/usr.sbin.rsyslogd

# 3. recreate the sockets so they pick up the new label  <-- the missing step
systemctl restart systemd-journald-dev-log.socket syslog.socket

# 4. reconnect both ends
systemctl restart systemd-journald
systemctl restart rsyslog
```

Restarting the container instead of steps 3–4 works too, and is the safer call
when the container runs something you would rather not interrupt mid-restart.

Verify — the probe must land in the file, and the host must go quiet:

```bash
pct exec <ctid> -- logger -t VERIFY "probe"
sleep 3
pct exec <ctid> -- grep -c VERIFY /var/log/syslog     # expect >= 1
journalctl -k --since "-1 min" | grep -c DENIED        # expect 0
```

`aa-complain` and friends may be missing — Ubuntu containers often ship
`apparmor` without `apparmor-utils`. Use `apparmor_parser -r` (enforce) and
`apparmor_parser -C -r` (complain) directly.

### Scope and a related check

Only containers whose distro installs both `rsyslog` and the AppArmor profile
are affected — typically Ubuntu. Debian containers that ship journald-only and
Alpine containers are not. An empty `/var/log/syslog` in a container with no
`rsyslogd` binary is just a stale file, not this bug.

A running container with **no** AppArmor namespace on the host is unaffected for
the opposite reason — it is not confined at all. Worth noticing, because it
usually means confinement silently failed to set up rather than being intended:

```bash
ls /sys/kernel/security/apparmor/policy/namespaces/   # one lxc-<ctid>_* per confined CT
```

Gaps in that list against `pct list` are the containers to look at.

## Recovery Procedures

### Remove Failed Node

```bash
# On healthy node
pvecm delnode <failed-node>

# Clean up node-specific configs
rm -rf /etc/pve/nodes/<failed-node>
```

### Force Stop Locked VM

```bash
# Remove lock
qm unlock <vmid>

# If still stuck, find and kill QEMU process
ps aux | grep <vmid>
kill <pid>

# Force cleanup
qm stop <vmid> --skiplock
```

### Recover from Corrupt Config

```bash
# Backup current config
cp /etc/pve/qemu-server/<vmid>.conf /root/<vmid>.conf.bak

# Edit config manually
nano /etc/pve/qemu-server/<vmid>.conf

# Or restore from backup
qmrestore <backup> <vmid>
```

## Health Check Script

```bash
#!/bin/bash
echo "=== Cluster Status ==="
pvecm status

echo -e "\n=== Node Resources ==="
for node in $(pvecm nodes | awk 'NR>1 {print $3}'); do
  echo "--- $node ---"
  pvesh get /nodes/$node/status --output-format yaml | grep -E '^(cpu|memory):'
done

echo -e "\n=== Storage Status ==="
pvesm status

echo -e "\n=== Running VMs ==="
qm list | grep running

echo -e "\n=== Running Containers ==="
pct list | grep running
```

## Systematic Debugging Approach

1. **Identify** - What service/component is affected?
2. **Check status** - Is it running? What state?
3. **Read logs** - What errors are reported?
4. **Verify config** - Has anything changed?
5. **Test connectivity** - Can it reach dependencies?
6. **Check resources** - CPU/memory/disk/network?
7. **Compare** - Does a known-good config work?
8. **Isolate** - Narrow down to root cause
9. **Fix and verify** - Apply fix, confirm resolution
10. **Document** - Record what happened and how it was fixed
