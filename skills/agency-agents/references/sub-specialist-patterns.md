# Sub-Specialist Delegation & Handoff Patterns

This reference documents the patterns for creating sub-specialists, delegation, cross-department handoffs, and Mycelium signal propagation in the Kojiki Decision System.

## Sub-Specialist Creation

### Directory Structure
```
kojiki/specialists/<dept>/
├── sub-agents/
│   ├── base.py              # Base class inheriting from <Dept>SubSpecialist
│   ├── <name>/
│   │   ├── __init__.py      # Specialist subclass with SUB_AGENT_NAME, SUB_AGENT_DESCRIPTION
│   │   ├── config.yaml      # Skills, tools, decision rights, handoffs
│   │   ├── prompts/         # 8 SYNAPSIS prompts (can inherit from base)
│   │   └── schemas/         # Can inherit shared schemas
```

### Base Class Pattern
```python
# sub-agents/base.py
class <Dept>SubSpecialist(Specialist):
    SUB_AGENT_NAME = ""
    SUB_AGENT_DESCRIPTION = ""
    
    @property
    def name(self) -> str:
        return f"<dept>.<self.SUB_AGENT_NAME>"
    
    @property
    def agent_prefix(self) -> str:
        return f"<dept>.<self.SUB_AGENT_NAME>"
    
    @property
    def decision_rights_node(self) -> str:
        return f"<Dept>.<self.SUB_AGENT_NAME.replace('-', ' ').title().replace(' ', '')}"
    
    @property
    def stages(self) -> Dict[str, StageConfig]:
        base_path = Path(__file__).parent
        return {
            "saccade": StageConfig(...),
            "evidence": StageConfig(...),
            "interpretation": StageConfig(...),
            "strategy": StageConfig(...),
            "output": StageConfig(...),
            "learning": StageConfig(...),
        }
```

### Specialist Registration
```python
# sub-agents/<name>/__init__.py
from ..base import <Dept>SubSpecialist

class <Name>Specialist(<Dept>SubSpecialist):
    SUB_AGENT_NAME = "<name>"
    SUB_AGENT_DESCRIPTION = "<description>"

specialist = <Name>Specialist()
```

### Parent Specialist Integration
```python
# In parent specialist __init__.py
def load_sub_specialist(sub_agent_name: str) -> Specialist:
    sub_path = Path(__file__).parent / "sub-agents" / sub_agent_name / "__init__.py"
    spec = importlib.util.spec_from_file_location(...)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    for attr_name in dir(module):
        attr = getattr(module, attr_name)
        if isinstance(attr, type) and issubclass(attr, Specialist) and attr is not Specialist:
            return attr()
    raise ValueError(f"No Specialist subclass found in {sub_agent_name}")

# In stages dict:
"delegation": StageConfig(
    name="delegation",
    prompt=str(base_path / "prompts" / "05-delegation.md"),
    tools=[],
    schema=str(base_path / "schemas" / "delegation.json"),
    inputs_allowed=["output", "strategy", "interpretation"],
    enabled=True,
),
```

### Sub-Agent Config
```yaml
# sub-agents/<name>/config.yaml
agent:
  name: "<name>"
  parent_department: "<Dept>"
  parent_agent: "<dept>"
  description: "<description>"

skills:
  - github-autodiscovery
  - deck-builder

model:
  provider: "openrouter"
  model: "anthropic/claude-3-haiku:beta"
  temperature: 0.3
  max_tokens: 4000

tools:
  - <tool1>
  - <tool2>

decision_rights:
  own: ["<right1>", "<right2>"]
  recommend: ["<right3>"]
  consult: ["<right4>"]
  approve: []
  execute: ["<action1>"]
  escalate: ["<escalation1>"]
  automate: ["<auto1>"]

handoffs:
  - target: "<target-dept>"
    trigger: "<trigger_name>"
    payload_schema: "schemas/handoff-<trigger>.json"
```

## Delegation Engine

### Task Mapping
The `DelegationEngine._map_task_to_sub_agent()` maps tasks to sub-agents via keyword matching:

```python
mapping = {
    "seo": "seo-specialist",
    "search": "seo-specialist",
    "keyword": "seo-specialist",
    "paid social": "paid-social-specialist",
    "meta ads": "paid-social-specialist",
    "content": "content-creator",
    "copywriting": "content-creator",
    "growth": "growth-hacker",
    "experiment": "growth-hacker",
    "email": "email-strategist",
    "newsletter": "email-strategist",
    "pr": "pr-communications",
    "carousel": "carousel-growth",
    "brand": "brand-guardian",
    "visual": "visual-storyteller",
    "aeo": "aeo-specialist",
    "agentic": "agentic-search-optimizer",
    "video": "video-optimizer",
}
```

### Execution Flow
```python
engine = DelegationEngine(specialist, dispatch, department)
sub_tasks = engine.parse_execution_plan(output_result)
results = await engine.execute_all(sub_tasks)  # Parallel with deps
aggregated = engine.aggregate_results()
```

### Dependency Resolution
- Topological sort on `depends_on` fields
- Ready tasks (all deps met) execute in parallel
- Circular deps fall back to sequential execution

## Handoff Execution

### Config Definition
```yaml
handoffs:
  - target: "engineering-platform"
    trigger: "feature_cost_estimate"
    payload_schema: "schemas/handoff-cost-estimate.json"
```

### Execution
```python
engine = HandoffEngine(dispatch)
handoffs = engine.discover_handoffs(specialist_name)
results = engine.execute_all_handoffs(source_specialist, source_output)
```

### Payload Validation
```python
if schema_path and not engine.validate_payload(payload, schema_path):
    return {"error": f"Payload validation failed for schema: {schema_path}"}
```

## Mycelium Signal Propagation

### Signal Extraction
```python
def extract_signals_from_outcome(self, outcome, context):
    evaluations = outcome.get("evaluations", [])
    for eval in evaluations:
        met = evaluate_target(eval)
        if not met or eval.get("signal_on_success"):
            signal = {
                "id": f"sig-{timestamp}-{metric}",
                "origin_kr": f"{department}.{metric}",
                "event": "evaluation",
                "new_status": "FAILURE" if not met else "SUCCESS",
                "diagnosed_cause": eval.get("diagnosed_cause", ...),
                "diagnosed_cause_category": eval.get("diagnosed_cause_category", "Threshold"),
                "status": "ROUTED",
                "fired_at": datetime.now().isoformat(),
                "signal_kind": "failure" if not met else "request",
                "subgraph": [],
                "evaluation": eval,
            }
            signals.append(signal)
    return signals
```

### Propagation
```python
propagator = MyceliumSignalPropagator(department, dispatch)
signals = propagator.extract_signals_from_outcome(outcome, context)
propagation_results = propagator.propagate_signals(signals)
```

### SignalPropagator Configuration
- Threshold: 0.15
- Max hops: 3
- Decision Rights gating via RACI
- Edge reinforcement with real flow signals
- SENTINEL Ed25519 signing via KeyManager

## SENTINEL Key Provisioning

### Node List
126 nodes covering all departments + sub-specialists:
- 8 Department heads
- 84 Sub-specialists
- 34 Supporting nodes (support, specialized, etc.)
- Registry key for audit log signing

### Provisioning
```bash
# Provision all keys
python scripts/provision_sentinel_keys.py --provision

# Verify all keys
python scripts/provision_sentinel_keys.py --verify

# Provision registry key
python scripts/provision_sentinel_keys.py --registry
```

### Key Storage
- Location: `~/.kojiki/sentinel/keys/`
- Format: `<sanitized_node_id>_private.pem`
- Sanitization: `re.sub(r'[^a-zA-Z0-9._-]', '_', node_id)`
- Legacy format fallback: dots → underscores

## Multi-Provider LLM Configuration

### Provider Configs
```python
PROVIDERS = {
    "openrouter": LLMProviderConfig(
        base_url="https://openrouter.ai/api/v1",
        api_key_env="OPENROUTER_API_KEY",
        models=["anthropic/claude-3-haiku:beta", ...],
        default_model="anthropic/claude-3-haiku:beta",
    ),
    "anthropic": LLMProviderConfig(...),
    "openai": LLMProviderConfig(...),
    "ollama": LLMProviderConfig(
        base_url="http://localhost:11434/v1",
        models=["qwen2.5:14b", "llama3.1:8b", ...],
        default_model="qwen2.5:14b",
        supports_functions=False,
    ),
}
```

### Usage
```python
config = get_llm_config()  # Auto-detects provider from env
result = await call_llm(prompt, context, tools, schema, stage_name, config)
```

### Environment Variables
- `KOJIKI_LLM_PROVIDER` — explicit provider override
- `KOJIKI_LLM_MODEL` — model override
- `KOJIKI_LLM_API_KEY` — API key (or use provider-specific env var)
- `KOJIKI_LLM_TEMPERATURE` — default 0.3
- `KOJIKI_LLM_MAX_TOKENS` — default 4000

## CI/CD Pipeline

### GitHub Actions Workflow
```yaml
# .github/workflows/ci.yml
jobs:
  lint: ruff + mypy
  schema-validation: jsonschema Draft7Validator
  specialist-tests: verify_all_runners.py
  mycelium-tests: pytest mycelium/tests/
  causal-signatures: verify_causal_signatures.py
  sentinel-keys: provision_sentinel_keys.py --verify
  security-scan: bandit + detect-secrets
  documentation: README existence + required sections
  build-package: python -m build
```

## Common Pitfalls & Fixes

| Issue | Fix |
|-------|-----|
| SACCADE schema expects `P-XXXXXXXX` | Relax pattern to `^P-[A-Z0-9]{10,}$` |
| COS strategy returns `actions[]` not `team_okrs` | Disable schema: `specialist.stages["strategy"].schema = None` |
| Department SACCADE returns arrays | Override prompt with COS generic prompt |
| LLM stub returns marketing output | Skip stub when `dept_head == "ChiefOfStaff"` |
| Circular import runner ↔ stages | Import `PipelineRunner` locally inside stage functions |
| Test stubs missing required fields | Add `enabled: false` or provide minimal valid stubs |
| Deck builder not found | Add `deck_builder` tool to DECK stage, import from `skills/deck-builder/bridge.py` |
| Missing SENTINEL keys | Run `provision_sentinel_keys.py --provision` before tests |
| Postgres import errors | Add `sys.path.insert(0, str(Path(__file__).parent.parent / "engine"))` |