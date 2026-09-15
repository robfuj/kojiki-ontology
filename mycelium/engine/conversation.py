"""
MYCELIUM Conversation Layer - Cross-department coordination via signals.

Enables department heads to:
- Send/receive signals across department boundaries
- Coordinate on shared decisions (deck_request)
- Escalate via NEURAXIS when guardrails breached
- SACCADE cache for repeated problem framings
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import defaultdict
import uuid


class ConversationType(str, Enum):
    """Types of conversations in MYCELIUM."""
    COORDINATION = "coordination"      # General cross-dept coordination
    DECK_REQUEST = "deck_request"      # Joint decision deck
    ESCALATION = "escalation"          # NEURAXIS escalation
    GUARDRAIL_ALERT = "guardrail_alert"  # Guardrail breach notification
    SACCADE_SHARE = "saccade_share"    # Share problem framing


class SignalPriority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class MyceliumSignal:
    """A signal propagating through MYCELIUM."""
    id: str
    conversation_id: str
    origin_kr: str
    signal_type: ConversationType
    payload: Dict[str, Any]
    priority: SignalPriority = SignalPriority.NORMAL
    fired_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + 'Z')
    signature: Optional[str] = None
    subgraph: List[str] = field(default_factory=list)
    status: str = "ROUTED"  # ROUTED, APPLIED_UNVERIFIED, CLOSED_VERIFIED, WITHDRAWN
    
    # Failure/Escalation specific
    diagnosed_cause: str = ""
    diagnosed_cause_category: str = ""
    
    # Deck request specific
    decision_ref: str = ""
    participating_departments: List[str] = field(default_factory=list)
    deck_ref: str = ""


@dataclass
class Conversation:
    """A multi-party conversation thread in MYCELIUM."""
    id: str
    title: str
    conversation_type: ConversationType
    participants: List[str]  # KR/node IDs
    created_at: str
    updated_at: str
    status: str = "ACTIVE"  # ACTIVE, RESOLVED, ESCALATED, ARCHIVED
    signals: List[str] = field(default_factory=list)  # Signal IDs
    resolution: Optional[Dict[str, Any]] = None
    escalation_ref: Optional[str] = None


@dataclass
class SaccadeCacheEntry:
    """Cached SACCADE problem framing for reuse."""
    problem_id: str
    goal: str
    constraints: List[str]
    assumptions: List[str]
    unknowns: List[str]
    department: str
    created_at: str
    usage_count: int = 0
    last_used: str = ""
    similarity_hash: str = ""


class MyceliumConversationLayer:
    """
    Conversation layer for MYCELIUM - enables cross-department coordination.
    
    Integrates with:
    - SignalPropagator for signed signal delivery
    - DecisionRightsGate for recipient filtering
    - NEURAXIS for escalation
    - OKR Engine for decision tracking
    """
    
    def __init__(
        self,
        conversation_store: str,
        signal_log: str,
        saccade_cache_path: str,
        signal_propagator=None,
        neuraxis_escalator=None,
        okr_engine=None
    ):
        self.conversation_store = Path(conversation_store)
        self.signal_log = Path(signal_log)
        self.saccade_cache_path = Path(saccade_cache_path)
        self.signal_propagator = signal_propagator
        self.neuraxis_escalator = neuraxis_escalator
        self.okr_engine = okr_engine
        
        self.conversations: Dict[str, Conversation] = {}
        self.saccade_cache: Dict[str, SaccadeCacheEntry] = {}
        
        self._load_conversations()
        self._load_saccade_cache()
        self._ensure_signal_log()
    
    def _load_conversations(self) -> None:
        if self.conversation_store.exists():
            with open(self.conversation_store, 'r') as f:
                data = json.load(f)
                for conv_data in data.get('conversations', []):
                    conv = Conversation(**conv_data)
                    self.conversations[conv.id] = conv
    
    def _save_conversations(self) -> None:
        self.conversation_store.parent.mkdir(parents=True, exist_ok=True)
        data = {"conversations": [asdict(c) for c in self.conversations.values()]}
        with open(self.conversation_store, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _load_saccade_cache(self) -> None:
        if self.saccade_cache_path.exists():
            with open(self.saccade_cache_path, 'r') as f:
                data = json.load(f)
                for entry_data in data.get('cache', []):
                    entry = SaccadeCacheEntry(**entry_data)
                    self.saccade_cache[entry.problem_id] = entry
    
    def _save_saccade_cache(self) -> None:
        self.saccade_cache_path.parent.mkdir(parents=True, exist_ok=True)
        data = {"cache": [asdict(e) for e in self.saccade_cache.values()]}
        with open(self.saccade_cache_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _ensure_signal_log(self) -> None:
        self.signal_log.parent.mkdir(parents=True, exist_ok=True)
        if not self.signal_log.exists():
            with open(self.signal_log, 'w') as f:
                pass
    
    # ============ Conversation Management ============
    
    def start_conversation(
        self,
        title: str,
        conversation_type: ConversationType,
        participants: List[str],
        initiator_kr: str
    ) -> Conversation:
        """Start a new cross-department conversation."""
        conv_id = f"CONV-{uuid.uuid4().hex[:12].upper()}"
        
        conversation = Conversation(
            id=conv_id,
            title=title,
            conversation_type=conversation_type,
            participants=participants,
            created_at=datetime.utcnow().isoformat() + 'Z',
            updated_at=datetime.utcnow().isoformat() + 'Z',
        )
        
        self.conversations[conv_id] = conversation
        self._save_conversations()
        
        # Notify participants via signal propagator
        if self.signal_propagator:
            self._notify_participants(conversation, initiator_kr)
        
        return conversation
    
    def _notify_participants(self, conversation: Conversation, initiator_kr: str) -> None:
        """Send coordination signal to all participants."""
        for participant in conversation.participants:
            if participant == initiator_kr:
                continue
            
            signal = MyceliumSignal(
                id=f"SIG-{uuid.uuid4().hex[:12].upper()}",
                conversation_id=conversation.id,
                origin_kr=initiator_kr,
                signal_type=conversation.conversation_type,
                payload={
                    "conversation_id": conversation.id,
                    "conversation_title": conversation.title,
                    "action": "invite",
                    "message": f"You have been invited to conversation: {conversation.title}"
                },
                priority=SignalPriority.NORMAL
            )
            self._send_signal(signal, participant)
    
    def _send_signal(self, signal: MyceliumSignal, target_kr: str) -> Dict[str, Any]:
        """Send a signal to a target via signal propagator."""
        if not self.signal_propagator:
            return {"success": False, "error": "No signal propagator configured"}
        
        # Add target to subgraph
        signal.subgraph = [target_kr]
        
        # Log locally
        self._log_signal(signal)
        
        # Propagate
        return self.signal_propagator.propagate(asdict(signal))
    
    def add_signal_to_conversation(self, conversation_id: str, signal: MyceliumSignal) -> bool:
        """Add a signal to an existing conversation."""
        if conversation_id not in self.conversations:
            return False
        
        conv = self.conversations[conversation_id]
        conv.signals.append(signal.id)
        conv.updated_at = datetime.utcnow().isoformat() + 'Z'
        
        # Log signal
        self._log_signal(signal)
        
        self._save_conversations()
        return True
    
    def resolve_conversation(
        self,
        conversation_id: str,
        resolution: Dict[str, Any],
        resolver_kr: str
    ) -> bool:
        """Resolve a conversation with a decision."""
        if conversation_id not in self.conversations:
            return False
        
        conv = self.conversations[conversation_id]
        conv.status = "RESOLVED"
        conv.resolution = {
            "decision": resolution,
            "resolver": resolver_kr,
            "resolved_at": datetime.utcnow().isoformat() + 'Z'
        }
        conv.updated_at = datetime.utcnow().isoformat() + 'Z'
        
        self._save_conversations()
        
        # Notify participants of resolution
        if self.signal_propagator:
            for participant in conv.participants:
                if participant == resolver_kr:
                    continue
                signal = MyceliumSignal(
                    id=f"SIG-{uuid.uuid4().hex[:12].upper()}",
                    conversation_id=conversation_id,
                    origin_kr=resolver_kr,
                    signal_type=ConversationType.COORDINATION,
                    payload={
                        "conversation_id": conversation_id,
                        "action": "resolved",
                        "resolution": resolution
                    }
                )
                self._send_signal(signal, participant)
        
        return True
    
    # ============ Deck Request Coordination ============
    
    def request_deck(
        self,
        decision_ref: str,
        participating_departments: List[str],
        origin_kr: str,
        deck_ref: str,
        context: Dict[str, Any]
    ) -> Conversation:
        """Request a joint decision deck from multiple departments."""
        title = f"Joint Decision: {decision_ref}"
        
        conversation = self.start_conversation(
            title=title,
            conversation_type=ConversationType.DECK_REQUEST,
            participants=participating_departments,
            initiator_kr=origin_kr
        )
        
        # Send deck_request signal via propagator
        if self.signal_propagator:
            signal = MyceliumSignal(
                id=f"SIG-{uuid.uuid4().hex[:12].upper()}",
                conversation_id=conversation.id,
                origin_kr=origin_kr,
                signal_type=ConversationType.DECK_REQUEST,
                payload={
                    "decision_ref": decision_ref,
                    "deck_ref": deck_ref,
                    "context": context
                },
                decision_ref=decision_ref,
                participating_departments=participating_departments,
                deck_ref=deck_ref,
                priority=SignalPriority.HIGH
            )
            self.signal_propagator.propagate(asdict(signal))
        
        return conversation
    
    # ============ Guardrail Alerts ============
    
    def alert_guardrail_breach(
        self,
        kr_id: str,
        guardrail_id: str,
        description: str,
        severity: str,
        current_value: float,
        threshold: float,
        origin_kr: str
    ) -> Conversation:
        """Alert department heads of a guardrail breach."""
        title = f"Guardrail Breach: {guardrail_id} on {kr_id}"
        
        # Determine affected departments from KR owners
        participants = self._get_kr_owners(kr_id)
        if origin_kr not in participants:
            participants.append(origin_kr)
        
        conversation = self.start_conversation(
            title=title,
            conversation_type=ConversationType.GUARDRAIL_ALERT,
            participants=participants,
            initiator_kr=origin_kr
        )
        
        # Send high-priority signal
        if self.signal_propagator:
            signal = MyceliumSignal(
                id=f"SIG-{uuid.uuid4().hex[:12].upper()}",
                conversation_id=conversation.id,
                origin_kr=origin_kr,
                signal_type=ConversationType.GUARDRAIL_ALERT,
                payload={
                    "kr_id": kr_id,
                    "guardrail_id": guardrail_id,
                    "description": description,
                    "severity": severity,
                    "current_value": current_value,
                    "threshold": threshold
                },
                priority=SignalPriority.CRITICAL if severity == "critical" else SignalPriority.HIGH,
                diagnosed_cause=description,
                diagnosed_cause_category="Threshold"
            )
            self.signal_propagator.propagate(asdict(signal))
        
        # Escalate to NEURAXIS if critical
        if severity == "critical" and self.neuraxis_escalator:
            self._escalate_to_neuraxis(conversation, {
                "type": "guardrail_breach",
                "kr_id": kr_id,
                "guardrail_id": guardrail_id,
                "severity": severity,
                "description": description
            })
        
        return conversation
    
    def _get_kr_owners(self, kr_id: str) -> List[str]:
        """Get department heads that own a KR. Would query OKR engine."""
        if self.okr_engine:
            # In practice, would query OKR engine for objective hierarchy
            pass
        # Fallback: infer from KR ID prefix
        if "Marketing" in kr_id:
            return ["Marketing.Growth", "Marketing.Brand", "Marketing.Content"]
        elif "Engineering" in kr_id:
            return ["Engineering.Technology.Platform", "Engineering.Technology.Referral", 
                    "Engineering.Technology.API", "Engineering.Technology.Infrastructure",
                    "Engineering.Technology.Data"]
        return []
    
    # ============ NEURAXIS Escalation ============
    
    def escalate_to_neuraxis(
        self,
        conversation_id: str,
        escalation_reason: str,
        escalation_data: Dict[str, Any],
        escalator_kr: str
    ) -> Optional[str]:
        """Escalate a conversation to NEURAXIS vertical escalation."""
        if conversation_id not in self.conversations:
            return None
        
        conv = self.conversations[conversation_id]
        conv.status = "ESCALATED"
        
        escalation_ref = f"ESC-{uuid.uuid4().hex[:12].upper()}"
        conv.escalation_ref = escalation_ref
        conv.updated_at = datetime.utcnow().isoformat() + 'Z'
        
        # Call NEURAXIS escalator
        if self.neuraxis_escalator:
            result = self.neuraxis_escalator.escalate(
                escalation_ref=escalation_ref,
                conversation_id=conversation_id,
                reason=escalation_reason,
                data=escalation_data,
                escalator=escalator_kr
            )
            if not result.get("success"):
                return None
        
        self._save_conversations()
        
        # Notify participants
        if self.signal_propagator:
            for participant in conv.participants:
                signal = MyceliumSignal(
                    id=f"SIG-{uuid.uuid4().hex[:12].upper()}",
                    conversation_id=conversation_id,
                    origin_kr=escalator_kr,
                    signal_type=ConversationType.ESCALATION,
                    payload={
                        "conversation_id": conversation_id,
                        "escalation_ref": escalation_ref,
                        "reason": escalation_reason,
                        "action": "escalated"
                    },
                    priority=SignalPriority.CRITICAL
                )
                self._send_signal(signal, participant)
        
        return escalation_ref
    
    def _escalate_to_neuraxis(self, conversation: Conversation, data: Dict[str, Any]) -> None:
        """Internal escalation helper."""
        if self.neuraxis_escalator:
            self.neuraxis_escalator.escalate(
                escalation_ref=f"ESC-{uuid.uuid4().hex[:12].upper()}",
                conversation_id=conversation.id,
                reason=data.get("type", "guardrail_breach"),
                data=data,
                escalator=conversation.participants[0] if conversation.participants else "system"
            )
    
    # ============ SACCADE Cache ============
    
    def cache_saccade(
        self,
        problem_id: str,
        goal: str,
        constraints: List[str],
        assumptions: List[str],
        unknowns: List[str],
        department: str
    ) -> SaccadeCacheEntry:
        """Cache a SACCADE problem framing for reuse."""
        # Generate similarity hash from problem components
        import hashlib
        content = f"{goal}|{'|'.join(constraints)}|{'|'.join(assumptions)}|{'|'.join(unknowns)}"
        similarity_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
        
        entry = SaccadeCacheEntry(
            problem_id=problem_id,
            goal=goal,
            constraints=constraints,
            assumptions=assumptions,
            unknowns=unknowns,
            department=department,
            created_at=datetime.utcnow().isoformat() + 'Z',
            similarity_hash=similarity_hash
        )
        
        self.saccade_cache[problem_id] = entry
        self._save_saccade_cache()
        return entry
    
    def find_similar_saccade(
        self,
        goal: str,
        constraints: List[str],
        assumptions: List[str],
        unknowns: List[str],
        department: str,
        similarity_threshold: float = 0.8
    ) -> Optional[SaccadeCacheEntry]:
        """Find a cached SACCADE with similar framing."""
        import hashlib
        content = f"{goal}|{'|'.join(constraints)}|{'|'.join(assumptions)}|{'|'.join(unknowns)}"
        query_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
        
        # Exact hash match first
        for entry in self.saccade_cache.values():
            if entry.similarity_hash == query_hash and entry.department == department:
                entry.usage_count += 1
                entry.last_used = datetime.utcnow().isoformat() + 'Z'
                self._save_saccade_cache()
                return entry
        
        # Could add fuzzy matching here (Levenshtein, etc.)
        return None
    
    def get_saccade_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        dept_counts = defaultdict(int)
        total_usage = 0
        for entry in self.saccade_cache.values():
            dept_counts[entry.department] += 1
            total_usage += entry.usage_count
        
        return {
            "total_entries": len(self.saccade_cache),
            "total_usage": total_usage,
            "by_department": dict(dept_counts),
            "hit_rate": total_usage / max(len(self.saccade_cache), 1)
        }
    
    # ============ Signal Logging ============
    
    def _log_signal(self, signal: MyceliumSignal) -> None:
        """Append signal to log file."""
        with open(self.signal_log, 'a') as f:
            f.write(json.dumps(asdict(signal)) + '\n')
    
    def get_conversation_history(self, conversation_id: str) -> List[MyceliumSignal]:
        """Retrieve all signals for a conversation from log."""
        signals = []
        if not self.signal_log.exists():
            return signals
        
        with open(self.signal_log, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                signal_data = json.loads(line)
                if signal_data.get('conversation_id') == conversation_id:
                    signals.append(MyceliumSignal(**signal_data))
        
        return signals
    
    # ============ Queries ============
    
    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        return self.conversations.get(conversation_id)
    
    def get_active_conversations(self, participant_kr: str) -> List[Conversation]:
        """Get all active conversations for a participant."""
        return [
            c for c in self.conversations.values()
            if participant_kr in c.participants and c.status == "ACTIVE"
        ]
    
    def get_conversations_by_type(self, conv_type: ConversationType) -> List[Conversation]:
        return [c for c in self.conversations.values() if c.conversation_type == conv_type]


# Integration with Chief of Staff
class ChiefOfStaffMyceliumIntegration:
    """Integration layer for Chief of Staff to use MYCELIUM conversation layer."""
    
    def __init__(self, conversation_layer: MyceliumConversationLayer):
        self.conversation_layer = conversation_layer
    
    def coordinate_cross_department(
        self,
        goal: str,
        departments: List[str],
        context: Dict[str, Any]
    ) -> Conversation:
        """Coordinate a goal across multiple departments via MYCELIUM."""
        # Chief of Staff SACCADEs the problem
        # Then starts a coordination conversation
        conversation = self.conversation_layer.start_conversation(
            title=f"Cross-Dept Coordination: {goal[:50]}",
            conversation_type=ConversationType.COORDINATION,
            participants=departments,
            initiator_kr="Finance"  # 7-dept consolidation
        )
        
        # Send initial context to all
        if self.conversation_layer.signal_propagator:
            for dept in departments:
                signal = MyceliumSignal(
                    id=f"SIG-{uuid.uuid4().hex[:12].upper()}",
                    conversation_id=conversation.id,
                    origin_kr="Finance",  # 7-dept consolidation
                    signal_type=ConversationType.COORDINATION,
                    payload={
                        "conversation_id": conversation.id,
                        "goal": goal,
                        "context": context,
                        "action": "coordinate"
                    },
                    priority=SignalPriority.HIGH
                )
                self.conversation_layer._send_signal(signal, dept)
        
        return conversation
    
    def check_saccade_cache(
        self,
        goal: str,
        constraints: List[str],
        assumptions: List[str],
        unknowns: List[str],
        department: str
    ) -> Optional[SaccadeCacheEntry]:
        """Check if a similar problem has been framed before."""
        return self.conversation_layer.find_similar_saccade(
            goal, constraints, assumptions, unknowns, department
        )
    
    def store_saccade(
        self,
        problem_id: str,
        goal: str,
        constraints: List[str],
        assumptions: List[str],
        unknowns: List[str],
        department: str
    ) -> SaccadeCacheEntry:
        """Store a SACCADE framing for future reuse."""
        return self.conversation_layer.cache_saccade(
            problem_id, goal, constraints, assumptions, unknowns, department
        )


if __name__ == "__main__":
    # Quick test
    import tempfile
    
    with tempfile.TemporaryDirectory() as tmpdir:
        conv_store = Path(tmpdir) / "conversations.json"
        signal_log = Path(tmpdir) / "signals.jsonl"
        cache_path = Path(tmpdir) / "saccade_cache.json"
        
        layer = MyceliumConversationLayer(
            conversation_store=str(conv_store),
            signal_log=str(signal_log),
            saccade_cache_path=str(cache_path)
        )
        
        # Test conversation
        conv = layer.start_conversation(
            title="Test Coordination",
            conversation_type=ConversationType.COORDINATION,
            participants=["Marketing.Growth", "Engineering.Technology.Platform"],
            initiator_kr="Finance"  # 7-dept consolidation
        )
        print(f"Started conversation: {conv.id}")
        
        # Test cache
        entry = layer.cache_saccade(
            problem_id="P-TEST123",
            goal="Test goal",
            constraints=["c1"],
            assumptions=["a1"],
            unknowns=["u1"],
            department="Marketing"
        )
        print(f"Cached SACCADE: {entry.problem_id}")
        
        # Test find similar
        found = layer.find_similar_saccade(
            "Test goal", ["c1"], ["a1"], ["u1"], "Marketing"
        )
        print(f"Found cached: {found is not None}")
        
        print("Mycelium Conversation Layer test passed!")