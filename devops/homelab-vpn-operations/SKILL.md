---
name: homelab-vpn-operations
description: "Operate or troubleshoot legacy VPN-based access into Sr. Kiwel's homelab when Hermes is outside the LAN; current default is local Proxmox homelab access with no VPN."
version: 1.2.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [homelab, vpn, pangolin, racknerd, operations]
    created_by: agent
---

# Homelab VPN Operations

Use this skill only when Sr. Kiwel asks to operate VPN access, troubleshoot Pangolin/Newt, or when Hermes is demonstrably outside the homelab LAN and needs a tunnel back in. Do not load this skill merely because a task touches homelab resources; local homelab access is now the default.

## Operating stance

- Treat the homelab like production infrastructure: verify prerequisites, make reversible changes, avoid exposing secrets, and report exact status.
- Address the user politely and operationally as Sr. Kiwel, patrão, or mestre.
- Current default: Hermes/J.A.R.V.I.S. runs in a VM on Sr. Kiwel's Proxmox homelab, so local resources should be reached directly on the LAN without VPN.
- Use Pangolin/VPN only when Sr. Kiwel explicitly asks for VPN work, or when live checks show this agent is outside the LAN and direct access is impossible.
- Do not claim a tunnel is connected until `pangolin status` and/or logs confirm the client is running and the peer/site is connected.

## Known architecture

- Current architecture: Hermes/J.A.R.V.I.S. runs on a VM inside Sr. Kiwel's Proxmox homelab.
- Homelab resources such as Home Assistant should normally be accessed directly by LAN IP/hostname from this VM.
- Legacy architecture: Hermes previously ran on a RackNerd VPS and used the Pangolin VPN/CLI client to reach the homelab. The Pangolin notes below are retained for future external-host or recovery scenarios only.
- If VPN is needed, use the Pangolin CLI/VPN client, not the Newt site client, unless Sr. Kiwel explicitly asks for Newt/site provisioning.
- Historical Pangolin endpoint for the homelab: `https://pangolin.kiwel.uk/`.
- Expected CLI binary path after install: `/usr/local/bin/pangolin`.

Session-specific setup notes are in:

- `references/pangolin-cli-racknerd.md`
- `references/pangolin-newt-racknerd.md` (historical note/pitfall: mistaken Newt site-client setup)

## Correct Pangolin CLI/VPN workflow

1. Check host prerequisites and avoid guessing the OS:

   ```bash
   . /etc/os-release && echo "$PRETTY_NAME"
   uname -m
   command -v curl || true
   command -v systemctl || true
   test -c /dev/net/tun && echo tun-present || echo tun-missing
   ```

2. Inspect the official Pangolin CLI installer before running it:

   ```bash
   curl -fsSL https://static.pangolin.net/get-cli.sh -o /tmp/get-pangolin-cli.sh
   sha256sum /tmp/get-pangolin-cli.sh
   sed -n '1,240p' /tmp/get-pangolin-cli.sh
   ```

3. Install/update the Pangolin CLI:

   ```bash
   sh /tmp/get-pangolin-cli.sh
   command -v pangolin
   pangolin version
   pangolin --help
   ```

4. Verify login/status before connecting:

   ```bash
   pangolin status --json 2>&1 || pangolin status 2>&1 || true
   ```

   If already logged in but no client is running, this commonly prints `No client is currently running`.

5. Connect only when local access is required:

   ```bash
   pangolin up --endpoint https://pangolin.kiwel.uk --silent
   sleep 3
   pangolin status --json 2>&1 || pangolin status 2>&1
   ```

6. Verify routes/interface/logs:

   ```bash
   ip -br addr show pangolin || true
   ip route | grep -E 'pangolin|100\\.90|100\\.96|192\\.168\\.1' || true
   pangolin logs client 2>&1 | tail -120 || true
   ```

7. After the requested homelab task is complete, disconnect and verify cleanup:

   ```bash
   pangolin down 2>&1 || true
   sleep 2
   pangolin status --json 2>&1 || pangolin status 2>&1 || true
   ip -br addr show pangolin 2>/dev/null || echo 'pangolin interface absent'
   ip route | grep -E 'pangolin|100\\.90|100\\.96|192\\.168\\.1' || echo 'no pangolin/homelab routes present'
   ```

## Direct credential connection, if needed

If Sr. Kiwel provides client credentials, connect with:

```bash
pangolin up --endpoint https://pangolin.kiwel.uk --id <id> --secret <secret> --silent
```

Never save client secrets in memory, skills, logs, or final replies.

## Newt vs Pangolin CLI pitfall

Pangolin has multiple related components. Do not conflate them:

- `get-cli.sh` installs the Pangolin CLI/VPN client (`pangolin`) used by this VPS to connect into the homelab as a client.
- `get-newt.sh` installs Newt (`newt`), a site/resource connector. It is not the client Sr. Kiwel requested for this VPS unless he explicitly asks for Newt/site setup.

If Newt was installed by mistake, remove the mistaken artifacts before installing the CLI:

```bash
systemctl disable --now newt.service >/dev/null 2>&1 || true
rm -f /etc/systemd/system/newt.service
rm -rf /etc/newt
rm -f /usr/local/sbin/configure-newt-pangolin
rm -f /usr/local/bin/newt
systemctl daemon-reload
```

## Reporting format

Briefly report:

- binary path and version,
- endpoint,
- connection status,
- tunnel IP/interface if connected,
- peer/site name and connected state when visible,
- routes added/removed,
- whether the VPN was disconnected afterward.
