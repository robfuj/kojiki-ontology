# DECK Stage — Decision Communication Artifact

## Authority
**Given accepted OUTPUT (and OUTCOME/LEARNING if available), produce a stakeholder-ready communication artifact.**

You format the decision for consumption. You do not re-decide, re-interpret, or re-design the intervention.

## Must Not Become
- STRATEGY: You do not re-decide the objective
- OUTPUT: You do not redesign the intervention
- INTERPRETATION/EVIDENCE: You do not re-diagnose

## Inputs Allowed
- `accepted_output`: The intervention design from OUTPUT stage
- `accepted_outcome` (optional): Observed results if decision already executed
- `accepted_learning` (optional): Key lessons captured

## Inputs Forbidden
- `raw_source`: Never see raw transcripts
- `accepted_evidence`: Already consumed upstream
- `accepted_interpretation`: Already consumed upstream

## Tools Allowed
- Template rendering only (no external API calls)

## Design Principles (from consultant reference)
**These are enforced by the deck validator (`validate_deck.py`):**

| Framework | Application | Validation Rule |
|-----------|-------------|-----------------|
| **Pyramid Principle** | Lead with the answer (decision + impact), then group supporting arguments MECE | Slide 1 must have layout `answer_first`; all supporting slides must follow |
| **SCQ Framework** | Structure as: Situation → Complication → Question → Answer | Slides with layouts `context`/`problem`/`question`/`answer_first` must appear in that order |
| **MECE** | Group supporting points Mutually Exclusive, Collectively Exhaustive | `mece_grouped` slide: no duplicate points across groups; all groups non-empty |
| **Storyboarding** | Each slide = one clear message; slide titles tell the story alone | All slides must have unique, non-empty titles |

## Validation

Run: `python scripts/validate_deck.py <deck.json>`

The validator checks:
1. **Pyramid**: First slide layout == `answer_first`
2. **SCQ**: Layout sequence contains `context` → `problem` → `question` → `answer_first` in order
3. **MECE**: In `mece_grouped` slides, no point text appears in more than one group; all groups have ≥1 point
4. **Storyboarding**: All slide titles non-empty and unique
5. **Schema**: Validates against `schema/deck.json`

## Output Contract
Schema: `schema/deck.json`

```json
{
  "deck_id": "DECK-001",
  "output_ref": "OUT-001",
  "title": "Referral Program Launch — Decision & Plan",
  "audience": ["Marketing.Head", "Sales.Head", "Finance.CFO"],
  "slides": [
    {
      "slide_id": "S-001",
      "title": "Launch referral incentive program by Nov 1 to grow pipeline 15%",
      "layout": "answer_first",
      "content": {
        "answer": "Approve 3-touch email sequence + landing page + CRM automation",
        "impact": "+15% qualified pipeline, $2.3M attributed revenue",
        "owner": "Brand",
        "deadline": "2026-11-01"
      }
    },
    {
      "slide_id": "S-002",
      "title": "Situation: Referral channel flat at 3% of pipeline",
      "layout": "context",
      "content": {
        "metrics": ["3% pipeline from referrals", "0.8% conversion rate", "No automated workflow"]
      }
    },
    {
      "slide_id": "S-003",
      "title": "Complication: Manual process caps scale; competitors at 12%",
      "layout": "problem",
      "content": {
        "drivers": ["No incentive structure", "Manual CRM entry loses 40% leads", "Sales not prompted to ask"]
      }
    },
    {
      "slide_id": "S-004",
      "title": "Question: How to unlock referral channel at scale?",
      "layout": "question",
      "content": {}
    },
    {
      "slide_id": "S-005",
      "title": "Answer: 3-touch automated sequence + incentive + Sales enablement",
      "layout": "answer_first",
      "content": {
        "intervention": "Email sequence (D0/D3/D7) + landing page + CRM auto-enrollment",
        "incentive": "$50 per qualified referral",
        "enablement": "Sales battlecard + Slack reminder workflow"
      }
    },
    {
      "slide_id": "S-006",
      "title": "Supporting arguments (MECE)",
      "layout": "mece_grouped",
      "content": {
        "groups": [
          {
            "label": "Demand generation",
            "points": ["Incentive unlocks latent advocate base", "Automation removes friction"]
          },
          {
            "label": "Sales execution",
            "points": ["Battlecard equips reps", "Slack workflow ensures ask"]
          },
          {
            "label": "Measurement",
            "points": ["Weekly referral submissions", "Referral→opportunity conversion", "Attributed pipeline $"]
          }
        ]
      }
    },
    {
      "slide_id": "S-007",
      "title": "Dependencies & Risks",
      "layout": "dependencies",
      "content": {
        "dependencies": ["Marketing.Head budget approval", "Engineering referral API"],
        "risks": [
          {"risk": "Engineering API delay", "mitigation": "Staggered launch: email first, API week 2"},
          {"risk": "Low Sales adoption", "mitigation": "Leaderboard + weekly Slack nudge"}
        ]
      }
    },
    {
      "slide_id": "S-008",
      "title": "Next Steps & Decision Required",
      "layout": "decision",
      "content": {
        "ask": "Approve budget $15K + Engineering sprint allocation",
        "decision_deadline": "2026-10-15",
        "decision_maker": "Marketing.Head"
      }
    }
  ],
  "format": "markdown_slides",
  "generated_at": "2026-09-07T10:00:00Z"
}
```

## Cross-Department Deck (MYCELIUM-coordinated)
When multiple departments contribute to a joint decision, MYCELIUM propagates a `deck_request` signal. Each department runs its own DECK stage against its OUTPUT, then a designated lead merges slides.

**Trigger:** `deck_request` signal with `origin_kr` = decision KR, `subgraph` = contributing departments

**Merge protocol:**
1. Each department produces its department-scoped slides (using same schema)
2. Designated lead (typically the KR owner) merges, deduplicates, reorders
3. Final deck tagged with `deck_id` and all contributing `output_refs`

## Human Authorization Boundary
**Deck is a communication artifact only.** It does not authorize execution. The decision was authorized at STRATEGY/OUTPUT; DECK only communicates it.