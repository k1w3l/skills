# Docker/Compose inventory through a Proxmox guest agent

Use this reference when Docker runs inside a Proxmox VM and direct guest SSH is unavailable or undesirable. The method is read-only and produces secret-safe documentation.

## Guest execution

Run commands through the Proxmox host:

```bash
ssh root@<PVE_IP> \
  "qm guest exec <VMID> -- bash -lc '<COMMAND>'"
```

`qm guest exec` returns JSON; command output is in `out-data`. Some PVE installations print warnings before the JSON, so locate the first JSON object before parsing instead of assuming byte zero.

Collect:

```bash
docker ps --format '{{json .}}'
docker inspect $(docker ps -q)
docker compose ls --all --format json
```

Filter inspect data to name, image, state/health, ports, networks, mounts, and `com.docker.compose.*` labels. Never place the complete inspect object or `Config.Env` in documentation.

## Map runtime containers to Compose

1. Start with `com.docker.compose.project`, `.service`, `.project.config_files`, and `.project.working_dir`.
2. A stack manager may run Compose inside its own container. Translate paths such as `/app/data/stacks/...` or `/data/compose/...` to host paths using the manager container’s bind mounts.
3. If labels are missing, search persisted Compose filenames and score candidates using:
   - exact container name;
   - exact image;
   - project-prefixed network;
   - bind-mount paths;
   - dependency/service relationships.
4. Generic database images are weak evidence. Require network and mount/service confirmation before assigning them to a stack.
5. Group the inventory by stack. A stack with three running services gets one YAML block and three summary rows.

## Secret-safe YAML reproduction

Read only the persisted Compose file. Do not read `.env`, Docker secrets, or a credential store.

Sanitize recursively:

- sensitive mapping keys: password, passwd, passphrase, token, secret, API key, access key, private key, cookie, authorization, credentials, client secret;
- environment-list assignments such as `TOKEN=value`;
- credentials inside URLs, for example `postgres://user:***@db/...`;
- command arguments such as `--password value` and `--token=value`;
- bearer tokens.

Keep a simple reference such as `${POSTGRES_PASSWORD}` because it reveals no value. Replace a literal value with `REDACTED`. Do not claim that the sanitized YAML is directly deployable.

## Verification checklist

- Query `docker ps` again and compare names/counts.
- Confirm every running container appears in the summary.
- Confirm every running stack has exactly one Compose block.
- Parse every sanitized YAML block.
- Check Markdown fences are balanced.
- Scan the final section for credential assignments and credential-bearing URLs.
- Remove temporary raw QGA output, Compose captures, and base64 payloads.

## What to record in the operational log

Record the collection timestamp, VM/host identity, number of running containers and stacks, access method, missing-label correlations, sanitization boundary, configuration validation, and final live-count comparison. Do not record raw output or secret values.