# Kojiki Ontology — the shared brain for the Kojiki Decision System

Kojiki is a local-first, open-source framework that turns a normal LLM into a
decision-centric organization. Every department agent reasons through one shared
**SYNAPSIS transformation chain** — and the chain is the structure of this repo.

```
SOURCE → RECORD → EVIDENCE → INTERPRETATION → STRATEGY → INTERACTION → OUTPUT → OUTCOME → LEARNING
 │
 ORGANIZATIONAL MEMORY
```

Each stage is a **bounded transformation** with one authority and an explicit "what it
must NOT silently become" (evidence ≠ interpretation ≠ belief ≠ doctrine). A **Brain**
orchestrates; an independent **Adversarial Audit** challenges. The full spec lives in
[`synapsis/`](synapsis/SYNAPSIS.md). This README is organized around the chain.

---

## 1. SOURCE → RECORD — what happened
The origin of every decision. `RECORD` captures what happened, when, involving whom,
and where it can be verified. It is never interpretation.
- Backed by: `ontology/organization.md` (ORG → LINE → FUNCTION → ROLE chain).
- Every department runs RECORD locally; cross-department SOURCE arrives peer-to-peer.

## 2. EVIDENCE — what the source actually establishes
`EVIDENCE` extracts what the source *proves*, separate from what anyone infers.
- Schema: `schemas/evidence` (mirrored in every department's `schema/`).
- Invariant: **evidence is not interpretation.**

## 3. INTERPRETATION — what evidence means for one question
`INTERPRETATION` answers a single defined analytical question. It must not become
strategy. Interpretations are the natural **cross-department handoff** unit
(e.g. Marketing's interpretation feeds Sales' strategy).
- See [`synapsis/synapse-xdept.md`](synapsis/synapsis-xdept.md) for the optional,
 fallback-safe handoff protocol.

## 4. STRATEGY — the binding constraint and next commitment
`STRATEGY` picks the objective to pursue. It consumes INTERPRETATION; it does not
choose the interaction.
- Decision rights (Own / Approve / Consult / Execute / Escalate / Automate) live in
 `decision-rights/`.

## 5. INTERACTION — how to pursue the objective with a stakeholder
`INTERACTION` designs the approach to a specific stakeholder. It may not redefine the
objective.

## 6. OUTPUT — render the approved decision as an artifact
`OUTPUT` produces the message, plan, or artifact. It does not reconstruct truth.

## 7. OUTCOME — what actually happened
`OUTCOME` records reality vs expectation. This is the input to learning.

## 8. LEARNING — extract the pattern (Organizational Memory)
`LEARNING` extracts a pattern under uncertainty. It may *propose* a rule update but
never silently rewrite doctrine. Landed in `learning/` (cases / patterns / rules /
exceptions / rule-changelog) — cross-line organizational memory.
- Schema: `schemas/learning-ledger.json` and `schemas/decision-object.json`.
- Invariant: **learning is not permission to rewrite doctrine.**

---

## Brain & Adversarial Audit (the coordination layer)
- **Brain** routes, sequences, and adjudicates — but never originates the specialist
 analysis it judges. Executive Strategy (`01-executive-strategy`) is the org-level meta-Brain.
- **Adversarial Audit** challenges a claim graph against a standard; it cannot replace
 the specialist's conclusion. Invariant: **audit is not authority; evaluation is not origination.**

## Cross-department handoff (standalone guarantee)
Every transformation runs locally. Sibling departments are **optional accelerators**:
when present, consume their typed output (`sibling-verified`); when absent, synthesize
locally (`self-generated`). No other package download is required. Proven at runtime:
`evaluations/run-xdept-001/`.

## The 20 lines (each its own repo, each runs the chain)
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

## Orientation Protocol (first run)
Every agent must: (1) name + function, (2) industry, (3) jurisdiction (country/region/
regime), (4) geography + business model, (5) register sibling agents in
`handoffs/registry.json`. See `prompts/orientation.md`.

## Design principles
Model decisions not documents · explicit ownership · explicit uncertainty · exceptions
are learning · never silently rewrite rules (version them) · separate activity from
outcome · capture dissent · explicit cross-functional deps · prefer evidence thresholds
+ state transitions · provenance for every rule.

## Memory backend (optional)
For durable, observable memory, point a department agent at **[OpenViking](https://github.com/volcengine/OpenViking)**
via the [`synapsis/openviking-plugin`](synapsis/openviking-plugin/README.md) (Agent Plugins 1.0).
External project (AGPL-3.0); not bundled.

## Quick start
```bash
bash install-all.sh # whole package: ontology + 20 depts + 2 meta agents
# or one department (clones the ontology sibling if missing):
bash install.sh
```
After install, the agent runs the Orientation Protocol, then runs its work through the
SYNAPSIS chain and validates with `synapsis/validate.py`.

## Runtime (any LLM)
This repo is provider-agnostic. Point any LLM (Claude, GPT, a local model, or an
agent harness) at `AGENT.md` as the entry point and follow the Kojiki Orientation
Protocol. No specific runtime or vendor is required.

## License
MIT — see [LICENSE](LICENSE).
