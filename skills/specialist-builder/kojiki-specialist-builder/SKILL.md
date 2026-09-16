---
name: kojiki-specialist-builder
description: Build Kojiki department specialists with shared core runner.
version: 0.1.0
author: Rob Fujita (robfuj), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [kojiki, specialist, builder, decision-system]
    related_skills: [hermes-agent-skill-authoring]
---

# Kojiki Specialist Builder Skill

Builds department specialists for the Kojiki Decision System. Each specialist is a department head that coordinates 3-5 team nodes via the shared 8-stage SYNAPSIS pipeline (SACCADE→EVIDENCE→INTERPRETATION→STRATEGY→OUTPUT→DECK→OUTCOME→LEARNING).

## When to Use

- Adding a new department specialist to the Kojiki system
- Need to create the full 8-stage prompt/schema structure for a department
- Verifying a specialist passes the pipeline test

## Prerequisites

- Kojiki core at `/kojiki/core/` with `Specialist`, `StageConfig`, `ScopedContext`
- Shared schemas at each specialist's `schemas/` directory (8 JSON schemas)
- PostgreSQL running with `kojiki` database for persistence
- `scripts/verify_all_runners.py` for validation

## Procedure

1. **Create directory structure**
   ```bash
   mkdir -p kojiki/specialists/<name>/{prompts,schemas,tools,validators,adapters,causal_chains}
   ```

2. **Write `__init__.py` with Specialist subclass**
   - Properties: `name` (kebab-case), `agent_prefix` (department node), `decision_rights_node` (owning node)
   - `stages` dict: 8 StageConfig entries with prompts, schemas, tools=[], inputs_allowed per stage
   - Stage inputs_allowed must match what dispatch passes (see step 3)

3. **Write 8 prompt files** (`prompts/01-saccade.md` through `prompts/08-learning.md`)
   - Each tailored to department's evidence sources, team nodes, decision rights
   - SACCADE: raw_record, dept_head, objective, description, team_nodes, parent_objective
   - EVIDENCE: dept_head, team_nodes, objective
   - INTERPRETATION: evidence, objective, team_nodes
   - STRATEGY: problem, evidence, interpretation, dept_objective, team_nodes, dept_head
   - OUTPUT: accepted_strategy
   - DECK: accepted_output
   - OUTCOME: accepted_output, deck_ref
   - LEARNING: all accepted_* fields

4. **Copy 8 shared schemas** to `schemas/`
   - saccade_problem.json, evidence_findings.json, interpretation_diagnosis.json
   - strategy_team_okrs.json, output_intervention.json, deck_request.json
   - outcome_kaizen.json, learning_kaizen.json

5. **Verify**
   ```bash
   python scripts/verify_all_runners.py
   ```
   Must show `✅ <name>` and `PASSED: N/N`

## Key Rules

- KL- prefix for learning_id (not LN)
- Ed25519 signatures via SENTINEL KeyManager only
- PostgreSQL for all persistence (causal_chains, mycelium_nodes, okr_*)
- Remove all build-tool/personal references from prompts/docs
- Private keys stored outside repo at ~/.kojiki/sentinel/keys/
- Shared schemas are identical across specialists (copied, not symlinked here)

## Pitfalls

- Missing `dept_head` in STRATEGY stage inputs_allowed → scoped context validation fails
- StageConfig must use `inputs_allowed` list, not `inputs_forbidden`
- Mock specialist in dept_head_base.py needs `dept_head` in STRATEGY inputs_allowed
- Verify runner fails if Kaizen schema root not found (ensure schemas/ dir exists with all 8 files)
- **Verification script must pass raw_record as string** — `scripts/verify_all_runners.py` test dispatch uses `raw_record: "Test goal for verification"` (string), not a dict. Dict input causes SACCADE schema validation to fail because the stub `call_model()` expects string raw_record for context matching.
- **Chief of Staff strategy schema must be disabled** — When Chief of Staff runs decomposition, it uses marketing-brand specialist with `dept_head=ChiefOfStaff` context. The strategy output format is `actions` array (department-level objectives), not `team_okrs` (team-level OKRs). Set `specialist.stages["strategy"].schema = None` before running to bypass schema validation.
- **Chief of Staff SACCADE uses task_id prefix for stub routing** — The stub `call_model()` checks for `cos-saccade` in `task_id` to return a problem matching the actual user goal. Department specialist SACCADEs don't need this — they use their own prompts.

## Verification

- `verify_all_runners.py` shows specialist in PASSED list
- Chief of Staff coordinate() routes to specialist via `_owner_to_specialist()` mapping
- Dept head decomposition creates team OKRs with Mycelium edges registered