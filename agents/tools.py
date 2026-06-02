"""Shared tools the autonomous agents can use.

These are intentionally self-contained and offline-friendly so the agents run
without external API keys beyond Anthropic. Swap the handlers for real
integrations (CRM, web search, analytics) when wiring into production.
"""

from __future__ import annotations

import json
import os
from datetime import date
from pathlib import Path
from typing import Any

from .core import Tool

# Where the agents persist their deliverables.
ARTIFACT_DIR = Path(os.environ.get("AGENT_ARTIFACT_DIR", "runs"))


def _save_artifact(payload: dict[str, Any]) -> str:
    name = payload["name"]
    content = payload["content"]
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    path = ARTIFACT_DIR / name
    path.write_text(content, encoding="utf-8")
    return f"Saved artifact to {path} ({len(content)} chars)."


def _scratchpad(payload: dict[str, Any]) -> str:
    """A durable note store so the agent can plan across many steps."""
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    path = ARTIFACT_DIR / "scratchpad.json"
    notes: list[str] = []
    if path.exists():
        notes = json.loads(path.read_text(encoding="utf-8"))

    action = payload.get("action", "add")
    if action == "add":
        notes.append(payload["note"])
        path.write_text(json.dumps(notes, indent=2), encoding="utf-8")
        return f"Note added. {len(notes)} note(s) on the scratchpad."
    if action == "list":
        return json.dumps(notes, indent=2) if notes else "Scratchpad is empty."
    if action == "clear":
        path.write_text("[]", encoding="utf-8")
        return "Scratchpad cleared."
    return f"Unknown scratchpad action: {action}"


def _calculator(payload: dict[str, Any]) -> str:
    """Evaluate a basic arithmetic expression (for funnel / ROI / TAM math)."""
    expr = payload["expression"]
    allowed = set("0123456789.+-*/() eE")
    if not set(expr) <= allowed:
        return "ERROR: expression contains disallowed characters."
    try:
        return str(eval(expr, {"__builtins__": {}}, {}))  # noqa: S307 - sandboxed chars
    except Exception as exc:
        return f"ERROR: {exc}"


def _today(_: dict[str, Any]) -> str:
    return date.today().isoformat()


def save_artifact_tool() -> Tool:
    return Tool(
        name="save_artifact",
        description="Persist a finished deliverable (plan, doc, CSV) to disk so "
                    "the human can use it. Call this for every major output.",
        input_schema={
            "type": "object",
            "properties": {
                "name": {"type": "string",
                          "description": "Filename, e.g. 'gtm_plan.md'."},
                "content": {"type": "string", "description": "Full file content."},
            },
            "required": ["name", "content"],
        },
        handler=_save_artifact,
    )


def scratchpad_tool() -> Tool:
    return Tool(
        name="scratchpad",
        description="Working memory. Jot intermediate findings, decisions, or a "
                    "running plan so you can reason across many steps.",
        input_schema={
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["add", "list", "clear"]},
                "note": {"type": "string",
                          "description": "Required when action is 'add'."},
            },
            "required": ["action"],
        },
        handler=_scratchpad,
    )


def calculator_tool() -> Tool:
    return Tool(
        name="calculator",
        description="Evaluate arithmetic for sizing markets, funnels, budgets "
                    "and ROI (e.g. '50000 * 0.03 * 1200').",
        input_schema={
            "type": "object",
            "properties": {"expression": {"type": "string"}},
            "required": ["expression"],
        },
        handler=_calculator,
    )


def today_tool() -> Tool:
    return Tool(
        name="today",
        description="Get today's date (ISO format) for scheduling roadmaps.",
        input_schema={"type": "object", "properties": {}},
        handler=_today,
    )


def common_tools() -> list[Tool]:
    """The default toolbelt shared by both agents."""
    return [save_artifact_tool(), scratchpad_tool(), calculator_tool(), today_tool()]
