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

# Run all 9 specialists (test mode)
KOJIKI_TEST_MODE=true python tests/scripts/verify_all_runners.py
```

---

## 🤖 Orchestrator

The **Orchestrator** (replacing Chief of Staff) provides transparent goal decomposition:

```bash
# Run orchestration with user approval gate
python -m engine.orchestrator.orchestrator "Create a beef broth brand for Canadian market"

# Run without approval gate (for automation)
python -m engine.orchestrator.orchestrator "Goal here" --no-approval
```

**Flow:**
1. **Orientation Protocol** — industry research on the goal
2. **SACCADE Framing** — sharpen raw goal into structured Problem
3. **Department Selection** — which dept heads own this, with reasoning
4. **OKR Decomposition** — corporate OKR → dept OKRs → team OKRs
5. **Parallel Dispatch** — each dept head runs full SYNAPSIS pipeline
6. **Mycelium Coordination** — cross-dept signals
7. **User Approval Gate** — review before re-loop

---

## 🤖 Sub-Agents by Department

| Department | Sub-Agents |
|------------|------------|
| Ai Intelligence | `agentic-identity`, `agents-orchestrator`, `ai-code-auditor`, `ai-engineer`, `ai-remediation`, `doc-generator`, `identity-graph`, `llm-post-training`, `mcp-builder`, `model-qa`, `multi-agent-architect`, `prompt-engineer`, `rag-pipeline`, `secrets-hygiene`, `strategy-duel`, `zk-steward` |
| Engineering Platform | `ai-engineer`, `api-engineer`, `appsec-engineer`, `backend-architect`, `code-reviewer`, `data-viz`, `database-optimizer`, `devops-automator`, `frontend-developer`, `llm-post-training`, `multi-agent-architect`, `platform-engineer`, `rag-engineer`, `reality-checker`, `security-architect`, `software-architect`, `sre`, `test-automation` |
| Finance Accounting | `accounts-payable`, `bookkeeper`, `cfo`, `esg-officer`, `financial-analyst`, `fp-a-analyst`, `grant-writer`, `investment-researcher`, `loan-officer`, `medical-billing`, `pricing-analyst`, `tax-strategist` |
| Legal Compliance | `compliance-auditor`, `data-privacy`, `esg-officer`, `fedramp`, `gov-presales`, `legal-billing`, `legal-client-intake`, `legal-doc-review` |
| Marketing Brand | `aeo-specialist`, `agentic-search-optimizer`, `brand-guardian`, `carousel-growth`, `content-creator`, `email-strategist`, `growth-hacker`, `paid-social-specialist`, `pr-communications`, `seo-specialist`, `video-optimizer`, `visual-storyteller` |
| Operations Ops | `business-strategist`, `change-management`, `ma-integration`, `operations-manager`, `supply-chain-strategist` |
| People Hr | `change-management`, `corporate-training`, `customer-service`, `customer-success`, `dev-advocate`, `hr-onboarding`, `org-psychologist`, `pr-comms`, `recruitment`, `support-responder` |
| Sales Outbound | `account-strategist`, `data-consolidation`, `deal-strategist`, `discovery-coach`, `lead-gen-strategist`, `outbound-strategist`, `pipeline-analyst`, `proposal-strategist`, `report-distribution`, `sales-coach`, `sales-data-extraction`, `sales-engineer`, `sales-outreach`, `salesforce-architect` |

**Total: 95 sub-agents across 8 departments**

---

## 🔍 Orientation Protocol — Research-Informed Goal Clarification

**Purpose:** Before any department selection or planning, the system runs an **adaptive, research-first orientation** that prevents wasted research on vague goals (e.g., "raise Q4 sales" → research adapts to "SaaS B2B pipeline acceleration").

### Flow

```
CLARIFYING QUESTIONS (2–4 adaptive) 
    → LIVE WEB RESEARCH (market, competitors, regulation, risks)
    → RESEARCH BRIEF + CONTEXTUAL FOLLOW-UPS (3–4 generated FROM findings)
    → USER ANSWERS
    → OPTIONAL: TARGETED RE-RESEARCH (if answers reveal gaps) + MORE FOLLOW-UPS
    → REFINED GOAL → DEPARTMENT SELECTION → OKR DECOMPOSITION
```

### Why Research-First?

- **Clarifying questions** make the goal specific enough for *targeted* research
- **Live research** grounds follow-ups in current reality (not stale templates)
- **Follow-ups generated FROM findings** — not a static question bank
- **Re-research loop** catches gaps opened by user answers

### Example (from Vercel flow)

```
Goal: "Launch gacha game"
Research finds: Belgium/Netherlands ban loot boxes; EU Digital Fairness Act pending
Follow-up Q1: "What is the launch-country sequence — soft-launch EU before UK/BE/NL?"
Follow-up Q2: "Does monetization need odds disclosure + spending controls for EU compliance?"
Follow-up Q3: "What revenue threshold defines FY27 launch success?"
```

### Research on Asking Good Questions (Open-Source Foundations)

| Source | Key Finding | Applied In |
|--------|-------------|------------|
| **Cognitive Interviewing Guide** (UCLA/Chime) | Open-ended, non-leading questions reduce recall bias; "What happened?" > "Did X happen?" | Clarifying phase: "What specifically does that involve?" |
| **Oxford Handbook of Survey Methodology** (2018) | Funnel sequence: broad → specific; avoid double-barreled questions | Phase 1 → Phase 3 narrowing |
| **Karpathy's LLM Wiki / Akinator-style entropy** | Adaptive question selection via information gain; stop when entropy < threshold | Dynamic question count (2–4) |
| **Deep Research pattern** (OpenAI/Perplexity) | Iterative: clarify → search → synthesize → follow-up → re-search | 3-phase orientation loop |
| **Police PEACE model / CI guidelines** | Context reinstatement before recall; free narrative before specific probes | "What happened recently that made this a priority?" |

---

## 🧠 MORPHEUS Protocol — Daily Memory Reset with SENTINEL Verification

**Purpose:** Prevents memory drift in long-running orchestrations by enforcing a daily **Hibernate → Hypnos → Morpheus → Awaken** cycle that cryptographically verifies no pending gates or active SLAs are lost.

| Phase | Action | SENTINEL Check |
|-------|--------|----------------|
| **Hibernate** | Snapshot working stores (experiences, kaizen, subgraph edges) | Hash written to chain |
| **Hypnos** | Seal snapshot — mark reset entry | Signed checkpoint |
| **Morpheus** | Wipe working stores; rematerialize gates with live SLA deadlines | Query real gate store (`escalation_engine.gate_requests`) |
| **Awaken** | Verify chain integrity; confirm pending gates restored | Fail-closed if hash mismatch |

**Key guarantees:**
- Any gate with a live SLA deadline survives the wipe (queried from real store, not stub)
- Chain verification is mandatory — orchestration cannot resume with broken provenance
- 7/7 acceptance criteria verified in test suite

---

## 🔄 How a Prompt Goes Through the System

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

| Stage | Purpose | Output | Authority |
|-------|---------|--------|-----------|
| **SACCADE** | A Priori Problem Framing | Structured Problem | Must NOT become EVIDENCE or STRATEGY |
| **EVIDENCE** | Source Retrieval | Findings with citations | Must NOT become INTERPRETATION or STRATEGY |
| **INTERPRETATION** | Evidence Synthesis | Diagnosis + insights | Must NOT become EVIDENCE or STRATEGY |
| **STRATEGY** | Decision Plan | Objective + decision rights | Must NOT become EVIDENCE or INTERPRETATION |
| **OUTPUT** | Intervention Design | Tactics + measurement | Must NOT become EVIDENCE/INTERPRETATION/STRATEGY |
| **DELEGATION** | Sub-Agent Dispatch | Task assignments | — |
| **HANDOFF** | Cross-Agent Coordination | Handoff tracking | — |
| **MYCELIUM** | Signal Propagation | Cross-dept signals | — |
| **OUTCOME** | Kaizen Evaluation | Score + convergence | — |
| **LEARNING** | Kaizen Synthesis | Patterns + redefinitions | — |

### Key Invariants

- `EVIDENCE ≠ INTERPRETATION ≠ STRATEGY` (no bleed)
- `LEARNING ≠ PERMISSION TO REWRITE DOCTRINE` (bounded L3)
- `SIGNALING ≠ ORCHESTRATION` (canopy autonomy)

---

## 📁 Repository Structure

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
├── mycelium_data/                   # Runtime data (renamed from mycelium/)
├── ui/                              # Next.js frontend
├── api_server.py                    # FastAPI backend
├── requirements.txt
└── README.md / .ja.md / .zh.md
```

---

## 🧪 Testing

```bash
# Verify all 9 specialists (test mode)
KOJIKI_TEST_MODE=true python tests/scripts/verify_all_runners.py

# Run mycelium tests (42 tests)
PYTHONPATH=. python -m pytest tests/engine/mycelium/ -v

# Run governance loop test
python -m pytest tests/integration/test_governance_loop.py -v
```

**All tests pass:**
- ✅ 9/9 specialists pass verification
- ✅ 42/42 mycelium tests pass
- ✅ Governance loop test passes

---

## 🔬 Research Foundations

The architecture is grounded in peer-reviewed research across six independent fields:

### Biology (Mycorrhizal Networks)

| Study | Finding | Architecture Mapping |
|-------|---------|---------------------|
| Tero et al., *Science* (2010) | Physarum reinforcement/decay converges on efficient, fault-tolerant topologies without central planner | MYCELIUM reinforcement formula, γ efficiency-redundancy tradeoff |
| Gorzelak et al., *AoB Plants* (2015) | Mainstream case for CMN-mediated plant communication | Signal propagation basis |
| Song et al., *PLoS ONE* (2010); Babikova et al. (2013) | Defense-signal propagation ("priming") | Scoped, subgraph-only Signal propagation |
| Karst et al., *Nature Ecology & Evolution* (2023) | Skeptical review: citation bias toward positive-effect studies | Caution in §II.5 — build only on well-supported mechanics |
| Frew et al., *Functional Ecology* (2025) | CMNs are heterogeneous, context/host/fungal-type dependent | Reinforces §II.5 caution |
| Bilgen & Akan, "Internet of Plants" (2024–2025) | Independent comms-engineering formalization: fungal network as "graph-based communication medium" | Validates `SIGNALING ≠ ORCHESTRATION` invariant |

### Neuroscience (Hierarchical Predictive Coding)

| Study | Finding | Architecture Mapping |
|-------|---------|---------------------|
| Rao & Ballard (1999) | Hierarchical predictive coding: predictions down, residual errors up; error climbs until absorbed | NEURAXIS escalation ladder — exact computational structure |
| Spinal cord → brainstem → cortex reflex arc | Fast local responses; ambiguous stimuli escalate; cortical inhibition modulates reflexes | NEURAXIS L0–L4 layers with governance gate at L3 |

### Immunology (Innate/Adaptive Boundary)

| Study | Finding | Architecture Mapping |
|-------|---------|---------------------|
| Innate immunity (TLRs, fixed) → Adaptive immunity (antibodies, memory) | Adaptive supplements innate; doesn't replace it; memory enables faster secondary response | SYNAPSIS root tier = innate (fixed pipeline); MYCELIUM canopy = adaptive (emergent coordination) |
| Janeway (1989) "Approaching the asymptote" | Innate recognition instructs adaptive; signal 2 (co-stimulation) required | MYCELIUM signals require both evidence (signal 1) and decision rights (signal 2) |
| Gause et al., *Nature* (2012) | Memory T cells persist decades; cross-reactive to novel pathogens | Kaizen learning: experiences compressed → reusable insights for novel problems |

### Decision Science (Dual-Process / Structured Analytic Techniques)

| Study | Finding | Architecture Mapping |
|-------|---------|---------------------|
| Kahneman & Klein (2009) "Conditions for intuitive expertise" | Expertise requires stable environment + rapid feedback + deliberate practice | Stage isolation prevents System 1 bleed: EVIDENCE ≠ INTERPRETATION ≠ STRATEGY |
| Heuer, *Psychology of Intelligence Analysis* (1999) | ACH (Analysis of Competing Hypotheses): matrix evidence × hypotheses prevents confirmation bias | INTERPRETATION stage requires `contradictions[]`, `alternative_diagnoses_considered[]` |
| Tetlock, *Superforecasting* (2015) | Fermi decomposition + base rates + belief updating beats experts | OKR decomposition → STRATEGY success_criteria → OUTCOME Bayesian update |
| Morgan et al., *Structured Decision Making* (2017) | Decision rights (OWN/CONSULT/INFORM) clarify accountability | DecisionRightsGate wired in MYCELIUM consultation |

### RL-for-LLM Research

| Study | Finding | Architecture Mapping |
|-------|---------|---------------------|
| Sparse trajectory-level reward → Process-level credit assignment | Per-step credit assignment produces better learning with less data | SYNAPSIS per-stage decomposition with `diagnosed_cause_category` from Learning Taxonomy |

### Enterprise Multi-Agent Reference Architectures

| Source | Finding | Architecture Mapping |
|--------|---------|---------------------|
| Microsoft multi-agent reference architecture (real deployments) | Registry → Orchestrator → Knowledge/State → Async replay-aware communication | Same component separation arrived at independently |

### Recursive Self-Improvement Taxonomy

| Study | Finding | Architecture Mapping |
|-------|---------|---------------------|
| Bounded (L3) vs Unbounded (L4/L5) self-improvement | Bounded: improvement mechanism externally maintained | `LEARNING ≠ PERMISSION TO REWRITE DOCTRINE` invariant keeps system at L3 |

---

## 📄 License

MIT — see [LICENSE](LICENSE).

---

## 🔗 Links

- **Thesis**: `MYCELIAL-GOVERNANCE-COMPLETE-THESIS.md` (two-tier architecture, biology, governance)
- **Reference mappings**: `engine/synapsis/REFERENCES.md`
- **Consulting frameworks**: `vendor/consultant/` (50+ frameworks)

---

## 🤖 Sub-Agents by Department

| Department | Sub-Agents |
|------------|------------|
| Ai Intelligence | `agentic-identity`, `agents-orchestrator`, `ai-code-auditor`, `ai-engineer`, `ai-remediation`, `doc-generator`, `identity-graph`, `llm-post-training`, `mcp-builder`, `model-qa`, `multi-agent-architect`, `prompt-engineer`, `rag-pipeline`, `secrets-hygiene`, `strategy-duel`, `zk-steward` |
| Engineering Platform | `ai-engineer`, `api-engineer`, `appsec-engineer`, `backend-architect`, `code-reviewer`, `data-viz`, `database-optimizer`, `devops-automator`, `frontend-developer`, `llm-post-training`, `multi-agent-architect`, `platform-engineer`, `rag-engineer`, `reality-checker`, `security-architect`, `software-architect`, `sre`, `test-automation` |
| Finance Accounting | `accounts-payable`, `bookkeeper`, `cfo`, `esg-officer`, `financial-analyst`, `fp-a-analyst`, `grant-writer`, `investment-researcher`, `loan-officer`, `medical-billing`, `pricing-analyst`, `tax-strategist` |
| Legal Compliance | `compliance-auditor`, `data-privacy`, `esg-officer`, `fedramp`, `gov-presales`, `legal-billing`, `legal-client-intake`, `legal-doc-review` |
| Marketing Brand | `aeo-specialist`, `agentic-search-optimizer`, `brand-guardian`, `carousel-growth`, `content-creator`, `email-strategist`, `growth-hacker`, `paid-social-specialist`, `pr-communications`, `seo-specialist`, `video-optimizer`, `visual-storyteller` |
| Operations Ops | `business-strategist`, `change-management`, `ma-integration`, `operations-manager`, `supply-chain-strategist` |
| People Hr | `change-management`, `corporate-training`, `customer-service`, `customer-success`, `dev-advocate`, `hr-onboarding`, `org-psychologist`, `pr-comms`, `recruitment`, `support-responder` |
| Sales Outbound | `account-strategist`, `data-consolidation`, `deal-strategist`, `discovery-coach`, `lead-gen-strategist`, `outbound-strategist`, `pipeline-analyst`, `proposal-strategist`, `report-distribution`, `sales-coach`, `sales-data-extraction`, `sales-engineer`, `sales-outreach`, `salesforce-architect` |

**Total: 95 sub-agents across 8 departments**

---

**Kojiki Decision System. No decision left unaudited.**