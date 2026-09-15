# SYNAPSIS Roadmap

## v1 (current) — verifiable evidence path
- 9 transformation chain + Brain + Adversarial Audit, enforced by `validate.py`.
- **Evidence grounding (anti-hallucination):** any `evidence` step with
  `requires_source_citation: true` MUST carry a `source_citation` (URL / file / record id).
  Uncited, document-backed evidence fails validation. This closes the hallucination gap
  for facts that *should* be citable.

## v2 — interaction-derived, client-scoped evidence (reflective step)
For functions with human interaction (Sales, Customer Success, BD, Communications, …), the
evidence created during a live client conversation is **different per client** and cannot
be pre-cited from a corpus. It emerges *during* the interaction. v1 permits such evidence
tagged `evidence_type: "interaction-derived"` but does not yet structure the sense-making.

v2 adds a **reflective transformation** between RECORD and EVIDENCE for interaction-derived
input:
- RECORD captures the raw interaction artifact (transcript / note), scoped to `client_id`.
- The reflective step splits **stated** (what the client actually said/did) from
  **inferred** (what the agent reads into it), and keeps them labeled separately.
- Only *stated* content feeds EVIDENCE; *inferred* content is flagged low-confidence until
  confirmed in a later interaction.
- This is where the real anti-hallucination work lives for human-facing functions: the
  agent cannot "remember" a client stance that was never actually stated.

### Why deferred from v1
The reflective split is a meaningful modeling change (new transformation + validator rule)
and benefits from real interaction transcripts to design well. v1 ships the verifiable
path now; v2 scopes the interaction path deliberately rather than bolting it on.

## Open questions for v2
- Should the reflective step be a dedicated bot (`bots/reflect`) or inline in the dept bot?
- How is `client_id` scoped in multi-tenant installs?
- Does interaction-derived evidence need a TTL / re-confirmation cadence?
