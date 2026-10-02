---
name: mcp-operations
description: "Use when configuring MCP servers in Hermes. Verify safely."
version: 1.0.0
author: "Hermes Agent"
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [mcp, hermes, configuration, integrations, tools]
    related_skills: [hermes-agent, context7-mcp]
---

# MCP Operations in Hermes

Use this skill for the class of work that adds, enables, authorizes, verifies, or troubleshoots Model Context Protocol servers in Hermes Agent. It covers catalog-backed remote servers and local servers without tying the workflow to one provider.

## Operating rules

- Prefer the Hermes MCP catalog when the requested server is listed.
- For catalog installation, enablement, or OAuth authorization, use the `setup_mcp` consent flow. Do not hand-edit `mcp_servers` in `config.yaml` and do not bypass a missing consent step with guessed credentials.
- Treat server installation as an external state change: verify the exact server afterward with both `hermes mcp list` and `hermes mcp test <name>`.
- Never put API keys, bearer tokens, cookies, or private headers in chat, the wiki, or a skill. Record only where credentials are managed and whether authentication was required.
- Do not claim that tools are available in the current conversation until the new session/process has loaded them.

## Workflow

### 1. Identify the server and transport

Use the server named by the user. If the request only says “configure MCP” and no server is implied, ask which catalog entry, HTTP endpoint, or stdio command is intended. Do not invent a private endpoint or select a write-capable integration merely because it is available.

For a catalog-backed server, inspect the local catalog before installation:

```bash
hermes mcp catalog
hermes mcp list
```

`hermes mcp list` is the preflight for the current profile. It distinguishes an absent server from a configured but disabled one.

### 2. Request the approved state change

Use the consent tool with the catalog name:

- `action="install"` for a new catalog server.
- `action="enable"` for a configured but disabled server.
- `action="authorize"` when the server requires an OAuth flow.

Give the consent card a short reason tied to the user's task. Do not ask the user to paste a token into the conversation.

If the consent card is not visible, do not edit the YAML or run an improvised install. First check `hermes mcp list`; if the server is still absent, reissue the same consent request once after the user reports the UI problem. If it still cannot be presented, stop with the actual blocker instead of claiming success.

For a custom server that is not in the catalog, obtain the exact endpoint or command and authentication method first, then use Hermes' documented CLI path. Keep custom configuration separate from catalog installation and verify it with the same readback/test steps.

### 3. Verify the resulting state

Run both checks after installation or enablement:

```bash
hermes mcp list
hermes mcp test <server-name>
```

Accept success only when the list shows the intended server enabled and the test reports a successful connection. Capture the discovered tool count and names when available. A successful installer call alone is not proof that the server is usable.

For HTTP servers, confirm the endpoint and reported authentication mode without printing secret headers. For stdio servers, confirm that the executable and package resolved. If a test fails, report the concrete connection error and do not substitute a plausible result.

### 4. Load the tools in Hermes

MCP discovery normally happens when the Hermes process starts. After adding or removing a server, start a new Hermes session or restart the relevant process before relying on the new tool schemas. This prevents a stale conversation from being treated as if it had already received the new tool definitions.

MCP tool names normally follow:

```text
mcp_<server>_<tool>
```

Hyphens and dots are normalized to underscores. Use the discovered names, not guessed names.

### 5. Record durable knowledge

If configuration succeeds, update the canonical wiki page for MCP or the relevant integration, the wiki index when navigation/status changes, and the append-only log. Record:

- server name and transport;
- endpoint or command when non-secret;
- enabled/disabled state;
- verification result and discovered tools;
- session-restart implication;
- where credentials are administered, without their values.

See `references/hermes-catalog-setup.md` for a compact catalog-installation example and verification checklist.

## Failure patterns

- **No servers configured**: the profile has no `mcp_servers` entries; inspect the catalog and use the approved setup flow.
- **Server absent after an install request**: the consent flow did not complete; check the list and retry the consent request once if the card was not rendered.
- **Connection failure**: check the endpoint, command/package availability, and connect timeout; do not mark the server enabled as usable until `hermes mcp test` passes.
- **Tools missing in chat**: verify discovery/test output, then start a new session; do not infer tool names from the provider's marketing page.
- **Credential exposure risk**: stop, redact the value, and continue only through the approved credential configuration path.

## Related skills

- `hermes-agent` — Hermes CLI and native MCP client reference.
- `context7-mcp` — when the configured server is Context7 and the task requires current library documentation.
