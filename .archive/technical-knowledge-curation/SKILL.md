---
name: technical-knowledge-curation
description: Curate authoritative technical documentation into a durable operational wiki. Use for multi-product documentation research, Context7 ingestion, runbook creation, class-level knowledge synthesis, source provenance, index/log maintenance, and verification of technical knowledge bases.
version: 1.0.0
created_by: agent
---

# Technical Knowledge Curation

Turn official technical documentation into a durable, navigable operational knowledge base rather than a session transcript or indiscriminate documentation mirror.

## When to use

Use this skill when asked to:

- update a wiki from vendor/framework documentation;
- research several infrastructure products and synthesize operational guidance;
- create or maintain DevOps runbooks and checklists;
- ingest Context7 or other authoritative sources into durable notes;
- organize technical knowledge into canonical class-level pages.

For Wiki-Jarvis, follow the `wiki-jarvis` skill first for location, consultation order, index, log, links and secret-handling rules. This skill adds the research and synthesis workflow.

## Core principles

1. **Consult before creating:** search the target knowledge base before external research.
2. **Authority before convenience:** prefer official/current documentation for APIs, versions and operational behavior.
3. **Class-level pages:** organize by durable domain or product, not by session, query or incident.
4. **Operational synthesis:** capture decisions, checks, failure modes, recovery and verification—not merely definitions.
5. **Precise provenance:** cite only sources actually resolved and consulted.
6. **Version awareness:** separate stable principles from version-sensitive procedures.
7. **Recovery-first safety:** destructive procedures need prerequisites, backup, rollback and verification.
8. **No secrets:** never persist credentials, tokens, keys or live secret-bearing examples.

## Workflow

### 1. Inspect the existing knowledge base

- Read the index and maintenance log.
- Search product names, aliases, acronyms and related concepts.
- Read canonical pages and follow internal links.
- Decide whether to patch an existing page or create a genuinely new class-level page.

### 2. Load domain skills

Load relevant product/platform skills as topic maps and operational context. Do not treat local skills as substitutes for current official documentation when facts are volatile.

### 3. Research authoritative sources

For Context7:

1. Resolve the official library ID for each product.
2. Choose by exact product match, source reputation, coverage and relevance.
3. Query coherent topics separately: architecture/operation, data/security, automation/troubleshooting.
4. For multiple independent products, research in parallel where practical.
5. Do not write “consulted via Context7” until the query result for that product has actually returned.

See `references/context7-research-ingestion.md` for the detailed procedure and pitfalls.

### 4. Design the page set

For a multi-product platform, prefer:

- one integrator page for cross-cutting architecture, dependencies and operating model;
- one canonical page per durable domain/product;
- links between related pages;
- no one-page-per-query or one-page-per-session sprawl.

A strong operational page usually contains:

- purpose and mental model;
- architecture and failure domains;
- prerequisites and health checks;
- routine operations;
- security and least privilege;
- backup, restore and disaster recovery;
- upgrades, compatibility and rollback;
- automation/API considerations;
- troubleshooting by symptom;
- production/readiness checklist;
- related pages and sources.

### 5. Synthesize, do not mirror

- Convert large documentation sets into concise operational knowledge.
- Preserve exact commands only when they are reusable and safe in context.
- Explain what success looks like and what evidence to collect.
- Call out dangerous shortcuts and first-response anti-patterns.
- Link to upstream documentation for exhaustive flags and version-specific details.

### 6. Record provenance

Each page should include:

- actual Context7 library ID(s) used;
- official URL/repository;
- consultation date;
- version/branch when known;
- a warning to verify against the installed version when procedures are version-sensitive.

Never claim a source was consulted based on memory, a local skill or an unfinished delegated task.

### 7. Close the knowledge loop

- Update the index for every new page.
- Add a concise dated maintenance-log entry.
- Use internal links to connect concepts.
- Patch locally rather than rewriting unrelated content.
- Report pages created/updated and sources consulted.

## Verification checklist

- [ ] Existing wiki was consulted first.
- [ ] Official source/library ID resolved for every researched product.
- [ ] Every source claim corresponds to a completed query/read.
- [ ] Pages are class-level and non-duplicative.
- [ ] New pages appear in the index.
- [ ] Maintenance log was updated.
- [ ] Internal links resolve.
- [ ] No credentials or secret values were persisted.
- [ ] Version-sensitive steps are labeled.
- [ ] Backup/rollback/restore guidance is actionable.
- [ ] Checklists and troubleshooting include verification, not just commands.

## Common pitfalls

- Finalizing while delegated research is still pending.
- Adding provenance placeholders before sources are actually consulted.
- Treating snapshots, replicas or RAID as independent backups.
- Copying upstream docs verbatim instead of curating operationally useful knowledge.
- Creating many narrow session pages instead of canonical product/domain pages.
- Publishing destructive commands without pre-checks and rollback.
- Mixing current environment state into a durable general runbook without dates or evidence.
