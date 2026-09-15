# OUTCOME Stage — Kaizen Loop CHECK Phase

## Purpose
Run the Kaizen Loop CHECK phase: compare measured actuals against success criteria with guardrails. This is where reality meets plan — actual measurements against success criteria, with guardrails that promote learning.

## Inputs
- **accepted_output**: The intervention from OUTPUT stage (required)
- **deck_ref**: Reference to communication artifact from DECK stage (optional)
- **success_criteria**: Success criteria from STRATEGY stage (required)

## Forbidden
- raw_source, accepted_evidence, accepted_interpretation, accepted_strategy

## Tools
- measurement_retrieval
- tracking

## Output Contract
Schema: `schema/outcome.json`

## Structure

### Required Fields
- `outcome_id`: Unique identifier (timestamp-based, e.g., "OC-20261231000000")
- `output_ref`: Reference to OUTPUT stage intervention (e.g., "OUT-001")
- `actuals`: Object with measured values for each success criterion metric
- `evaluations`: Array of criterion evaluations with passed/failed
- `outcome_score`: Weighted score of passed criteria (0.0-1.0)
- `target_met`: Whether outcome_score >= convergence_threshold
- `converged`: Whether Kaizen Loop converged
- `iteration_count`: Number of PDCA iterations run
- `guardrail_violations`: Array of guardrail violations (promote learning)
- `deviation_analysis`: Root cause analysis for any failed criteria
- `confidence`: 0.0-1.0 confidence in measurement completeness

### Example
```json
{
  "outcome_id": "OC-20261231000000",
  "output_ref": "OUT-001",
  "actuals": {
    "referral_pipeline_qoq": 0.18,
    "paid_cac_delta_pct": -0.18,
    "referral_to_opp_conversion": 0.24
  },
  "evaluations": [
    {
      "criterion": "pipeline_growth",
      "metric": "referral_pipeline_qoq",
      "target": 0.15,
      "actual": 0.18,
      "operator": ">=",
      "passed": true,
      "weight": 1.0
    },
    {
      "criterion": "cac_reduction",
      "metric": "paid_cac_delta_pct",
      "target": -0.20,
      "actual": -0.18,
      "operator": "<=",
      "passed": false,
      "weight": 1.0
    },
    {
      "criterion": "conversion_rate",
      "metric": "referral_to_opp_conversion",
      "target": 0.20,
      "actual": 0.24,
      "operator": ">=",
      "passed": true,
      "weight": 0.5
    }
  ],
  "outcome_score": 0.6,
  "target_met": false,
  "converged": false,
  "iteration_count": 3,
  "guardrail_violations": [
    {
      "validator": "variance",
      "severity": "warning",
      "message": "High variance on paid_cac_delta_pct: 10% from target",
      "suggested_fix": "Investigate root cause: measurement error or real deviation?"
    }
  ],
  "deviation_analysis": "Referral exceeded target (+18% vs +15%), paid CAC close (-18% vs -20%)",
  "confidence": 0.9
}
```

## Guidelines
- **Measure what you said you'd measure** — use the `success_criteria` from STRATEGY stage
- **Time-box** — define measurement_window explicitly
- **Be honest about gaps** — if data is missing, note it in deviation_analysis and lower confidence
- **Guardrails promote learning** — violations don't just fail, they generate learning cases
- **No recommendations here** — that's STRATEGY or next-cycle SACCADE