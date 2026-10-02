---
name: wiki-knowledge-management
description: "Use for Eduardo's unified wiki queries and maintenance."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [wiki, knowledge-management, research, documentation]
    related_skills: []
---

# Unified Wiki Knowledge Management

Use this skill for questions about, research into, ingestion for, or maintenance of Eduardo Kiwel Teixeira's unified wiki.

## When to Use

Use this skill when the user asks about the unified wiki, asks a question whose answer may be documented there, provides a source to ingest, requests a wiki audit, or asks to record durable knowledge, decisions, routines, or guidance.

## Canonical locations

Define these paths before working:

```text
WIKI_ROOT=/mnt/NAS/Sync/Documentos/Pessoal/Wiki/wiki
POLICY=$WIKI_ROOT/sobre-a-wiki.md
INDEX=$WIKI_ROOT/wiki/index.md
LOG=$WIKI_ROOT/wiki/log.md
RAW=$WIKI_ROOT/raw
```

The wiki vault and this skill are separate: the vault stores knowledge; this skill stores the procedure for consulting and maintaining it.

## Query procedure

1. **Check the canonical vault first.** If the NAS is unavailable or the paths cannot be read, say that the wiki was not consulted; never imply that it was.
2. **Read `INDEX` before any other knowledge source** when answering a wiki-domain question. Use it to identify the canonical page or pages.
3. **Search for the topic** with `search_files` when the index is ambiguous or the vault is large, then read the relevant pages with `read_file`. Prefer updating an existing canonical page over creating a duplicate.
4. **Synthesize only from pages actually read.** Cite each consulted page as `(wiki: page-name)`; do not cite an index entry as if its target page had been read.
5. **Check freshness.** Treat dated state pages as snapshots, not live state. Verify operational facts on the machine or through the appropriate current tool before making an operational recommendation.
6. **Escalate technical documentation in order.** If the wiki lacks documentation for a library, framework, SDK, API, CLI, or cloud service, or its documentation is stale, consult Context7 first, then current official web sources, and only then general knowledge.
7. **Do not force the wiki onto clearly unrelated subjects.** Answer those normally without artificial lookup.

### Query pitfall

Read the index before the policy, web, or training when the user asks a wiki-domain question — the index is the navigation source and prevents selecting a stale or duplicate page.

## Documentation closeout

When a task creates something, teaches a durable fact, changes a routine, or establishes guidance:

1. Search the wiki before writing.
2. Update the existing canonical page when it covers the subject; create a new lowercase, hyphenated page only when no suitable page exists.
3. Record the useful final state, rationale, procedure, implications, and source provenance; omit raw trial-and-error and ephemeral logs.
4. Add `[[wiki-links]]` to related pages.
5. Update `INDEX` with a one-line description for every new page.
6. Append the operation and changed pages to `LOG`.
7. Report what was changed, and treat this documentation as part of task completion rather than an optional later offer.

Agents are authorized to create and edit wiki pages without asking first. Deleting files, resources, or data still requires explicit permission.

## Ingestion and preservation

- Never modify anything under `RAW`; source documents are immutable.
- For the isolated command `raw`, ingest only new or changed sources incrementally, skip unchanged processed sources, and preserve originals. When changes are incorporated, update `INDEX` and `LOG`.
- Keep secrets out of the wiki: never record passwords, tokens, private keys, cookies, or credential values. Record only where a credential is administered.
- Distinguish confirmed facts, decisions, hypotheses, and claims needing verification; note contradictions explicitly.

## Verification checklist

Before answering or closing the task, verify:

- the canonical index was consulted first for wiki-domain questions;
- every cited wiki page was actually read;
- volatile operational facts were checked live;
- missing or stale technical documentation followed the Context7-before-web order;
- required page, index, and log updates were completed;
- raw sources and secrets were preserved safely.
