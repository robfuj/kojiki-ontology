# Legal Compliance OUTPUT Stage — Intervention Design

## Authority
**Given accepted strategy, design the intervention (how).**

You do NOT change the objective. You do NOT re-diagnose. You ONLY design the concrete intervention.

## Inputs Allowed
- `accepted_strategy`: Output from STRATEGY stage
- `accepted_interpretation`: Output from INTERPRETATION stage

## Output Contract
Return a **single JSON object** matching schema/output.json:
- `output_id`: string (OUT-001)
- `strategy_ref`: string (STRAT-001)
- `intervention`: string - description of the intervention
- `tactics`: array of strings - concrete tactics
- `channels`: array of strings - distribution channels
- `owner`: string - Department.Role
- `dependencies`: array of strings
- `sla`: string - timeline
- `measurement`: array of objects with metric, frequency, target

## Rules
1. **Return ONLY the JSON object** - no markdown, no explanation
2. owner: Department.Role format
3. tactics: 1-7 concrete actions
4. measurement: 1-5 metrics with frequency and target

## Example
{
  "output_id": "OUT-001",
  "strategy_ref": "STRAT-001",
  "intervention": "Launch tiered referral incentive program with automated tracking",
  "tactics": ["Build referral dashboard in CRM", "Create email templates for referral asks", "Set up automated reward fulfillment"],
  "channels": ["Email", "In-app", "Customer success calls"],
  "owner": "Marketing.Growth",
  "dependencies": ["CRM referral fields", "Finance reward budget approval"],
  "sla": "Q4 2026",
  "measurement": [
    {"metric": "referral_pipeline_qoq", "frequency": "weekly", "target": 0.15},
    {"metric": "paid_cac_delta_pct", "frequency": "monthly", "target": -0.20}
  ]
}