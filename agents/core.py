"""Core autonomous-agent engine.

A small, dependency-light agent loop in the spirit of AutoGPT / BabyAGI but
built directly on the Anthropic Messages API with tool use:

    goal -> [ think -> call tool -> observe ] * N -> final answer

The loop is *autonomous*: once given a goal it decides on its own which tools
to call and when it is finished. It stops when the model emits a final answer
(no more tool calls) or when ``max_steps`` is reached.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Any, Callable, Optional

try:
    from anthropic import Anthropic
except ImportError as exc:  # pragma: no cover - friendly hint
    raise ImportError(
        "The 'anthropic' package is required. Run: pip install -r requirements.txt"
    ) from exc


DEFAULT_MODEL = os.environ.get("AGENT_MODEL", "claude-sonnet-4-6")
DEFAULT_MAX_STEPS = int(os.environ.get("AGENT_MAX_STEPS", "12"))


@dataclass
class Tool:
    """A capability the agent can invoke.

    ``handler`` receives the tool input dict and returns any JSON-serialisable
    result (or a plain string).
    """

    name: str
    description: str
    input_schema: dict[str, Any]
    handler: Callable[[dict[str, Any]], Any]

    def spec(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema,
        }


@dataclass
class AgentResult:
    """Outcome of an autonomous run."""

    answer: str
    steps: int
    transcript: list[dict[str, Any]] = field(default_factory=list)
    stopped_early: bool = False


class AutonomousAgent:
    """A goal-driven agent that plans and acts using tools until done."""

    def __init__(
        self,
        name: str,
        system_prompt: str,
        tools: Optional[list[Tool]] = None,
        model: str = DEFAULT_MODEL,
        max_steps: int = DEFAULT_MAX_STEPS,
        max_tokens: int = 2048,
        client: Optional[Anthropic] = None,
        verbose: bool = True,
    ) -> None:
        self.name = name
        self.system_prompt = system_prompt
        self.tools = {t.name: t for t in (tools or [])}
        self.model = model
        self.max_steps = max_steps
        self.max_tokens = max_tokens
        self.verbose = verbose
        self.client = client or Anthropic()

    # -- internals -----------------------------------------------------------

    def _log(self, msg: str) -> None:
        if self.verbose:
            print(f"[{self.name}] {msg}")

    def _run_tool(self, name: str, tool_input: dict[str, Any]) -> str:
        tool = self.tools.get(name)
        if tool is None:
            return f"ERROR: unknown tool '{name}'"
        try:
            result = tool.handler(tool_input)
        except Exception as exc:  # surface tool errors back to the model
            return f"ERROR while running '{name}': {exc}"
        if isinstance(result, str):
            return result
        return json.dumps(result, indent=2, default=str)

    # -- public API ----------------------------------------------------------

    def run(self, goal: str) -> AgentResult:
        """Pursue ``goal`` autonomously and return the final answer."""

        messages: list[dict[str, Any]] = [{"role": "user", "content": goal}]
        # Cache the (often large) system prompt across turns to cut cost/latency.
        system = [{"type": "text", "text": self.system_prompt,
                   "cache_control": {"type": "ephemeral"}}]
        tool_specs = [t.spec() for t in self.tools.values()]

        transcript: list[dict[str, Any]] = []
        self._log(f"goal: {goal}")

        for step in range(1, self.max_steps + 1):
            kwargs: dict[str, Any] = {
                "model": self.model,
                "max_tokens": self.max_tokens,
                "system": system,
                "messages": messages,
            }
            if tool_specs:
                kwargs["tools"] = tool_specs

            response = self.client.messages.create(**kwargs)
            messages.append({"role": "assistant", "content": response.content})

            text_parts = [b.text for b in response.content if b.type == "text"]
            tool_uses = [b for b in response.content if b.type == "tool_use"]

            for text in text_parts:
                if text.strip():
                    self._log(f"thought: {text.strip()}")
                    transcript.append({"step": step, "type": "thought", "text": text})

            if not tool_uses:
                answer = "\n".join(text_parts).strip()
                self._log(f"done in {step} step(s).")
                return AgentResult(answer=answer, steps=step, transcript=transcript)

            tool_results = []
            for tu in tool_uses:
                self._log(f"action: {tu.name}({json.dumps(tu.input)})")
                output = self._run_tool(tu.name, tu.input)
                transcript.append({
                    "step": step, "type": "action",
                    "tool": tu.name, "input": tu.input, "output": output,
                })
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tu.id,
                    "content": output,
                })
            messages.append({"role": "user", "content": tool_results})

        # Out of steps: ask for a best-effort final summary.
        self._log("max steps reached; requesting final summary.")
        messages.append({
            "role": "user",
            "content": "You have reached your step budget. Stop using tools and "
                       "give your best final answer now.",
        })
        final = self.client.messages.create(
            model=self.model, max_tokens=self.max_tokens,
            system=system, messages=messages,
        )
        answer = "".join(b.text for b in final.content if b.type == "text").strip()
        return AgentResult(answer=answer, steps=self.max_steps,
                           transcript=transcript, stopped_early=True)
