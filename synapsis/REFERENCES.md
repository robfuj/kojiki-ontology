# External framework reference (design-time only — not a runtime dependency)

Install for whoever is doing design/implementation work on this repo:
```
/plugin marketplace add yoichiojima-2/consultant
/plugin install consulting@consultant
```

No agent or pipeline calls this at runtime. It's a named-method reference
for closing specific gaps below — use the method, don't add the plugin
as a dependency.

## Mapped to SYNAPSIS stages directly (primary use)
- 5 Whys / Fishbone → the self-adversarial audit stage's root-cause method
  (§III.1: "assume my work contains a hidden failure — what would it most
  likely be?" currently has no named method behind it)
- MECE / Issue Tree → EVIDENCE's evidence-decomposition and INTERPRETATION's
  non-overlapping-interpretation discipline
- Pyramid Principle / SCQ / Storyboarding → PRODUCTION's answer-first,
  MECE-grouped output structure (currently unspecified)
- Case frameworks (Profitability, Pricing, Market Entry, M&A) → domain-specific
  STRATEGY templates for Sales/Finance-type bots (STRATEGY is currently
  "propose an objective" with no named reasoning pattern)

## Mapped to SACCADE / NEURAXIS / the governance gate (secondary use)
- MECE → SACCADE's check_completeness() (§III.4.3)
- 5 Whys / Fishbone → NEURAXIS error classification / escalation ladder
  (§VII.5.4-5.5) — third independent field (after biology, neuroscience)
  converging on the same escalation rule
- RACI → cross-check against §VII.5.5.1 Decision Rights
- SCQ → cross-check against the Problem object schema (§VII.5.3)
- Balanced Scorecard → cross-check against Hermes KPI Architecture (§III.2)
- PDCA → cross-check against the MYCELIUM operating cycle (§IV.7)
- Sensitivity Analysis → calibration method for gamma/decay_rate/
  SUBGRAPH_THRESHOLD (open item, hole #7)

No code changes yet. No schema changes yet. This file only prevents the
mapping from being lost before it's actually implemented.