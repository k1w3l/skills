# Hermes catalog MCP: installation and verification reference

Use this as a compact example for catalog-backed MCP configuration. It is an example, not a requirement to install Context7 for every task.

## Validated Context7 shape

- Catalog name: `context7`
- Transport: HTTP
- Endpoint: `https://mcp.context7.com/mcp`
- Authentication reported by the test: none
- Verification commands:

```bash
hermes mcp list
hermes mcp test context7
```

A successful test reported a connected server and two discovered tools: `resolve-library-id` and `query-docs`.

## UI recovery rule

When the consent card is not visible, confirm the server is still absent with `hermes mcp list`, then reissue the approved consent request once. Do not hand-edit `~/.hermes/config.yaml`, guess an endpoint, or paste credentials as a workaround.

## Completion checklist

- [ ] Correct catalog name selected.
- [ ] Consent/install flow completed.
- [ ] `hermes mcp list` shows the intended server as enabled.
- [ ] `hermes mcp test <name>` connects and discovers tools.
- [ ] A new Hermes session/process is started before using the new schemas.
- [ ] Wiki records transport, status, and tool names without secrets.
