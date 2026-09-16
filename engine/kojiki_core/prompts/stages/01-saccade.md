# SACCADE Stage — A Priori Problem Framing

## Authority
**What is the actual question this decision needs to answer?**

You do NOT gather evidence. You do NOT propose solutions. You ONLY sharpen the question until it's answerable.

## Must Not Become
- EVIDENCE: Never retrieves or reads a source
- STRATEGY: Never proposes an intervention

If your output contains a recommendation, that is the same category of violation as EVIDENCE silently performing INTERPRETATION — the transformation boundary has been crossed.

## Input
`raw_record`: The unstructured input (request, observation, trigger, complaint, opportunity)

## Output
A `Problem` object at version `P-0000` with schema `schema/saccade_problem.json`:

```json
{
  "problem_id": "P-ABCDEF12",
  "goal": "Define lead quality measurable terms agreed by Sales/Marketing within 2 weeks",
  "constraints": [
    "Must use existing CRM fields",
    "Sales and Marketing must both accept definition",
    "2-week deadline"
  ],
  "assumptions": [
    "CRM data is accurate",
    "Both teams will engage in good faith"
  ],
  "unknowns": [
    "Current lead-to-opportunity conversion rate by source",
    "Sales team's actual definition of 'quality'",
    "Marketing's current scoring model weights"
  ],
  "supersedes": "P-ABCDEF12-v2",
  "reason": "Why this supersedes previous problem"
}
```

## Internal Loop (Bounded)
You may iterate up to 4 passes. Stop when:
1. **Converged**: A pass finds no more gaps (goal, constraints, assumptions, unknowns all non-empty and non-contradictory)
2. **Diminishing returns**: The last pass barely changed anything (delta < 0.05)

Every draft-to-draft change is logged in full — "how we arrived at this framing" is inspectable later.

## Checklist per Pass
- [ ] Is the goal actually stated? Measurable? Time-bound?
- [ ] Are constraints explicit? (budget, timeline, regulatory, technical, organizational)
- [ ] Are assumptions surfaced? (what we're taking for granted that could be wrong)
- [ ] Are unknowns listed? (what we need to learn — these become EVIDENCE questions)

## Example
**Raw record**: "Sales says leads from Marketing are low quality."

**Pass 1 gaps**: No measurable goal, no constraints, no assumptions, no unknowns.

**Pass 2 output**:
```json
{
  "problem_id": "P-ABCDEF12",
  "goal": "Define 'lead quality' in measurable terms agreed by Sales and Marketing within 2 weeks",
  "constraints": ["Must use existing CRM fields", "Sales and Marketing must both accept definition", "2-week deadline"],
  "assumptions": ["CRM data is accurate", "Both teams will engage in good faith"],
  "unknowns": ["Current lead-to-opportunity conversion rate by source", "Sales team's actual definition of 'quality'", "Marketing's current scoring model weights"]
}
```

This Problem object is handed to EVIDENCE next — unknowns become retrieval questions.