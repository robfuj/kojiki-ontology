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

### Two-Tier Design (Thesis: `MYCELIAL-GOVERNANCE-COMPLETE-THESIS.md`)

| Tier | Purpose | Key Property |
|------|---------|--------------|
| **Root (Rigid)** | Single bot's internal pipeline | Enforced order, context isolation, `EVALUATION ≠ ORIGINATION` |
| **Canopy (Emergent)** | Cross-bot coordination | Redundant routing, reciprocal reinforcement, no central controller |

```
┌─────────────────────────────────────────────────────────────┐
│  MYCELIUM Canopy Tier (emergent coordination)               │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐        │
│  │Marketing│──│  Sales  │──│Finance  │──│Engineer │ 7      │
│  │  Head   │  │  Head   │  │  Head   │  │  Head   │ lines  │
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
│  SYNAPSIS Root Tier (per-bot rigid pipeline)                │
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

## 🏛️ The 7 Consolidated Departments

| Department | Scope |
|------------|-------|
| **Finance** | Budget, CAC, ROI, FP&A, treasury |
| **Marketing** | Brand, growth, referral, paid media |
| **Sales** | Outbound, growth, Biz Dev, Corp Dev |
| **Engineering** | Product, Customer Success, Technology, Referral tech |
| **Operations** | Supply chain, procurement, day-to-day ops |
| **Legal** | Compliance, Risk, contracts, regulatory |
| **People & Comms** | HR, Internal comms, Public Affairs |
| **Technology Platform** | AI, IT, Security, Data Analytics |

---

## 🚀 Quick Start

```bash
# Clone the decision systems
git clone <your-repo-url>
cd decision-systems

# Install the full package: ontology + 7 departments + meta agents
bash install-all.sh

# Or install a single department (clones ontology sibling if missing)
cd 03-marketing
bash bots/install_bots.py brand growth
```

### After Install

Each agent runs the **Kojiki Orientation Protocol** on first run:
1. **Name + function** — who am I?
2. **Industry / sector** — triggers research
3. **Jurisdiction** (country / region / regulatory)
4. **Geography + business model**
5. **Sibling registration** under parent `group_id` in `handoffs/registry.json`

Then the agent runs work through the SYNAPSIS chain and validates with:
```bash
python3 ../00-kojiki-ontology/synapsis/validate.py --mycelium-registry ../00-kojiki-ontology/handoffs/registry.json bot-output.json
```

---

## 📁 Repository Structure

```
decision-systems/
├── 00-kojiki-ontology/          # Shared brain (this is the core)
│   ├── synapsis/                # SYNAPSIS chain + validator
│   │   ├── SYNAPSIS.md          # Full specification
│   │   ├── validate.py          # Invariant checker (stdlib only)
│   │   ├── REFERENCES.md        # Consultant framework mappings
│   │   └── transformations.json # Stage definitions
│   ├── schemas/                 # Core JSON schemas (mirrored in bots)
│   │   ├── evidence.json
│   │   ├── interpretation.json
│   │   ├── strategy.json
│   │   ├── problem.json
│   │   ├── learning-ledger.json
│   │   └── decision-object.json
│   ├── mycelium/                # Canopy tier (emergent coordination)
│   │   ├── schemas/             # node, objective, key_result, edge, signal, provenance_token
│   │   ├── engine/              # registry, graph, reinforcement, propagate, prune, sentinel, saccade
│   │   ├── neuraxis/            # Vertical axis: experience, problem, gate_request, escalation
│   │   ├── tests/               # All passing
│   │   └── examples/            # demo_marketing_sales.py
│   ├── learning/                # Organizational memory (cases, patterns, rules)
│   ├── handoffs/                # Cross-department registry + handoff standard
│   ├── decision-rights/         # Own/Recommend/Consult/Approve/Execute/Escalate/Automate
│   ├── consultant/              # 50+ consulting frameworks (copied, MIT, design-time reference)
│   └── build_repos.py           # Generates the department repos
│
├── kojiki/                      # NEW: Unified runtime (slim orchestrator)
│   ├── core/                    # Shared execution engine
│   │   ├── runner.py            # Slim orchestrator (~500 lines)
│   │   ├── stages/              # 8 stage executors
│   │   └── registry.py          # Specialist auto-discovery
│   ├── specialists/             # Specialist configurations (consolidated to 7 depts)
│   │   ├── marketing-brand/
│   │   ├── marketing-growth/
│   │   ├── finance-accounting/
│   │   └── ... (7 consolidated departments)
│   ├── configs/                 # Dept Head + Chief of Staff configs
│   │   ├── dept-heads/
│   │   └── chief-of-staff.yaml
│   └── cli.py                   # Simple CLI: `kojiki decide "goal"`
│
├── scripts/                     # Verification & CI
│   ├── verify_all_runners.py
│   ├── verify_causal_signatures.py
│   └── test_runner_group.py
│
├── shared/                      # Shared resources (symlinked)
│   ├── prompts/                 # 8 stage prompts
│   └── schemas/                 # 11 JSON schemas
│
├── test_governance_loop.py      # End-to-end governance test
├── install-all.sh               # Installs ontology + 7 depts + meta
├── README.md
├── README.ja.md
├── README.zh.md
└── LICENSE
```

---

## 🏛️ The 7 Layers

| Layer | Answers | Scope |
|-------|---------|-------|
| **KOJIKI** | What exists — the ontology | Entities, relationships, the 7 consolidated departments |
| **SACCADE** | Is the question well-posed, before anything is tried | A priori, bounded iterative framing (converges or hits a pass cap) |
| **SYNAPSIS** | How one bounded decision gets made | Per-bot, rigid, auditable — Evidence ≠ Interpretation ≠ Strategy |
| **NEURAXIS** | How far up the abstraction ladder a failure needs to go to be explained | A posteriori, escalates only on real divergence, governed at L3/L4 |
| **MYCELIUM** | How many decisions, across many departments, stay coordinated | Emergent OKR-dependency graph, subgraph-scoped signals, never a directive |
| **SENTINEL** | Who actually said that | Signed, hash-chained, non-fungible provenance for every cross-node claim |

---

## ⚙️ Core Engines

### SYNAPSIS Transformation Chain (Rigid Tier)

| Stage | Authority | Must NOT Become | Input | Output Schema |
|-------|-----------|-----------------|-------|---------------|
| **RECORD** | What happened | — | Raw input | `decision-object.json` |
| **SACCADE** | What is the actual question? | EVIDENCE, STRATEGY | `raw_record` | `problem.json` (P-0000) |
| **EVIDENCE** | What does the source establish? | INTERPRETATION, STRATEGY | `raw_source`, `prior_accepted_evidence` | `evidence.json` (Verified Extracts) |
| **INTERPRETATION** | What does evidence mean? | EVIDENCE, STRATEGY | `accepted_evidence` | `interpretation.json` |
| **STRATEGY** | What should we do and when? | EVIDENCE, INTERPRETATION | `accepted_interpretation` | `strategy.json` |
| **OUTPUT** | How do we execute? | EVIDENCE, INTERPRETATION, STRATEGY | `accepted_strategy` | `output.json` |
| **OUTCOME** | What actually happened? | — | Reality | `decision-object.json` (update) |
| **LEARNING** | Extract pattern | — | Outcome vs expectation | `learning.json` |

**Invariants enforced by `kojiki/core/runner.py`:**
- `inputs_forbidden` are *not supplied* to the model call — stronger than "please don't"
- Each stage is a separate model call with scoped context
- `validate.py` checks output against schema + invariant rules

### MYCELIUM Canopy Tier (Emergent)

| Primitive | Schema | Key Rule |
|-----------|--------|----------|
| **Node** | `node.schema.json` | `id = parent + "." + local` (lineage-enforced) |
| **Objective** | `objective.schema.json` | Flexible horizon (not forced quarterly) |
| **Key Result** | `key_result.schema.json` | `status` + `confidence` + `depends_on[]` |
| **Edge** | `edge.schema.json` | Cross-Functional Handoff fields; weight reinforced by reciprocity |
| **Signal** | `signal.schema.json` | Requires `diagnosed_cause` + 14-category taxonomy; subgraph-bounded |

**Operating Cycle** (per edge, per review):
```
KR status change → Signal (cause + category) → Subgraph (threshold 0.15) 
→ Propagate (not a directive) → Reinforce/Decay/Prune → next cycle
```

**Reinforcement** (Tero et al. 2010, discrete):
```
weight = weight * (1 - decay) + rate * (flow_signal ** gamma)
# gamma=1.15 default; lower = more redundant/fault-tolerant
```

**Pruning** (parasitism guard):
```
prune if weight < 0.05 OR reciprocity < 0.2
# reciprocity = reciprocal_exchanges / (reciprocal + one_directional)
```

### NEURAXIS (Vertical Axis)

| Layer | Scope | Autonomy |
|-------|-------|----------|
| **L0** Execution | Retry with corrected input | Autonomous |
| **L1** Reasoning | Revise inference | Autonomous |
| **L2** Problem Representation | Supersede Problem object | Autonomous |
| **L3** Ontology | Revise ontology relations | **Governance gate required** |
| **L4** Meta-Strategy | Revise selection mechanism | **Governance gate required** |

Governance gate: repetition threshold (N distinct experiences), Decision Rights (Recommend/Consult/Approve), SLA with fail-closed default.

### SENTINEL (Provenance)

| Property | Implementation |
|----------|----------------|
| **Signing** | Ed25519, private key held by node runtime only |
| **Non-fungibility** | `entry_id = hash(payload_hash + signer + prev_entry_id)` |
| **Chain** | Per-log (`signals.jsonl`, `edges_history.jsonl`, `gate_evidence.jsonl`) |
| **Verification** | Before commit + before governance gate counts evidence |

### Kaizen Loop (Continuous Improvement)

| Capability | Implementation |
|------------|----------------|
| **Problem detection** | Outcome check with guardrails (completeness, variance, confidence calibration) |
| **Root cause** | PDCA cycle with 14-category error taxonomy |
| **Reclassification** | Auto-escalates L0→L4 based on failure type |
| **Governance integration** | L3/L4 changes require gate approval |
| **Redefinition capture** | Experiences include superseding Problem objects |
| **Learning ledger** | Versioned cases, patterns, rules — never silently overwritten |

### Chief of Staff (Coordinator)

| Capability | Implementation |
|------------|----------------|
| **Goal decomposition** | Pattern matching + LLM planning → specialist tasks |
| **Specialist discovery** | Registry auto-discovers `specialists/<dept>/<agent>/` |
| **Parallel execution** | Runs independent specialists simultaneously |
| **Dependency management** | Sales waits for Product spec; Finance waits for Eng estimate |
| **Conflict resolution** | Detect overlapping decision rights; escalate to governance |
| **Synthesis** | Merge into single plan with unified decision rights |

---

## 📚 Studies & References

The architecture is grounded in peer-reviewed research across four independent fields:

### Biology (Mycorrhizal Networks)
| Study | Finding | Architecture Mapping |
|-------|---------|---------------------|
| Tero et al., *Science* (2010) | Physarum reinforcement/decay converges on efficient, fault-tolerant topologies without central planner | MYCELIUM reinforcement formula (§IV.6.1), γ efficiency-redundancy tradeoff |
| Gorzelak et al., *AoB Plants* (2015) | Mainstream case for CMN-mediated plant communication | Signal propagation basis (§II.2, §IV.6.3) |
| Song et al., *PLoS ONE* (2010); Babikova et al. (2013) | Defense-signal propagation ("priming") | Scoped, subgraph-only Signal propagation |
| Karst, Jones & Hoeksema, *Nature Ecology & Evolution* (2023) | Skeptical review: citation bias toward positive-effect studies in CMN literature | Caution in §II.5 — build only on well-supported mechanics |
| Frew et al., *Functional Ecology* special issue (2025) | CMNs are heterogeneous, context/host/fungal-type dependent | Reinforces §II.5 caution |
| Silvestri et al. (2025), *New Phytologist* status report (2026) | New molecular regulatory mechanism (`ckRNAi`) discovered in AM symbiosis | §II.6 — cellular tier keeps proving more rigid |
| Bilgen & Akan, "Internet of Plants" (2024–2025, Cambridge/Koç) | Independent comms-engineering formalization: fungal network as "graph-based communication medium" | Validates `SIGNALING ≠ ORCHESTRATION` invariant (§IV.3, §II.7) |
| Adamatzky, *Royal Society Open Science* (2022) | Fungal electrical spikes show statistical structure resembling rudimentary code | Flagged as speculative (§II.4), not load-bearing |

### Neuroscience (Hierarchical Predictive Coding)
| Study | Finding | Architecture Mapping |
|-------|---------|---------------------|
| Rao & Ballard (1999) | Hierarchical predictive coding: predictions down, residual errors up; error climbs until absorbed | NEURAXIS escalation ladder (§VII.5.2) — exact computational structure |
| Spinal cord → brainstem → cortex reflex arc | Fast local responses; ambiguous stimuli escalate; cortical inhibition modulates reflexes | NEURAXIS L0–L4 layers with governance gate at L3 |

### Immunology (Innate/Adaptive Boundary)
| Study | Finding | Architecture Mapping |
|-------|---------|---------------------|
| Innate immunity (TLRs, fixed) → Adaptive immunity (antibodies, memory) | Adaptive supplements innate with learned layer; never rewrites innate recognition machinery | NEURAXIS governance gate: L0–L2 autonomous, L3–L4 require external validation (§VII.5.2, §VII.5.5) |

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

## 🔧 Consulting Frameworks (Design-Time Reference)

The SYNAPSIS stages map to standard consulting frameworks — not as runtime dependencies, but as **named methods** for closing specific gaps:

| Framework | Mapped Mechanism | Section |
|-----------|------------------|---------|
| **5 Whys / Fishbone** | Adversarial Audit root-cause | §III.1 |
| **MECE / Issue Tree** | EVIDENCE decomposition, INTERPRETATION non-overlap | §III.1, III.2 |
| **Pyramid Principle / SCQ** | PRODUCTION answer-first output | §III.1 (OUTPUT) |
| **Case frameworks** | Domain-specific STRATEGY templates | §III.1 (STRATEGY) |
| **RACI** | Decision Rights Model | §VII.5.5.1, §III.2 |
| **Balanced Scorecard** | Hermes KPI Architecture | §III.2 |
| **PDCA** | MYCELIUM operating cycle | §IV.7 |
| **Sensitivity Analysis** | γ / decay_rate / threshold calibration | *Open item* |

Full mapping: `synapsis/REFERENCES.md`  
Frameworks copied from: `consultant/` (50+ frameworks, MIT, no `.git`)

---

## 🛣️ Roadmap

| Phase | Focus | Status |
|-------|-------|--------|
| **v1** | Rigid tier (SYNAPSIS) + Canopy tier (MYCELIUM) + NEURAXIS + SENTINEL | ✅ Complete |
| **v2** | Deterministic grading for Task 3, CI with py_compile, pass/fail thresholds, schema versioning, expanded demo matrix | 📋 Planned |
| **v3** | Adversarial re-derivation of stage outputs, retrofitting all 18 depts, artifact cross-check | 📋 Planned |

See `MYCELIAL-GOVERNANCE-COMPLETE-THESIS.md` for full thesis.

---

## 🤝 Contributing

1. **No closed-source dependencies** — all code MIT
2. **Local-first** — runs on qwen2.5:14b (M1 Max 32GB), no cloud required
3. **Provider-agnostic** — point any LLM at `AGENT.md`
4. **Tests required** — `python3 -m py_compile` + validator pass before PR
5. **Design-time references only** — `consultant/` is a copy, not a dependency

---

## 📄 License

MIT — see [LICENSE](LICENSE).

---

## 🔗 Links

- **Thesis**: `MYCELIAL-GOVERNANCE-COMPLETE-THESIS.md` (two-tier architecture, biology, governance)
- **Reference mappings**: `synapsis/REFERENCES.md`
- **Consulting frameworks**: `consultant/` (50+ frameworks, slash-commands)
- **Demo**: `mycelium/examples/demo_marketing_sales.py`

---

**Kojiki Decision System. No decision left unaudited.**