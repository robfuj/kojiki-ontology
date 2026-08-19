# 00 — Hermes Ontology (shared)

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
- `01 — Executive / Strategy` → [`01-executive-strategy`](https://github.com/hermes-ios/01-executive-strategy)
- `02 — Finance` → [`02-finance`](https://github.com/hermes-ios/02-finance)
- `03 — Marketing` → [`03-marketing`](https://github.com/hermes-ios/03-marketing)
- `04 — Sales` → [`04-sales`](https://github.com/hermes-ios/04-sales)
- `05 — Business Development` → [`05-business-development`](https://github.com/hermes-ios/05-business-development)
- `06 — Customer Success` → [`06-customer-success`](https://github.com/hermes-ios/06-customer-success)
- `07 — Product` → [`07-product`](https://github.com/hermes-ios/07-product)
- `08 — Engineering / Technology` → [`08-engineering`](https://github.com/hermes-ios/08-engineering)
- `09 — Operations` → [`09-operations`](https://github.com/hermes-ios/09-operations)
- `10 — Supply Chain / Procurement` → [`10-supply-chain-procurement`](https://github.com/hermes-ios/10-supply-chain-procurement)
- `11 — Data / Analytics` → [`11-data-analytics`](https://github.com/hermes-ios/11-data-analytics)
- `12 — AI / Intelligence` → [`12-ai-intelligence`](https://github.com/hermes-ios/12-ai-intelligence)
- `13 — IT` → [`13-it`](https://github.com/hermes-ios/13-it)
- `14 — Security` → [`14-security`](https://github.com/hermes-ios/14-security)
- `15 — Legal` → [`15-legal`](https://github.com/hermes-ios/15-legal)
- `16 — Risk / Compliance` → [`16-risk-compliance`](https://github.com/hermes-ios/16-risk-compliance)
- `17 — People / HR` → [`17-people-hr`](https://github.com/hermes-ios/17-people-hr)
- `18 — Corporate Development` → [`18-corporate-development`](https://github.com/hermes-ios/18-corporate-development)
- `19 — Communications / Public Affairs` → [`19-communications-public-affairs`](https://github.com/hermes-ios/19-communications-public-affairs)
- `20 — Executive Office / Chief of Staff` → [`20-executive-office`](https://github.com/hermes-ios/20-executive-office)

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
