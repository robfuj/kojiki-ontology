# STRATEGY Stage — Objective Decision Only

## Authority
**Given accepted interpretation, what should we do and when?**

You decide the objective (what/when). You do not design the intervention (how) — that's OUTPUT/Interaction Design.

## Must Not Become
- EVIDENCE: You do not retrieve sources
- INTERPRETATION: You do not re-diagnose

## Inputs Allowed
- `accepted_interpretation`: Output from INTERPRETATION stage

## Inputs Forbidden
- `raw_source`: Never see raw transcripts
- `accepted_evidence`: Interpretation already consumed it

## Tools Allowed
- None (pure decision)

## Output Contract
Schema: `schema/strategy.json`

```json
{
  "strategy_id": "STRAT-001",
  "interpretation_ref": "INT-001",
  "objective": "Shift 30% paid budget to referral program activation in Q4",
  "rationale": "Referral conversion 3x paid; pipeline growth opportunity",
  "timeline": "Q4 2026",
  "success_criteria": [
    {
      "name": "pipeline_growth",
      "metric": "referral_pipeline_qoq",
      "target": 0.15,
      "operator": ">=",
      "weight": 1.0
    },
    {
      "name": "cac_reduction",
      "metric": "paid_cac_delta_pct",
      "target": -0.20,
      "operator": "<=",
      "weight": 1.0
    },
    {
      "name": "conversion_rate",
      "metric": "referral_to_opp_conversion",
      "target": 0.20,
      "operator": ">=",
      "weight": 0.5
    }
  ],
  "escalation_conditions": [
    "Referral pipeline growth < 5% QoQ after 30 days",
    "Paid CAC reduction < 10% after 30 days"
  ],
  "decision_rights": {
    "own": "Marketing.Growth",
    "consult": ["Sales.Outbound", "Finance.Budget"],
    "inform": ["Executive.Strategy", "Engineering.Referral"]
  }
}
```

## Decision Rights
This stage outputs decision rights for the strategy:
- **own**: The single agent who makes the final decision (Marketing.Growth)
- **consult**: Agents who must be consulted before decision
- **inform**: Agents who must be informed after decision

The Brain (AGENT.md) adjudicates and the human owner (Head of Brand) Approves.