from __future__ import annotations

import json
import sys
from typing import Any

from .engine import reconcile
from .io import read_attendance, read_shifts


def describe_project() -> dict[str, Any]:
    return {
        "name": "Attendance Reconciliation Engine",
        "status": "local-clean-room-scaffold",
        "tools": ["describe_project", "reconcile_sample", "explain_exception"],
        "privacy": "Synthetic examples only; operational files stay local.",
    }


def explain_exception(code: str) -> dict[str, str]:
    explanations = {
        "ABSENT_WHILE_ROSTERED": "A planned shift has no matching clock events.",
        "PRESENT_WHILE_UNROSTERED": "An attendance event exists without a planned shift on the same date and site.",
        "LATE_ARRIVAL": "The first clock-in is later than the configured grace window.",
        "EARLY_DEPARTURE": "The final clock-out is earlier than the configured grace window.",
        "MISSING_CLOCK_EVENT": "A matching clock-in or clock-out is missing.",
        "UNMATCHED_CLOCK_EVENT": "A clock event was not matched to a shift and requires review.",
    }
    return {"code": code, "explanation": explanations.get(code, "Unknown exception code.")}


def reconcile_sample(shifts_path: str, attendance_path: str) -> dict[str, Any]:
    return reconcile(read_shifts(shifts_path), read_attendance(attendance_path))


TOOLS: dict[str, dict[str, Any]] = {
    "describe_project": {
        "description": "Describe the project, status and privacy boundary.",
        "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
    },
    "explain_exception": {
        "description": "Explain an attendance exception code.",
        "inputSchema": {
            "type": "object",
            "properties": {"code": {"type": "string"}},
            "required": ["code"],
            "additionalProperties": False,
        },
    },
    "reconcile_sample": {
        "description": "Run reconciliation for local CSV or JSON sample files.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "shifts_path": {"type": "string"},
                "attendance_path": {"type": "string"},
            },
            "required": ["shifts_path", "attendance_path"],
            "additionalProperties": False,
        },
    },
}


def _content(payload: Any) -> dict[str, Any]:
    return {"content": [{"type": "text", "text": json.dumps(payload, indent=2, default=str)}]}


def _call_tool(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    if name == "describe_project":
        return _content(describe_project())
    if name == "explain_exception":
        return _content(explain_exception(str(arguments["code"])))
    if name == "reconcile_sample":
        return _content(
            reconcile_sample(
                shifts_path=str(arguments["shifts_path"]),
                attendance_path=str(arguments["attendance_path"]),
            )
        )
    raise KeyError(name)


def handle(request: dict[str, Any]) -> dict[str, Any] | None:
    request_id = request.get("id")
    method = request.get("method")
    params = request.get("params") or {}

    try:
        if method == "notifications/initialized":
            return None
        if method == "initialize":
            result = {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "attendance-reconciliation-engine", "version": "0.1.0-local"},
            }
        elif method == "tools/list":
            result = {
                "tools": [
                    {"name": name, **metadata}
                    for name, metadata in TOOLS.items()
                ]
            }
        elif method == "tools/call":
            result = _call_tool(str(params["name"]), dict(params.get("arguments") or {}))
        else:
            return {"jsonrpc": "2.0", "id": request_id, "error": {"code": -32601, "message": "Method not found"}}
        return {"jsonrpc": "2.0", "id": request_id, "result": result}
    except KeyError as exc:
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32602, "message": f"Invalid params: missing or unknown {exc}"},
        }
    except Exception as exc:  # pragma: no cover - defensive JSON-RPC boundary
        return {"jsonrpc": "2.0", "id": request_id, "error": {"code": -32000, "message": str(exc)}}


def main() -> int:
    for line in sys.stdin:
        if not line.strip():
            continue
        response = handle(json.loads(line))
        if response is not None:
            print(json.dumps(response), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
