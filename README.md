# 00 — Kojiki Ontology (shared)

The shared foundation for the 20 line repos. Every line repo references this one
for the **canonical schemas, taxonomy, decision-rights, handoffs, and prompts** so
that any agent can reason across all lines with one model.

## What's here
- `ontology/` — the organization → line → function → role → decision → action →
  evidence → outcome → learning → rule chain (docx S2), plus function/role/decision/
  evidence/outcome/learning definitions.
- `schemas/` — canonical JSON Schemas: `learning-ledger.json` (S7),
  `decision-object.json` (S9), `orientation.json` (first-run protocol).
- `prompts/` — the Universal Function Architecture Prompt (S4) + the per-line
  specialized prompts (S6).
- `learning/` — `cases/`, `patterns/`, `rules/`, `exceptions/`, `rule-changelog/`
  (the learning ledger lands here, cross-line).
- `decision-rights/` — Own/Recommend/Consult/Execute/Approve/Escalate/Automate (S10).
- `handoffs/` — Cross-Functional Handoff Standard (S11) + `registry.json` for
  sibling-agent discovery.
- `evaluations/` — how to test that an agent follows the protocol + schemas.

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
Every agent, on first run, must: (1) be named + state its function, (2) state
industry, (3) state jurisdiction (country/region/regime), (4) state geography +
business model, (5) discover/register sibling agents. See `prompts/orientation.md`.

## Design principles (docx S19, summary)
Model decisions not documents · explicit ownership · explicit uncertainty ·
exceptions are learning · never silently rewrite rules (version them) · separate
activity from outcome metrics · capture dissent · explicit cross-functional deps ·
prefer evidence thresholds + state transitions · humans/software/agents share one
framework at different authority levels · provenance for every rule.
