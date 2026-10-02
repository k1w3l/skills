# Pangolin CLI on RackNerd VPS for Sr. Kiwel's homelab

This reference captures the durable operational lesson from the RackNerd VPS setup.

## Correct component

For this VPS to access Sr. Kiwel's homelab as a VPN client, use the Pangolin CLI/VPN client:

```bash
curl -fsSL https://static.pangolin.net/get-cli.sh -o /tmp/get-pangolin-cli.sh
sha256sum /tmp/get-pangolin-cli.sh
sed -n '1,240p' /tmp/get-pangolin-cli.sh
sh /tmp/get-pangolin-cli.sh
```

Expected installed binary:

```bash
/usr/local/bin/pangolin
pangolin version
```

Observed good version during setup: `0.9.0`.

## Endpoint

Use:

```bash
https://pangolin.kiwel.uk
```

Connect when needed:

```bash
pangolin up --endpoint https://pangolin.kiwel.uk --silent
```

Check status:

```bash
pangolin status --json 2>&1 || pangolin status 2>&1
pangolin logs client 2>&1 | tail -120 || true
ip -br addr show pangolin || true
ip route | grep -E 'pangolin|100\\.90|100\\.96|192\\.168\\.1' || true
```

Disconnect after use:

```bash
pangolin down 2>&1 || true
sleep 2
pangolin status --json 2>&1 || pangolin status 2>&1 || true
ip -br addr show pangolin 2>/dev/null || echo 'pangolin interface absent'
ip route | grep -E 'pangolin|100\\.90|100\\.96|192\\.168\\.1' || echo 'no pangolin/homelab routes present'
```

## Known-good status shape

A successful connection may show:

- `connected: true`
- `registered: true`
- `agent: Pangolin CLI`
- `orgId: kwl`
- peer/site name like `Lab`
- tunnel interface `pangolin`
- tunnel IPv4 similar to `100.90.128.7/24`
- included routes for `100.96.128.0/24` and `192.168.1.0/24`

## Pitfall: Newt is not the requested client

`curl -fsSL https://static.pangolin.net/get-newt.sh | bash` installs Newt, a site connector. That is the wrong component when Sr. Kiwel asks for the Pangolin VPN client on this VPS.

If Newt was installed by mistake, remove it:

```bash
systemctl disable --now newt.service >/dev/null 2>&1 || true
rm -f /etc/systemd/system/newt.service
rm -rf /etc/newt
rm -f /usr/local/sbin/configure-newt-pangolin
rm -f /usr/local/bin/newt
systemctl daemon-reload
```

## Default posture

Sr. Kiwel wants the VPN disconnected by default. Connect only for a requested local-resource task, then disconnect and verify route/interface cleanup.
