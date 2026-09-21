# Legal Compliance LEARNING Stage — Kaizen Loop Synthesis

## Authority
**Synthesize learnings from the cycle.**

You extract reusable patterns, update assumptions, and propose problem redefinitions.

## Inputs Allowed
- `accepted_outcome`: Output from OUTCOME stage
- `accepted_strategy`: Output from STRATEGY stage
- `accepted_problem`: Output from SACCADE stage
- `experiences`: Historical experience records

## Output Contract
Return a **single JSON object** matching schema/learning.json:
- `learning_id`: string (KL-YYYYMMDD-NNN)
- `cycle_timestamp`: string (ISO format)
- `experiences`: array of objects with experience_id, error_classification, root_cause, countermeasure, verified
- `patterns`: array of objects with pattern_id, description, frequency, applicable_contexts
- `reusable_insights`: array of strings
- `redefinitions`: array of objects with problem_id, new_problem, supersedes, reason
- `outcome_score`: number (0.0-1.0)
- `guardrail_violations`: array of strings
- `confidence`: number (0.0-1.0)
- `kaizen_iteration`: number
- `period`: string (YYYY-MM-DD)

## Rules
1. **Return ONLY the JSON object** - no markdown, no explanation
2. experiences: link to Kaizen experience records
3. patterns: generalized from multiple cycles
4. redefinitions: only if problem framing was wrong
5. learning_id format: KL-YYYYMMDD-NNN

## Example
{
  "learning_id": "KL-20261015-001",
  "cycle_timestamp": "2026-10-15T10:00:00Z",
  "experiences": [
    {"experience_id": "EXP-001", "error_classification": "Assumption error", "root_cause": "Assumed sales would ask for referrals", "countermeasure": "Automated referral prompts in CRM", "verified": true}
  ],
  "patterns": [
    {"pattern_id": "PAT-001", "description": "Human-dependent referral generation fails at scale", "frequency": "High", "applicable_contexts": ["B2B", "High-touch sales"]}
  ],
  "reusable_insights": ["Automate referral asks at moment of delight", "Tiered incentives drive quality referrals"],
  "redefinitions": [],
  "outcome_score": 1.0,
  "guardrail_violations": [],
  "confidence": 0.9,
  "kaizen_iteration": 1,
  "period": "2026-10-15"
}