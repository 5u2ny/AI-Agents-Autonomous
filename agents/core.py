"""Core autonomous-agent engine — runs on your Claude subscription.

Built on the **Claude Agent SDK**, which drives the Claude Code agent loop as a
library. Authentication piggybacks on whatever Claude Code is logged into, so
once you've run ``claude login`` with your Pro/Max (or Team) subscription these
agents run with **no ``ANTHROPIC_API_KEY``** and no per-token billing.

The SDK owns the autonomous loop (think -> call tool -> observe -> repeat). We
just hand it a system prompt, a toolbelt, and a goal.
"""

from __future__ import annotations

import asyncio
import os
from dataclasses import dataclass, field
from typing import Any, Optional

try:
    from claude_agent_sdk import (
        query,
        ClaudeAgentOptions,
        AssistantMessage,
        TextBlock,
        ResultMessage,
    )
except ImportError as exc:  # pragma: no cover - friendly hint
    raise ImportError(
        "The 'claude-agent-sdk' package is required. Run:\n"
        "  pip install -r requirements.txt\n"
        "and make sure the Claude Code CLI is installed and logged in "
        "(`claude login`)."
    ) from exc


# Optional model override. If unset, the SDK uses your subscription's default.
DEFAULT_MODEL = os.environ.get("AGENT_MODEL")  # e.g. "claude-sonnet-4-6"
DEFAULT_MAX_TURNS = int(os.environ.get("AGENT_MAX_TURNS", "30"))


@dataclass
class AgentResult:
    """Outcome of an autonomous run."""

    answer: str
    thoughts: list[str] = field(default_factory=list)


class SubscriptionAgent:
    """A goal-driven autonomous agent powered by your Claude subscription."""

    def __init__(
        self,
        name: str,
        system_prompt: str,
        mcp_servers: Optional[dict[str, Any]] = None,
        allowed_tools: Optional[list[str]] = None,
        model: Optional[str] = DEFAULT_MODEL,
        max_turns: int = DEFAULT_MAX_TURNS,
        cwd: Optional[str] = None,
        verbose: bool = True,
    ) -> None:
        self.name = name
        self.system_prompt = system_prompt
        self.mcp_servers = mcp_servers or {}
        self.allowed_tools = allowed_tools or []
        self.model = model
        self.max_turns = max_turns
        self.cwd = cwd or os.getcwd()
        self.verbose = verbose

    def _log(self, msg: str) -> None:
        if self.verbose:
            print(f"[{self.name}] {msg}")

    def _options(self) -> "ClaudeAgentOptions":
        opts: dict[str, Any] = {
            "system_prompt": self.system_prompt,
            "mcp_servers": self.mcp_servers,
            "allowed_tools": self.allowed_tools,
            # Auto-accept file writes so the agent can save deliverables
            # without an interactive prompt.
            "permission_mode": "acceptEdits",
            "max_turns": self.max_turns,
            "cwd": self.cwd,
        }
        if self.model:
            opts["model"] = self.model
        return ClaudeAgentOptions(**opts)

    async def run_async(self, goal: str) -> AgentResult:
        """Pursue ``goal`` autonomously and return the final answer."""
        self._log(f"goal: {goal}")
        thoughts: list[str] = []
        final = ""

        async for message in query(prompt=goal, options=self._options()):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock) and block.text.strip():
                        thoughts.append(block.text)
                        self._log(block.text.strip())
            elif isinstance(message, ResultMessage):
                final = getattr(message, "result", "") or final

        if not final and thoughts:
            final = thoughts[-1]
        self._log("done.")
        return AgentResult(answer=final.strip(), thoughts=thoughts)

    def run(self, goal: str) -> AgentResult:
        """Synchronous wrapper around :meth:`run_async`."""
        return asyncio.run(self.run_async(goal))
