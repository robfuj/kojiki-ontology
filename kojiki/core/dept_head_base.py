#!/usr/bin/env python3
"""
Department Head Base Specialist

Each department head:
1. Receives department-level objective from Chief of Staff
2. Runs SACCADE→EVIDENCE→INTERPRETATION→STRATEGY to decompose into team OKRs
3. Uses Mycelium for cross-team signals and edge reinforcement
4. Registers team OKRs with OKR Engine
"""

import json
import asyncio
import concurrent.futures
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

# Import from kojiki core
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from kojiki.core import (
    Specialist, ScopedContext, load_specialist, call_model, StageName
)
from kojiki.core.runner import PipelineRunner
from kojiki.core.stages import (
    run_saccade_stage,
    run_evidence_stage,
    run_interpretation_stage,
    run_strategy_stage
)

# Import Mycelium
mycelium_path = Path(__file__).parent.parent.parent / "mycelium" / "engine"
sys.path.insert(0, str(mycelium_path))
from propagate import SignalPropagator
from registry import NodeRegistry
from sentinel import SentinelEngine, KeyManager
from governance_handler import GovernanceHandler
from okr_engine import OKREngine, Objective, KeyResult, OKRLevel, OKRStatus, KRType
from conversation import MyceliumConversationLayer, ConversationType, SignalPriority, MyceliumSignal, SaccadeCacheEntry


@dataclass
class TeamOKR:
    """A team-level OKR created by a department head."""
    team: str
    objective_id: str
    title: str
    description: str
    key_results: List[Dict[str, Any]]
    dependencies: List[Dict[str, Any]]  # [{"target_team": "Engineering.Referral", "weight": 0.8}]
    parent_dept_objective: str


class DeptHeadBase:
    """Base class for department head specialists."""

    def __init__(
        self,
        dept_head_node: str,
        specialist_name: str,
        registry: NodeRegistry,
        propagator: SignalPropagator,
        sentinel: SentinelEngine,
        okr_engine: OKREngine,
        team_nodes: List[str],  # List of team node IDs under this dept head
        conversation_layer: Optional[MyceliumConversationLayer] = None
    ):
        self.dept_head_node = dept_head_node
        self.specialist_name = specialist_name
        self.registry = registry
        self.propagator = propagator
        self.sentinel = sentinel
        self.okr_engine = okr_engine
        self.team_nodes = team_nodes
        self.conversation_layer = conversation_layer

        # Capability manifest path
        self.manifest_path = Path(f"kojiki/specialists/{specialist_name}/dept_capability_manifest.json")
        self.manifest_path.parent.mkdir(parents=True, exist_ok=True)

    def decompose_objective(self, dept_objective: Objective) -> List[TeamOKR]:
        """
        Decompose department objective into team OKRs.

        Flow: SACCADE (frame problem) → EVIDENCE (gather team data)
              → INTERPRETATION (analyze gaps) → STRATEGY (propose team OKRs)
        """
        print(f"\n=== {self.dept_head_node} Decomposing Objective ===")
        print(f"Objective: {dept_objective.objective_id} - {dept_objective.title}")

        # Stage 1: SACCADE - Frame the decomposition problem
        problem = self._saccade_frame(dept_objective)

        # Stage 2: EVIDENCE - Gather team capabilities and current state
        evidence = self._gather_team_evidence(dept_objective)

        # Stage 3: Check/answer open consultations before INTERPRETATION
        self._resolve_open_consultations()

        # Stage 4: INTERPRETATION - Analyze gaps and opportunities
        interpretation = self._analyze_gaps(evidence, dept_objective)

        # Stage 5: STRATEGY - Propose team OKRs
        team_okrs = self._propose_team_okrs(problem, evidence, interpretation, dept_objective)

        # Stage 6: Register Mycelium edges for cross-team dependencies
        self._register_mycelium_edges(team_okrs)

        # Stage 7: Create OKR artifacts in engine
        self._create_team_okrs(team_okrs, dept_objective)

        # Update capability manifest
        self._update_manifest(team_okrs)

        return team_okrs

    def _resolve_open_consultations(self):
        """Check and answer any open consultations targeted at this department."""
        if not self.conversation_layer:
            return

        active_convs = self.conversation_layer.get_active_conversations(self.dept_head_node)
        for conv in active_convs:
            if conv.conversation_type == ConversationType.COORDINATION:
                # Get latest signal in conversation
                signals = self.conversation_layer.get_conversation_history(conv.id)
                for signal in reversed(signals):
                    if signal.payload.get("action") == "consultation_request" and signal.origin_kr != self.dept_head_node:
                        question = signal.payload.get("question", "")
                        needs_by_stage = signal.payload.get("needs_by_stage", "interpretation")

                        # Answer the consultation
                        answer = self.answer_consultation(question, {"needs_by_stage": needs_by_stage})

                        # Send response back via conversation layer
                        response_signal = MyceliumSignal(
                            id=f"SIG-{uuid.uuid4().hex[:12].upper()}",
                            conversation_id=conv.id,
                            origin_kr=self.dept_head_node,
                            signal_type=ConversationType.COORDINATION,
                            payload={
                                "question": question,
                                "answer": answer,
                                "action": "consultation_response",
                                "needs_by_stage": needs_by_stage
                            },
                            priority=SignalPriority.NORMAL
                        )
                        self.conversation_layer._send_signal(response_signal, signal.origin_kr)
                        print(f"  💬 Answered consultation from {signal.origin_kr}: {question[:60]}...")
                        break

    def answer_consultation(self, question: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Answer a cross-department consultation question.

        Uses the department's existing EVIDENCE/INTERPRETATION context plus the specific
        question to provide a targeted answer. This is a single call_model() call,
        not a full pipeline re-run.

        Args:
            question: The specific question from another department
            context: Optional additional context (e.g., which stage the answer is needed for)

        Returns:
            Structured answer with: answer, confidence, source_stage, caveats
        """
        print(f"  💬 {self.dept_head_node} answering consultation: {question[:80]}...")

        # Build context from what this department has already produced
        dept_context = {
            "dept_head": self.dept_head_node,
            "specialist": self.specialist_name,
            "question": question,
            "needs_by_stage": context.get("needs_by_stage", "interpretation") if context else "interpretation",
            "evidence_summary": context.get("evidence", "Not available"),
            "interpretation_summary": context.get("interpretation", "Not available"),
        }

        # Add department-specific context if available
        if self.manifest_path.exists():
            try:
                with open(self.manifest_path) as f:
                    manifest = json.load(f)
                    dept_context["team_okrs"] = manifest.get("team_okrs", [])
                    dept_context["mycelium_edges"] = manifest.get("mycelium_edges", [])
            except Exception:
                pass

        # Single call_model for consultation answer
        from kojiki.core import call_model

        # Create a minimal prompt for consultation answering
        prompt = f"""# CONSULTATION ANSWER - {self.dept_head_node}

You are the {self.dept_head_node} Department Head. Another department has asked a specific question that requires your expertise.

DEPARTMENT: {self.dept_head_node}
SPECIALIST: {self.specialist_name}
QUESTION: {question}
NEEDED FOR STAGE: {dept_context['needs_by_stage']}

YOUR EVIDENCE SUMMARY:
{dept_context['evidence_summary']}

YOUR INTERPRETATION SUMMARY:
{dept_context['interpretation_summary']}

TEAM OKRs:
{json.dumps(dept_context.get('team_okrs', []), indent=2)[:2000]}

CROSS-TEAM DEPENDENCIES:
{json.dumps(dept_context.get('mycelium_edges', []), indent=2)[:1000]}

Provide a focused, structured answer to the question. Do NOT run a full pipeline - just answer this specific question.

OUTPUT FORMAT - JSON object with:
{{
  "answer": "Direct answer to the question",
  "confidence": 0.0-1.0,
  "source_stage": "evidence|interpretation|strategy|knowledge",
  "caveats": ["Any limitations or assumptions"],
  "follow_up_needed": false,
  "related_team": "Optional team node if answer depends on specific team"
}}"""

        # Use call_model with low temperature for consistent answers
        try:
            dispatch = {"task_id": f"consult-{self.dept_head_node}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"}
            mock_context = type('MockContext', (), {
                'get_allowed_context': lambda self, keys: {k: v for k, v in dept_context.items() if k in keys},
                'set_stage_output': lambda self, stage, output: None,
                'stage_outputs': {},
                'dispatch': dispatch,
                'get': lambda self, key, default=None: dept_context.get(key, default)
            })()

            result = call_model(prompt, mock_context, [], None, "consultation")

            # Validate response structure
            if isinstance(result, dict) and "answer" in result:
                return result
            else:
                # Fallback structured answer
                return {
                    "answer": str(result) if result else "No answer generated",
                    "confidence": 0.5,
                    "source_stage": "knowledge",
                    "caveats": ["Generated from fallback - real LLM call needed"],
                    "follow_up_needed": False,
                    "related_team": None
                }
        except Exception as e:
            print(f"  ⚠️ Consultation answer failed: {e}")
            return {
                "answer": f"Error generating answer: {e}",
                "confidence": 0.0,
                "source_stage": "error",
                "caveats": [str(e)],
                "follow_up_needed": True,
                "related_team": None
            }

    def open_consultation(self, target_dept: str, question: str, needs_by_stage: str = "interpretation") -> Optional[str]:
        """
        Open a consultation conversation with another department via Mycelium.

        Returns the conversation ID if successful.
        """
        if not self.conversation_layer:
            return None

        conversation = self.conversation_layer.start_conversation(
            title=f"Consultation: {self.dept_head_node} -> {target_dept}",
            conversation_type=ConversationType.COORDINATION,
            participants=[self.dept_head_node, target_dept],
            initiator_kr=self.dept_head_node
        )

        # Send the question as a signal
        signal = MyceliumSignal(
            id=f"SIG-{uuid.uuid4().hex[:12].upper()}",
            conversation_id=conversation.id,
            origin_kr=self.dept_head_node,
            signal_type=ConversationType.COORDINATION,
            payload={
                "question": question,
                "needs_by_stage": needs_by_stage,
                "action": "consultation_request"
            },
            priority=SignalPriority.NORMAL
        )

        self.conversation_layer._send_signal(signal, target_dept)
        return conversation.id

    def _create_mock_specialist(self):
        """Create a mock specialist with prompts for dept head decomposition."""
        class MockSpecialist:
            def __init__(self, dept_head_node, team_nodes):
                self.dept_head_node = dept_head_node
                self.team_nodes = team_nodes
                self.agent_prefix = dept_head_node.replace('.', '-')
                self.stages = {
                    "saccade": type('StageConfig', (), {
                        'inputs_allowed': ['raw_record', 'dept_head', 'objective', 'description', 'team_nodes', 'parent_objective'],
                        'tools': [],
                        'prompt': '',
                        'schema': ''
                    })(),
                    "evidence": type('StageConfig', (), {
                        'inputs_allowed': ['dept_head', 'team_nodes', 'objective'],
                        'tools': [],
                        'prompt': '',
                        'schema': ''
                    })(),
                    "interpretation": type('StageConfig', (), {
                        'inputs_allowed': ['evidence', 'objective', 'team_nodes'],
                        'tools': [],
                        'prompt': '',
                        'schema': ''
                    })(),
                    "strategy": type('StageConfig', (), {
                        'inputs_allowed': ['problem', 'evidence', 'interpretation', 'dept_objective', 'team_nodes', 'dept_head'],
                        'tools': [],
                        'prompt': '',
                        'schema': ''
                    })(),
                }

            def get_prompt(self, stage_name: str) -> str:
                dept_objective_ref = self  # capture for closure
                if stage_name == "saccade":
                    return f"""# SACCADE Stage - Department Head Decomposition

You are the {self.dept_head_node} Department Head. Decompose the department objective into team-level OKRs.

DEPARTMENT: {self.dept_head_node}
OBJECTIVE: {{objective}}
DESCRIPTION: {{description}}
TEAMS: {', '.join(self.team_nodes)}
PARENT OBJECTIVE: {{parent_objective}}

Frame this as a structured problem for team OKR decomposition. Output a problem_id, goal, constraints, assumptions, unknowns.
Key phrase: "department head decomposition" for model routing."""
                elif stage_name == "evidence":
                    return f"""# EVIDENCE Stage - Team Capability Assessment

You are the {self.dept_head_node} Department Head. Gather current state of each team.

TEAMS: {', '.join(self.team_nodes)}
OBJECTIVE: {{objective}}

For each team, provide findings on: capacity, current metrics, blockers, dependencies.
Key phrase: "team capability assessment" for model routing."""
                elif stage_name == "interpretation":
                    return f"""# INTERPRETATION Stage - Gap Analysis

You are the {self.dept_head_node} Department Head. Analyze gaps between current state and objective.

EVIDENCE: {{evidence}}
OBJECTIVE: {{objective}}
TEAMS: {', '.join(self.team_nodes)}

Provide synthesis, confidence, key_insights, contradictions, evidence_gaps.
Key phrase: "gap analysis" for model routing."""
                elif stage_name == "strategy":
                    return f"""# STRATEGY Stage - Team OKR Proposals

You are the {self.dept_head_node} Department Head. Decompose the department objective into team-level OKRs.

Each team creates ONE objective with 3-5 measurable key results.

PROBLEM: {{problem}}
EVIDENCE: {{evidence}}
INTERPRETATION: {{interpretation}}
DEPT OBJECTIVE: {{dept_objective}}
TEAMS: {', '.join(self.team_nodes)}

OUTPUT FORMAT - JSON object with "team_okrs" array. Each team OKR:
- team: team node ID (e.g., "Marketing.Growth")
- objective_id: unique ID (e.g., "OKR-Marketing.Growth-P-ABCDEF12-001")
- title: QUALITATIVE, ambitious, outcome-focused objective (e.g., "Improve customer onboarding experience")
- description: detailed description of WHY this matters
- key_results: 3-5 objects with:
  - description: QUANTITATIVE, measurable outcome (e.g., "Increase onboarding completion rate to 85%")
  - kr_type: "metric" | "milestone" | "task"
  - target: numeric target value
  - unit: "%" | "count" | "rate" | "days" | "$"
  - weight: 1.0 (default)
  - source: data source for measurement
  - frequency: "weekly" | "monthly" | "quarterly"
  - confidence: 0.0-1.0
  - is_leading: true (leading indicators preferred)
- dependencies: array of objects with: target_team (from TEAMS list), weight (0.0-1.0)

EXAMPLE OF GOOD OKR:
{{
  "team": "Marketing.Growth",
  "objective_id": "OKR-Marketing.Growth-P-ABCDEF12-001",
  "title": "Improve referral program activation experience",
  "description": "New users struggle to understand and activate referral incentives. This team owns the end-to-end activation flow.",
  "key_results": [
    {{"description": "Increase referral program activation rate to 40%", "kr_type": "metric", "target": 40, "unit": "%", "weight": 1.0, "source": "CRM", "frequency": "weekly", "confidence": 0.8, "is_leading": true}},
    {{"description": "Reduce time-to-first-referral from 14 days to 3 days", "kr_type": "metric", "target": 3, "unit": "days", "weight": 1.0, "source": "Analytics", "frequency": "weekly", "confidence": 0.7, "is_leading": true}},
    {{"description": "Achieve 4.5/5 NPS on referral onboarding survey", "kr_type": "metric", "target": 4.5, "unit": "score", "weight": 0.5, "source": "Survey", "frequency": "monthly", "confidence": 0.6, "is_leading": true}}
  ],
  "dependencies": [{{"target_team": "Engineering.Technology.Referral", "weight": 0.8}}]
}}

BAD EXAMPLE (tasks, not outcomes):
- "Launch email sequence" → TASK, not outcome
- "Build landing page" → OUTPUT, not outcome

Key phrase: "team okr" for model routing.

"""
                return f"# {stage_name.upper()} Stage\n\nExecute {stage_name} transformation."

            def get_schema(self, stage_name: str):
                return None

        return MockSpecialist(self.dept_head_node, self.team_nodes)

    def _create_mock_runner(self, specialist, registry=None):
        """Create a mock runner."""
        class MockRunner:
            def __init__(self, specialist, registry):
                self.specialist = specialist
                self.chain_builder = None
                self.registry = registry

        return MockRunner(specialist, registry or self.registry)

    def _create_mock_context(self, dept_objective: Objective, dept_head_node: str, team_nodes: List[str], allowed_keys: List[str]):
        """Create mock context with get_allowed_context and set_stage_output methods."""
        # Include all possible keys that stages might need
        context_map = {
            "dept_head": dept_head_node,
            "objective": dept_objective.title,
            "description": dept_objective.description,
            "team_nodes": team_nodes,
            "parent_objective": dept_objective.parent_objective_id,
            "evidence": "EVIDENCE_PLACEHOLDER",
            "interpretation": "INTERPRETATION_PLACEHOLDER",
            "problem": {"problem_id": f"P-DH-{dept_objective.objective_id[-8:]}", "goal": f"Decompose {dept_objective.title} into team OKRs"},
            "dept_objective": {
                "id": dept_objective.objective_id,
                "title": dept_objective.title,
                "key_results": [{"description": kr.description, "target": kr.target, "metric": kr.description} for kr in dept_objective.key_results]
            },
            "accepted_interpretation": "INTERPRETATION_PLACEHOLDER",
            "accepted_evidence": "EVIDENCE_PLACEHOLDER",
            "accepted_problem": {"problem_id": f"P-DH-{dept_objective.objective_id[-8:]}", "goal": f"Decompose {dept_objective.title} into team OKRs"},
            "dept_head": dept_head_node,
        }

        class MockContext:
            def __init__(self, context_map, allowed_keys):
                self._context = {k: v for k, v in context_map.items() if k in allowed_keys}
                self.stage_outputs = {}

            def get_allowed_context(self, allowed_keys: List[str]) -> Dict[str, Any]:
                return {k: v for k, v in self._context.items() if k in allowed_keys}

            def set_stage_output(self, stage: str, output: Dict[str, Any]):
                self.stage_outputs[stage] = output

            def update(self, other: Dict):
                self._context.update(other)

            def __getitem__(self, key):
                return self._context[key]

            def __setitem__(self, key, value):
                self._context[key] = value

            def __contains__(self, key):
                return key in self._context

        return MockContext(context_map, allowed_keys)

    def _run_stage_async(self, stage_func, mock_runner, dispatch, mock_context, dept_head_node):
        """Run an async stage function, handling event loop issues."""
        try:
            loop = asyncio.get_running_loop()
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run,
                    stage_func(mock_runner, dispatch, mock_context, dept_head_node))
                return future.result(timeout=60)
        except RuntimeError:
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(
                stage_func(mock_runner, dispatch, mock_context, dept_head_node)
            )

    def _saccade_frame(self, dept_objective: Objective) -> Dict[str, Any]:
        """SACCADE: Frame the decomposition as a structured problem."""
        mock_specialist = self._create_mock_specialist()
        mock_runner = self._create_mock_runner(mock_specialist, self.registry)
        mock_context = self._create_mock_context(dept_objective, self.dept_head_node, self.team_nodes,
            ['raw_record', 'dept_head', 'objective', 'description', 'team_nodes', 'parent_objective'])

        dispatch = {
            "raw_record": f"Decompose {dept_objective.title} into team OKRs"
        }

        return self._run_stage_async(run_saccade_stage, mock_runner, dispatch, mock_context, self.dept_head_node)

    def _gather_team_evidence(self, dept_objective: Objective) -> Dict[str, Any]:
        """EVIDENCE: Gather current state of each team."""
        mock_specialist = self._create_mock_specialist()
        mock_runner = self._create_mock_runner(mock_specialist, self.registry)
        mock_context = self._create_mock_context(dept_objective, self.dept_head_node, self.team_nodes,
            ['dept_head', 'team_nodes', 'objective'])

        dispatch = {}

        return self._run_stage_async(run_evidence_stage, mock_runner, dispatch, mock_context, self.dept_head_node)

    def _analyze_gaps(self, evidence: Dict, dept_objective: Objective) -> Dict[str, Any]:
        """INTERPRETATION: Analyze gaps between current state and objective."""
        mock_specialist = self._create_mock_specialist()
        mock_runner = self._create_mock_runner(mock_specialist, self.registry)
        mock_context = self._create_mock_context(dept_objective, self.dept_head_node, self.team_nodes,
            ['evidence', 'objective', 'team_nodes'])
        # Inject evidence into context
        mock_context['evidence'] = evidence

        dispatch = {}

        return self._run_stage_async(run_interpretation_stage, mock_runner, dispatch, mock_context, self.dept_head_node)

    def _propose_team_okrs(
        self,
        problem: Dict,
        evidence: Dict,
        interpretation: Dict,
        dept_objective: Objective
    ) -> List[TeamOKR]:
        """STRATEGY: Propose team OKRs with dependencies."""
        mock_specialist = self._create_mock_specialist()
        mock_runner = self._create_mock_runner(mock_specialist, self.registry)
        mock_context = self._create_mock_context(dept_objective, self.dept_head_node, self.team_nodes,
            ['problem', 'evidence', 'interpretation', 'dept_objective', 'team_nodes', 'dept_head'])
        # Inject dynamic data
        mock_context['evidence'] = evidence
        mock_context['interpretation'] = interpretation
        mock_context['dept_objective'] = {
            "id": dept_objective.objective_id,
            "title": dept_objective.title,
            "key_results": [{"description": kr.description, "target": kr.target, "metric": kr.description} for kr in dept_objective.key_results]
        }
        mock_context['problem'] = problem

        dispatch = {}

        result = self._run_stage_async(run_strategy_stage, mock_runner, dispatch, mock_context, self.dept_head_node)

        # Parse strategy output into TeamOKR objects
        team_okrs = []
        for team_okr_data in result.get("team_okrs", []):
            # Convert key_results to have string kr_type for JSON serialization
            key_results = team_okr_data.get("key_results", [])
            for kr in key_results:
                if "kr_type" in kr and hasattr(kr["kr_type"], "value"):
                    kr["kr_type"] = kr["kr_type"].value

            team_okr = TeamOKR(
                team=team_okr_data.get("team"),
                objective_id=team_okr_data.get("objective_id"),
                title=team_okr_data.get("title"),
                description=team_okr_data.get("description", ""),
                key_results=key_results,
                dependencies=team_okr_data.get("dependencies", []),
                parent_dept_objective=dept_objective.objective_id
            )
            team_okrs.append(team_okr)

        return team_okrs

    def _register_mycelium_edges(self, team_okrs: List[TeamOKR]):
        """Register cross-team dependencies as Mycelium edges."""
        for okr in team_okrs:
            for dep in okr.dependencies:
                target_team = dep.get("target_team")
                weight = dep.get("weight", 0.5)

                if target_team in self.team_nodes:
                    # Propose edge within department
                    signal = {
                        "id": f"sig-edge-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
                        "origin_kr": self.dept_head_node,
                        "event": "edge_create",
                        "new_status": "PROPOSED",
                        "signal_kind": "coordination",  # Use valid SignalType
                        "target_kr": target_team,
                        "weight": weight,
                        "diagnosed_cause": f"Cross-team dependency for {okr.objective_id}",
                        "diagnosed_cause_category": "Coordination",
                        "subgraph": [self.dept_head_node, target_team],
                        "fired_at": datetime.utcnow().isoformat() + "Z"
                    }
                    self.propagator.propagate(signal)
                    print(f"  Mycelium edge proposed: {self.dept_head_node} -> {target_team} (weight: {weight})")

    def _create_team_okrs(self, team_okrs: List[TeamOKR], dept_objective: Objective):
        """Create team OKR objectives in the OKR Engine."""
        # First, register all team nodes in the registry if they don't exist
        for team_okr in team_okrs:
            team_node = team_okr.team
            # Check if node exists using registry's get_node method
            existing_node = self.registry.get_node(team_node)
            if not existing_node:
                # Register team node under this department head
                _, pub_key = self.registry.key_manager.generate_keypair(team_node)
                self.registry.register_node(
                    node_data={
                        "id": team_node,
                        "domain": team_node.lower().replace('.', '/'),
                        "type": "agent",
                        "status": "active",
                        "pipeline_manifest_ref": f"bots/{team_node.lower().replace('.', '-')}/manifest.json#transformation_pipeline",
                        "pipeline_validated": False,
                        "parent": self.dept_head_node
                    },
                    signer=self.dept_head_node,
                    signature="governance_bypass"  # Governance bypass for dept head
                )
                print(f"  Registered team node: {team_node} under {self.dept_head_node}")

        for team_okr in team_okrs:
            objective = Objective(
                objective_id=team_okr.objective_id,
                title=team_okr.title,
                description=team_okr.description,
                level=OKRLevel.TEAM,
                owner_node=team_okr.team,
                parent_objective_id=dept_objective.objective_id,
                key_results=[
                    KeyResult(
                        kr_id=kr.get("kr_id", f"KR-{team_okr.objective_id}-{i+1:03d}"),
                        objective_id=team_okr.objective_id,
                        description=kr.get("description", ""),
                        kr_type=kr.get("kr_type", "metric").value if hasattr(kr.get("kr_type", "metric"), "value") else kr.get("kr_type", "metric"),
                        target=kr.get("target", 100.0),
                        current=0.0,
                        unit=kr.get("unit", "%"),
                        weight=kr.get("weight", 1.0),
                        source=kr.get("source", "dept_head_decomposition"),
                        frequency=kr.get("frequency", "weekly"),
                        confidence=kr.get("confidence", 0.7),
                        is_leading=kr.get("is_leading", True)
                    )
                    for i, kr in enumerate(team_okr.key_results)
                ],
                status=OKRStatus.ACTIVE,
                start_date=datetime.utcnow().strftime("%Y-%m-%d"),
                end_date=(datetime.utcnow() + timedelta(days=90)).strftime("%Y-%m-%d"),
                tags=["dept_head_decomposition", self.dept_head_node, dept_objective.objective_id]
            )
            self.okr_engine.create_objective(objective)
            print(f"  Created team OKR: {team_okr.objective_id} for {team_okr.team}")

    def _update_manifest(self, team_okrs: List[TeamOKR]):
        """Update department capability manifest."""
        manifest = {
            "dept_head": self.dept_head_node,
            "specialist": self.specialist_name,
            "team_okrs": [
                {
                    "team": okr.team,
                    "objective_id": okr.objective_id,
                    "dependencies": okr.dependencies
                }
                for okr in team_okrs
            ],
            "mycelium_edges": [
                {"from": self.dept_head_node, "to": dep["target_team"], "weight": dep["weight"]}
                for okr in team_okrs
                for dep in okr.dependencies
            ],
            "last_reinforcement": datetime.utcnow().isoformat() + "Z"
        }
        with open(self.manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2, default=str)

    def reinforce_mycelium_edges(self):
        """Reinforce Mycelium edges based on delivery confirmation."""
        if not self.manifest_path.exists():
            return

        with open(self.manifest_path) as f:
            manifest = json.load(f)

        for edge in manifest.get("mycelium_edges", []):
            # In production, check actual delivery via team reports
            # For now, simulate confirmation
            delivery_confirmed = self._check_delivery(edge["from"], edge["to"])

            flow_signal = 1.0 if delivery_confirmed else 0.0

            signal = {
                "id": f"sig-reinf-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
                "origin_kr": edge["from"],
                "event": "edge_reinforce",
                "new_status": "DELIVERED" if delivery_confirmed else "PARTIAL",
                "signal_kind": "coordination",  # Use valid SignalType
                "target_kr": edge["to"],
                "weight": flow_signal * edge["weight"],
                "diagnosed_cause": f"Reinforcement: {edge['from']} -> {edge['to']}",
                "diagnosed_cause_category": "Reinforcement",
                "subgraph": [edge["from"], edge["to"]],
                "fired_at": datetime.utcnow().isoformat() + "Z"
            }
            self.propagator.propagate(signal)

            # Run reinforcement engine
            from reinforcement import ReinforcementEngine
            reinf = ReinforcementEngine(str(self.propagator.edge_store_path))
            reinf.reinforce_edge(edge["from"], edge["to"], flow_signal)

        manifest["last_reinforcement"] = datetime.utcnow().isoformat() + "Z"
        with open(self.manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)

    def _check_delivery(self, from_kr: str, to_kr: str) -> bool:
        """Check if delivery was confirmed. Override in subclass with real logic."""
        return True  # Placeholder

    def query_mycelium_subgraph(self, team_node: str) -> Dict[str, Any]:
        """Query dependency subgraph for a team via Mycelium."""
        return self.propagator.compute_subgraph(team_node)

    def send_mycelium_signal(self, target_kr: str, event: str, signal_kind: str, weight: float = 0.5, **kwargs):
        """Send a Mycelium signal to another team/department."""
        signal = {
            "id": f"sig-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            "origin_kr": self.dept_head_node,
            "event": event,
            "new_status": kwargs.get("new_status", "PROPOSED"),
            "signal_kind": signal_kind,
            "target_kr": target_kr,
            "weight": weight,
            "diagnosed_cause": kwargs.get("diagnosed_cause", ""),
            "diagnosed_cause_category": kwargs.get("diagnosed_cause_category", "Coordination"),
            "subgraph": [self.dept_head_node, target_kr],
            "fired_at": datetime.utcnow().isoformat() + "Z"
        }
        return self.propagator.propagate(signal)


class MarketingDeptHead(DeptHeadBase):
    """Marketing Department Head - coordinates Growth, Brand, Content, SEO, Paid teams."""

    def __init__(self, registry, propagator, sentinel, okr_engine, conversation_layer=None):
        team_nodes = [
            "Marketing.Growth",
            "Marketing.Brand",
            "Marketing.Content",
            "Marketing.SEO",
            "Marketing.Paid",
            "Marketing.Email",
            "Marketing.Analytics"
        ]
        super().__init__(
            dept_head_node="Marketing",
            specialist_name="marketing-brand",
            registry=registry,
            propagator=propagator,
            sentinel=sentinel,
            okr_engine=okr_engine,
            team_nodes=team_nodes,
            conversation_layer=conversation_layer
        )

    def _check_delivery(self, from_kr: str, to_kr: str) -> bool:
        """Check if cross-team delivery was confirmed."""
        # In production, query team completion status
        # For now, simulate based on OKR progress
        return True


class EngineeringDeptHead(DeptHeadBase):
    """Engineering Department Head - coordinates Platform, Referral, API, Infra teams."""

    def __init__(self, registry, propagator, sentinel, okr_engine, conversation_layer=None):
        team_nodes = [
            "Engineering.Technology.Platform",
            "Engineering.Technology.Referral",
            "Engineering.Technology.API",
            "Engineering.Technology.Infrastructure",
            "Engineering.Technology.Data"
        ]
        super().__init__(
            dept_head_node="Engineering.Technology",
            specialist_name="engineering-platform",
            registry=registry,
            propagator=propagator,
            sentinel=sentinel,
            okr_engine=okr_engine,
            team_nodes=team_nodes,
            conversation_layer=conversation_layer
        )

    def _check_delivery(self, from_kr: str, to_kr: str) -> bool:
        """Check if cross-team delivery was confirmed."""
        # In production, query team completion status
        # For now, simulate based on OKR progress
        return True


# Factory to get dept head by node
def get_dept_head(
    dept_head_node: str,
    registry: NodeRegistry,
    propagator: SignalPropagator,
    sentinel: SentinelEngine,
    okr_engine: OKREngine,
    conversation_layer: Optional[MyceliumConversationLayer] = None
) -> Optional[DeptHeadBase]:
    """Get department head instance by node name."""
    dept_heads = {
        "Marketing": MarketingDeptHead,
        "Engineering.Technology": EngineeringDeptHead,
    }

    cls = dept_heads.get(dept_head_node)
    if cls:
        return cls(registry, propagator, sentinel, okr_engine, conversation_layer)
    return None


if __name__ == "__main__":
    # Quick test
    from pathlib import Path
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        registry = NodeRegistry(str(Path(tmpdir) / "nodes.json"))
        propagator = SignalPropagator(
            edge_store_path=str(Path(tmpdir) / "edges.json"),
            log_path=str(Path(tmpdir) / "signals.jsonl"),
            registry=registry
        )
        sentinel = SentinelEngine(tmpdir)
        okr_engine = OKREngine(f"postgresql://localhost/kojiki")

        # Initialize with root departments
        for dept in ["Marketing", "Engineering", "Finance"]:
            _, pub_key = registry.key_manager.generate_keypair(dept)
            registry.nodes[dept] = {
                "id": dept, "domain": dept.lower().replace(".", "/"), "type": "agent",
                "status": "active", "public_key": pub_key, "key_status": "active",
                "key_issued_at": datetime.utcnow().isoformat() + "Z", "key_revoked_at": None, "parent": None
            }
        registry.save()

        # Create Marketing dept head
        marketing_head = MarketingDeptHead(registry, propagator, sentinel, okr_engine)
        print(f"Created: {marketing_head.dept_head_node}")
        print(f"Teams: {marketing_head.team_nodes}")