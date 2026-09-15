# Promote Kojiki Decision System

Copy-paste assets. All open source (MIT), local-first (Ollama), harness-agnostic.

---

## One-paragraph pitch (GitHub About / HN / Reddit)

**Kojiki Decision System** is an open-source, local-first framework that turns a normal LLM into a decision-centric organization. You install one organization — the Chief of Staff runs the shared Orientation Protocol on first run, figures out what needs to be done to accomplish the goal, then delegates research and execution to the 7 departments (Marketing, Legal, Finance, Engineering, Operations, People & Comms, Technology Platform). Every decision is captured as a versioned Decision Object + Learning Ledger entry, so the org gets smarter each time it decides. 7 consolidated department configs share one MIT ontology; runs fully offline on Ollama `qwen2.5:14b` (or any model you point at the repo); installs into Claude, or any agent, with no lock-in.

---

## Hacker News / Reddit (r/LocalLLaMA, r/aiagents) post

Title: *Show HN: An org of local LLM agents that record every decision as a versioned object*

Most multi-agent setups are chatbots wired together. Kojiki is different: you install one organization — the Chief of Staff runs the Orientation Protocol on first run, figures out what needs to be done to accomplish the goal, then delegates research and execution to the 7 departments (Finance, Marketing, Sales, Engineering, Operations, Legal, People & Comms, Technology Platform). Each department operates as a *decision system* — every call produces a Decision Object (owner, evidence threshold, options, risk, delegation rights) plus a Learning Ledger entry (assumption → action → expected → actual → variance → learning → rule update). The learning is versioned, never silently rewritten.

- 7 consolidated departments (Finance, Marketing, Sales, Engineering, Operations, Legal, People & Comms, Technology Platform) + an Ontology (shared schemas) + Chief of Staff coordinator.
- Local-first: runs on Ollama `qwen2.5:14b` (or any local model), no API keys, MIT.
- Specialists self-instantiate their own sub-function bots after research (e.g. Marketing → Brand, Growth).
- Agent-to-agent handoff via a shared registry; optional external memory backend.

We just ran the Marketing agent end-to-end on a local 14B model: it oriented, made a GTM decision for a Germany/GDPR launch, then closed the loop with a real learning ("German procurement needs certifications beyond GDPR"). Record validated against the schema. Repos + the evaluation run are linked.

---

## Demo script (copy-paste, ~2 min, fully local)

```bash
# 1. Clone and install
git clone <your-repo-url> && cd decision-systems
pip install -r requirements.txt

# 2. Run a specialist (e.g., marketing-brand)
python -m kojiki.core.runner marketing-brand dispatch.json

# 3. Or run all 7 specialists
python scripts/verify_all_runners.py
```

See the worked example: `kojiki/specialists/marketing-brand/evaluations/` (orientation transcript + open + closed-loop decision records, all schema-validated on `qwen2.5:14b`).

---

## Suggested GitHub Topics (add per repo)

`ai-agents` `multi-agent` `decision-making` `local-llm` `ollama` `agent-framework`
`knowledge-management` `organization` `prompt-engineering` `mit-license`

Ontology repo extra: `ontology` `schemas` `agent-protocol`

---

## Honest scope (put in README / landing)

> Kojiki is a proven *framework*: we have run a department agent end-to-end on a local 14B model and it produces valid, closed-loop decision records. It is harness-agnostic and MIT. It is not a hosted product — you bring the model (Ollama or any local LLM) and the host (Claude or any agent). Extensibility (the bot menu, the Chief of Staff recommendations) is real but best demonstrated by running it on your own org.

---

## Where to post

- GitHub: set the repo description + topics above on `decision-systems` and each specialist.
- Hacker News: Show HN (above).
- Reddit: r/LocalLLaMA, r/aiagents, r/selfhosted.