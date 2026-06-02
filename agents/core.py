"""Core autonomous-agent engine — runs on ANY coding agent you subscribe to.

An agent here is just a name + a system prompt. The heavy lifting (the
think -> act -> observe loop, tool use, file writing) is delegated to whichever
coding-agent CLI you already have — Claude Code, OpenAI Codex, Gemini CLI,
GitHub Copilot, Cursor, etc. (see ``backends.py``). Authentication is whatever
that tool is logged into, so there's **no API key to manage**.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

from .backends import Backend, get_backend

DEFAULT_TIMEOUT = int(os.environ.get("AGENT_TIMEOUT", "1800"))  # seconds


@dataclass
class AgentResult:
    """Outcome of an autonomous run."""

    answer: str
    backend: str


class AutonomousAgent:
    """A goal-driven agent that runs on the user's coding-agent subscription."""

    def __init__(
        self,
        name: str,
        system_prompt: str,
        backend: Optional[Backend] = None,
        cwd: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
        verbose: bool = True,
    ) -> None:
        self.name = name
        self.system_prompt = system_prompt
        self.backend = backend or get_backend()
        self.cwd = cwd or os.getcwd()
        self.timeout = timeout
        self.verbose = verbose

    def run(self, goal: str) -> AgentResult:
        """Pursue ``goal`` autonomously via the selected coding agent."""
        if self.verbose:
            print(f"[{self.name}] backend: {self.backend.name} "
                  f"({self.backend.description})")
            print(f"[{self.name}] goal: {goal}\n")

        # Every coding agent takes a single prompt, so fold the persona/system
        # instructions into it. This keeps the engine truly cross-agent.
        prompt = (
            f"{self.system_prompt}\n\n"
            "----------------------------------------\n"
            f"TASK:\n{goal}\n"
        )
        out = self.backend.run(prompt, cwd=self.cwd, timeout=self.timeout,
                               echo=self.verbose)
        return AgentResult(answer=out, backend=self.backend.name)
