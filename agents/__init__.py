"""Autonomous AI agents that run on ANY coding-agent subscription (no API key).

Two ready-to-run autonomous agents that drive whatever coding agent you already
use — Claude Code, OpenAI Codex, Gemini CLI, GitHub Copilot, Cursor, and more:

  * GTMAgent          - go-to-market strategy autopilot
  * AIAdoptionAgent   - guides a business adopting AI for the first time
"""

from .core import AutonomousAgent, AgentResult
from .backends import (
    Backend,
    get_backend,
    available_backends,
    all_backends,
)
from .gtm_agent import GTMAgent
from .ai_adoption_agent import AIAdoptionAgent

__all__ = [
    "AutonomousAgent",
    "AgentResult",
    "Backend",
    "get_backend",
    "available_backends",
    "all_backends",
    "GTMAgent",
    "AIAdoptionAgent",
]
