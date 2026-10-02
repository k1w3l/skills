# Pangolin/Newt setup on RackNerd VPS for Sr. Kiwel

This reference captures the reusable details discovered while preparing the RackNerd VPS to access Sr. Kiwel's homelab through Pangolin.

## Current known endpoint

- Pangolin endpoint: `https://pangolin.kiwel.uk/`

## Installed components from the session

- Newt binary: `/usr/local/bin/newt`
- Installed version observed: `Newt version 1.12.5`
- Config path: `/etc/newt/newt.env`
- systemd unit path: `/etc/systemd/system/newt.service`
- Helper script path: `/usr/local/sbin/configure-newt-pangolin`

## State after preparation

The client was installed and the service/config skeletons were created, but the service was intentionally left disabled/inactive until Sr. Kiwel provides valid Pangolin credentials.

Required credential options:

1. Existing site credentials:
   - `NEWT_ID`
   - `NEWT_SECRET`

2. Or a one-time provisioning key:
   - `NEWT_PROVISIONING_KEY`

Do not persist actual secrets in memory or skill files.

## Official installer source used

- Installer URL: `https://static.pangolin.net/get-newt.sh`
- GitHub release endpoint used by installer: `https://api.github.com/repos/fosrl/newt/releases/latest`
- Latest observed release during setup: `1.12.5`

The installer downloads platform binaries from:

`https://github.com/fosrl/newt/releases/download/<version>/newt_<os>_<arch>`

On Ubuntu x86_64 this resolved to:

`newt_linux_amd64`

## Activation examples

With site credentials:

```bash
configure-newt-pangolin --id "$NEWT_ID" --secret "$NEWT_SECRET"
```

With provisioning key:

```bash
configure-newt-pangolin --provisioning-key "$NEWT_PROVISIONING_KEY"
```

Then verify:

```bash
systemctl status --no-pager --lines=50 newt.service
journalctl -u newt.service -n 100 --no-pager
```

Look for successful tunnel/control-plane connection logs before telling Sr. Kiwel the homelab is connected.
