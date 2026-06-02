"""Autonomous AI agents.

Two ready-to-run autonomous agents built on a shared Claude-powered
plan -> act -> observe loop:

  * GTMAgent          - go-to-market strategy autopilot
  * AIAdoptionAgent   - guides a business adopting AI for the first time
"""

from .core import AutonomousAgent, Tool, AgentResult
from .gtm_agent import GTMAgent
from .ai_adoption_agent import AIAdoptionAgent

__all__ = [
    "AutonomousAgent",
    "Tool",
    "AgentResult",
    "GTMAgent",
    "AIAdoptionAgent",
]
