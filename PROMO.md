# Promote Kojiki Decision System

Copy-paste assets. All open source (MIT), local-first (Ollama), harness-agnostic.

---

## One-paragraph pitch (GitHub About / HN / Reddit)

**Kojiki Decision System** is an open-source, local-first framework that turns a normal LLM into a decision-centric organization. Instead of one chatbot, you install departments (Marketing, Legal, Security, …) that each run a shared Orientation Protocol on first run — name yourself, state your industry, jurisdiction, and siblings — then research their field and spin up the specialist bots they actually need. Every decision is captured as a versioned Decision Object + Learning Ledger entry, so the org gets smarter each time it decides. 20+ department repos share one MIT ontology; runs fully offline on Ollama `qwen2.5:14b`; installs into Hermes, Claude, or any agent with no lock-in.

---

## Hacker News / Reddit (r/LocalLLaMA, r/aiagents) post

Title: *Show HN: An org of local LLM agents that record every decision as a versioned object*

Most multi-agent setups are chatbots wired together. Kojiki is different: each department is a repo that, on first run, orients itself (what's my name / industry / jurisdiction / who are my sibling agents) and then operates as a *decision system* — every call produces a Decision Object (owner, evidence threshold, options, risk, delegation rights) plus a Learning Ledger entry (assumption → action → expected → actual → variance → learning → rule update). The learning is versioned, never silently rewritten.

- 20+ departments (Sales, Legal, Security, Finance, Product, …) + an Ontology (shared schemas) + an Org Builder + an Installer.
- Local-first: runs on Ollama `qwen2.5:14b`, no API keys, MIT.
- Departments self-instantiate their own sub-function bots after research (e.g. Marketing → SEO, Performance, Market Research).
- Agent-to-agent handoff via a shared registry; optional OpenViking memory backend.

We just ran the Marketing agent end-to-end on a local 14B model: it oriented, made a GTM decision for a Germany/GDPR launch, then closed the loop with a real learning ("German procurement needs certifications beyond GDPR"). Record validated against the schema. Repos + the evaluation run are linked.

---

## Demo script (copy-paste, ~2 min, fully local)

```bash
# 1. Install the whole org (ontology + 20 departments + 2 meta agents)
git clone https://github.com/robfuj/kojiki-ontology && cd kojiki-ontology
bash install-all.sh

# 2. Install the Marketing department as a Hermes bot (local-first, Ollama qwen2.5:14b)
hermes profile install https://github.com/robfuj/kojiki-marketing-department

# 3. Open the bot's chat — it runs the Kojiki Orientation Protocol:
#    Q1 name+function · Q2 industry · Q3 jurisdiction · Q4 geography/model · Q5 sibling register
#    Then ask it a real decision, e.g. "Plan our Germany/GDPR GTM launch."

# 4. It produces a Decision Object + Learning Ledger JSON (validated by tools/validate.py),
#    and after the outcome, closes the loop with extracted learning.
```

See the worked example: `03-marketing/evaluations/run-001/` (orientation transcript + open + closed-loop decision records, all schema-validated on `qwen2.5:14b`).

---

## Suggested GitHub Topics (add per repo)

`ai-agents` `multi-agent` `decision-making` `local-llm` `ollama` `agent-framework`
`knowledge-management` `organization` `prompt-engineering` `mit-license` `hermes`

Ontology repo extra: `ontology` `schemas` `agent-protocol` `openviking`

---

## Honest scope (put in README / landing)

> Kojiki is a proven *framework*: we have run a department agent end-to-end on a local 14B model and it produces valid, closed-loop decision records. It is harness-agnostic and MIT. It is not a hosted product — you bring the model (Ollama) and the host (Hermes/Claude/any LLM). Extensibility (the bot menu, the Org Builder recommendations) is real but best demonstrated by running it on your own org.

---

## Where to post
- GitHub: set the repo description + topics above on `kojiki-ontology` and each department.
- Hacker News: Show HN (above).
- Reddit: r/LocalLLaMA, r/aiagents, r/selfhosted.
- Hermes Discord (#plugins-skills-and-skins) if you want the Nous community to try the Bot Mode install.
