#!/usr/bin/env python3
"""
Research-Informed Orientation Protocol
======================================

Flow:
1. CLARIFYING QUESTIONS (adaptive, 2-4) → make goal specific enough for targeted research
2. RESEARCH PHASE (live web: market, competitors, regulation, risks)
3. RESEARCH BRIEF + CONTEXTUAL FOLLOW-UPS (generated FROM research)
4. USER ANSWERS
5. OPTIONAL: TARGETED RE-RESEARCH (if answers reveal new gaps) + MORE FOLLOW-UPS
6. BUILD PROJECT

Registry bootstrap: Orchestrator registers 8 root depts + head nodes on init.
Orchestrator ownership: Orchestrator node is registered; ownership is tracked via registry.
"""

import asyncio
import json
import os
import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from engine.kojiki_core.utils import get_llm_config, is_test_mode, call_model
from engine.sentinel import SentinelEngine


# ============================================================================
# Core Types
# ============================================================================

class ResearchPhase(Enum):
    CLARIFYING = "clarifying"           # Initial questions to make goal specific
    RESEARCH = "research"               # Live web research
    FOLLOW_UPS = "follow_ups"           # Research-informed follow-ups
    RE_RESEARCH = "re_research"         # Targeted re-research
    RE_FOLLOW_UPS = "re_follow_ups"     # Re-research follow-ups
    COMPLETE = "complete"


@dataclass
class ClarifyingQuestion:
    """A clarifying question asked before research."""
    id: str
    prompt: str
    why: str
    category: str  # scope, constraints, stakeholders, success, context
    required: bool = True


@dataclass
class ResearchBrief:
    """Structured research output from live web search."""
    market_scan: str
    competitive_landscape: str
    regulatory_considerations: str
    key_risks: List[str]
    sources: List[str]
    methodology: str
    timestamp: str


@dataclass
class FollowUpQuestion:
    """A research-informed follow-up question."""
    id: str
    prompt: str
    why: str
    research_basis: str  # Which research finding prompted this
    category: str


@dataclass
class OrientationTurn:
    """A single Q&A turn in any phase."""
    phase: ResearchPhase
    question_id: str
    question: str
    user_response: str
    think_aloud: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OrientationResult:
    """Final result of the orientation protocol."""
    raw_goal: str
    refined_goal: str
    clarifying_questions: List[ClarifyingQuestion]
    clarifying_answers: List[OrientationTurn]
    research_brief: ResearchBrief
    follow_up_questions: List[FollowUpQuestion]
    follow_up_answers: List[OrientationTurn]
    re_research_brief: Optional[ResearchBrief]
    re_follow_up_answers: List[OrientationTurn]
    confidence: float
    timestamp: str


# ============================================================================
# Clarifying Question Bank (Adaptive - only ask what's needed)
# ============================================================================

CLARIFYING_QUESTION_BANK = [
    ClarifyingQuestion(
        id="c_goal_meaning",
        prompt="You said: '{raw_goal}'. What specifically does that involve? Give a concrete example.",
        why="Users use shorthand; need shared vocabulary before research",
        category="scope",
        required=True,
    ),
    ClarifyingQuestion(
        id="c_goal_trigger",
        prompt="What happened recently that made this a priority now?",
        why="Trigger events reveal urgency and context",
        category="context",
        required=False,
    ),
    ClarifyingQuestion(
        id="c_success_criteria",
        prompt="Six months from now, what specific metrics or outcomes mean 'this succeeded'?",
        why="Maps abstract goals to observable criteria for research",
        category="success",
        required=True,
    ),
    ClarifyingQuestion(
        id="c_constraints",
        prompt="What's absolutely non-negotiable? (Hard budget cap? Regulatory deadline? Team capacity?)",
        why="Hard constraints shape research scope; soft preferences don't",
        category="constraints",
        required=True,
    ),
    ClarifyingQuestion(
        id="c_stakeholders",
        prompt="Who else cares about this outcome? Who must sign off? Who might push back?",
        why="Reveals hidden decision-makers and political constraints",
        category="stakeholders",
        required=True,
    ),
    ClarifyingQuestion(
        id="c_boundaries",
        prompt="What's explicitly OUT of scope? What would make you say 'that's a different project'?",
        why="Boundary conditions prevent scope creep in research",
        category="scope",
        required=False,
    ),
    ClarifyingQuestion(
        id="c_decision_context",
        prompt="Is this a one-time decision or ongoing capability? Will you repeat this analysis?",
        why="Determines research depth and tooling needs",
        category="context",
        required=False,
    ),
    ClarifyingQuestion(
        id="c_existing_data",
        prompt="What data or reports do you already have? (CRM, analytics, financials, customer feedback?)",
        why="Identifies research starting points and gaps",
        category="context",
        required=False,
    ),
]


# ============================================================================
# Orientation Protocol Runner
# ============================================================================

class OrientationProtocol:
    """
    Research-Informed Orientation Protocol with adaptive phases.
    """

    def __init__(self, max_clarifying: int = 4, max_follow_ups: int = 4):
        self.max_clarifying = max_clarifying
        self.max_follow_ups = max_follow_ups
        self.sentinel = SentinelEngine()

    async def run(self, raw_goal: str, context: Optional[Dict[str, Any]] = None) -> OrientationResult:
        """Run the full orientation protocol."""

        print(f"\n{'='*60}")
        print(f"ORIENTATION PROTOCOL STARTED")
        print(f"Goal: {raw_goal}")
        print(f"{'='*60}")

        # Phase 1: Clarifying Questions (adaptive)
        clarifying_questions, clarifying_answers = await self._run_clarifying_phase(raw_goal, context)

        # Phase 2: Research
        research_brief = await self._run_research_phase(raw_goal, clarifying_answers)

        # Phase 3: Follow-up Questions (generated from research)
        follow_up_questions, follow_up_answers = await self._run_follow_up_phase(raw_goal, research_brief, clarifying_answers)

        # Phase 4: Optional re-research
        re_research_brief, re_follow_up_answers = await self._run_re_research_phase(
            raw_goal, research_brief, follow_up_answers
        )

        # Synthesize refined goal
        refined_goal = await self._synthesize_refined_goal(
            raw_goal, clarifying_answers, research_brief, follow_up_answers
        )

        # Build result
        result = OrientationResult(
            raw_goal=raw_goal,
            refined_goal=refined_goal,
            clarifying_questions=clarifying_questions,
            clarifying_answers=clarifying_answers,
            research_brief=research_brief,
            follow_up_questions=follow_up_questions,
            follow_up_answers=follow_up_answers,
            re_research_brief=re_research_brief,
            re_follow_up_answers=re_follow_up_answers,
            confidence=0.85,
            timestamp=datetime.utcnow().isoformat() + "Z"
        )

        # Sign in SENTINEL
        self._sign_orientation(result)

        print(f"\n{'='*60}")
        print(f"ORIENTATION COMPLETE")
        print(f"Refined Goal: {refined_goal}")
        print(f"Phases: Clarifying → Research → Follow-ups → {'Re-research' if re_research_brief else 'Complete'}")
        print(f"{'='*60}")

        return result

    # ========================================================================
    # Phase 1: Clarifying Questions (Adaptive)
    # ========================================================================

    async def _run_clarifying_phase(
        self, 
        raw_goal: str, 
        context: Optional[Dict[str, Any]]
    ) -> Tuple[List[ClarifyingQuestion], List[OrientationTurn]]:
        """Run adaptive clarifying questions to make goal specific enough for research."""

        print(f"\n{'='*60}")
        print(f"PHASE 1: CLARIFYING QUESTIONS")
        print(f"{'='*60}")

        clarifying_questions = self._select_clarifying_questions(raw_goal, context)
        answers = []

        for q in clarifying_questions[:self.max_clarifying]:
            print(f"\n  📋 Clarifying {q.id}: {q.prompt.format(raw_goal=raw_goal)}")
            
            user_response = await self._get_user_response(q, raw_goal, context)
            think_aloud = await self._get_think_aloud(q, user_response) if not is_test_mode() else None
            
            turn = OrientationTurn(
                phase=ResearchPhase.CLARIFYING,
                question_id=q.id,
                question=q.prompt.format(raw_goal=raw_goal),
                user_response=user_response,
                think_aloud=think_aloud,
                metadata={"category": q.category, "required": q.required}
            )
            answers.append(turn)

        return clarifying_questions, answers

    def _select_clarifying_questions(
        self, 
        raw_goal: str, 
        context: Optional[Dict[str, Any]]
    ) -> List[ClarifyingQuestion]:
        """Select clarifying questions adaptively based on what's already known."""
        
        known = set()
        if context:
            if context.get("success_criteria"): known.add("success")
            if context.get("constraints"): known.add("constraints")
            if context.get("stakeholders"): known.add("stakeholders")
            if context.get("scope_boundaries"): known.add("scope")
            if context.get("trigger"): known.add("context")
            if context.get("existing_data"): known.add("context")
        
        selected = []
        for q in CLARIFYING_QUESTION_BANK:
            if q.required or q.category not in known:
                selected.append(q)
        
        return selected

    # ========================================================================
    # Phase 2: Research
    # ========================================================================

    async def _run_research_phase(
        self, 
        raw_goal: str, 
        clarifying_answers: List[OrientationTurn]
    ) -> ResearchBrief:
        """Run live web research based on clarified goal."""

        print(f"\n{'='*60}")
        print(f"PHASE 2: LIVE WEB RESEARCH")
        print(f"{'='*60}")

        research_context = self._build_research_context(raw_goal, clarifying_answers)
        print(f"  🔍 Researching: market, competitors, regulation, risks...")

        if is_test_mode():
            return self._mock_research_brief(raw_goal)

        research_prompt = f"""Research the field for this goal using live web search.

RAW GOAL: {raw_goal}

CLARIFIED CONTEXT:
{research_context}

Search for and synthesize current information on FOUR areas. Return JSON with:
1. market_scan: Market size, growth direction, forces moving it, key players
2. competitive_landscape: Who competes, how positioned, where gaps are
3. regulatory_considerations: Compliance exposure, naming regimes that apply
4. key_risks: Top 3-5 risks most likely to derail this goal
5. sources: URLs cited inline as [n] and listed at end

Be specific and current; prefer named companies, figures, regulations over generalities.
If web search unavailable, reason from knowledge and leave sources empty."""

        try:
            response = call_model(
                prompt=research_prompt,
                context={},
                tools=[],
                schema={},
                stage_name="orientation_research"
            )
            
            if isinstance(response, dict) and "error" not in response:
                json_match = re.search(r'\{.*\}', str(response), re.DOTALL)
                if json_match:
                    data = json.loads(json_match.group())
                    return ResearchBrief(
                        market_scan=data.get("market_scan", ""),
                        competitive_landscape=data.get("competitive_landscape", ""),
                        regulatory_considerations=data.get("regulatory_considerations", ""),
                        key_risks=data.get("key_risks", []),
                        sources=data.get("sources", []),
                        methodology="web-search" if data.get("sources") else "model-reasoning",
                        timestamp=datetime.utcnow().isoformat() + "Z"
                    )
        except Exception as e:
            print(f"  [Research error: {e}]")

        return self._mock_research_brief(raw_goal)

    def _build_research_context(self, raw_goal: str, clarifying_answers: List[OrientationTurn]) -> str:
        lines = [f"Goal: {raw_goal}"]
        for turn in clarifying_answers:
            meta = turn.metadata.get("category", "")
            lines.append(f"[{meta.upper()}] Q: {turn.question}")
            lines.append(f"  A: {turn.user_response[:200]}")
        return "\n".join(lines)

    def _mock_research_brief(self, raw_goal: str) -> ResearchBrief:
        return ResearchBrief(
            market_scan=f"Market research for: {raw_goal}",
            competitive_landscape="Competitive landscape analysis",
            regulatory_considerations="Regulatory landscape review",
            key_risks=["Market risk", "Technical risk", "Regulatory risk"],
            sources=[],
            methodology="model-reasoning",
            timestamp=datetime.utcnow().isoformat() + "Z"
        )

    # ========================================================================
    # Phase 3: Follow-up Questions (Generated from Research)
    # ========================================================================

    async def _run_follow_up_phase(
        self,
        raw_goal: str,
        research_brief: ResearchBrief,
        clarifying_answers: List[OrientationTurn]
    ) -> Tuple[List[FollowUpQuestion], List[OrientationTurn]]:
        """Generate and ask follow-up questions based on research findings."""

        print(f"\n{'='*60}")
        print(f"PHASE 3: RESEARCH-INFORMED FOLLOW-UPS")
        print(f"{'='*60}")

        follow_ups = await self._generate_follow_ups(raw_goal, research_brief)
        
        print(f"\n  📋 Research complete. Generated {len(follow_ups)} follow-up questions.")
        print(f"\n  Here is what I found. Read this before answering.")
        print(f"  Where it is wrong or stale, say so in the questions that follow —")
        print(f"  the plan is built from both.\n")
        self._print_research_brief(research_brief)

        answers = []
        for i, q in enumerate(follow_ups[:self.max_follow_ups]):
            print(f"\n  ❓ Question {i+1} of {len(follow_ups)}")
            print(f"     {q.prompt}")
            print(f"     [{q.research_basis}]")
            
            user_response = await self._get_user_response(q, raw_goal, None)
            think_aloud = await self._get_think_aloud(q, user_response) if not is_test_mode() else None
            
            turn = OrientationTurn(
                phase=ResearchPhase.FOLLOW_UPS,
                question_id=q.id,
                question=q.prompt,
                user_response=user_response,
                think_aloud=think_aloud,
                metadata={"research_basis": q.research_basis, "category": q.category}
            )
            answers.append(turn)

        return follow_ups, answers

    async def _generate_follow_ups(
        self, 
        raw_goal: str, 
        research_brief: ResearchBrief
    ) -> List[FollowUpQuestion]:
        """Generate contextual follow-up questions from research findings."""

        if is_test_mode():
            return [
                FollowUpQuestion("fu_1", "What is the launch-country sequence?", "Regulatory variance across markets", "regulation", "regulation"),
                FollowUpQuestion("fu_2", "Does the model need odds disclosure?", "EU Digital Fairness Act exposure", "compliance", "compliance"),
                FollowUpQuestion("fu_3", "What is the revenue threshold for FY27 success?", "Unit-economics threshold", "success", "success"),
            ]

        prompt = f"""Generate 3-4 specific follow-up questions based on this research.

RAW GOAL: {raw_goal}

RESEARCH FINDINGS:
Market: {research_brief.market_scan[:500]}
Competition: {research_brief.competitive_landscape[:500]}
Regulation: {research_brief.regulatory_considerations[:500]}
Risks: {research_brief.key_risks}

Generate questions that:
1. Are SPECIFIC to this goal (not generic)
2. Reference concrete research findings
3. Resolve ambiguities that would change the plan
4. Have clear "why" tied to research

Return JSON array of: {{"id": "", "prompt": "", "why": "", "research_basis": "", "category": ""}}"""

        try:
            response = call_model(
                prompt=prompt,
                context={},
                tools=[],
                schema={},
                stage_name="follow_up_generation"
            )
            
            if isinstance(response, dict) and "error" not in response:
                json_match = re.search(r'\[.*\]', str(response), re.DOTALL)
                if json_match:
                    data = json.loads(json_match.group())
                    return [FollowUpQuestion(**q) for q in data]
        except Exception as e:
            print(f"  [Follow-up generation error: {e}]")

        return [
            FollowUpQuestion("fu_1", "What is the launch-country sequence?", "Regulatory variance across markets", "regulation", "regulation"),
            FollowUpQuestion("fu_2", "Does the model need odds disclosure?", "EU Digital Fairness Act exposure", "compliance", "compliance"),
            FollowUpQuestion("fu_3", "What is the revenue threshold for FY27 success?", "Unit-economics threshold", "success", "success"),
        ]

    def _print_research_brief(self, brief: ResearchBrief):
        """Print research brief in the format from Vercel."""
        print(f"\n  {'─'*50}")
        print(f"  RESEARCH BRIEF")
        print(f"  {'─'*50}")
        print(f"\n  📊 MARKET SCAN:")
        print(f"     {brief.market_scan[:300]}...")
        print(f"\n  🏢 COMPETITIVE LANDSCAPE:")
        print(f"     {brief.competitive_landscape[:300]}...")
        print(f"\n  ⚖️  REGULATORY:")
        print(f"     {brief.regulatory_considerations[:300]}...")
        print(f"\n  ⚠️  KEY RISKS:")
        for r in brief.key_risks:
            print(f"     • {r}")
        if brief.sources:
            print(f"\n  📚 SOURCES:")
            for s in brief.sources[:5]:
                print(f"     • {s}")
        print(f"  {'─'*50}\n")

    # ========================================================================
    # Phase 4: Optional Re-Research
    # ========================================================================

    async def _run_re_research_phase(
        self,
        raw_goal: str,
        research_brief: ResearchBrief,
        follow_up_answers: List[OrientationTurn]
    ) -> Tuple[Optional[ResearchBrief], List[OrientationTurn]]:
        """Optional targeted re-research if follow-up answers reveal new gaps."""

        needs_re_research = self._check_re_research_needed(follow_up_answers)
        
        if not needs_re_research:
            return None, []

        print(f"\n{'='*60}")
        print(f"PHASE 4: TARGETED RE-RESEARCH")
        print(f"{'='*60}")

        re_context = self._build_re_research_context(raw_goal, follow_up_answers)

        if is_test_mode():
            return self._mock_research_brief(raw_goal), []

        re_prompt = f"""Targeted re-research based on follow-up answers.

ORIGINAL GOAL: {raw_goal}
FOLLOW-UP ANSWERS:
{re_context}

Research SPECIFICALLY the new gaps revealed. Return JSON with same structure as initial research."""

        try:
            response = call_model(
                prompt=re_prompt,
                context={},
                tools=[],
                schema={},
                stage_name="re_research"
            )
            
            if isinstance(response, dict) and "error" not in response:
                json_match = re.search(r'\{.*\}', str(response), re.DOTALL)
                if json_match:
                    data = json.loads(json_match.group())
                    re_brief = ResearchBrief(
                        market_scan=data.get("market_scan", ""),
                        competitive_landscape=data.get("competitive_landscape", ""),
                        regulatory_considerations=data.get("regulatory_considerations", ""),
                        key_risks=data.get("key_risks", []),
                        sources=data.get("sources", []),
                        methodology="targeted-re-research",
                        timestamp=datetime.utcnow().isoformat() + "Z"
                    )
                    
                    re_follow_ups = await self._generate_follow_ups(raw_goal, re_brief)
                    re_answers = []
                    for q in re_follow_ups[:2]:
                        response = await self._get_user_response(q, raw_goal, None)
                        think_aloud = await self._get_think_aloud(q, response) if not is_test_mode() else None
                        re_answers.append(OrientationTurn(
                            phase=ResearchPhase.RE_FOLLOW_UPS,
                            question_id=q.id,
                            question=q.prompt,
                            user_response=response,
                            think_aloud=think_aloud,
                            metadata={"research_basis": q.research_basis}
                        ))
                    return re_brief, re_answers
        except Exception as e:
            print(f"  [Re-research error: {e}]")

        return None, []

    def _check_re_research_needed(self, answers: List[OrientationTurn]) -> bool:
        trigger_keywords = ["new market", "different regulation", "budget changed", "timeline shifted", 
                           "stakeholder added", "scope expanded", "country", "jurisdiction"]
        for a in answers:
            if any(k in a.user_response.lower() for k in trigger_keywords):
                return True
        return False

    def _build_re_research_context(self, raw_goal: str, answers: List[OrientationTurn]) -> str:
        lines = [f"Original Goal: {raw_goal}"]
        for a in answers:
            lines.append(f"Q: {a.question}")
            lines.append(f"A: {a.user_response}")
        return "\n".join(lines)

    # ========================================================================
    # Goal Synthesis
    # ========================================================================

    async def _synthesize_refined_goal(
        self,
        raw_goal: str,
        clarifying_answers: List[OrientationTurn],
        research_brief: ResearchBrief,
        follow_up_answers: List[OrientationTurn]
    ) -> str:
        """Synthesize precise, actionable goal statement."""

        prompt = f"""Synthesize a precise, actionable goal statement.

RAW GOAL: {raw_goal}

CLARIFYING ANSWERS:
{json.dumps([{"q": a.question, "a": a.user_response[:200]} for a in clarifying_answers], indent=2)}

RESEARCH KEY FINDINGS:
- Market: {research_brief.market_scan[:200]}
- Competition: {research_brief.competitive_landscape[:200]}
- Regulation: {research_brief.regulatory_considerations[:200]}
- Risks: {research_brief.key_risks}

FOLLOW-UP ANSWERS:
{json.dumps([{"q": a.question, "a": a.user_response[:200]} for a in follow_up_answers], indent=2)}

Write a refined goal that is:
1. Specific and measurable
2. Includes constraints and success criteria
3. Identifies key stakeholders
4. Notes boundaries/out-of-scope
5. One paragraph, professional tone"""

        try:
            response = call_model(prompt=prompt, context={}, tools=[], stage_name="goal_synthesis")
            return str(response) if response else raw_goal
        except:
            return raw_goal

    # ========================================================================
    # Helpers
    # ========================================================================

    async def _get_user_response(self, question: Any, raw_goal: str, context: Optional[Dict]) -> str:
        """Get user response. In production, this comes from UI."""
        if is_test_mode():
            return f"Test response for {getattr(question, 'id', 'unknown')}"
        
        sim_prompt = f"""Simulate a realistic user responding to this question.

GOAL: {raw_goal}
QUESTION: {question.prompt if hasattr(question, 'prompt') else question}

Generate a realistic, specific response (2-4 sentences) with concrete details."""

        try:
            response = call_model(prompt=sim_prompt, context={}, tools=[], stage_name="orientation_simulation")
            if isinstance(response, dict):
                return response.get("response", "Simulated response")
            return str(response)
        except:
            return f"Simulated response for: {raw_goal}"

    async def _get_think_aloud(self, question: Any, user_response: str) -> Optional[str]:
        if is_test_mode():
            return None
        prompt = f'User answered: "{user_response}"\nQuestion: {question.prompt if hasattr(question, "prompt") else question}\n\nGenerate brief think-aloud (1-2 sentences).'
        try:
            response = call_model(prompt=prompt, context={}, tools=[], stage_name="think_aloud")
            return str(response) if response else None
        except:
            return None

    def _sign_orientation(self, result: OrientationResult):
        self.sentinel.write_signal(
            signer="registry",
            signal_id=f"ORIENT-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            signal={
                "raw_goal": result.raw_goal,
                "refined_goal": result.refined_goal,
                "confidence": result.confidence,
                "phases_completed": [
                    "clarifying",
                    "research",
                    "follow_ups",
                    "re_research" if result.re_research_brief else "none"
                ],
            }
        )
        print(f"  🔐 Signed in SENTINEL")


# ============================================================================
# API Function for Orchestrator Integration
# ============================================================================

async def run_orientation_protocol(
    raw_goal: str,
    context: Optional[Dict[str, Any]] = None,
    max_clarifying: int = 4,
    max_follow_ups: int = 4
) -> Dict[str, Any]:
    """
    Main entry point called by Orchestrator._run_orientation()
    """
    protocol = OrientationProtocol(max_clarifying=max_clarifying, max_follow_ups=max_follow_ups)
    result = await protocol.run(raw_goal, context)

    return {
        "goal": result.raw_goal,
        "refined_goal": result.refined_goal,
        "clarifying_questions": [
            {"id": a.question_id, "question": a.question, "response": a.user_response}
            for a in result.clarifying_answers
        ],
        "research_brief": {
            "market_scan": result.research_brief.market_scan,
            "competitive_landscape": result.research_brief.competitive_landscape,
            "regulatory_considerations": result.research_brief.regulatory_considerations,
            "key_risks": result.research_brief.key_risks,
            "sources": result.research_brief.sources,
            "methodology": result.research_brief.methodology,
        },
        "follow_up_questions": [
            {"id": a.question_id, "question": a.question, "response": a.user_response}
            for a in result.follow_up_answers
        ],
        "confidence": result.confidence,
        "methodology": "research_informed_orientation_v1",
        "timestamp": result.timestamp
    }


# ============================================================================
# CLI for Testing
# ============================================================================

async def main():
    import sys
    goal = sys.argv[1] if len(sys.argv) > 1 else "Launch a referral program to reduce CAC by 20%"
    print(f"Testing Orientation Protocol with goal: {goal}")
    result = await run_orientation_protocol(goal, max_clarifying=3, max_follow_ups=3)
    print(f"\n{'='*60}")
    print(f"RESULT:")
    print(f"  Refined Goal: {result['refined_goal']}")
    print(f"  Confidence: {result['confidence']:.1%}")
    print(f"{'='*60}")

if __name__ == "__main__":
    asyncio.run(main())