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

## The 18 lines (each its own repo, each runs the chain)
- `01 — Executive / Strategy` → [`01-executive-strategy`](../01-executive-strategy)
- `02 — Finance` → [`02-finance`](../02-finance)
- `03 — Marketing` → [`03-marketing`](../03-marketing)
- `04 — Sales` → [`04-sales`](../04-sales)
- `05 — Business Development` → [`05-business-development`](../05-business-development)
- `06 — Customer Success` → [`06-customer-success`](../06-customer-success)
- `07 — Product` → [`07-product`](../07-product)
- `08 — Engineering / Technology` → [`08-engineering`](../08-engineering)
- `09 — Operations` → [`09-operations`](../09-operations)
- `10 — Supply Chain / Procurement` → [`10-supply-chain-procurement`](../10-supply-chain-procurement)
- `11 — IT` → [`11-it`](../11-it)
- `12 — Security` → [`12-security`](../12-security)
- `13 — Legal` → [`13-legal`](../13-legal)
- `14 — People / HR` → [`14-people-hr`](../14-people-hr)
- `15 — Corporate Development` → [`15-corporate-development`](../15-corporate-development)
- `16 — Communications / Public Affairs` → [`16-communications-public-affairs`](../16-communications-public-affairs)
- `17 — Executive Org Builder` → [`17-executive-org-builder`](../17-executive-org-builder)
- `18 — Decision System Installer` → [`18-decision-system-installer`](../18-decision-system-installer)

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
bash install-all.sh # whole package: ontology + 18 depts + 2 meta agents
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