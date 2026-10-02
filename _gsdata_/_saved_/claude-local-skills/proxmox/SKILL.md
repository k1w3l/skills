---
name: proxmox
description: |
  Proxmox VE virtualization platform reference for VM/LXC management, clustering,
  storage, and networking. Includes Terraform and Ansible integration patterns.
  Use when working with Proxmox configurations, CLI commands, troubleshooting
  VMs/containers, or planning resource allocation.
  Triggers: proxmox, qemu, kvm, lxc, pve, vm, container, cluster, vzdump, qm, pct,
  apparmor denial in an lxc namespace, empty container logs.
agent: proxmox-expert
---

# Proxmox Skill

Proxmox VE virtualization platform reference for VM management, containers, clustering, and homelab infrastructure.

## Quick Reference

```bash
# VM management (qm)
qm list                           # List all VMs
qm status <vmid>                  # Check VM status
qm start <vmid>                   # Start VM
qm stop <vmid>                    # Stop VM (hard, like pulling power)
qm shutdown <vmid> --timeout 120  # Shutdown VM (graceful ACPI; falls back to stop)
qm unlock <vmid>                  # Remove lock
qm config <vmid>                  # Show VM config
qm status <vmid> --verbose        # Full runtime state (mem, memhost, freemem...)
qm guest exec <vmid> -- <cmd>     # Run in guest via agent (NOT `qm agent exec`)

# Container management (pct)
pct list                          # List all containers
pct status <ctid>                 # Check container status
pct start <ctid>                  # Start container
pct stop <ctid>                   # Stop container
pct enter <ctid>                  # Enter container shell

# Cluster management (pvecm)
pvecm status                      # Cluster status and quorum
pvecm nodes                       # List cluster nodes

# API shell (pvesh)
pvesh get /nodes                  # List nodes via API
pvesh get /nodes/<node>/status    # Node resource status
pvesh get /cluster/resources --type vm   # All guests, one call — correct `mem`
                                  # (/nodes/<node>/qemu reports memhost in `mem`)

# Backup (vzdump)
vzdump <vmid> --mode snapshot --storage <storage>
vzdump --all --compress zstd
```

## Reference Files

Load on-demand based on task:

| Topic | File | When to Load |
|-------|------|--------------|
| VM vs LXC | [vm-lxc.md](references/vm-lxc.md) | Choosing virtualization type |
| Docker Hosting | [docker-hosting.md](references/docker-hosting.md) | Running Docker on Proxmox |
| Networking | [networking.md](references/networking.md) | Bridges, VLANs, SDN, firewall |
| Storage | [storage.md](references/storage.md) | Storage backends, content types |
| Cloud-init | [cloud-init-templates.md](references/cloud-init-templates.md) | VM provisioning with cloud-init |
| Clustering | [clustering.md](references/clustering.md) | HA, quorum, fencing |
| Backup | [backup.md](references/backup.md) | vzdump modes, restore |
| CLI Tools | [cli-tools.md](references/cli-tools.md) | qm, pct, pvecm, pvesh commands |
| Troubleshooting | [troubleshooting.md](references/troubleshooting.md) | Common errors, diagnostics, **VM memory reported at ~100%**, **LXC AppArmor denial flood / empty container logs** |
| Automation Tools | [automation-tools.md](references/automation-tools.md) | Terraform/Ansible integration |

## Gotchas Worth Knowing Up Front

**A VM reporting ~100% RAM is usually a reporting artifact, not a shortage.**
Two independent causes stack here, and the second is invisible until the first
is fixed — so "I enabled the balloon and my dashboard still shows 100%" is the
expected halfway state, not a failed fix. Read the "VM Memory Reported at ~100%"
section of [troubleshooting.md](references/troubleshooting.md) before touching
allocations. Short version: `balloon: 0` makes PVE fall back to host memory that
only ever grows, and `/nodes/{node}/qemu` reports that host memory in its `mem`
field no matter what the balloon says.

**Config changes to a running VM often land in `[PENDING]`.** `qm config <vmid>`
shows the live value, so a change can look like it silently failed. Check the
`[PENDING]` section of `/etc/pve/qemu-server/<vmid>.conf` — device-level changes
need a full stop/start, and a reboot from inside the guest will not apply them.

**An AppArmor denial naming an `lxc-<ctid>` namespace is rarely cosmetic.** In
unprivileged Ubuntu containers running rsyslog it means journald cannot forward
to rsyslog: `/var/log/syslog` stays at 0 bytes and the flood (~50/min) evicts
real kernel messages from the *host's* `dmesg`. AppArmor mediates these sockets
by the **socket's** label, pinned at container boot — so reloading the profile,
restarting journald, and even switching to complain mode all appear to change
nothing. You must recreate the socket units. See "LXC: Empty `/var/log/syslog`
and an AppArmor Denial Flood" in [troubleshooting.md](references/troubleshooting.md).

## Validation Checklist

Before deploying VMs/containers:

- [ ] Cluster status healthy (`pvecm status`)
- [ ] Node resources available (CPU, RAM, disk)
- [ ] Storage accessible and mounted
- [ ] Network bridges configured correctly
- [ ] VLAN tags match network design
- [ ] Resource allocation within node limits
- [ ] HA configuration correct (if enabled)
- [ ] Backup schedule in place
- [ ] Naming convention followed

## VM vs LXC Quick Decision

| Factor | Use VM | Use LXC |
|--------|--------|---------|
| OS | Windows, BSD, any | Linux only |
| Isolation | Full kernel isolation | Shared kernel |
| Performance | Good | Better (lighter) |
| Startup | Slower | Fast |
| Density | Lower | Higher |
| Complexity | Any workload | Simple services |

## Homelab Network VLANs

| VLAN | Purpose | Proxmox Bridge |
|------|---------|----------------|
| 5 | Management (Web UI, API, SSH) | vmbr5 |
| 1 | Trusted network | vmbr0 |
| 11 | Storage (NFS/Ceph, MTU 9000) | vmbr11 |
| 12 | High-speed transfers | vmbr12 |
