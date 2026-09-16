# Department Configurations

## Config File Location

Each department has a config at:
```
kojiki/specialists/<dept-name>/config.yaml
```

## Config Schema

```yaml
agent:
  name: "marketing-brand"           # Unique agent identifier
  department: "Marketing"           # Department name (1 of 8)
  description: "Brand, growth, referral, paid media"  # Scope

skills:
  - deck-builder                    # Skill names from agency-agents registry
  - github-autodiscovery
  - multi-agent-orchestration

model:
  provider: "openrouter"            # LLM provider
  model: "anthropic/claude-3-haiku:beta"
  temperature: 0.3
  max_tokens: 4000

tools:
  - brand_analysis                  # Custom tools for this department
  - campaign_optimizer
  - referral_tracker
  - paid_media_analyzer

prompts:
  # Override default SYNAPSIS prompts if needed
  saccade: "prompts/01-saccade.md"
  evidence: "prompts/02-evidence.md"
  interpretation: "prompts/03-interpretation.md"
  strategy: "prompts/04-strategy.md"
  output: "prompts/05-output.md"
  deck: "prompts/06-deck.md"
  outcome: "prompts/07-outcome.md"
  learning: "prompts/08-learning.md"

schemas:
  # Override default schemas if needed
  strategy: "schemas/strategy-marketing.json"

decision_rights:
  # RACI for this department's decisions
  own: ["brand_strategy", "campaign_budget", "creative_direction"]
  recommend: ["product_positioning", "pricing_strategy"]
  consult: ["engineering_roadmap", "legal_compliance"]
  approve: []
  execute: ["campaign_launch", "content_publishing"]
  escalate: ["budget_over_100k", "brand_crisis"]
  automate: ["social_scheduling", "ab_test_variants"]

handoffs:
  # Cross-department handoffs this department initiates
  - target: "sales-outbound"
    trigger: "qualified_lead"
    payload_schema: "schemas/handoff-lead.json"
  - target: "engineering-platform"
    trigger: "feature_request"
    payload_schema: "schemas/handoff-feature.json"

okrs:
  # Department OKRs (populated by Chief of Staff)
  corporate_objective_ref: "CORP-OBJ-001"
  department_objectives:
    - id: "MKT-OBJ-001"
      title: "Increase brand awareness"
      key_results:
        - id: "MKT-KR-001"
          metric: "unaided_brand_recall"
          target: 0.45
          current: 0.32
          confidence: 0.7
```

## All 8 Department Configs

| Department | Config Path | Key Skills |
|------------|-------------|------------|
| Finance | `kojiki/specialists/finance-accounting/config.yaml` | deck-builder, github-autodiscovery |
| Marketing | `kojiki/specialists/marketing-brand/config.yaml` | deck-builder, github-autodiscovery, multi-agent-orchestration |
| Sales | `kojiki/specialists/sales-outbound/config.yaml` | deck-builder, github-autodiscovery, multi-agent-orchestration |
| Engineering | `kojiki/specialists/engineering-platform/config.yaml` | github-autodiscovery, specialist-builder, multi-agent-orchestration |
| Operations | `kojiki/specialists/operations-ops/config.yaml` | deck-builder, github-autodiscovery |
| Legal | `kojiki/specialists/legal-compliance/config.yaml` | deck-builder, github-autodiscovery |
| People & Comms | `kojiki/specialists/people-hr/config.yaml` | deck-builder, github-autodiscovery |
| AI Intelligence | `kojiki/specialists/ai-intelligence/config.yaml` | github-autodiscovery, specialist-builder, multi-agent-orchestration |

## Validation

Run validation on all configs:
```bash
python scripts/validate_department_configs.py
```

Checks:
- All 8 departments have configs
- All listed skills exist in agency-agents registry
- Decision rights are valid RACI values
- Handoff targets are valid departments
- OKR references are valid