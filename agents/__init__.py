"""Autonomous AI agents that run on your Claude subscription (no API key).

Two ready-to-run autonomous agents built on the Claude Agent SDK:

  * GTMAgent          - go-to-market strategy autopilot
  * AIAdoptionAgent   - guides a business adopting AI for the first time
"""

from .core import SubscriptionAgent, AgentResult
from .gtm_agent import GTMAgent
from .ai_adoption_agent import AIAdoptionAgent

__all__ = [
    "SubscriptionAgent",
    "AgentResult",
    "GTMAgent",
    "AIAdoptionAgent",
]
