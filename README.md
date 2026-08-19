# Kojiki Ontology

**Kojiki Ontology** is the shared brain for the Kojiki Decision System — a family of 20+ AI decision agents. It stores the canonical schemas, taxonomy, decision-rights, and agent-handoff standards as one coherent model, so every department agent reasons across the org with the same definitions instead of inventing its own.

An agent doesn't query a black-box prompt — it loads the ontology: the decision object, the learning ledger, the orientation protocol, and the handoff standard. Every decision is captured as a Decision Object + Learning Ledger entry, with provenance for every rule. The result is an organization that becomes more intelligent each time it decides.

Full introduction: [How it fits together](#how-the-pieces-fit-together).

## Why Kojiki Ontology

- **One model for every line.** Every department agent (Sales, Legal, Product, …) references these canonical schemas, so they speak one language and can hand off to each other deterministically.
- **Decisions, not documents.** The unit of memory is a *decision* — its evidence, outcome, and the learning extracted — not a file you hope an agent reads.
- **Explicit ownership and uncertainty.** Decision rights (Own / Approve / Consult / Execute / Escalate) and evidence thresholds are first-class, so an agent knows what it may decide and what it must route.
- **Self-improving.** Every outcome feeds the Learning Ledger; rules are versioned, never silently rewritten. Exceptions become organizational knowledge.
- **Observable by design.** Each agent runs the Kojiki Orientation Protocol on first activation, then records its Decision Objects + Ledger entries where you can read them.
- **Harness-agnostic.** Plain markdown + JSON. Installs into Hermes (Bot Mode), Claude, or any LLM with no vendor lock-in.

## How the pieces fit together

```
kojiki-ontology/
├── schemas/                 # Canonical JSON Schemas (the contract every agent shares)
│   ├── decision-object.json   # docx S9 — one decision: owner, evidence, risk, delegation
│   ├── learning-ledger.json   # docx S7 — case → decision → assumption → action → learning → rule
│   └── orientation.json       # first-run protocol every agent executes
├── ontology/                # The definition chain (docx S2)
│   ├── organization.md        # ORG → LINE → FUNCTION → ROLE → DECISION → ACTION →
│   ├── functions.md           #   EVIDENCE → OUTCOME → LEARNING → RULE
│   ├── learning-taxonomy.md    # docx S8 — 10-type learning taxonomy
│   └── kpi-architecture.md     # docx S12 — activity / quality / outcome KPI layers
├── prompts/                 # Reusable reasoning prompts
│   ├── orientation.md          # Kojiki Orientation Protocol (Q1–Q5)
│   ├── universal-function-architecture.md   # docx S4
│   └── line-prompts.md         # docx S6 — specialized prompt per line
├── decision-rights/         # Own / Approve / Consult / Execute / Escalate / Automate (S10)
├── handoffs/                # Cross-Functional Handoff Standard (S11)
│   └── registry.json          # sibling-agent discovery (group_id)
├── learning/                # the ledger lands here, cross-line
│   ├── cases/  patterns/  rules/  exceptions/  rule-changelog/
└── evaluations/             # how to test an agent follows the protocol + schemas
```

Every department repo (`kojiki-<line>-department`) mirrors `schemas/` so it runs offline, but the **source of truth** is here. When you install a department, the ontology travels with it (`install.sh` clones this repo if missing).

## The 20 lines (each its own repo)

- `01 — Executive / Strategy` → [`01-executive-strategy`](https://github.com/robfuj/kojiki-executive-strategy)
- `02 — Finance` → [`02-finance`](https://github.com/robfuj/kojiki-finance-department)
- `03 — Marketing` → [`03-marketing`](https://github.com/robfuj/kojiki-marketing-department)
- `04 — Sales` → [`04-sales`](https://github.com/robfuj/kojiki-sales-department)
- `05 — Business Development` → [`05-business-development`](https://github.com/robfuj/kojiki-business-development)
- `06 — Customer Success` → [`06-customer-success`](https://github.com/robfuj/kojiki-customer-success)
- `07 — Product` → [`07-product`](https://github.com/robfuj/kojiki-product-department)
- `08 — Engineering / Technology` → [`08-engineering`](https://github.com/robfuj/kojiki-engineering-department)
- `09 — Operations` → [`09-operations`](https://github.com/robfuj/kojiki-operations-department)
- `10 — Supply Chain / Procurement` → [`10-supply-chain-procurement`](https://github.com/robfuj/kojiki-supply-chain-procurement-department)
- `11 — Data / Analytics` → [`11-data-analytics`](https://github.com/robfuj/kojiki-data-analytics)
- `12 — AI / Intelligence` → [`12-ai-intelligence`](https://github.com/robfuj/kojiki-ai-intelligence-department)
- `13 — IT` → [`13-it`](https://github.com/robfuj/kojiki-IT-department)
- `14 — Security` → [`14-security`](https://github.com/robfuj/kojiki-security-department)
- `15 — Legal` → [`15-legal`](https://github.com/robfuj/kojiki-legal-department)
- `16 — Risk / Compliance` → [`16-risk-compliance`](https://github.com/robfuj/kojiki-risk-compliance-department)
- `17 — People / HR` → [`17-people-hr`](https://github.com/robfuj/kojiki-hr-department)
- `18 — Corporate Development` → [`18-corporate-development`](https://github.com/robfuj/kojiki-corporate-development-department)
- `19 — Communications / Public Affairs` → [`19-communications-public-affairs`](https://github.com/robfuj/kojiki-communications-public-affairs-department)
- `20 — Executive Office / Chief of Staff` → [`20-executive-office`](https://github.com/robfuj/kojiki-executive-office-department)

## Orientation Protocol

Every agent, on first run, must: (1) be named + state its function, (2) state industry, (3) state jurisdiction (country/region/regime), (4) state geography + business model, (5) discover/register sibling agents. See `prompts/orientation.md`.

## Design principles (docx S19, summary)

Model decisions not documents · explicit ownership · explicit uncertainty · exceptions are learning · never silently rewrite rules (version them) · separate activity from outcome metrics · capture dissent · explicit cross-functional deps · prefer evidence thresholds + state transitions · humans/software/agents share one framework at different authority levels · provenance for every rule.

## Memory backend (optional)

For long-term, observable agent memory, Kojiki agents can use **[OpenViking](https://github.com/volcengine/OpenViking)** — an open-source context database that stores memories, resources, and skills under a `viking://` virtual filesystem with tiered (L0/L1/L2) on-demand loading and a watchable retrieval trajectory. This repo ships an **[OpenViking Agent Plugin](openviking-plugin/README.md)** (Agent Plugins 1.0): point a department agent's host at `openviking-plugin/` and it gains `find` / `search` / `read` / `remember` / `write` over its Decision Objects + Ledger entries. OpenViking is an external project (AGPL-3.0); it is not bundled — the plugin fetches OpenViking's stdio proxy at install time. Wire it in at the host agent's config.

## Quick start

Install the whole package (ontology + 20 departments + the two meta agents) in one command:

```bash
bash install-all.sh            # -> ./kojiki-decision-system/ with everything
```

Or install one department and let it pull the ontology:

```bash
git clone https://github.com/robfuj/kojiki-marketing-department.git
cd kojiki-marketing-department
bash install.sh                # clones kojiki-ontology sibling if absent, then this dept
```

Install as a Hermes Bot-Mode profile (local-first, Ollama `qwen2.5:14b`):

```bash
hermes profile install https://github.com/robfuj/kojiki-ontology
hermes profile install https://github.com/robfuj/kojiki-marketing-department
```

After install, open the bot's chat — it runs the Kojiki Orientation Protocol, then installs its own sub-function bots via `bots/install_bots.py <slugs>`.

## License

MIT — see [LICENSE](LICENSE).
