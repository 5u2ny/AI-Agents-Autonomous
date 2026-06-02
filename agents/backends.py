"""Coding-agent backends.

Run the autonomous agents on **whatever coding agent you already subscribe to**.
Each backend shells out to a coding-agent CLI in its non-interactive / headless
mode, so authentication is whatever that tool is already logged into — your
Claude, ChatGPT, Gemini, Copilot, or Cursor subscription. No API keys here.

Supported out of the box (auto-detected on your PATH):

  * claude        Claude Code            (Anthropic Pro / Max / Team)
  * codex         OpenAI Codex CLI       (ChatGPT Plus / Pro)
  * gemini        Gemini CLI             (Google / Gemini subscription)
  * copilot       GitHub Copilot CLI     (GitHub Copilot subscription)
  * cursor-agent  Cursor CLI             (Cursor subscription)
  * opencode      opencode               (your configured provider)
  * aider         Aider                  (your configured provider)

Don't see yours? Set CODING_AGENT_CMD to any command template containing
``{prompt}`` (or the prompt is appended), e.g.:

    export CODING_AGENT_CMD='mytool run --yes {prompt}'

Headless flags differ between tool versions; override per-agent with
``CODING_AGENT_CMD`` if a default doesn't match your install.
"""

from __future__ import annotations

import os
import shlex
import subprocess
import time
from dataclasses import dataclass
from shutil import which
from typing import Callable, Optional


@dataclass
class Backend:
    """A coding-agent CLI we can drive headlessly."""

    name: str
    bin: str
    build_argv: Callable[[str], list[str]]
    login_hint: str = ""
    description: str = ""

    def available(self) -> bool:
        return which(self.bin) is not None

    def run(self, prompt: str, cwd: str, timeout: Optional[int] = None,
            echo: bool = True) -> str:
        """Run the agent on ``prompt`` and return its stdout."""
        argv = self.build_argv(prompt)
        proc = subprocess.Popen(
            argv, cwd=cwd, text=True, bufsize=1,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        )
        start = time.time()
        chunks: list[str] = []
        try:
            assert proc.stdout is not None
            for line in proc.stdout:
                chunks.append(line)
                if echo:
                    print(line, end="", flush=True)
                if timeout and time.time() - start > timeout:
                    proc.kill()
                    raise TimeoutError(
                        f"{self.name} exceeded timeout of {timeout}s")
            proc.wait()
        finally:
            if proc.poll() is None:
                proc.kill()
        out = "".join(chunks).strip()
        if proc.returncode not in (0, None):
            raise RuntimeError(
                f"'{self.name}' exited with code {proc.returncode}.\n"
                f"Output:\n{out or '(none)'}\n"
                f"Hint: is it installed and logged in? {self.login_hint}")
        return out


# --- the known coding agents -------------------------------------------------

_REGISTRY: list[Backend] = [
    Backend(
        name="claude", bin="claude",
        build_argv=lambda p: ["claude", "-p", p,
                              "--permission-mode", "acceptEdits"],
        login_hint="Install: npm i -g @anthropic-ai/claude-code; then `claude login`.",
        description="Claude Code (Anthropic Pro / Max / Team)",
    ),
    Backend(
        name="codex", bin="codex",
        build_argv=lambda p: ["codex", "exec", "--full-auto", p],
        login_hint="Install the OpenAI Codex CLI; then `codex login` (ChatGPT).",
        description="OpenAI Codex CLI (ChatGPT Plus / Pro)",
    ),
    Backend(
        name="gemini", bin="gemini",
        build_argv=lambda p: ["gemini", "-y", "-p", p],
        login_hint="Install the Gemini CLI; then `gemini` and sign in with Google.",
        description="Gemini CLI (Google / Gemini subscription)",
    ),
    Backend(
        name="copilot", bin="copilot",
        build_argv=lambda p: ["copilot", "-p", p, "--allow-all-tools"],
        login_hint="Install the GitHub Copilot CLI; then `copilot` and sign in.",
        description="GitHub Copilot CLI (Copilot subscription)",
    ),
    Backend(
        name="cursor-agent", bin="cursor-agent",
        build_argv=lambda p: ["cursor-agent", "-p", p, "--force"],
        login_hint="Install the Cursor CLI; then `cursor-agent login`.",
        description="Cursor CLI (Cursor subscription)",
    ),
    Backend(
        name="opencode", bin="opencode",
        build_argv=lambda p: ["opencode", "run", p],
        login_hint="Install opencode and configure a provider.",
        description="opencode (your configured provider)",
    ),
    Backend(
        name="aider", bin="aider",
        build_argv=lambda p: ["aider", "--message", p,
                              "--yes-always", "--no-auto-commits"],
        login_hint="Install aider and configure a provider/model.",
        description="Aider (your configured provider)",
    ),
]

_BY_NAME = {b.name: b for b in _REGISTRY}


def _custom_backend_from_env() -> Optional[Backend]:
    """A user-defined backend via CODING_AGENT_CMD='tool --flag {prompt}'."""
    template = os.environ.get("CODING_AGENT_CMD")
    if not template:
        return None
    parts = shlex.split(template)
    if not parts:
        return None

    def build(prompt: str, _parts=parts) -> list[str]:
        if any("{prompt}" in tok for tok in _parts):
            return [tok.replace("{prompt}", prompt) for tok in _parts]
        return [*_parts, prompt]  # append prompt if no placeholder

    return Backend(
        name="custom", bin=parts[0], build_argv=build,
        login_hint="Defined via CODING_AGENT_CMD.",
        description=f"Custom: {template}",
    )


def all_backends() -> list[Backend]:
    custom = _custom_backend_from_env()
    return ([custom] if custom else []) + _REGISTRY


def available_backends() -> list[Backend]:
    return [b for b in all_backends() if b.available()]


def get_backend(name: Optional[str] = None) -> Backend:
    """Resolve a backend by name, env, or auto-detection.

    Priority: explicit ``name`` -> ``$CODING_AGENT`` -> ``$CODING_AGENT_CMD``
    -> first installed CLI from the registry.
    """
    name = name or os.environ.get("CODING_AGENT")
    if name:
        if name == "custom" or os.environ.get("CODING_AGENT_CMD"):
            custom = _custom_backend_from_env()
            if custom and (name == "custom" or name == custom.bin):
                return custom
        backend = _BY_NAME.get(name)
        if backend is None:
            raise ValueError(
                f"Unknown coding agent '{name}'. "
                f"Known: {', '.join(_BY_NAME)} (or set CODING_AGENT_CMD).")
        return backend

    custom = _custom_backend_from_env()
    if custom and custom.available():
        return custom

    for backend in _REGISTRY:
        if backend.available():
            return backend

    raise RuntimeError(
        "No coding-agent CLI found on PATH. Install one of: "
        f"{', '.join(b.bin for b in _REGISTRY)} — or set CODING_AGENT_CMD. "
        "See the README for per-tool setup.")
