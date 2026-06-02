# AI-Agents-Autonomous

Two ready-to-run **autonomous AI agents**, built in the spirit of projects from
[e2b-dev/awesome-ai-agents](https://github.com/e2b-dev/awesome-ai-agents)
(AutoGPT, BabyAGI, etc.): goal-driven loops that plan, call tools, observe
results, and iterate until the job is done — no step-by-step human input.

| Agent | What it does |
|-------|--------------|
| 🚀 **GTM-Pilot** (`GTMAgent`) | Autonomous go-to-market strategist. Give it a product and it produces a launch-ready GTM plan: ICP & personas, positioning, market sizing, channel mix, funnel math, a 90-day roadmap, and KPIs. |
| 🤖 **AI-Onboard** (`AIAdoptionAgent`) | Autonomous advisor for businesses adopting AI **for the first time**. Scores candidate use cases, picks a low-risk pilot, covers build-vs-buy, data/skills readiness, governance & risk, budget/ROI, and a Crawl→Walk→Run rollout. |

Both run on the same lightweight engine and produce a polished Markdown
deliverable in `runs/`.

## How it works

```
goal ──▶ [ think ──▶ call tool ──▶ observe ] × N ──▶ final plan
```

- **`agents/core.py`** — `AutonomousAgent`, a Claude-powered plan→act→observe
  loop using the Anthropic Messages API with tool use and prompt caching.
- **`agents/tools.py`** — a shared toolbelt: `scratchpad` (working memory),
  `calculator` (sizing/funnel/ROI math), `today` (date anchoring for roadmaps),
  and `save_artifact` (writes the final deliverable to `runs/`).
- **`agents/gtm_agent.py`** / **`agents/ai_adoption_agent.py`** — the two
  agents, each just a specialized system prompt + the shared toolbelt.

The loop is genuinely autonomous: the model decides which tools to call and
when it is finished. It stops when no more tool calls are emitted, or when the
`max_steps` budget is hit (then it's asked for a best-effort summary).

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env        # then add your ANTHROPIC_API_KEY
```

## Run

```bash
# Go-to-market plan
python run.py gtm "Acme — an AI notetaker for remote B2B sales teams, $30/seat/mo"

# First-time AI adoption plan
python run.py adopt "A 40-person regional law firm drowning in contract review"
```

Run with no brief to use a built-in demo brief. Deliverables are written to
`runs/gtm_plan.md` and `runs/ai_adoption_plan.md`.

### Use from Python

```python
from agents import GTMAgent, AIAdoptionAgent

gtm = GTMAgent()
result = gtm.build_plan("Acme — AI notetaker for sales teams, $30/seat/mo")
print(result.answer)        # executive summary
print(result.steps)         # how many autonomous steps it took
# full plan saved to runs/gtm_plan.md

advisor = AIAdoptionAgent()
advisor.build_plan("A regional law firm exploring AI for document review")
```

## Configuration

Set in `.env` or the environment:

| Variable | Default | Purpose |
|----------|---------|---------|
| `ANTHROPIC_API_KEY` | — | Required. |
| `AGENT_MODEL` | `claude-sonnet-4-6` | Model the agents run on. |
| `AGENT_MAX_STEPS` | `12` | Default tool-use step budget. |
| `AGENT_ARTIFACT_DIR` | `runs` | Where deliverables are saved. |

## Extending

Add a new capability by defining a `Tool` (name, description, JSON input
schema, handler) in `agents/tools.py` and dropping it in the agent's toolbelt —
swap the offline handlers for real web search, CRM, or analytics integrations
to take these to production.
