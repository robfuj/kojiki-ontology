# LEARNING Stage — Kaizen Loop ACT Phase

## Purpose
Synthesize the full decision cycle into reusable experiences and patterns. This is the Kaizen Loop ACT phase — generates `experiences` (atomic unit of organizational learning) that feed NEURAXIS escalation.

## Inputs
- **accepted_problem**: From SACCADE (P-XXXXXXXX)
- **accepted_evidence**: From EVIDENCE (findings)
- **accepted_interpretation**: From INTERPRETATION (diagnosis)
- **accepted_strategy**: From STRATEGY (decision)
- **accepted_output**: From OUTPUT (intervention)
- **accepted_outcome**: From OUTCOME (actuals vs. targets)
- **accepted_deck**: From DECK (communication artifact)

## Forbidden
- raw_source, raw_record

## Tools
- pattern_extraction
- experience_synthesis

## Output Contract
Schema: `schema/learning.json`

## Structure

### Required Fields
- `learning_id`: Unique identifier (KL-YYYYMMDD-NNN format, e.g., "KL-20261231-001")
- `cycle_timestamp`: ISO 8601 timestamp of cycle completion
- `experiences`: Array of experience objects (each feeds NEURAXIS)
- `patterns`: Array of cross-cycle patterns (text, not structured)
- `reusable_insights`: Array of actionable insights for future cycles
- `redefinitions`: Array of problem redefinitions to feed back to SACCADE
- `outcome_score`: Weighted score from OUTCOME stage
- `guardrail_violations`: Array of guardrail violations from OUTCOME
- `confidence`: 0.0-1.0 confidence in synthesis quality
- `kaizen_iteration`: Which Kaizen iteration this learning came from

### Experience Object (feeds NEURAXIS)
Each experience must have:
- `id`: e.g., "EXP-YYYYMMDDHHMMSS"
- `problem_id`: Links back to SACCADE problem (P-XXXXXXXX)
- `hypothesis`: What was being tested
- `evidence_summary`: Concise summary of what evidence showed
- `error_classification`: One of `L0_execution`, `L1_reasoning`, `L2_problem_representation`, `L3_ontology`, `L4_meta_strategy`
- `outcome`: `confirmed` | `invalidated` | `inconclusive`
- `learning_ref`: Back-reference to this learning output
- `redefinition`: If `outcome=invalidated`, the new problem triggered (object with `new_problem`, `supersedes`, `reason`, `goal`, `constraints`, `assumptions`, `unknowns`) or `null`
- `agents`: Array of agent IDs involved (format: Department.Role)
- `recorded_at`: ISO 8601 timestamp

### Example
```json
{
  "learning_id": "KL-20261231-001",
  "cycle_timestamp": "2026-12-31T00:00:00Z",
  "experiences": [
    {
      "id": "EXP-20261231000000",
      "problem_id": "P-ABCDEF12",
      "hypothesis": "Referral program activation drives higher conversion than paid spend",
      "evidence_summary": "Referral 24% conversion vs paid 8%; referral pipeline +18% QoQ after incentive program",
      "error_classification": "L1_reasoning",
      "outcome": "confirmed",
      "learning_ref": "KL-20261231-001",
      "redefinition": null,
      "agents": ["Marketing.Brand", "Marketing.Growth"],
      "recorded_at": "2026-12-31T00:00:00Z"
    }
  ],
  "patterns": [
    "Source-mix matters more than scoring model for lead quality",
    "Referral incentives have compounding network effects",
    "Cross-department deck alignment reduced execution friction"
  ],
  "reusable_insights": [
    "When referral conversion > 2x paid, shift budget aggressively",
    "Deck-builder native mode enables stakeholder alignment before launch"
  ],
  "redefinitions": [],
  "outcome_score": 0.6,
  "guardrail_violations": [
    {
      "validator": "variance",
      "severity": "warning",
      "message": "High variance on paid_cac_delta_pct: 10% from target"
    }
  ],
  "confidence": 0.88,
  "kaizen_iteration": 1
}
```

## Guidelines
- **Every invalidated hypothesis creates a new problem** — if `outcome=invalidated`, `redefinition` must contain the new problem ID and reason
- **Error classification drives NEURAXIS** — L0/L1 handled locally; L2 triggers assumption review; L3/L4 open governance gates
- **Experiences are append-only** — never modify recorded experiences; new learning creates new experiences
- **Patterns are free text** — structured patterns belong in ontology (L3); these are narrative observations
- **KL- prefix for learning IDs** — distinguishes Kaizen Loop learning from legacy LN- format