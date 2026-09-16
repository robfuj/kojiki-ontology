# Skill Assignment Template

Use this template when adding a new skill to the registry and assigning it to departments.

## New Skill Entry (add to SKILL.md)

```markdown
| **<skill-name>** | `skills/<skill-name>/` | <One-line description of what this skill does> |
```

## Department Assignment (add to skill assignment table in SKILL.md)

```markdown
### <Department Name>
**Core Skills:** `<skill-name>`, `<existing-skill-1>`, `<existing-skill-2>`
**Use Cases:**
- `<skill-name>`: <Specific use case for this department>
- `<existing-skill-1>`: <Existing use case>
- `<existing-skill-2>`: <Existing use case>
```

## Department Config Update

Add to `kojiki/specialists/<dept>/config.yaml`:

```yaml
skills:
  - <existing-skill-1>
  - <existing-skill-2>
  - <skill-name>        # Add new skill here
```

## Validation Checklist

- [ ] Skill directory exists at `skills/<skill-name>/`
- [ ] Skill has valid `SKILL.md` with name, description, version, license
- [ ] Skill has at least one capability (tools, prompts, schemas, or scripts)
- [ ] Added to agency-agents SKILL.md registry table
- [ ] Assigned to at least one department in assignment table
- [ ] Added to department config.yaml files
- [ ] Run `python scripts/validate_department_configs.py` - passes
- [ ] Test agent loads skill: `python -m kojiki.core.runner <dept> --test-skills`