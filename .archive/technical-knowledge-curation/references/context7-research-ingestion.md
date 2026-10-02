# Context7 research ingestion

Detailed procedure for curating current vendor/framework documentation into a technical wiki.

## Source discovery

For each product:

1. Resolve the Context7 library ID using the official product name and a query that describes the operational scope.
2. Prefer exact official repositories/documentation sites over community forks, OpenAPI mirrors or curated link lists.
3. Record the chosen ID, why it was selected, branch/version if exposed, and consultation date.
4. If no authoritative match exists, say so and use another primary source rather than presenting a weak match as official.

## Query design

Use a small number of cohesive queries rather than one enormous prompt:

- **Architecture and operations:** components, lifecycle, health, routine administration.
- **Data and resilience:** persistence, backup, restore, HA, failure domains.
- **Security and automation:** identity, least privilege, API/CLI, updates, troubleshooting.

Keep each query product-specific. When researching several independent products, parallelize them, but integrate only after each result is complete.

## Integration sequence

1. Read the target wiki index and search existing pages.
2. Create/update canonical domain pages.
3. Add a cross-domain integrator page when products form one platform.
4. Add precise source sections with actual library IDs.
5. Update index and maintenance log.
6. Verify links, provenance, version warnings and absence of secrets.

## Evidence discipline

A source is “consulted” only after a successful documentation query/read returned content. These do **not** count on their own:

- a library ID guessed from memory;
- a local skill describing the product;
- a delegated research task still running;
- a placeholder source section;
- a generic vendor homepage that was not read.

If delegated research is used, inspect the completed result before integrating claims. Do not finalize the wiki while required research remains pending.

## Operational synthesis template

```markdown
# Product — operações

Resumo e escopo.

## Modelo mental e arquitetura
## Saúde e inventário
## Operação diária
## Rede e dependências
## Persistência e dados
## Segurança
## Backup e recuperação
## Atualização e rollback
## Automação e API
## Troubleshooting por sintomas
## Checklist de produção
## Relacionados
## Fontes
```

Adapt sections to the product. For storage systems, expand topology, integrity and restore. For orchestrators, expand reconciliation, workloads and control plane. For runtimes, expand builds, supply chain and isolation.

## Safety requirements

- State the failure domain of snapshots, replicas, RAID and clusters.
- Distinguish redundancy from backup.
- Require restore tests, not only successful backup jobs.
- Put pre-checks and rollback before destructive commands.
- Flag commands that force quorum, delete storage, prune volumes, reset ACLs or bypass safety.
- Never store real tokens, API keys, passwords, certificates or private endpoints unless the wiki policy explicitly permits the non-secret location reference.

## Quality bar

The result should let an experienced operator:

- understand architecture and dependencies;
- perform routine health checks;
- plan a safe change;
- identify first diagnostic commands;
- recognize dangerous shortcuts;
- recover from common failures;
- find the official source for version-specific detail.

Avoid mirroring every upstream option. Curate decision-relevant and recovery-relevant information.
