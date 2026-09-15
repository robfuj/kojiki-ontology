# SYNAPSIS Invariants

The meta-rule: **one kind of state must not silently masquerade as another.** Each
pair below is a boundary a SYNAPSIS transformation is forbidden to cross. They are not
slogans — they are enforced in `validate.py` against every decision record.

| # | Invariant | Meaning |
|---|---|---|
| 1 | Evidence is not interpretation | A fact established by a source must stay distinct from what we infer it means. |
| 2 | Memory is not belief | A stored record is not a conclusion the org has adopted. |
| 3 | Acknowledgement is not verified persistence | A stakeholder saying "ok" is not the same as durable, verified state. |
| 4 | Audit is not authority | The auditor may challenge a claim; it does not get to replace the owner's decision. |
| 5 | Completion is not success | Producing an artifact ≠ the objective being achieved. |
| 6 | Synchronization is not adjudication | Copying state between systems ≠ judging which conclusion is correct. |
| 7 | Learning is not permission to rewrite doctrine | A pattern across outcomes may propose a rule change; it may not silently edit doctrine. |
| 8 | Evaluation is not origination | Brain/Audit may judge a specialist's output without authoring the analysis themselves. |

## Enforcement pattern
A SYNAPSIS decision record carries, per transformation, an explicit `state_kind`
(record / evidence / interpretation / strategy / plan / artifact / audit / learning /
coordination). `validate.py` asserts:

- A downstream transformation did not overwrite an upstream `state_kind` (e.g. EVIDENCE
  output was not relabeled as INTERPRETATION).
- AUDIT and BRAIN outputs carry `independent: true` / `no_origination: true` and contain
  no field that re-implements the specialist transformation they reviewed.
- LEARNING proposals are stored separately from `doctrine` and flagged `proposed`, never
  auto-applied.
- Every conclusion traces to a `record` (origin) + `evidence` (basis) + `boundary`
  (which transformation owned it) + `reviewer` (Audit/Brain that checked it).

If any invariant fails, the record is **rejected**, not silently repaired.
