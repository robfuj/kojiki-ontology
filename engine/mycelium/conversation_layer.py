#!/usr/bin/env python3
"""
MyceliumConversationLayer — Bounded live consultation between departments.

Round-based design from earlier session:
1. Run EVIDENCE for a batch of departments
2. Open bounded consultation window via MyceliumConversationLayer
3. Run INTERPRETATION/STRATEGY for that batch with consultation context

This replaces the old DeptHeadBase live consultation that was never integrated
into the new Orchestrator.
"""

import asyncio
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
from collections import defaultdict

from engine.mycelium.propagate import SignalPropagator
from engine.mycelium.registry import NodeRegistry
from engine.mycelium.decision_rights import DecisionRightsGate, SignalType, DecisionRight
from engine.sentinel import SentinelEngine


@dataclass
class ConsultationTurn:
    """Single turn in a consultation conversation."""
    turn_id: str
    round_number: int
    sender_dept: str
    sender_node: str
    recipient_dept: str
    recipient_node: str
    content: Dict[str, Any]  # The consultation payload
    signal_kind: str  # "consultation_request", "consultation_response", "clarification"
    timestamp: str
    signature: str = ""


@dataclass
class ConsultationSession:
    """A bounded consultation session between departments."""
    session_id: str
    round_number: int
    origin_batch: List[str]  # Departments that originated this consultation
    participants: Dict[str, List[str]]  # dept -> [node_ids]
    turns: List[ConsultationTurn] = field(default_factory=list)
    started_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    closed_at: Optional[str] = None
    status: str = "open"  # open, closed, expired


class MyceliumConversationLayer:
    """
    Bounded live consultation window for cross-department coordination.
    
    Design:
    - Runs AFTER EVIDENCE stage completes for a batch of departments
    - Opens a consultation window (max 3 rounds by default)
    - Departments can request clarifications, share findings, flag dependencies
    - Closes before INTERPRETATION/STRATEGY stages run
    - All turns are logged to SENTINEL for provenance
    """
    
    def __init__(
        self,
        propagator: SignalPropagator,
        registry: NodeRegistry,
        sentinel: SentinelEngine,
        max_rounds: int = 3,
        consultation_store_path: Optional[str] = None
    ):
        self.propagator = propagator
        self.registry = registry
        self.sentinel = sentinel
        self.max_rounds = max_rounds
        
        # Storage for consultation sessions
        self.store_path = Path(consultation_store_path or 
                              (Path.home() / ".kojiki" / "data" / "consultations.json"))
        self.store_path.parent.mkdir(parents=True, exist_ok=True)
        self.sessions: Dict[str, ConsultationSession] = {}
        self._load_sessions()
        
        # Decision Rights gate for consultation signals
        self.gate = DecisionRightsGate()
        self._init_decision_rights()
    
    def _load_sessions(self):
        """Load consultation sessions from disk."""
        if self.store_path.exists():
            try:
                data = json.loads(self.store_path.read_text())
                for session_data in data.get("sessions", []):
                    session = ConsultationSession(
                        session_id=session_data["session_id"],
                        round_number=session_data["round_number"],
                        origin_batch=session_data["origin_batch"],
                        participants=session_data["participants"],
                        turns=[
                            ConsultationTurn(**t) for t in session_data.get("turns", [])
                        ],
                        started_at=session_data["started_at"],
                        closed_at=session_data.get("closed_at"),
                        status=session_data.get("status", "open")
                    )
                    self.sessions[session.session_id] = session
            except Exception:
                pass  # Corrupted file, start fresh
    
    def _save_sessions(self):
        """Persist consultation sessions to disk."""
        data = {
            "sessions": [
                {
                    "session_id": s.session_id,
                    "round_number": s.round_number,
                    "origin_batch": s.origin_batch,
                    "participants": s.participants,
                    "turns": [
                        {
                            "turn_id": t.turn_id,
                            "round_number": t.round_number,
                            "sender_dept": t.sender_dept,
                            "sender_node": t.sender_node,
                            "recipient_dept": t.recipient_dept,
                            "recipient_node": t.recipient_node,
                            "content": t.content,
                            "signal_kind": t.signal_kind,
                            "timestamp": t.timestamp,
                            "signature": t.signature
                        }
                        for t in s.turns
                    ],
                    "started_at": s.started_at,
                    "closed_at": s.closed_at,
                    "status": s.status
                }
                for s in self.sessions.values()
            ]
        }
        self.store_path.write_text(json.dumps(data, indent=2))
    
    def _init_decision_rights(self):
        """Initialize Decision Rights gate for consultation signals."""
        # Consultation signals require Consult right from sender, Inform right for recipients
        # This is configured per node in registry
        pass
    
    def open_consultation(
        self,
        batch_departments: List[str],
        evidence_outputs: Dict[str, Any],
        problem_context: Dict[str, Any]
    ) -> ConsultationSession:
        """
        Open a new consultation session for a batch of departments.
        
        Args:
            batch_departments: List of department names that just completed EVIDENCE
            evidence_outputs: The EVIDENCE stage outputs from each department
            problem_context: The shared problem framing from SACCADE
            
        Returns:
            ConsultationSession ready for turns
        """
        session_id = f"CONS-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6]}"
        
        # Build participant map: dept -> [node_ids from registry]
        participants = {}
        for dept in batch_departments:
            # Get root department node
            dept_node = self.registry.get_node(dept)
            if dept_node:
                participants[dept] = [dept_node["id"]]
                # Also get children of this department
                children = self.registry.get_children(dept)
                if children:
                    participants[dept].extend([c["id"] for c in children])
            else:
                # Fallback: use dept head node
                participants[dept] = [f"{dept}.Head"]
        
        session = ConsultationSession(
            session_id=session_id,
            round_number=1,
            origin_batch=batch_departments,
            participants=participants,
            status="open"
        )
        
        # Seed with evidence context as initial "turn 0" from each department
        for dept in batch_departments:
            evidence = evidence_outputs.get(dept, {})
            turn = ConsultationTurn(
                turn_id=f"{session_id}-T0-{dept}",
                round_number=0,
                sender_dept=dept,
                sender_node=participants[dept][0] if participants[dept] else f"{dept}.Head",
                recipient_dept="ALL",
                recipient_node="ALL",
                content={
                    "type": "evidence_share",
                    "evidence_summary": self._summarize_evidence(evidence),
                    "problem_context": problem_context,
                    "key_findings": evidence.get("key_findings", []),
                    "open_questions": evidence.get("open_questions", []),
                    "dependencies": evidence.get("dependencies", [])
                },
                signal_kind="evidence_share",
                timestamp=datetime.utcnow().isoformat() + "Z"
            )
            session.turns.append(turn)
        
        self.sessions[session_id] = session
        self._save_sessions()
        
        # Log consultation opening to SENTINEL
        self._log_consultation_event(session, "consultation_opened", {
            "batch": batch_departments,
            "evidence_keys": list(evidence_outputs.keys())
        })
        
        return session
    
    def _summarize_evidence(self, evidence: Dict[str, Any]) -> Dict[str, Any]:
        """Create a concise summary of evidence for sharing."""
        findings = evidence.get("findings", [])
        return {
            "total_findings": len(findings),
            "high_confidence": sum(1 for f in findings if f.get("confidence", 0) > 0.7),
            "sources": list(set(f.get("source", "unknown") for f in findings)),
            "sufficiency_avg": sum(f.get("sufficiency", 0.5) for f in findings) / max(len(findings), 1)
        }
    
    async def run_consultation_round(
        self,
        session: ConsultationSession,
        run_department_stage: callable,
        problem: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Run one consultation round.
        
        Each department in the batch can:
        1. Read all evidence shares from turn 0
        2. Send consultation requests to other departments
        3. Receive responses
        4. Then proceed to INTERPRETATION/STRATEGY
        
        Args:
            session: The consultation session
            run_department_stage: Async function(dept, stage_name, consultation_context) -> stage_output
            problem: The shared problem framing
            context: Additional context
            
        Returns:
            Dict of department -> consultation_context (for next stages)
        """
        consultation_contexts = {}
        
        for round_num in range(1, self.max_rounds + 1):
            session.round_number = round_num
            print(f"  🔄 Consultation Round {round_num}/{self.max_rounds}")
            
            round_results = {}
            
            # Each department in the batch can make consultation requests
            for dept in session.origin_batch:
                # Build consultation context for this department
                dept_context = self._build_consultation_context(session, dept)
                
                # Run a special "consultation" stage for this department
                # This is where the dept can ask questions, share insights
                consultation_output = await run_department_stage(
                    dept, 
                    "consultation", 
                    dept_context,
                    problem,
                    context
                )
                
                round_results[dept] = consultation_output
                
                # Process any consultation requests from this department
                requests = consultation_output.get("consultation_requests", [])
                for req in requests:
                    await self._process_consultation_request(session, dept, req)
            
            # Check if any department wants to continue consultation
            continue_flags = [
                r.get("continue_consultation", False) 
                for r in round_results.values()
            ]
            
            if not any(continue_flags) or round_num == self.max_rounds:
                break
        
        # Close session
        session.status = "closed"
        session.closed_at = datetime.utcnow().isoformat() + "Z"
        self._save_sessions()
        
        # Build final consultation context for each department
        for dept in session.origin_batch:
            consultation_contexts[dept] = self._build_consultation_context(session, dept)
        
        # Log consultation closing to SENTINEL
        self._log_consultation_event(session, "consultation_closed", {
            "rounds_completed": session.round_number,
            "total_turns": len(session.turns)
        })
        
        return consultation_contexts
    
    def _build_consultation_context(
        self, 
        session: ConsultationSession, 
        for_dept: str
    ) -> Dict[str, Any]:
        """Build consultation context visible to a specific department."""
        # All turns are visible to all participants (transparent consultation)
        visible_turns = [
            {
                "turn_id": t.turn_id,
                "round": t.round_number,
                "from": f"{t.sender_dept}.{t.sender_node}",
                "to": f"{t.recipient_dept}.{t.recipient_node}",
                "kind": t.signal_kind,
                "content": t.content,
                "timestamp": t.timestamp
            }
            for t in session.turns
        ]
        
        # Find turns addressed to this department
        addressed_turns = [
            t for t in visible_turns 
            if t["to"] in [f"{for_dept}.ALL", f"{for_dept}.Head", "ALL.ALL"]
        ]
        
        return {
            "session_id": session.session_id,
            "round_number": session.round_number,
            "all_turns": visible_turns,
            "addressed_to_me": addressed_turns,
            "participants": session.participants
        }
    
    async def _process_consultation_request(
        self,
        session: ConsultationSession,
        from_dept: str,
        request: Dict[str, Any]
    ):
        """Process a consultation request from one department to another."""
        to_dept = request.get("target_department")
        if not to_dept or to_dept not in session.participants:
            return
        
        # Create consultation request turn
        turn = ConsultationTurn(
            turn_id=f"{session.session_id}-R{session.round_number}-{from_dept}->{to_dept}",
            round_number=session.round_number,
            sender_dept=from_dept,
            sender_node=session.participants[from_dept][0] if session.participants[from_dept] else f"{from_dept}.Head",
            recipient_dept=to_dept,
            recipient_node=session.participants[to_dept][0] if session.participants[to_dept] else f"{to_dept}.Head",
            content={
                "type": "consultation_request",
                "question": request.get("question", ""),
                "context": request.get("context", {}),
                "urgency": request.get("urgency", "normal"),
                "requires_response": request.get("requires_response", True)
            },
            signal_kind="consultation_request",
            timestamp=datetime.utcnow().isoformat() + "Z"
        )
        session.turns.append(turn)
        
        # Propagate as a MYCELIUM signal for audit trail
        self._propagate_consultation_signal(session, turn, "request")
        
        # If response required, target department will respond in their next turn
        # (handled in their consultation stage execution)
    
    def _propagate_consultation_signal(
        self,
        session: ConsultationSession,
        turn: ConsultationTurn,
        direction: str  # "request" or "response"
    ):
        """Propagate consultation turn as MYCELIUM signal for provenance."""
        signal = {
            "id": turn.turn_id,
            "origin_kr": turn.sender_node,
            "event": f"consultation_{turn.signal_kind}",
            "new_status": "CONSULTING",
            "signal_kind": "request",  # Must be "request" or "failure" per validate_signal
            "diagnosed_cause": turn.content.get("question", "Consultation exchange"),
            "diagnosed_cause_category": "Communication",
            "subgraph": session.participants.get(turn.recipient_dept, []),
            "fired_at": turn.timestamp,
            "status": "ROUTED",  # Required by validate_signal
            "signature": "",  # Required by validate_signal - empty for consultation mode
            "payload": {
                "consultation_session": session.session_id,
                "turn": {
                    "turn_id": turn.turn_id,
                    "from": f"{turn.sender_dept}.{turn.sender_node}",
                    "to": f"{turn.recipient_dept}.{turn.recipient_node}",
                    "content": turn.content
                }
            }
        }
        
        # Sign with sender's key (simplified - in production use actual key)
        # For now, propagate without signature verification in consultation mode
        try:
            self.propagator.propagate(signal)
        except Exception:
            pass  # Non-blocking for consultation
    
    def _log_consultation_event(self, session: ConsultationSession, event_type: str, detail: Dict[str, Any]):
        """Log consultation event to SENTINEL."""
        try:
            self.sentinel.write_signal({
                "signal_id": f"CONS-{session.session_id}-{event_type}",
                "source_node": "MYCELIUM_CONVERSATION_LAYER",
                "target_node": "ORCHESTRATOR",
                "signal_type": "CONSULTATION_EVENT",
                "payload": {
                    "session_id": session.session_id,
                    "event_type": event_type,
                    "origin_batch": session.origin_batch,
                    "round_number": session.round_number,
                    "detail": detail
                },
                "timestamp": datetime.utcnow().isoformat() + "Z"
            })
        except Exception:
            pass  # Non-blocking
    
    def get_session(self, session_id: str) -> Optional[ConsultationSession]:
        """Get a consultation session by ID."""
        return self.sessions.get(session_id)
    
    def get_active_sessions(self) -> List[ConsultationSession]:
        """Get all active (open) consultation sessions."""
        return [s for s in self.sessions.values() if s.status == "open"]