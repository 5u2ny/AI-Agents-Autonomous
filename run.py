#!/usr/bin/env python3
"""CLI to run the autonomous agents.

Examples:
    python run.py gtm "Acme - an AI notetaker for remote sales teams, $30/seat/mo"
    python run.py adopt "A 40-person regional law firm drowning in document review"

If no brief is passed, a built-in demo brief is used.
"""

from __future__ import annotations

import sys

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv is optional; env vars may be set another way

from agents import AIAdoptionAgent, GTMAgent

DEMOS = {
    "gtm": "Acme - an AI meeting-notetaker for remote B2B sales teams. "
           "$30/seat/month. Competes with Gong and Otter. Pre-seed, no sales team yet.",
    "adopt": "A 40-person regional law firm. Partners spend huge amounts of time "
             "on contract and document review. No AI in use today; cautious about "
             "client confidentiality.",
}

USAGE = "Usage: python run.py {gtm|adopt} [\"brief describing the product/business\"]"


def main(argv: list[str]) -> int:
    if len(argv) < 2 or argv[1] not in ("gtm", "adopt"):
        print(USAGE)
        return 1

    mode = argv[1]
    brief = argv[2] if len(argv) > 2 else DEMOS[mode]

    if mode == "gtm":
        agent = GTMAgent()
        result = agent.build_plan(brief)
    else:
        agent = AIAdoptionAgent()
        result = agent.build_plan(brief)

    print("\n" + "=" * 70)
    print(f"FINAL ANSWER ({result.steps} steps"
          f"{', stopped early' if result.stopped_early else ''}):\n")
    print(result.answer)
    print("=" * 70)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
