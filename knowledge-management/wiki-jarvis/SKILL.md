---
name: wiki-jarvis
description: >-
  Compatibility alias for the user's unified wiki at
  /mnt/NAS/Sync/Documentos/Pessoal/Wiki/wiki/. The former Wiki-Jarvis and
  Wiki-Devops vaults were merged; use the `wiki` skill and the canonical policy
  in sobre-a-wiki.md for all consultation, documentation, and incremental `raw`
  ingestion. Never write to the former split-vault paths.
---

# Wiki-Jarvis compatibility alias

The former Wiki-Jarvis vault no longer operates as a separate knowledge base.
All durable knowledge, operational state, procedures, decisions, and source
ingestion now belong to the unified vault:

```text
/mnt/NAS/Sync/Documentos/Pessoal/Wiki/wiki/
```

For every task that triggers this compatibility skill:

1. Load and follow the `wiki` skill.
2. Read `/mnt/NAS/Sync/Documentos/Pessoal/Wiki/wiki/sobre-a-wiki.md` as the
   canonical policy.
3. Consult pages under `wiki/wiki/`, beginning with `wiki/wiki/index.md`.
4. Record durable changes in the canonical page, `wiki/wiki/index.md`, and
   `wiki/wiki/log.md` as required by the policy.
5. Treat the isolated command `raw` as incremental ingestion of only new or
   changed sources under `wiki/raw/`, preserving originals.
6. Never store credentials, raw operational dumps, or ephemeral task progress.
7. Do not read from or write to the former `Wiki-Jarvis/` or `Wiki-Devops/`
   paths as if they were active vaults.

This skill intentionally contains no independent workflow; it exists only to
redirect older triggers and references to the unified `wiki` skill.
