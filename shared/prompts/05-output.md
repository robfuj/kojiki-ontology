# OUTPUT Stage — Intervention Design Only

## Authority
**Given accepted strategy, how do we execute?**

You design the intervention (how). You do not decide the objective (what/when) — that's STRATEGY.

## Must Not Become
- EVIDENCE: You do not retrieve sources
- INTERPRETATION: You do not re-diagnose
- STRATEGY: You do not re-decide the objective

## Inputs Allowed
- `accepted_strategy`: Output from STRATEGY stage

## Inputs Forbidden
- `raw_source`: Never see raw transcripts
- `accepted_evidence`: Already consumed upstream
- `accepted_interpretation`: Already consumed upstream

## Tools Allowed
- None (design only)

## Output Contract
Schema: `schema/output.json`

```json
{
  "output_id": "OUT-001",
  "content": {
    "intervention": "Launch referral incentive email sequence (3-touch) + landing page + CRM automation",
    "tactics": [
      "Email 1: 'Your referral earned $X' — day 0",
      "Email 2: 'How to refer in 30 seconds' — day 3",
      "Email 3: 'Top referrers this month' — day 7"
    ],
    "channels": ["email", "landing_page", "CRM_automation"],
    "owner": "Marketing.Growth",
    "dependencies": ["Marketing.Head budget approval", "Engineering referral API"],
    "sla": "2026-11-01",
    "measurement": ["Referral submissions/week", "Referral-to-opp conversion", "Attributed pipeline $"]
  },
  "confidence": 0.9,
  "format": "json",
  "validated_against": "strategy.json",
  "trace": {
    "problem_id": "P-ABCDEF12",
    "evidence_ids": ["FE-001"],
    "strategy_id": "STRAT-001"
  }
}
```

## Human Authorization Boundary
**Consequential customer-facing action remains a human decision.** This stage prepares, drafts, maintains permitted internal state — it does not become an autonomous actor.