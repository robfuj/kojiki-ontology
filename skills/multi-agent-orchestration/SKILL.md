---
name: multi-agent-orchestration
category: autonomous-ai-agents
description: Use when building Chief of Staff orchestration.
---

# Multi-Agent Orchestration (Chief of Staff Pattern)

## When to Use
Building a Chief of Staff that frames problems, decomposes goals into department objectives, runs each department's SACCADE with their specialist, and executes in parallel batches with dependency management.

## Core Principles

### 1. Prompt Separation — Each Role Gets Its Own Prompt
- **Chief of Staff SACCADE** → `01-saccade-cos.md` (generic problem framing)
- **Chief of Staff Strategy** → `04-strategy-cos.md` (returns department actions array)
- **Department SACCADE** → each specialist's own `01-saccade.md`
- **Never** reuse marketing-brand prompts for other departments or Chief of Staff

### 2. Chief of Staff Flow
```
1. frame_problem() → SACCADE (Chief of Staff prompt) → Problem object
2. decompose_goal() → EVIDENCE → INTERPRETATION → STRATEGY (COS prompt) → actions[]
3. For each action: run department's SACCADE with their specialist
4. Build execution order (topological sort by dependencies)
5. Execute in parallel batches
6. Synthesize results
```

### 3. Real LLM Integration
- `_call_real_llm()` in `call_model()` checks `KOJIKI_LLM_API_KEY`, `KOJIKI_LLM_BASE_URL`, `KOJIKI_LLM_MODEL`
- Supports any OpenAI-compatible API (Groq, OpenRouter, Together, etc.)
- Falls back to structured stubs when no key configured
- Skip real LLM for department SACCADE (returns arrays, need Problem objects)

## Procedure

### Step 1: Create Chief of Staff Prompts
```bash
# Chief of Staff SACCADE prompt (generic problem framing)
cat > kojiki/specialists/marketing-brand/prompts/01-saccade-cos.md

# Chief of Staff Strategy prompt (department decomposition)
cat > kojiki/specialists/marketing-brand/prompts/04-strategy-cos.md
```

### Step 2: Wire Chief of Staff to Use Its Prompts
```python
# In chief_of_staff.py frame_problem():
specialist = load_specialist("marketing-brand")
specialist.stages["saccade"].prompt = PATH_TO_01_SACCAD_COS

# In chief_of_staff.py decompose_goal():
specialist = load_specialist("marketing-brand")
specialist.stages["strategy"].prompt = PATH_TO_04_STRATEGY_COS
specialist.stages["strategy"].schema = None  # Different output format
```

### Step 3: Skip Hardcoded Stubs for COS Strategy
```python
# In call_model() _call_real_llm():
if context.get("dept_head") == "ChiefOfStaff" or "cos-decomp" in task_id:
    pass  # Fall through to real LLM
```

### Step 4: Pass Dispatch Context to Strategy Stage
```python
# In stages/strategy.py:
stage_context = context.get_allowed_context(allowed_keys)
stage_context.update(dispatch)  # Pass dept_head, task_id
```

### Step 5: Department SACCADEs Use Their Own Specialists
```python
for sg in sub_goals:
    dept_specialist = load_specialist(available_departments[dept_name])
    dept_specialist.stages["saccade"].prompt = PATH_TO_01_SACCAD_COS
    dept_runner = PipelineRunner(dept_specialist, dept_dispatch)
    # Run SACCADE only
```

### Step 6: Parallel Batch Execution
```python
execution_order = topological_sort(sub_goals, key=lambda sg: sg.dependencies)
for batch in execution_order:
    run_parallel([run_subgoal(sg) for sg in batch])
```

## Pitfalls

- **Schema validation on SACCADE**: Expects `P-XXXXXXXX` but we use timestamps `P-YYYYMMDDHHMMSS`. Fix: relax schema or change ID format.
- **Strategy stage returns wrong format**: Marketing-brand strategy expects single decision object, COS needs `actions[]` array. Fix: disable schema validation for COS strategy, use COS-specific prompt.
- **Department SACCADE returns arrays**: Their prompts expect department decomposition output, not Problem objects. Fix: override their SACCADE prompt to use generic COS prompt.
- **LLM returns marketing hardcoded output**: Stub in `call_model()` matches "objective decision only". Fix: skip stub when `dept_head == "ChiefOfStaff"` or `cos-decomp` in task_id.
- **Groq 429/400 errors**: Rate limits and model compatibility. Not a code issue — wait or switch model.
- **Finance objective unrealistic**: $5M budget for bootstrap. Fix: $100K budget, 40% margin, 12mo breakeven.
- **Postgres imports broken after move**: Add `sys.path.insert(0, str(Path(__file__).parent.parent / "engine"))` before importing sentinel.
- **Runtime data in source tree**: Move `mycelium/mycelium/log` and `mycelium/mycelium/sentinel` to `var/`.
- **Delegation stage (5.5) must parse execution_plan from OUTPUT** — The DELEGATION stage runs after OUTPUT, discovers sub-agents from `specialists/<dept>/sub-agents/`, maps tasks via keyword matching, and executes in parallel with dependency resolution.
- **Handoff stage (5.7) executes cross-department handoffs** — Defined in specialist config.yaml. Payloads validated against schemas before spawning target specialists. Target specialists run full SYNAPSIS pipeline.
- **Mycelium stage (7.5) propagates signals through canopy** — Extracts failure signals from OUTCOME evaluations, signs with SENTINEL Ed25519, propagates via SignalPropagator with Decision Rights gating and edge reinforcement.
- **Circular import avoidance** — Import `PipelineRunner` locally inside stage functions, not at module top level, to avoid circular imports between `runner.py` and `stages/__init__.py`.

## Delegation Engine Pattern

1. **Discover sub-agents**: Scan `specialists/<dept>/sub-agents/` for directories with `__init__.py`
2. **Parse execution_plan** from OUTPUT stage: map tasks to sub-agents via keyword matching on task type/category/description
3. **Execute in parallel** with dependency resolution: topological sort on `depends_on` fields
4. **Aggregate results** into unified output for DECK/OUTCOME/LEARNING stages

```python
# In DelegationEngine:
sub_tasks = engine.parse_execution_plan(output_result)
results = await engine.execute_all(sub_tasks)  # Parallel with deps
aggregated = engine.aggregate_results()
```

## Handoff Execution Pattern

1. **Discover handoffs** from specialist config.yaml
2. **Validate payload** against schema from `payload_schema`
3. **Spawn target specialist** with handoff dispatch context
4. **Record in handoff history** for audit trail

```python
# In HandoffEngine:
for handoff in handoffs:
    result = engine.execute_handoff(handoff, source_output)
    history.append(result)
```

## Mycelium Signal Propagation Pattern

1. **Extract signals** from OUTCOME evaluations where target not met
2. **Sign with SENTINEL Ed25519** via KeyManager (loads from `~/.kojiki/sentinel/keys/`)
3. **Compute subgraph** via SignalPropagator (threshold 0.15, max 3 hops)
4. **Apply Decision Rights gating** — filter recipients by RACI rights
5. **Reinforce edges** with real flow signals (delivery_confirmed from signal kind)
6. **Log to SENTINEL-wrapped signals.jsonl** with provenance tokens

## Test Gates
```bash
# All specialists
python3 scripts/verify_all_runners.py

# Mycelium engine tests
python3 -m pytest 00-kojiki-ontology/mycelium/tests/ -v

# Governance loop
python3 -m pytest test_governance_loop.py -v

# Chief of Staff end-to-end
KOJIKI_LLM_API_KEY=... python3 -m kojiki.core.chief_of_staff "<goal>"
```

## References
- `references/prompt-separation.md` — why each role needs its own prompt
- `references/schema-validation.md` — handling schema mismatches between roles
- `references/llm-integration.md` — real LLM setup, fallback stubs, provider quirks
- `references/parallel-execution.md` — batch execution, dependency ordering, synthesis