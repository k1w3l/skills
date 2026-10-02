# LM Studio with Hermes

## Exact runtime and route

- Follow the user's chosen backend; do not substitute Ollama merely because its service is active.
- Use `lms ls --json`, `lms ps --json`, `lms server status --json` and installed `--help`. The API identifier is `identifier`; usable loaded context is `contextLength`, not `maxContextLength`.
- Never print raw inference-worker argv: it can contain internal API keys.
- Prefer native `lmstudio` only if the installed runtime actually resolves it. Otherwise use the verified OpenAI-compatible custom route, not an assumed new feature from upstream docs.

```yaml
model:
  provider: custom
  default: <exact-api-model-id>
  base_url: http://127.0.0.1:1234/v1
  api_mode: chat_completions
  api_key: no-key-required
  context_length: 65536
```

The key is a non-secret SDK placeholder, valid only for an unauthenticated loopback endpoint. Preserve cloud credentials separately. Back up config and use `hermes config set` when config-file tools refuse writes; never work around the protected write with Python.

## Load and restore safely

```bash
lms load <exact-model-key> --context-length 65536 --parallel 1 --identifier <exact-api-id> -y
lms server start --port 1234 --bind 127.0.0.1
lms ps --json
ss -ltn '( sport = :1234 )'
```

Reload only the exact target when idle and its queue is empty. `lms unload <identifier>` releases the runtime, not downloaded weights; never use `unload --all` for a single-model correction. Do not force `--gpu max` when weights plus KV cache exceed VRAM. Keep concurrency low when the desktop shares the GPU.

Hermes preserves an already-loaded instance's context. A client `context_length` pin does not fix an instance reloaded in the GUI with 8K. Set per-model defaults in LM Studio or supply an on-demand helper that restores context/concurrency, refuses to interrupt busy instances, starts the loopback server when stopped, checks `/v1/models`, and launches an explicit local model alias. Do not enable heavy model loading at boot unless requested. An alias needs its own endpoint and credential placeholder, never a borrowed cloud key.

## Auxiliaries and evidence

- Audit vision, compression, titles, approvals, review, skills hub, MCP and curator. Rely on `provider: main` only after installed-runtime validation; explicit `custom` per-task model/URL/key is the fallback.
- Verify actual auxiliary inference in addition to route resolution. If vision changes, use a clearly labelled synthetic image fixture and confirm the expected colour/text is recognized.
- Allow enough completion tokens for reasoning plus final text. A tiny token limit can yield reasoning only, which is not a successful text smoke test.
- Verify tool calls via `--format stream-json`: require `tool_use` with the requested harmless command plus matching successful `tool_result`, not merely a model claim.
- Check the exact gateway after an authorized reload; do not kill the Desktop host.
- Distinguish doctor model-routing failures from unrelated npm or optional-integration warnings. Exit 1 is not globally clean even if local routing passes.
- Web, remote MCP, hosted image/video generation and voice tools can still use the network; do not claim strict offline operation from local LLM routes alone.

Sources: official Hermes providers/configuration docs via Context7, installed CLI/source, LM Studio CLI and Developer Docs. Recheck version-sensitive flags before use.
