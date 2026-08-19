# SYNAPSIS — Kojiki Cognitive Substrate

SYNAPSIS is the **reasoning engine** that sits between a Kojiki department and its
decisions. Every department (Sales, Finance, Product, …) runs its work on the same
SYNAPSIS substrate rather than inventing its own decomposition. It is part of the
Kojiki Organizational Architecture:

```
KOJIKI  (Organizational Architecture)
            │
   ┌────────┼────────┐
   ↓        ↓        ↓
 SALES   FINANCE   PRODUCT        ← departments (each its own repo)
   │        │        │
   ↓        ↓        ↓
SYNAPSIS  SYNAPSIS  SYNAPSIS         ← this substrate (shared, not reimplemented)
   │        │        │
   ↓        ↓        ↓
Transformations → Decisions → Outcomes → Learning → Organizational Memory
```

## Core thesis
Decompose the problem by **the type of reasoning being performed**, not by role or
workflow. A workflow agent can still acquire evidence, interpret it, choose a
strategy, draft the action, and learn from its own outcome in one context. SYNAPSIS
deliberately prevents those responsibilities from collapsing into one another. Each
important conclusion has an identifiable **origin, evidence base, boundary, and reviewer**.

## The transformation chain
```
SOURCE → RECORD → EVIDENCE → INTERPRETATION → STRATEGY → INTERACTION → OUTPUT → OUTCOME → LEARNING
```
Each transformation is a bounded function with **one authority** and an explicit
"what it must NOT silently become." See `transformations.json`.

| Transformation | May answer | Must NOT silently become |
|---|---|---|
| Record / Memory | What happened, when, involving whom, where verifiable? | Interpretation or strategy |
| Evidence Extraction | What does the source actually establish? | Deal/domain analysis |
| Interpretation specialist | What does accepted evidence mean for one defined question? | General strategy |
| Strategy | What is the binding constraint & next commitment to seek? | Evidence retrieval or drafting |
| Interaction Design | How to pursue a supplied objective with this stakeholder? | Choosing the objective |
| Production | How to render an approved decision as an artifact? | Reconstructing customer truth |
| Adversarial Audit | Does the claim graph survive challenge vs the standard? | The specialist's preferred conclusion |
| Learning | What patterns appear across outcomes, under what uncertainty? | Permission to rewrite doctrine |
| Brain | What work is needed, what outputs accepted, what routes next? | Originating the specialist analysis it adjudicates |

## The meta-rule (invariants)
One kind of state must not masquerade as another. See `invariants.md` + `validate.py`.
The hard pairs:

- **Evidence is not interpretation.**
- **Memory is not belief.**
- **Acknowledgement is not verified persistence.**
- **Audit is not authority.**
- **Completion is not success.**
- **Synchronization is not adjudication.**
- **Learning is not permission to rewrite doctrine.**
- **Evaluation is not origination.**

## Brain (orchestration, not a super-agent)
Brain routes, sequences, enforces dependencies, adjudicates bounded outputs, and
decides what work is required next. It is **not** the hidden department agent above
the specialists. Critically: **Brain may adjudicate a specialist proposal it did not
author, but it must not quietly redo the specialist's transformation.** Brain can
delay synthesis until every transformation required for a decision is available
(Brain-defined decision barriers), without the automation layer interpreting results.

## Why this produces better failure behavior
When a recommendation fails, SYNAPSIS asks *where unsupported or incorrect reasoning
first entered the chain*. The reasoning lineage becomes inspectable: upstream errors
may still contaminate downstream work, but the origin and transformation boundaries
are visible in a way a broad task agent is not. Bounded responsibility → clearer
evaluation → easier attribution → smaller blast radius → easier replacement.

## When SYNAPSIS is NOT the right call
A simple, low-consequence task ("summarize this call in three bullets") may be better
as a single task agent. SYNAPSIS's structure is most defensible when the system must
maintain evolving truth, coordinate multiple interpretations, learn across outcomes,
recommend consequential actions, and stay auditable over time. State the cost openly:
more interfaces, more contracts, more artifacts that can fail, higher latency.

## Source
Condensed from *Sales V2 — Why a Transformation-Based AI Architecture Is Different*
(leadership case for cognitive decomposition). SYNAPSIS generalizes that argument from
Sales to every Kojiki department.

## Cross-department handoff
See [`synapsis-xdept.md`](synapsis-xdept.md) — the optional-handoff protocol that keeps
every department **standalone-functional** while letting sibling departments upgrade
fidelity when present. Cross-dept inputs are typed, peer-to-peer, and tagged
`sibling-verified` vs `self-generated` (enforced by `validate.py`).
