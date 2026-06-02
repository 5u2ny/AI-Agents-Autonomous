#!/usr/bin/env python3
"""CLI to run the autonomous agents on your coding-agent subscription.

These agents drive whatever coding-agent CLI you already have logged in —
Claude Code, OpenAI Codex, Gemini CLI, GitHub Copilot, Cursor, etc. No API key.

Examples:
    python run.py gtm "Acme - an AI notetaker for remote sales teams, $30/seat/mo"
    python run.py adopt "A 40-person regional law firm drowning in document review"

    python run.py --list                 # show detected coding agents
    python run.py gtm "..." --agent codex   # force a specific backend

The backend can also be set with the CODING_AGENT env var, or a fully custom
command with CODING_AGENT_CMD='mytool --yes {prompt}'.
"""

from __future__ import annotations

import argparse
import sys

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv is optional

from agents import AIAdoptionAgent, GTMAgent, all_backends, get_backend

DEMOS = {
    "gtm": "Acme - an AI meeting-notetaker for remote B2B sales teams. "
           "$30/seat/month. Competes with Gong and Otter. Pre-seed, no sales team yet.",
    "adopt": "A 40-person regional law firm. Partners spend huge amounts of time "
             "on contract and document review. No AI in use today; cautious about "
             "client confidentiality.",
}


def list_agents() -> int:
    print("Coding agents (✓ = found on your PATH):\n")
    for b in all_backends():
        mark = "✓" if b.available() else " "
        print(f"  [{mark}] {b.name:<13} {b.description}")
        if not b.available() and b.login_hint:
            print(f"        ↳ {b.login_hint}")
    print("\nSelect one with --agent NAME or CODING_AGENT=NAME. "
          "Default: first one found.")
    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("mode", nargs="?", choices=["gtm", "adopt"],
                        help="which agent to run")
    parser.add_argument("brief", nargs="?", help="product/business description")
    parser.add_argument("-a", "--agent", help="coding-agent backend to use")
    parser.add_argument("-l", "--list", action="store_true",
                        help="list detected coding agents and exit")
    args = parser.parse_args(argv[1:])

    if args.list:
        return list_agents()
    if not args.mode:
        parser.print_help()
        return 1

    backend = get_backend(args.agent)
    brief = args.brief or DEMOS[args.mode]

    Agent = GTMAgent if args.mode == "gtm" else AIAdoptionAgent
    agent = Agent(backend=backend)
    result = agent.build_plan(brief)

    print("\n" + "=" * 70)
    print(f"EXECUTIVE SUMMARY (via {result.backend}):\n")
    print(result.answer)
    print("=" * 70)
    print("Full plan saved under ./runs/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
