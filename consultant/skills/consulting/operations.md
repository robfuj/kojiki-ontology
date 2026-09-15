# Operations & Process Improvement Frameworks

Frameworks for analyzing processes, identifying inefficiencies, and driving operational excellence.

## Process Mapping

**Purpose**: Visualize workflows to understand and improve processes.

### Types of Process Maps

| Type | Purpose | Detail Level |
|------|---------|--------------|
| High-Level (SIPOC) | Overview of process boundaries | Low |
| Flowchart | Standard process steps | Medium |
| Swimlane | Cross-functional handoffs | Medium |
| Value Stream Map | Lean analysis with timing | High |

### SIPOC Diagram

**S**uppliers → **I**nputs → **P**rocess → **O**utputs → **C**ustomers

```
┌──────────┬──────────┬──────────────────┬──────────┬──────────┐
│ SUPPLIERS│  INPUTS  │     PROCESS      │ OUTPUTS  │CUSTOMERS │
├──────────┼──────────┼──────────────────┼──────────┼──────────┤
│          │          │  ┌───┐   ┌───┐   │          │          │
│ Vendor A │ Material │  │ 1 │──▶│ 2 │   │ Product  │ Customer │
│          │          │  └───┘   └───┘   │          │          │
│ Dept. B  │ Data     │    │       │     │ Report   │ Manager  │
│          │          │    ▼       ▼     │          │          │
│          │          │  ┌───┐   ┌───┐   │          │          │
│          │          │  │ 3 │──▶│ 4 │   │          │          │
│          │          │  └───┘   └───┘   │          │          │
└──────────┴──────────┴──────────────────┴──────────┴──────────┘
```

### Flowchart Symbols

| Symbol | Meaning |
|--------|---------|
| ⬭ (Oval) | Start / End |
| ▭ (Rectangle) | Process Step |
| ◇ (Diamond) | Decision |
| ▱ (Parallelogram) | Input / Output |
| → (Arrow) | Flow Direction |

### Swimlane Diagram

```
┌─────────────────────────────────────────────────────────────┐
│ CUSTOMER    │ Request ──▶ Receive ────────────────▶ Pay     │
├─────────────┼───────────────────────────────────────────────┤
│ SALES       │    │                  ▲                       │
│             │    ▼                  │                       │
│             │ Review ──▶ Quote ─────┘                       │
├─────────────┼───────────────────────────────────────────────┤
│ OPERATIONS  │              │                                │
│             │              ▼                                │
│             │         Fulfill ──▶ Ship                      │
└─────────────┴───────────────────────────────────────────────┘
```

### Value Stream Map Elements

| Element | Symbol | Measures |
|---------|--------|----------|
| Process | Box | Cycle time, changeover time |
| Inventory | Triangle | Units, days of supply |
| Information Flow | Dashed arrow | Electronic vs manual |
| Material Flow | Solid arrow | Push vs pull |
| Timeline | Zigzag line | Value-add vs wait time |

---

## Root Cause Analysis

**Purpose**: Identify the underlying causes of problems, not just symptoms.

### 5 Whys

Repeatedly ask "Why?" to drill down to the root cause.

**Example**:

| Level | Question | Answer |
|-------|----------|--------|
| Problem | Customer complaints increased | - |
| Why 1? | Why increased? | Delivery times got longer |
| Why 2? | Why longer? | Shipping department understaffed |
| Why 3? | Why understaffed? | Two people quit last month |
| Why 4? | Why quit? | Better pay at competitor |
| Why 5? | Why not matched? | No market salary review in 2 years |

**Root Cause**: Outdated compensation practices
**Solution**: Implement annual market salary reviews

### 5 Whys Best Practices

1. Focus on process, not people (avoid blame)
2. Base answers on facts, not assumptions
3. May need more or fewer than 5 whys
4. Often multiple root causes - branch out
5. Verify the chain - does fixing root cause fix problem?

### Fishbone (Ishikawa) Diagram

**Purpose**: Categorize potential causes systematically.

```
                                    ┌─────────────────┐
         ┌──────────────────────────│    PROBLEM      │
         │                          └─────────────────┘
         │                                   │
    ─────┼─────────────────────────────────────────────
    Man  │  Machine        Method  │  Material
         │     │              │    │     │
    ┌────┴───┐ │          ┌───┴──┐ │ ┌───┴───┐
    │Cause 1 │ │          │Cause4│ │ │Cause 6│
    └────────┘ │          └──────┘ │ └───────┘
           ┌───┴───┐           ┌───┴──┐
           │Cause 2│           │Cause5│
           └───────┘           └──────┘
        ┌───────┐
        │Cause 3│
        └───────┘
```

### 6M Categories (Manufacturing)

| Category | Examples |
|----------|----------|
| **M**an (People) | Training, skills, fatigue, communication |
| **M**achine | Equipment, tools, technology |
| **M**ethod | Procedures, processes, standards |
| **M**aterial | Raw materials, supplies, data |
| **M**easurement | Metrics, inspection, calibration |
| **M**other Nature (Environment) | Temperature, humidity, lighting |

### 8P Categories (Service)

| Category | Examples |
|----------|----------|
| **P**roduct/Service | Design, features, quality |
| **P**rice | Pricing strategy, value perception |
| **P**lace | Location, accessibility, distribution |
| **P**romotion | Marketing, communication |
| **P**eople | Staff, customers, partners |
| **P**rocess | Procedures, workflows |
| **P**hysical Evidence | Facilities, equipment, materials |
| **P**roductivity | Efficiency, capacity, throughput |

---

## Lean Principles

**Origin**: Toyota Production System

**Purpose**: Eliminate waste and maximize customer value.

### The 8 Wastes (DOWNTIME)

| Waste | Description | Examples |
|-------|-------------|----------|
| **D**efects | Rework, scrap, errors | Product returns, corrections |
| **O**verproduction | Making more than needed | Excess inventory, unused reports |
| **W**aiting | Idle time | Approvals, information, equipment |
| **N**on-utilized Talent | Underused skills | Micromanagement, wrong role |
| **T**ransportation | Unnecessary movement of things | Moving materials, data transfers |
| **I**nventory | Excess stock | Work in progress, email backlog |
| **M**otion | Unnecessary movement of people | Walking, searching, reaching |
| **E**xtra Processing | Work beyond requirements | Over-engineering, redundant steps |

### Lean Tools

| Tool | Purpose |
|------|---------|
| **5S** | Workplace organization |
| **Kanban** | Visual workflow management |
| **Kaizen** | Continuous improvement |
| **Poka-Yoke** | Error-proofing |
| **Value Stream Mapping** | Process visualization |
| **Takt Time** | Pace production to demand |

### 5S Methodology

| Step | Japanese | English | Action |
|------|----------|---------|--------|
| 1 | Seiri | Sort | Remove unnecessary items |
| 2 | Seiton | Set in Order | Organize remaining items |
| 3 | Seiso | Shine | Clean the workspace |
| 4 | Seiketsu | Standardize | Create standards for above |
| 5 | Shitsuke | Sustain | Maintain discipline |

---

## Six Sigma

**Origin**: Motorola, 1980s

**Purpose**: Reduce variation and defects using statistical methods.

### DMAIC Framework

| Phase | Purpose | Key Activities |
|-------|---------|----------------|
| **D**efine | Define the problem | Project charter, SIPOC, Voice of Customer |
| **M**easure | Measure current performance | Data collection, baseline metrics |
| **A**nalyze | Analyze root causes | Statistical analysis, root cause tools |
| **I**mprove | Improve the process | Solution development, pilot testing |
| **C**ontrol | Control and sustain | Control charts, documentation |

### Sigma Levels

| Sigma Level | Defects per Million | Yield |
|-------------|--------------------:|------:|
| 1σ | 691,462 | 30.9% |
| 2σ | 308,538 | 69.1% |
| 3σ | 66,807 | 93.3% |
| 4σ | 6,210 | 99.4% |
| 5σ | 233 | 99.98% |
| 6σ | 3.4 | 99.9997% |

### Key Six Sigma Metrics

| Metric | Formula | Purpose |
|--------|---------|---------|
| **DPU** | Defects / Units | Defects per unit |
| **DPMO** | (Defects / Opportunities) × 1,000,000 | Defects per million |
| **Yield** | (Good Units / Total Units) × 100% | Process success rate |
| **Cp/Cpk** | Process capability indices | Process stability |

---

## Pareto Analysis (80/20 Rule)

**Purpose**: Focus on the vital few causes that create most impact.

### Pareto Principle

**80% of effects come from 20% of causes**

Examples:
- 80% of revenue from 20% of customers
- 80% of defects from 20% of causes
- 80% of complaints from 20% of issues

### Pareto Chart

```
Defect Count                              Cumulative %
    │                                           100%
100 │ ████                                 ──────●
    │ ████                           ──────●
 80 │ ████ ████                 ────●
    │ ████ ████           ────●     ─────────────80%
 60 │ ████ ████ ████ ────●
    │ ████ ████ ████●
 40 │ ████ ████ ████ ████
    │ ████ ████ ████ ████ ████
 20 │ ████ ████ ████ ████ ████ ████
    │ ████ ████ ████ ████ ████ ████ ████
    └─────────────────────────────────────────────
      Cat A Cat B Cat C Cat D Cat E Cat F Cat G
```

### How to Create

1. List all categories/causes
2. Count occurrences or impact for each
3. Sort descending by count
4. Calculate cumulative percentage
5. Draw bar chart (counts) and line (cumulative %)
6. Identify the 20% causing 80% of issues

---

## Continuous Improvement Cycle (PDCA)

**Origin**: W. Edwards Deming

**Purpose**: Iterative improvement through experimentation.

### The PDCA Cycle

```
         ┌─────────────┐
         │    PLAN     │
         │  - Identify │
         │  - Analyze  │
         │  - Plan     │
         └──────┬──────┘
                │
    ┌───────────┴───────────┐
    │                       │
    ▼                       ▼
┌───────┐             ┌───────┐
│  ACT  │◄────────────│  DO   │
│       │             │       │
│Adopt  │             │Test   │
│Adjust │             │Pilot  │
│Abandon│             │Execute│
└───┬───┘             └───┬───┘
    │                     │
    └──────────┬──────────┘
               │
        ┌──────┴──────┐
        │    CHECK    │
        │  - Measure  │
        │  - Compare  │
        │  - Learn    │
        └─────────────┘
```

### Phase Details

| Phase | Questions | Activities |
|-------|-----------|------------|
| **Plan** | What are we trying to accomplish? | Define problem, analyze causes, plan change |
| **Do** | How do we test the change? | Implement on small scale, document observations |
| **Check** | Did it work? | Measure results, compare to baseline |
| **Act** | What's next? | Adopt, adapt, or abandon the change |

---

## Key Metrics Dashboard

### Operational Metrics

| Metric | Formula | Target |
|--------|---------|--------|
| **OEE** | Availability × Performance × Quality | >85% |
| **Throughput** | Units produced / Time | Varies |
| **Cycle Time** | End time - Start time | Minimize |
| **Lead Time** | Delivery time - Order time | Minimize |
| **Utilization** | Actual output / Capacity | 80-90% |
| **First Pass Yield** | Good units / Total units | >95% |

### Process Capability

| Metric | Meaning | Good Value |
|--------|---------|------------|
| **Cp** | Potential capability (centered) | >1.33 |
| **Cpk** | Actual capability (may be off-center) | >1.33 |
| **Pp/Ppk** | Long-term performance | >1.33 |
