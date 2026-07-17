from __future__ import annotations

from attendance_reconciliation.mcp_server import handle


def test_mcp_initialize_and_list_tools():
    init = handle({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
    tools = handle({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})

    assert init is not None
    assert init["result"]["capabilities"] == {"tools": {}}
    assert tools is not None
    tool_names = {tool["name"] for tool in tools["result"]["tools"]}
    assert {"describe_project", "reconcile_sample", "explain_exception"} <= tool_names


def test_mcp_tool_call_returns_content():
    response = handle(
        {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {"name": "explain_exception", "arguments": {"code": "LATE_ARRIVAL"}},
        }
    )

    assert response is not None
    assert response["result"]["content"][0]["type"] == "text"
    assert "configured grace window" in response["result"]["content"][0]["text"]
