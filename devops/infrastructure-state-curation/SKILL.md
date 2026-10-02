---
name: infrastructure-state-curation
description: >-
  Reconcile live infrastructure state with durable operational documentation. Use
  whenever the user asks to inventory, audit, document, or refresh the current
  state of hosts, VMs, containers, Compose stacks, Kubernetes workloads, services,
  networks, storage, backups, or scheduled routines. Trigger especially for
  requests such as “atualize a wiki com o que está rodando”, “documente todos os
  containers”, “gere um retrato atual do ambiente”, or “reconcile docs with the
  live system”. The workflow requires live read-only collection, source
  correlation, secret-safe curation, canonical-page updates, and end-to-end
  verification rather than copying raw command output.
---

# Infrastructure State Curation

Turn volatile live-system observations into a concise, dated, and verifiable
operational record. This skill governs the boundary between **what is running
now** and **what the documentation claims is running**.

The intended output is a durable snapshot with provenance—not a transcript of
commands and not a blind dump of configuration.

## Core principles

1. **Read documentation first.** Find the canonical page and its maintenance
   rules before collecting. Preserve its structure and update it instead of
   creating a competing page.
2. **Collect live state read-only.** Prefer APIs, agents, inspect commands, and
   status endpoints. Do not restart, recreate, pull, prune, migrate, or mutate a
   service merely to document it.
3. **Separate structural and volatile facts.** Architecture, IDs, mounts, and
   config paths age slowly; health, IPs, versions, counts, and running state need
   a verification date.
4. **Correlate rather than assume.** A name match alone is weak evidence. Combine
   identifiers, labels, images, networks, mounts, config paths, and service
   relationships.
5. **Curate, do not dump.** Record the state, reason, operational implications,
   and source. Exclude noisy output and failed attempts once the final method is
   known.
6. **Secrets never enter durable docs.** Do not publish raw environment dumps,
   `.env` files, secret objects, tokens, passwords, cookies, private keys, or
   credential-bearing URLs.
7. **Verification is part of completion.** Re-check the live inventory, parse
   embedded configuration, scan for secrets, and update the index/log before
   reporting success.

## Workflow

### 1. Establish scope and source of truth

- Identify the canonical operational page and its index/log.
- Read any environment-specific status skill or runbook before touching the
  system.
- Define precisely what “currently running” means: active containers, enabled
  services, ready workloads, attached volumes, or another observable state.
- Record the collection time and timezone.

### 2. Collect the live inventory

Gather only fields needed for the documentation:

- stable identifier and human name;
- type and ownership/project;
- image/version or executable;
- running/health/readiness state;
- exposed ports and networks;
- persistent mounts or storage;
- canonical configuration path;
- source and collection method.

Avoid broad commands that expose all environment variables or credentials. If
an API returns secrets alongside metadata, filter before the result reaches the
final artifact.

### 3. Correlate runtime objects with configuration

Use the strongest available identifiers first:

1. explicit ownership labels or annotations;
2. project/service IDs and config-file paths;
3. runtime image plus network and mount relationships;
4. name-based matching only as supporting evidence.

When metadata is missing, document the correlation method and confidence. For a
generic dependency such as PostgreSQL or Redis, require network, mount, and
service-level evidence; image similarity is not enough.

### 4. Sanitize configuration

When configuration must be embedded in documentation:

- Prefer the persisted source file, not an environment-expanded rendering.
- Do not read `.env`, secret stores, or runtime environment unless the task
  explicitly requires secure migration and has an approved destination.
- Preserve simple references such as `${VAR}`.
- Replace literal password, token, secret, API key, private key, cookie,
  authorization, credential, and client-secret values with `REDACTED`.
- Redact credentials embedded in URLs and command arguments.
- Mark every embedded configuration block as sanitized and point to the original
  path for operations.

### 5. Update documentation atomically

- Replace the previous live-inventory section instead of appending duplicate
  snapshots indefinitely, unless the canonical rules require historical pages.
- Include a summary table before detailed configuration.
- Group multi-service workloads by project/stack; do not repeat one Compose file
  for every container.
- Update the canonical index description when the page’s coverage changes.
- Append a dated log entry describing scope, collection method, sanitization,
  correlations, and verification.

### 6. Verify before finalizing

Check all of the following:

- live object count equals documented object count;
- every active object appears exactly once in the summary;
- every documented stack/config path exists or is explicitly marked missing;
- embedded YAML/JSON/TOML parses successfully;
- Markdown fences and tables are structurally valid;
- no suspicious secret pattern remains;
- a second lightweight live query still matches the snapshot;
- temporary files containing raw or base64-encoded configuration are removed.

Report concrete verification results rather than “updated successfully”.

## Access fallback pattern

If direct SSH to a VM is unavailable but the hypervisor has a working guest
agent, use the agent for read-only introspection. Treat this as an access path,
not permission to mutate the guest. See
`references/docker-compose-inventory.md` for the Docker/Compose implementation.

## Pitfalls

- **Copying `docker inspect` wholesale:** it may contain environment secrets.
- **Using expanded Compose output:** interpolation can turn safe `${VAR}`
  references into exposed credentials.
- **Documenting one YAML per container:** multi-service stacks become duplicated
  and inconsistent.
- **Trusting stale labels blindly:** managers may migrate paths while containers
  retain old labels; reconcile labels with persisted mounts.
- **Treating a dated snapshot as live forever:** always label volatile state with
  a verification date.
- **Leaving temporary raw captures behind:** base64 is encoding, not protection.

## Completion report

The final response should state:

- live objects and grouped projects documented;
- canonical files changed;
- sanitization boundaries (`.env`/secrets not read, literals redacted);
- exceptional correlations or missing metadata;
- actual verification results;
- any access fallback used, without portraying a transient access failure as a
  permanent limitation.
