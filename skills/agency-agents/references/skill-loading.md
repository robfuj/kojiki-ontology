# Skill Loading at Runtime

## How Skills Are Loaded

When a department agent starts, the skill loader in `kojiki/core/__init__.py` performs:

1. **Read agent config** - Loads `kojiki/specialists/<dept>/config.yaml`
2. **Resolve skill paths** - Maps skill names to `skills/<skill-name>/` in repo
3. **Load skill manifests** - Reads each skill's `SKILL.md` for metadata
4. **Inject capabilities** - Makes skill's tools, prompts, schemas available to agent

## Config Schema

```yaml
# kojiki/specialists/<dept>/config.yaml
agent:
  name: "finance-accounting"
  department: "Finance"
  
skills:
  - deck-builder
  - github-autodiscovery
  
model:
  provider: "openrouter"
  model: "anthropic/claude-3-haiku:beta"
  
tools:
  - financial_modeling
  - treasury_management
  - budget_analysis
```

## Skill Structure

Each skill in `skills/<name>/` must have:

```
skills/<name>/
├── SKILL.md              # Manifest (required)
├── tools/                # Python tool modules (optional)
├── prompts/              # Prompt templates (optional)
├── schemas/              # JSON schemas (optional)
├── scripts/              # Executable scripts (optional)
├── references/           # Documentation (optional)
└── templates/            # Template files (optional)
```

## Loading Order

Skills load in the order listed in config. Later skills can override earlier ones (tools, prompts).

## Runtime Access

Once loaded, agents access skills via:

```python
# In specialist __init__.py or tools
from kojiki.core import get_skill

deck_builder = get_skill("deck-builder")
slides = deck_builder.generate(mode="investor", data=financial_data)
```

## Validation

On agent startup, the loader validates:
- All listed skills exist in `skills/`
- Each skill has valid `SKILL.md`
- No circular dependencies between skills
- Required tools/prompts/schemas are present