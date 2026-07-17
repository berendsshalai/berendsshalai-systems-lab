# MCP

The local stdio MCP server implements JSON-RPC methods for `initialize`, `tools/list` and `tools/call`.

It exposes safe tools:

- `describe_project`
- `reconcile_sample`
- `explain_exception`

Start it with:

```bash
python -m attendance_reconciliation.mcp_server
```

Example tool call:

```json
{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"explain_exception","arguments":{"code":"LATE_ARRIVAL"}}}
```
