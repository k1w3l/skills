# Gmail inbox organization workflow

Use these notes when Sr. Kiwel asks to organize Gmail Inbox tabs or bulk-label email.

## User preferences captured

- Do not include `JARVIS` or the assistant name in Gmail label names. Use clean labels such as `Financeiro e Contas`, not `JARVIS/Financeiro e Contas`.
- Before the first organization pass, show the proposed labels and any proposed ignored/newsletter senders before applying changes.
- After the user approves a concrete proposal, subsequent requests to apply the same process to another Gmail tab/category may proceed with the same approved rules.
- Never delete messages for this workflow. Add labels and remove the source label/category such as `INBOX` or `CATEGORY_UPDATES` so mail remains searchable/archived.

## Label taxonomy that worked well

Approved labels:

- `Financeiro e Contas`
- `Compras e Entregas`
- `Cursos e Carreira`
- `Jogos e Lazer`
- `Viagens e Eventos`
- `Promoções e Marketing`
- `Tecnologia e Infra`
- `Streaming e Assinaturas`
- `Notícias e Newsletters`
- `Segurança e Acessos`
- `Outros`

## Safe workflow

1. Read a representative sample first, e.g. `in:inbox newer_than:180d`, and summarize counts by proposed label.
2. Show proposed ignored/newsletter senders before applying them to monitoring filters.
3. Once approved, create/reuse labels with the clean names above.
4. Apply exactly one primary label per message using ordered rules from most specific/important to broadest.
5. Remove only the source label/category (`INBOX`, `CATEGORY_UPDATES`, etc.). Do not trash or delete messages.
6. Verify independently after the run: count remaining messages in the source query and report any failures.

## Efficient implementation pattern

For small samples, per-message `messages.modify` is acceptable. For large categories/tabs, use Gmail search queries plus `users.messages.batchModify` in chunks of up to 1000 IDs:

- Build a service with Hermes Google OAuth token at `~/.hermes/google_token.json` using scopes including `gmail.modify`.
- For each label, list IDs matching the source query plus category terms.
- Batch modify: `addLabelIds: [label_id]`, `removeLabelIds: [source_label]`.
- After each label batch removes the source label, those messages are not captured by later broader categories.
- Finish by labeling all remaining source messages as `Outros`.

Examples of source queries:

- Inbox: `in:inbox`
- Updates tab: `category:updates`, source label `CATEGORY_UPDATES`

## Rule order

Use this order so specific/important items win before broad promotional/newsletter matches:

1. `Segurança e Acessos`
2. `Financeiro e Contas`
3. `Compras e Entregas`
4. `Viagens e Eventos`
5. `Cursos e Carreira`
6. `Tecnologia e Infra`
7. `Streaming e Assinaturas`
8. `Jogos e Lazer`
9. `Notícias e Newsletters`
10. `Promoções e Marketing`
11. `Outros`

## Pitfalls

- Gmail `batchModify` can return transient `backendError` or `failedPrecondition` on large chunks. Treat this as a batch-level failure to report/retry, not a reason to abandon the workflow. Verify the final source count; if it is zero, the tab/source is successfully cleared even if some earlier broader query chunks failed after messages had already moved.
- An inline shell one-liner containing sensitive-looking token path text can be mangled by secret redaction. Prefer writing a script file and reading it back for syntax validation before executing.
- Gmail category labels such as `CATEGORY_UPDATES` are removable through `batchModify`; use independent verification with `category:updates` afterward.
- The `Outros` category is expected for anything not confidently classified; do not overfit rules from a single sample.
