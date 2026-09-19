# Kojiki Decision System

**A local-first, open-source framework that turns any LLM into a decision-centric organization.**

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://python.org)
[![Tests Passing](https://img.shields.io/badge/Tests-All%20Passing-brightgreen.svg)](#testing)

---

## 🌐 Language / 言語 / 语言

[**English**](README.md) • [**日本語**](README.ja.md) • [**中文**](README.zh.md)

---

## 🎯 What is this?

Kojiki gives any LLM (Claude, GPT, local models, agent harnesses) a **shared, auditable decision structure** — not just chat. Every department agent reasons through the same **SYNAPSIS transformation chain**:

```
RECORD → SACCADE → EVIDENCE → INTERPRETATION → STRATEGY → OUTPUT → OUTCOME → LEARNING
```

Each stage is a **bounded transformation** with explicit authority and an explicit "what it must NOT silently become" (evidence ≠ interpretation ≠ belief ≠ doctrine). A **Brain** orchestrates; an independent **Adversarial Audit** challenges. Cross-department coordination happens through the **MYCELIUM canopy tier** — a decentralized, need-driven substrate modeled on mycorrhizal networks.

> **The present is the cheap part.** The moment you try to trace *why* a decision was made — what evidence supported it, what assumptions failed, what the governance gate required — the structure pays for itself.

---

## 🏗️ Architecture Overview

### Two-Tier Design

| Tier | Purpose | Key Property |
|------|---------|--------------|
| **Root (Rigid)** | Single specialist's internal pipeline | Enforced order, context isolation, `EVALUATION ≠ ORIGINATION` |
| **Canopy (Emergent)** | Cross-specialist coordination | Redundant routing, reciprocal reinforcement, no central controller |

```
┌─────────────────────────────────────────────────────────────┐
│  MYCELIUM Canopy Tier (emergent coordination)               │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐        │
│  │Marketing│──│  Sales  │──│Finance  │──│Engineer │  8     │
│  │  Head   │  │  Head   │  │  Head   │  │  Head   │ lines  │
│  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘        │
│       │            │            │            │              │
│       ▼            ▼            ▼            ▼              │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐        │
│  │Operations│  │ Legal   │  │People & │  │Tech Plat│        │
│  │  Head   │  │  Head   │  │ Comms   │  │  Head   │        │
│  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘        │
│       │            │            │            │              │
│       ▼            ▼            ▼            ▼              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Signal Bus (propagate.py)  │  Reinforcement (Tero)   │   │
│  │  Pruning (reciprocity)      │  Centrality (computed)  │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  SYNAPSIS Root Tier (per-specialist rigid pipeline)         │
│  RECORD → SACCADE → EVIDENCE → INTERPRETATION → STRATEGY    │
│       → OUTPUT → OUTCOME → LEARNING                          │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐        │
│  │Runner.py│  │Schema   │  │Adversary│  │Brain    │        │
│  │context  │  │validate │  │Audit    │  │adjudicate│        │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘        │
└─────────────────────────────────────────────────────────────┘
```

### Three Vertical Axes

| Axis | Component | Purpose |
|------|-----------|---------|
| **Horizontal** | MYCELIUM | Cross-department coordination (OKR substrate) |
| **Vertical** | NEURAXIS | Recursive problem redefinition (L0–L4 escalation) |
| **A Priori** | SACCADE | Problem framing before evidence gathering |

### Provenance Layer (SENTINEL)

Every signal, edge change, and gate evidence is wrapped in a **non-fungible, hash-chained, Ed25519-signed provenance token** — so the governance gate's "N distinct experiences" bar counts *verified* corroboration, not fabricated claims.

---

## 🏛️ The 8 Consolidated Departments

| Department | Scope |
|------------|-------|
| **Finance** | Budget, CAC, ROI, FP&A, treasury |
| **Marketing** | Brand, growth, referral, paid media |
| **Sales** | Outbound, growth, Biz Dev, Corp Dev |
| **Engineering** | Product, Customer Success, Technology, Referral tech |
| **Operations** | Supply chain, procurement, day-to-day ops |
| **Legal** | Compliance, Risk, contracts, regulatory |
| **People & Comms** | HR, Internal comms, Public Affairs |
| **Technology Platform** | AI strategy, models, governance, InfoSec, identity, tools |

---

## 🚀 Quick Start

```bash
# Clone the decision systems
git clone <your-repo-url>
cd decision-systems

# Install dependencies
pip install -r requirements.txt

# Run a specialist
python -m engine.kojiki_core.runner marketing-brand dispatch.json

# Run all 8 specialists
python scripts/verify_all_runners.py
```

---

## 📁 Repository Structure (Simplified)

```
decision-systems/
├── engine/                          # All engine modules by division of task
│   ├── kojiki_core/                 # Core SYNAPSIS pipeline
│   │   ├── types.py                 # Unified type definitions (single source of truth)
│   │   ├── utils/__init__.py        # Consolidated helpers (load_prompt, validate_schema, etc.)
│   │   ├── stages/                  # 8 stage executors
│   │   │   ├── base.py              # StageExecutor base class
│   │   │   ├── saccade.py
│   │   │   ├── evidence.py
│   │   │   ├── interpretation.py
│   │   │   ├── strategy.py
│   │   │   ├── output.py
│   │   │   ├── delegation.py
│   │   │   ├── handoff.py
│   │   │   ├── mycelium.py
│   │   │   ├── outcome.py
│   │   │   └── learning.py
│   │   ├── runner.py                # Slim orchestrator (~180 lines)
│   │   └── skills/                  # Shared tools (github, specialist autodiscovery)
│   ├── mycelium/                    # Horizontal signal propagation
│   │   ├── registry.py              # JSON file-based node registry + SENTINEL key lifecycle
│   │   ├── postgres_registry.py     # PostgreSQL sync target (optional)
│   │   ├── postgres_persistence.py  # PostgreSQL connection pooling
│   │   ├── propagate.py             # Signal propagation across subgraph-bounded edges
│   │   ├── reinforcement.py         # Tero-style discrete reinforcement/decay
│   │   ├── governance_handler.py    # L3/L4 governance gates
│   │   ├── measurement_adapter.py   # Adapter registry for real BI/analytics
│   │   ├── saccade.py               # SACCADE: a priori problem framing
│   │   └── decision_rights.py       # Decision Rights gating
│   ├── neuraxis/                    # Vertical escalation engine (L0–L4)
│   │   └── escalation.py            # NEURAXIS: recursive problem redefinition
│   ├── kaizen/                      # Learning loop
│   │   ├── kaizen_loop.py           # PDCA continuous improvement
│   │   └── kaizen_compression.py    # Context compression for Kaizen learning
│   ├── sentinel/                    # Provenance: Ed25519, hash-chained logs
│   │   └── sentinel.py
│   └── synapsis/                    # Causal chains, schemas, validation
│       ├── causal_chain.py
│       ├── schema_validator.py
│       ├── evidence_compression.py
│       ├── validate.py
│       └── schemas/                 # Core JSON schemas
├── tests/
│   ├── engine/                      # Tests organized by engine component
│   │   └── mycelium/                # 42 passing tests
│   ├── fixtures/
│   │   └── test_stubs.py            # Test stubs (only loaded in test mode)
│   ├── results/
│   └── unit/
├── scripts/                         # Verification & CI
│   ├── verify_all_runners.py        # Verifies all 9 specialists pass
│   └── verify_causal_signatures.py
├── skills/                          # Agent skills (agency-agents, github-autodiscovery, etc.)
├── bots/                            # Reference bots
├── vendor/                          # External references (consultant frameworks)
├── var/                             # Runtime data (gitignored)
├── test_governance_loop.py          # End-to-end governance test
├── requirements.txt
├── .github/workflows/ci.yml
├── README.md / .ja.md / .zh.md
└── LICENSE
```

---

## 🔄 How a Prompt Flows Through the System

### 1. Entry Point: Dispatch Creation

```python
dispatch = {
    "task_id": "verify-marketing-brand",
    "raw_record": "Test goal for verification",
    "raw_source": {},
    "prior_accepted_evidence": []
}
```

The dispatch is the immutable input contract. It contains the raw goal, any source data, and prior evidence.

### 2. Pipeline Initialization (`engine/kojiki_core/runner.py`)

```python
specialist = load_specialist("marketing-brand")
runner = PipelineRunner(specialist, dispatch)
```

The `PipelineRunner`:
- Loads the specialist configuration (stages, schemas, tools, validators)
- Creates a `ScopedContext` for context isolation
- Initializes the `CausalChainRunner` for SENTINEL provenance
- Loads registry for Decision Rights

### 3. Stage Execution Loop

The runner executes stages in strict order:

```python
STAGE_EXECUTORS = [
    ("saccade", run_saccade_stage),
    ("evidence", run_evidence_stage),
    ("interpretation", run_interpretation_stage),
    ("strategy", run_strategy_stage),
    ("output", run_output_stage),
    ("delegation", run_delegation_stage),
    ("handoff", run_handoff_stage),
    ("mycelium", run_mycelium_stage),
    ("outcome", run_outcome_stage),
    ("learning", run_learning_stage),
]
```

**Each stage execution follows this pattern:**

1. **Get StageConfig** from specialist (prompt, tools, schema, allowed inputs)
2. **Build scoped context** — only `inputs_allowed` keys from dispatch + prior stage outputs
3. **Load prompt** from file
4. **Call model** via `call_model()` (test stubs in test mode, real LLM in production)
5. **Validate output** against JSON schema
6. **Store in context** for downstream stages
7. **Record in causal chain** for SENTINEL provenance

### 4. Stage-by-Stage Breakdown

#### STAGE 1: SACCADE (A Priori Problem Framing)
- **Input**: `raw_record` + context
- **Prompt**: `prompts/01-saccade.md` (Pyramid/SCQ/MECE framing)
- **Schema**: `schemas/saccade_problem.json` (P-XXXXXXXX format)
- **Output**: Structured Problem with `problem_id`, `goal`, `constraints`, `assumptions`, `unknowns`
- **Authority**: Must NOT become EVIDENCE or STRATEGY

#### STAGE 2: EVIDENCE (Source Retrieval)
- **Input**: Problem + department context
- **Tools**: CRMQuery, SEOAudit, CompetitorIntel, GitHub autodiscovery
- **Schema**: `schemas/evidence_findings.json`
- **Output**: Findings with `finding_id`, `question`, `answer`, `source`, `confidence`, `sufficiency`
- **Authority**: Must NOT become INTERPRETATION or STRATEGY

#### STAGE 3: INTERPRETATION (Evidence Synthesis)
- **Input**: Evidence findings
- **Prompt**: `prompts/03-interpretation.md`
- **Schema**: `schemas/interpretation.json`
- **Output**: `interpretation_id`, `synthesis`, `key_insights`, `evidence_refs`, `department_requirements`
- **Authority**: Must NOT become EVIDENCE or STRATEGY

#### STAGE 4: STRATEGY (Decision Plan)
- **Input**: Problem + Evidence + Interpretation
- **Prompt**: `prompts/04-strategy.md`
- **Schema**: `schemas/strategy.json`
- **Output**: `strategy_id`, `objective`, `rationale`, `success_criteria`, `decision_rights`, `escalation_conditions`
- **Authority**: Must NOT become EVIDENCE or INTERPRETATION

#### STAGE 5: OUTPUT (Execution Plan)
- **Input**: Strategy
- **Prompt**: `prompts/05-output.md`
- **Schema**: `schemas/output.json`
- **Output**: `output_id`, `actions[]`, `execution_plan{ tasks[] }`
- **Authority**: Must NOT become EVIDENCE/INTERPRETATION/STRATEGY

#### STAGE 5.5: DELEGATION (Sub-specialist Spawning)
- Parses `execution_plan.tasks[]` from OUTPUT
- Maps tasks to sub-agents via config.yaml
- Executes sub-agents in parallel
- Aggregates results

#### STAGE 5.7: HANDOFF (Cross-department)
- Discovers handoffs defined in specialist config
- Validates payload against schema
- Executes target department's SACCADE

#### STAGE 7.5: MYCELIUM (Signal Propagation)
- Extracts signals from OUTCOME evaluations
- Propagates through MYCELIUM canopy tier
- Reinforces/decays/prunes edges based on reciprocity

#### STAGE 7: OUTCOME (Kaizen Loop PDCA)
- Runs Kaizen Loop (Plan-Do-Check-Act)
- Compares actuals vs success_criteria from STRATEGY
- Guardrails: completeness, variance, trend, confidence_calibration
- Output: `outcome_id`, `outcome_score`, `target_met`, `converged`, `guardrail_violations`

#### STAGE 8: LEARNING (Kaizen Synthesis)
- Extracts experiences from failed outcomes
- Synthesizes patterns across experiences
- Generates reusable insights
- Identifies problem redefinitions for SACCADE feedback
- Output: `learning_id`, `experiences[]`, `patterns[]`, `redefinitions[]`

### 5. Final Adjudication

```python
adjudicated = {
    "problem": runner.context.stage_outputs.get("saccade"),
    "evidence": runner.context.stage_outputs.get("evidence"),
    "interpretation": runner.context.stage_outputs.get("interpretation"),
    "strategy": runner.context.stage_outputs.get("strategy"),
    "output": runner.context.stage_outputs.get("output"),
    "outcome": runner.context.stage_outputs.get("outcome"),
    "learning": runner.context.stage_outputs.get("learning"),
    "adjudication": "ACCEPTED",
    "adjudicator": "Marketing.Brain",
    "timestamp": datetime.utcnow().isoformat() + "Z"
}
```

### 6. Causal Chain Finalization

- Saves signed causal chain to `specialists/<name>/causal_chains/`
- Persists to PostgreSQL if registry available

---

## 🧪 Testing

```bash
# Verify all 9 specialists (test mode)
KOJIKI_TEST_MODE=true python scripts/verify_all_runners.py

# Run mycelium tests (42 tests)
PYTHONPATH=. python -m pytest tests/engine/mycelium/ -v

# Run governance loop test
python -m pytest test_governance_loop.py -v
```

**All tests pass:**
- ✅ 9/9 specialists pass verification
- ✅ 42/42 mycelium tests pass
- ✅ Governance loop test passes

---\n\n## 🔬 Research Foundations\n\nThe architecture is grounded in peer-reviewed research across four independent fields:\n\n### Biology (Mycorrhizal Networks)\n\n| Study | Finding | Architecture Mapping |\n|-------|---------|---------------------|\n| Tero et al., *Science* (2010) | Physarum reinforcement/decay converges on efficient, fault-tolerant topologies without central planner | MYCELIUM reinforcement formula, γ efficiency-redundancy tradeoff |\n| Gorzelak et al., *AoB Plants* (2015) | Mainstream case for CMN-mediated plant communication | Signal propagation basis |\n| Song et al., *PLoS ONE* (2010); Babikova et al. (2013) | Defense-signal propagation (\"priming\") | Scoped, subgraph-only Signal propagation |\n| Karst et al., *Nature Ecology & Evolution* (2023) | Skeptical review: citation bias toward positive-effect studies | Caution in §II.5 — build only on well-supported mechanics |\n| Frew et al., *Functional Ecology* (2025) | CMNs are heterogeneous, context/host/fungal-type dependent | Reinforces §II.5 caution |\n| Bilgen & Akan, \"Internet of Plants\" (2024–2025) | Independent comms-engineering formalization: fungal network as \"graph-based communication medium\" | Validates `SIGNALING ≠ ORCHESTRATION` invariant |\n\n### Neuroscience (Hierarchical Predictive Coding)\n\n| Study | Finding | Architecture Mapping |\n|-------|---------|---------------------|\n| Rao & Ballard (1999) | Hierarchical predictive coding: predictions down, residual errors up; error climbs until absorbed | NEURAXIS escalation ladder — exact computational structure |\n| Spinal cord → brainstem → cortex reflex arc | Fast local responses; ambiguous stimuli escalate; cortical inhibition modulates reflexes | NEURAXIS L0–L4 layers with governance gate at L3 |\n\n### Immunology (Innate/Adaptive Boundary)\n\n| Study | Finding | Architecture Mapping |\n|-------|---------|---------------------|\n| Innate immunity (TLRs, fixed) → Adaptive immunity (antibodies, memory) | Adaptive supplements innate with learned layer; never rewrites innate recognition machinery | NEURAXIS governance gate: L0–L2 autonomous, L3–L4 require external validation |\n\n### RL-for-LLM Research\n\n| Study | Finding | Architecture Mapping |\n|-------|---------|---------------------|\n| Sparse trajectory-level reward → Process-level credit assignment | Per-step credit assignment produces better learning with less data | SYNAPSIS per-stage decomposition with `diagnosed_cause_category` from Learning Taxonomy |\n\n### Enterprise Multi-Agent Reference Architectures\n\n| Source | Finding | Architecture Mapping |\n|--------|---------|---------------------|\n| Microsoft multi-agent reference architecture (real deployments) | Registry → Orchestrator → Knowledge/State → Async replay-aware communication | Same component separation arrived at independently |\n\n### Recursive Self-Improvement Taxonomy\n\n| Study | Finding | Architecture Mapping |\n|-------|---------|---------------------|\n| Bounded (L3) vs Unbounded (L4/L5) self-improvement | Bounded: improvement mechanism externally maintained | `LEARNING ≠ PERMISSION TO REWRITE DOCTRINE` invariant keeps system at L3 |\n\n---\n\n## 🤖 Orchestrator\n\nThe **Orchestrator** (replacing Chief of Staff) provides transparent goal decomposition:\n\n```bash\n# Run orchestration with user approval gate\npython -m engine.orchestrator.orchestrator \"Create a beef broth brand for Canadian market\"\n\n# Run without approval gate (for automation)\npython -m engine.orchestrator.orchestrator \"Goal here\" --no-approval\n```\n\n**Flow:**\n1. **Orientation Protocol** — industry research on the goal\n2. **SACCADE Framing** — sharpen raw goal into structured Problem\n3. **Department Selection** — which dept heads own this, with reasoning\n4. **OKR Decomposition** — corporate OKR → dept OKRs → team OKRs\n5. **Parallel Dispatch** — each dept head runs full SYNAPSIS pipeline\n6. **Mycelium Coordination** — cross-dept signals\n6. **User Approval Gate** — review before re-loop\n\n---\n\n## 📄 License

MIT — see [LICENSE](LICENSE).

---

## 🔗 Links

- **Thesis**: `MYCELIAL-GOVERNANCE-COMPLETE-THESIS.md` (two-tier architecture, biology, governance)
- **Reference mappings**: `engine/synapsis/REFERENCES.md`
- **Consulting frameworks**: `vendor/consultant/` (50+ frameworks)

---

**Kojiki Decision System. No decision left unaudited.**