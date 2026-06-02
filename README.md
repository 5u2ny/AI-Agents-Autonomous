# AI-Agents-Autonomous

Two ready-to-run **autonomous AI agents** — built in the spirit of the projects
in [e2b-dev/awesome-ai-agents](https://github.com/e2b-dev/awesome-ai-agents)
(AutoGPT, BabyAGI, etc.): goal-driven loops that plan, call tools, observe
results, and iterate until the job is done.

> **No API key.** They run on your existing **Claude subscription** (Pro / Max /
> Team) through the [Claude Agent SDK](https://code.claude.com/docs/en/agent-sdk/overview).
> Log in once with `claude login` and you're done — no `ANTHROPIC_API_KEY`, no
> per-token billing.

| Agent | What it does |
|-------|--------------|
| 🚀 **GTM-Pilot** (`GTMAgent`) | Autonomous go-to-market strategist. Give it a product and it researches the market, then produces a launch-ready GTM plan: ICP & personas, positioning, market sizing, channel mix, funnel math, a 90-day roadmap, and KPIs. |
| 🤖 **AI-Onboard** (`AIAdoptionAgent`) | Autonomous advisor for businesses adopting AI **for the first time**. Scores candidate use cases, picks a low-risk pilot, covers build-vs-buy, data/skills readiness, governance & risk, budget/ROI, and a Crawl→Walk→Run rollout. |

Each writes a polished Markdown deliverable to `runs/`.

## How it works

```
goal ──▶ [ think ──▶ call tool ──▶ observe ] × N ──▶ saved plan + summary
```

The **Claude Agent SDK** owns the autonomous loop and the auth. Each agent is
just a system prompt + a toolbelt:

- **Built-in tools** — `WebSearch` / `WebFetch` for live market research and
  `Write` to save the deliverable.
- **Custom in-process tools** (`agents/tools.py`) — `calculator` (sizing /
  funnel / ROI math) and `scratchpad` (working memory), exposed via an
  in-process MCP server. No extra services.
- **`agents/core.py`** — `SubscriptionAgent`, a thin wrapper over the SDK's
  `query()` that wires the prompt, tools, and options together.

## Setup (one time)

```bash
# 1. Install the Claude Code CLI and log in with your subscription
npm install -g @anthropic-ai/claude-code
claude login            # choose your Claude Pro / Max / Team account

# 2. Install the Python deps
pip install -r requirements.txt     # needs Python 3.10+
```

That's it — no API key to manage.

## Run

```bash
# Go-to-market plan
python run.py gtm "Acme — an AI notetaker for remote B2B sales teams, $30/seat/mo"

# First-time AI adoption plan
python run.py adopt "A 40-person regional law firm drowning in contract review"
```

Run with no brief to use a built-in demo. Deliverables land in
`runs/gtm_plan.md` and `runs/ai_adoption_plan.md`.

### Use from Python

```python
from agents import GTMAgent, AIAdoptionAgent

gtm = GTMAgent()
result = gtm.build_plan("Acme — AI notetaker for sales teams, $30/seat/mo")
print(result.answer)        # executive summary; full plan saved to runs/

advisor = AIAdoptionAgent()
advisor.build_plan("A regional law firm exploring AI for document review")
```

## Configuration

All optional — set in `.env` or the environment:

| Variable | Default | Purpose |
|----------|---------|---------|
| `AGENT_MODEL` | subscription default | Pin a specific model, e.g. `claude-sonnet-4-6`. |
| `AGENT_MAX_TURNS` | `30` | Max autonomous turns before wrapping up. |

## Extending

Add a capability by writing a `@tool`-decorated function in `agents/tools.py`,
add it to `build_toolkit()` and to the agent's `allowed_tools`. You can also
hand the agents any of the SDK's built-in tools (`Read`, `Bash`, `Glob`,
`Grep`, …) or connect external [MCP servers](https://code.claude.com/docs/en/agent-sdk/mcp)
(CRM, analytics, databases) to take these to production.

---

> Note: per Anthropic's terms, the Agent SDK on a subscription plan is for
> **your own** use. To distribute an agent to your end users, use API-key
> authentication instead.
