# AI-Agents-Autonomous

Two ready-to-run **autonomous AI agents** — built in the spirit of the projects
in [e2b-dev/awesome-ai-agents](https://github.com/e2b-dev/awesome-ai-agents)
(AutoGPT, BabyAGI, etc.): goal-driven loops that plan, call tools, observe
results, and iterate until the job is done.

> **No API key. Bring your own coding agent.** These agents drive whatever
> coding-agent CLI you already subscribe to — **Claude Code, OpenAI Codex,
> Gemini CLI, GitHub Copilot, Cursor**, and more — using *its* login. Whatever
> you're already paying for runs the show.

| Agent | What it does |
|-------|--------------|
| 🚀 **GTM-Pilot** (`GTMAgent`) | Autonomous go-to-market strategist. Give it a product and it researches the market, then produces a launch-ready GTM plan: ICP & personas, positioning, market sizing, channel mix, funnel math, a 90-day roadmap, and KPIs. |
| 🤖 **AI-Onboard** (`AIAdoptionAgent`) | Autonomous advisor for businesses adopting AI **for the first time**. Scores candidate use cases, picks a low-risk pilot, covers build-vs-buy, data/skills readiness, governance & risk, budget/ROI, and a Crawl→Walk→Run rollout. |

Each writes a polished Markdown deliverable into `runs/`.

## Supported coding agents

Auto-detected on your `PATH`:

| Backend | Tool | Subscription |
|---------|------|--------------|
| `claude` | Claude Code | Anthropic Pro / Max / Team |
| `codex` | OpenAI Codex CLI | ChatGPT Plus / Pro |
| `gemini` | Gemini CLI | Google / Gemini |
| `copilot` | GitHub Copilot CLI | GitHub Copilot |
| `cursor-agent` | Cursor CLI | Cursor |
| `opencode` | opencode | your configured provider |
| `aider` | Aider | your configured provider |

Using something else? Point it at any headless command:

```bash
export CODING_AGENT_CMD='mytool run --yes {prompt}'   # {prompt} = the task text
```

## How it works

```
goal ──▶ [ your coding agent: think ──▶ call tool ──▶ observe ] × N ──▶ saved plan
```

An agent in this repo is just a **name + a system-prompt persona**
(`agents/gtm_agent.py`, `agents/ai_adoption_agent.py`). The autonomous loop,
tool use, web search, and file writing are delegated to your coding-agent CLI:

- **`agents/backends.py`** — the provider layer. Each backend knows how to run
  one coding-agent CLI in non-interactive / headless mode and auto-detects
  whether it's installed. Auth is whatever that tool is logged into.
- **`agents/core.py`** — `AutonomousAgent`, which folds the persona into the
  task prompt and hands it to the selected backend.

Because the work runs inside a real coding agent, the plans get that agent's
native abilities — live web research and writing files to `runs/` — with **zero
extra API keys**.

## Setup

1. **Have a coding agent installed and logged in.** Pick whichever you already
   pay for, e.g.:
   ```bash
   # Claude Code
   npm install -g @anthropic-ai/claude-code && claude login
   # …or OpenAI Codex CLI, Gemini CLI, GitHub Copilot CLI, Cursor CLI, etc.
   ```
2. **Install this project's (tiny) deps:**
   ```bash
   pip install -r requirements.txt      # Python 3.10+ ; only python-dotenv
   ```

Check what was detected:

```bash
python run.py --list
```

## Run

```bash
# Go-to-market plan (uses the first coding agent it finds)
python run.py gtm "Acme — an AI notetaker for remote B2B sales teams, $30/seat/mo"

# First-time AI adoption plan, forcing a specific backend
python run.py adopt "A 40-person law firm drowning in contract review" --agent codex
```

Run with no brief to use a built-in demo. Deliverables land in
`runs/gtm_plan.md` and `runs/ai_adoption_plan.md`.

### Use from Python

```python
from agents import GTMAgent, AIAdoptionAgent, get_backend

# Auto-detect, or pick one: get_backend("gemini")
gtm = GTMAgent(backend=get_backend())
result = gtm.build_plan("Acme — AI notetaker for sales teams, $30/seat/mo")
print(result.backend)       # which coding agent ran it
print(result.answer)        # executive summary; full plan saved to runs/

AIAdoptionAgent().build_plan("A regional law firm exploring AI for doc review")
```

## Configuration

All optional — set in `.env` or the environment:

| Variable | Purpose |
|----------|---------|
| `CODING_AGENT` | Force a backend: `claude`, `codex`, `gemini`, `copilot`, `cursor-agent`, `opencode`, `aider`. |
| `CODING_AGENT_CMD` | Custom headless command; include `{prompt}` (or it's appended). |
| `AGENT_TIMEOUT` | Max seconds per run (default `1800`). |

> Headless flags vary by tool version. If a default doesn't match your install,
> override that agent with `CODING_AGENT_CMD`.

## Extending

- **Add a coding agent:** append a `Backend(...)` to the registry in
  `agents/backends.py` (executable name + how to build its headless argv).
- **Add an agent persona:** subclass `AutonomousAgent` with a new system
  prompt, like `GTMAgent` / `AIAdoptionAgent`.
