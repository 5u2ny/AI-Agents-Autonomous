"""Shared in-process tools for the autonomous agents (Claude Agent SDK).

These are defined with the SDK's ``@tool`` decorator and exposed via an
in-process MCP server, so they run inside this Python process — no extra
services, no API key. They sit alongside the SDK's built-in tools (``Write``
for saving deliverables, ``WebSearch`` for live market research).
"""

from __future__ import annotations

from typing import Any

from claude_agent_sdk import tool, create_sdk_mcp_server

# In-memory working memory for the duration of a run.
_SCRATCHPAD: list[str] = []

# The MCP server name; tool names are addressed as mcp__<server>__<tool>.
SERVER_NAME = "toolkit"


def _text(msg: str) -> dict[str, Any]:
    return {"content": [{"type": "text", "text": msg}]}


@tool(
    "calculator",
    "Evaluate an arithmetic expression for market sizing, funnels, budgets and "
    "ROI, e.g. '50000 * 0.03 * 1200'. Use this for ALL numeric reasoning.",
    {"expression": str},
)
async def calculator(args: dict[str, Any]) -> dict[str, Any]:
    expr = str(args.get("expression", ""))
    allowed = set("0123456789.+-*/() eE")
    if not expr or not set(expr) <= allowed:
        return _text("ERROR: expression empty or contains disallowed characters.")
    try:
        return _text(str(eval(expr, {"__builtins__": {}}, {})))  # noqa: S307
    except Exception as exc:  # surface the error to the model
        return _text(f"ERROR: {exc}")


@tool(
    "scratchpad",
    "Working memory across steps. action='add' with a note to record a "
    "decision/finding; action='list' to read everything back; action='clear' "
    "to reset.",
    {"action": str, "note": str},
)
async def scratchpad(args: dict[str, Any]) -> dict[str, Any]:
    action = str(args.get("action", "add"))
    if action == "add":
        note = str(args.get("note", "")).strip()
        if not note:
            return _text("ERROR: 'note' is required when action='add'.")
        _SCRATCHPAD.append(note)
        return _text(f"Note added. {len(_SCRATCHPAD)} note(s) on the scratchpad.")
    if action == "list":
        if not _SCRATCHPAD:
            return _text("Scratchpad is empty.")
        return _text("\n".join(f"{i+1}. {n}" for i, n in enumerate(_SCRATCHPAD)))
    if action == "clear":
        _SCRATCHPAD.clear()
        return _text("Scratchpad cleared.")
    return _text(f"Unknown scratchpad action: {action!r}")


def build_toolkit():
    """Return the in-process MCP server exposing the shared tools."""
    return create_sdk_mcp_server(
        name=SERVER_NAME,
        version="1.0.0",
        tools=[calculator, scratchpad],
    )


def toolkit_tool_names() -> list[str]:
    """Fully-qualified names so they can be pre-approved in allowed_tools."""
    return [f"mcp__{SERVER_NAME}__calculator", f"mcp__{SERVER_NAME}__scratchpad"]
