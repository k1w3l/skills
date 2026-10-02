# Subject diversity and cron model-drift recovery

## Semantic diversity contract

Use this pattern when an operator asks for a maximum number of items per subject:

1. Define broad, stable editorial groups in the deterministic collector. Group by the central subject, not by exact wording, product, company, version, or application.
2. Emit a canonical `subject_group` with every candidate. Typical examples are `IA` for AI/LLMs/agents/inference and `Linux` for Linux/kernel/distributions/Linux desktop.
3. Repeat the cap in the cron prompt. Require the curator to copy the canonical group into each selected article, replace excess items with strong candidates from unused groups, and send fewer items rather than padding the edition.
4. Add a delivery-side validator before the first header or card is sent. Return an actionable `subject_limit_exceeded` error so the curator can retry once with a smaller or more diverse selection.
5. Accept only canonical group labels from the collector. If a selection supplies an unknown label, infer the group again from title, summary, and source so labels cannot bypass the cap.
6. Scope the validator to the edition that requested it; a technology-news diversity rule should not silently alter a separate focused community digest.

The invariant is `up to N total items` and `at most M per semantic subject`. If fewer than N strong items remain after the cap, keep the edition shorter.

## Model-drift recovery

A scheduled job may show `last_status: error` while its collector and delivery path are healthy. Inspect the saved cron output for `drift_skip` before changing feeds or Telegram routing. This means the job was created with a different global inference model and is unpinned, so Hermes intentionally made no model call.

Recover a recurring job by pinning the intended current provider and model, preserving its schedule and prompt:

```fish
hermes cron edit <JOB_ID> --provider <provider> --model <model>
```

Then verify the job is enabled, the pin is present, the next run is scheduled in the editorial timezone, and the collector returns parseable candidates. Do not force a manual rich-card run merely to test a fix unless the operator explicitly authorizes an extra edition; validate the collector, prompt, and saved schedule instead.

## Verification evidence

Report these stages separately:

- collector: candidate count, date window, source errors, and real URLs;
- generation: whether the curator selected within the subject cap;
- delivery: card-tool result and platform acceptance;
- persistence: sent rows/feedback records where applicable.

A scheduler `ok` or a `[SILENT]` response alone does not prove that cards were delivered.
