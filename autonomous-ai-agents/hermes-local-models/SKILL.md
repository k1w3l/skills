---
name: hermes-local-models
description: "Use when configuring Hermes with a local model."
version: 1.1.0
author: Hermes Agent + local environment
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [hermes, local-models, ollama, llama.cpp, vllm, openai-compatible, tool-calling]
    related_skills: [hermes-agent, llama-cpp, huggingface-local-models]
---

# Hermes with local models

Use this class-level workflow to connect Hermes Agent to a locally served LLM through an OpenAI-compatible endpoint. The procedure covers Ollama first, then generalizes to llama.cpp, vLLM, LM Studio, and similar servers.

## Standing rules

- Consult the user's wiki index and the relevant local-LLM page before selecting a backend or model; a dated hardware page is context, not live state.
- Treat “local model” as two separate scopes: the main conversation model and auxiliary tasks such as compression, vision, titles, approvals, and background review. Do not claim an all-local setup until both scopes have been checked.
- Use an agentic model with reliable tool calling for Hermes. A model that answers chat correctly but cannot emit function calls is not a valid Hermes replacement.
- Size the runtime from model weights **plus** KV cache, context window, desktop/compositor usage, and auxiliary workloads; do not choose solely from the advertised model-file size.
- Keep the endpoint literal and exact. For Ollama through the OpenAI-compatible client, use a base URL ending in `/v1`; do not “repair” it to a bare server root.
- For local endpoints, leave the API key empty when the wizard accepts that, or use the documented non-secret placeholder `no-key` when a client requires a value. Never invent or expose a real credential.
- Keep the model's server-side context window and Hermes' configured context length aligned. A successful configuration write is not proof that the server accepted the requested window.
- After changing the provider, endpoint, model, or tool-routing configuration, start a new CLI session or reload the gateway before validating behavior.

## Procedure

### 1. Inventory the live host

Read the wiki first, then inspect the actual machine and current Hermes profile. Follow the user's explicitly chosen backend; prefer an already active backend only when no backend was requested. For LM Studio, use `lms server status --json` and `lms ps --json` to confirm the live server and loaded-instance context rather than reusing a prior snapshot. At minimum establish:

```bash
command -v hermes
command -v ollama
hermes --version
ollama --version
systemctl is-active ollama
curl -fsS --max-time 5 http://127.0.0.1:11434/api/tags
hermes config
```

Redact credentials in any captured config output. If no backend was requested and Ollama is already installed and active, prefer it instead of introducing a second local server. If no backend is active, choose one deliberately and record whether it will be managed by systemd, a user service, Docker, or a foreground process. Do not print raw process command lines: local inference workers can carry internal API keys in argv.

### 2. Choose a tool-capable model that fits

Select the exact model tag from the backend's current model catalog or official model page. For Ollama:

```bash
ollama pull <model-tag>
ollama run <model-tag> "Respond only: OK"
```

On a 16-GB GPU, start with a tool-capable model in the roughly 7–12B class when reliable interactive latency matters. A 20B model can be a better reasoning/coding choice but may spill to system RAM once Hermes' large context and tool schemas are included. Do not use a 20GB+ model as the first recommendation for a 16-GB card merely because it has stronger benchmark claims.

### 3. Give Hermes enough context for tool use

The current Hermes agentic path requires at least 64,000 tokens of context. Use a safe power-of-two target such as `65536`, subject to the model and hardware actually sustaining it.

For systemd-managed Ollama, configure the service rather than only exporting a variable in the current shell:

```bash
sudo systemctl edit ollama.service
```

Add:

```ini
[Service]
Environment="OLLAMA_CONTEXT_LENGTH=65536"
```

Then reload and restart the service:

```bash
sudo systemctl daemon-reload
sudo systemctl restart ollama
```

For a per-model Ollama window, use a Modelfile instead:

```text
FROM <model-tag>
PARAMETER num_ctx 65536
```

Create a derived model with `ollama create` and configure Hermes to use that derived tag. Keep the server-side setting authoritative; `model.context_length` in Hermes describes or caps the usable window but should not be treated as a substitute for configuring Ollama.

### 4. Connect Hermes through a custom endpoint

Use the official picker on an existing install:

```bash
hermes model
```

Select **Custom endpoint** and enter:

- Base URL: `http://127.0.0.1:11434/v1` for local Ollama.
- API key: empty, or `no-key` if the prompt/client requires a value.
- Model: the exact pulled tag.
- Transport: OpenAI Chat Completions when the picker asks; otherwise allow endpoint auto-detection.
- Context length: match the server-side runtime window, normally `65536` for Hermes tool use.

A direct configuration has the equivalent shape:

```yaml
model:
  default: "<model-tag>"
  provider: "custom"
  base_url: "http://127.0.0.1:11434/v1"
  context_length: 65536
```

Use `hermes config set` for individual keys or `hermes config edit` to merge the block; do not overwrite unrelated profile settings.

### 5. Audit auxiliary routing

Inspect `hermes config` and `config.yaml` for explicit `auxiliary.*.provider`, `model`, `base_url`, and `api_key` values. For a fully local setup:

- Set text-only auxiliary tasks such as compression or title generation to `provider: main` when the main model supports that workload.
- Use a local multimodal model for `auxiliary.vision` if the main model cannot accept images.
- Remove stale cloud overrides only with the user's permission if removal would discard a deliberate fallback; otherwise replace them with the intended local route and preserve a cloud fallback explicitly.

For a main multimodal local model, the common shape is:

```yaml
auxiliary:
  compression:
    provider: "main"
    model: ""
  vision:
    provider: "main"
    model: ""
```

For a text-only main model, point only vision at a separate local multimodal custom endpoint instead of pretending the main model can process images.

### 6. Verify the complete path

Run configuration and endpoint checks after a fresh Hermes process:

```bash
hermes doctor
hermes config
curl -fsS http://127.0.0.1:11434/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{"model":"<model-tag>","messages":[{"role":"user","content":"Respond only: API OK"}]}'
hermes chat -q 'Respond only: Hermes local OK.'
ollama ps
```

Then perform one harmless tool test in an interactive session, such as asking Hermes to list the current directory without changing anything. Check that `ollama ps` shows the intended model and observe whether execution remains on GPU or spills to RAM. Verify an auxiliary task separately when claiming a fully local setup.

## Troubleshooting rules

- **HTTP 404 from Ollama:** inspect the exact `model.base_url`; the OpenAI SDK appends `/chat/completions`, so the configured base URL must already include `/v1`.
- **“Context too small” or startup rejection:** inspect the Ollama service environment or Modelfile and raise the actual runtime window to at least 64K; changing only Hermes' display/config value is insufficient.
- **Slow responses or GPU spill:** move down to a smaller tool-capable model, close competing GPU workloads, or accept RAM spill explicitly. Do not silently lower the agentic context below Hermes' floor to hide the symptom.
- **No tool calls:** verify the model's current official capability list, the OpenAI-compatible request path, the fresh Hermes session, and that toolsets are enabled. A plain text smoke test does not validate tool calling.
- **Main model is local but privacy is incomplete:** inspect auxiliary routing; explicit cloud providers for vision/compression/title/background tasks remain active even when `model.provider` is `custom`.

## References

- Read [`references/lmstudio-hermes.md`](references/lmstudio-hermes.md) for LM Studio live discovery, safe reload, explicit local/auxiliary routing, launch persistence and tool-event verification.
- Read [`references/ollama-hermes.md`](references/ollama-hermes.md) for the Ollama-specific decision table, exact configuration snippets, context sizing, and local-only auxiliary routing.
- Use `hermes-agent` for Hermes configuration semantics and lifecycle commands.
- Use `llama-cpp` or `huggingface-local-models` when the backend is llama.cpp/GGUF rather than Ollama.
