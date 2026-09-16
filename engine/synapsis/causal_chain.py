"""
Full Causal Chain - Structured trace from Problem → Evidence → Interpretation → Strategy → Output → Deck → Outcome → Learning.

Enables complete auditability and reconstruction of decision reasoning.
"""

import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict, field
from enum import Enum


class StageName(Enum):
    SACCADE = "saccade"
    EVIDENCE = "evidence"
    INTERPRETATION = "interpretation"
    STRATEGY = "strategy"
    OUTPUT = "output"
    DECK = "deck"
    OUTCOME = "outcome"
    LEARNING = "learning"


@dataclass
class StageTransition:
    """Single stage transition in the causal chain."""
    from_stage: StageName
    to_stage: StageName
    input_hash: str
    output_hash: str
    agent_id: str
    timestamp: str
    model_call_id: Optional[str] = None
    tools_used: List[str] = field(default_factory=list)

    # Signed provenance
    signer: str = ""  # Agent that produced this output
    signature: str = ""  # Ed25519 signature over output_hash
    public_key: str = ""  # Public key for verification

    # For reconstruction
    input_summary: str = ""
    output_summary: str = ""


@dataclass
class CausalLink:
    """Link between two artifacts in the chain."""
    source_type: str
    source_id: str
    target_type: str
    target_id: str
    relationship: str = "derives_from"


@dataclass
class CausalChain:
    """
    Complete causal chain for a single decision pipeline execution.

    Immutable append-only log of all stage transitions and cross-references.
    """
    chain_id: str
    dispatch_id: str
    started_at: str
    completed_at: Optional[str] = None

    # Stage transitions (append-only)
    transitions: List[StageTransition] = field(default_factory=list)

    # Cross-references (problem → evidence → interpretation → strategy → output)
    causal_links: List[CausalLink] = field(default_factory=list)

    # Final artifacts
    final_problem_id: Optional[str] = None
    final_output_id: Optional[str] = None
    final_learning_id: Optional[str] = None

    # Metadata
    total_tokens: int = 0
    total_latency_ms: int = 0

    def add_transition(self, transition: StageTransition):
        """Add a stage transition to the chain."""
        self.transitions.append(transition)

    def add_causal_link(self, link: CausalLink):
        """Add a causal link between artifacts."""
        self.causal_links.append(link)

    def get_stage_output(self, stage: StageName) -> Optional[Dict]:
        """Get the output for a specific stage by finding its transition."""
        for t in reversed(self.transitions):
            if t.to_stage == stage:
                return {
                    "stage": stage.value,
                    "output_hash": t.output_hash,
                    "timestamp": t.timestamp,
                    "agent": t.agent_id,
                }
        return None

    def reconstruct_reasoning(self, artifact_type: str, artifact_id: str) -> List[Dict]:
        """
        Reconstruct the reasoning chain leading to an artifact.

        Returns list of {stage, artifact_id, relationship, source} tracing back.
        """
        chain = []
        current = (artifact_type, artifact_id)
        visited = set()

        while current and current not in visited:
            visited.add(current)
            src_type, src_id = current

            # Find links pointing TO this artifact
            incoming = [l for l in self.causal_links if l.target_type == src_type and l.target_id == src_id]
            if not incoming:
                break

            # Take the first incoming link (could be multiple)
            link = incoming[0]
            chain.append({
                "stage": link.source_type,
                "artifact_id": link.source_id,
                "relationship": link.relationship,
                "target": f"{link.target_type}:{link.target_id}",
            })
            current = (link.source_type, link.source_id)

        return list(reversed(chain))  # Root to leaf

    def to_json(self) -> str:
        """Serialize to JSON."""
        data = asdict(self)
        for t in data.get("transitions", []):
            t["from_stage"] = t["from_stage"].value if hasattr(t["from_stage"], "value") else t["from_stage"]
            t["to_stage"] = t["to_stage"].value if hasattr(t["to_stage"], "value") else t["to_stage"]
        return json.dumps(data, indent=2, default=str)

    @classmethod
    def from_json(cls, json_str: str) -> 'CausalChain':
        """Deserialize from JSON."""
        data = json.loads(json_str)
        # Convert string enums back
        for t in data.get("transitions", []):
            t["from_stage"] = StageName(t["from_stage"])
            t["to_stage"] = StageName(t["to_stage"])
        for c in data.get("causal_links", []):
            c["source_type"] = c["source_type"]
            c["target_type"] = c["target_type"]
        return cls(**data)


class CausalChainBuilder:
    """Builds a causal chain during pipeline execution."""

    def __init__(self, dispatch_id: str, key_manager=None):
        self.chain = CausalChain(
            chain_id=hashlib.sha256(f"{dispatch_id}{datetime.utcnow().isoformat()}".encode()).hexdigest()[:16],
            dispatch_id=dispatch_id,
            started_at=datetime.utcnow().isoformat() + "Z",
        )
        self._stage_outputs: Dict[StageName, Dict] = {}
        self._artifact_ids: Dict[str, str] = {}  # (type, temp_id) -> actual_id
        self.key_manager = key_manager

    def record_stage_transition(
        self,
        from_stage: Optional[StageName],
        to_stage: StageName,
        input_data: Dict,
        output_data: Dict,
        agent_id: str,
        model_call_id: Optional[str] = None,
        tools_used: List[str] = None,
    ) -> str:
        """Record a stage transition and return output hash."""
        input_hash = hashlib.sha256(json.dumps(input_data, sort_keys=True).encode()).hexdigest()[:16]
        output_hash = hashlib.sha256(json.dumps(output_data, sort_keys=True).encode()).hexdigest()[:16]

        # Sign the output hash using SENTINEL KeyManager
        # Use department-level key for signing (not per-stage agent ID)
        # Extract department from agent_id (e.g., "marketing.Saccade" -> "marketing")
        dept = agent_id.split('.')[0] if '.' in agent_id else agent_id
        signer = dept
        signature = ""
        public_key = ""
        if self.key_manager:
            try:
                signature = self.key_manager.sign(signer, output_hash)
                public_key = self.key_manager.get_public_key(signer) or ""
            except Exception:
                # Signing failed (no private key for this agent) - leave unsigned
                pass

        transition = StageTransition(
            from_stage=from_stage or StageName.SACCADE,
            to_stage=to_stage,
            input_hash=input_hash,
            output_hash=output_hash,
            agent_id=agent_id,
            timestamp=datetime.utcnow().isoformat() + "Z",
            model_call_id=model_call_id,
            tools_used=tools_used or [],
            signer=agent_id,
            signature=signature,
            public_key=public_key,
            input_summary=self._summarize(input_data),
            output_summary=self._summarize(output_data),
        )
        self.chain.add_transition(transition)
        self._stage_outputs[to_stage] = output_data

        # Extract artifact IDs for cross-referencing
        self._extract_artifact_ids(to_stage, output_data)

        return output_hash

    def add_causal_link(
        self,
        source_type: str,
        source_id: str,
        target_type: str,
        target_id: str,
        relationship: str = "derives_from",
    ):
        """Add a causal link between artifacts."""
        link = CausalLink(
            source_type=source_type,
            source_id=source_id,
            target_type=target_type,
            target_id=target_id,
            relationship=relationship,
        )
        self.chain.add_causal_link(link)

    def _extract_artifact_ids(self, stage: StageName, output: Dict):
        """Extract IDs from stage output for cross-referencing."""
        id_fields = {
            "saccade": ["problem_id"],
            "evidence": ["findings"],  # findings list, extract all finding_ids
            "interpretation": ["synthesis", "interpretation_refs"],  # also extract finding_ids from refs
            "strategy": ["strategy_id", "objective"],
            "output": ["output_id"],
            "deck": ["deck_id"],
            "outcome": ["outcome_id"],
            "learning": ["learning_id"],
        }

        stage_key = stage.value if hasattr(stage, 'value') else str(stage)
        for field in id_fields.get(stage_key, []):
            if field in output:
                if field == "findings" and isinstance(output[field], list) and output[field]:
                    # Extract finding_id from ALL findings, not just first
                    for finding in output[field]:
                        finding_id = finding.get("finding_id")
                        if finding_id:
                            # Store by field name for lookup in auto_link_stages
                            field_key = f"{stage_key}:finding_id"
                            self._artifact_ids[field_key] = finding_id
                            # Also store by value for reverse lookup
                            value_key = f"{stage_key}:{finding_id}"
                            self._artifact_ids[value_key] = finding_id
                elif field == "interpretation_refs" and isinstance(output[field], list) and output[field]:
                    # Extract finding_ids from interpretation refs
                    for ref in output[field]:
                        field_key = f"{stage_key}:finding_id"
                        self._artifact_ids[field_key] = ref
                        value_key = f"{stage_key}:{ref}"
                        self._artifact_ids[value_key] = ref
                else:
                    # Store by field name for lookup in auto_link_stages
                    field_key = f"{stage_key}:{field}"
                    self._artifact_ids[field_key] = output[field]
                    # Also store by value for reverse lookup
                    value_key = f"{stage_key}:{output[field]}"
                    self._artifact_ids[value_key] = output[field]

    def _summarize(self, data: Dict) -> str:
        """Create brief summary for transition record."""
        if not data:
            return ""
        if isinstance(data, list):
            return f"list with {len(data)} items"
        keys = list(data.keys())[:3]
        return f"keys: {', '.join(keys)}"

    def auto_link_stages(self):
        """Automatically create causal links between consecutive stages."""
        stage_order = [
            StageName.SACCADE,
            StageName.EVIDENCE,
            StageName.INTERPRETATION,
            StageName.STRATEGY,
            StageName.OUTPUT,
            StageName.DECK,
            StageName.OUTCOME,
            StageName.LEARNING,
        ]

        for i in range(len(stage_order) - 1):
            from_stage = stage_order[i]
            to_stage = stage_order[i + 1]

            if from_stage in self._stage_outputs and to_stage in self._stage_outputs:
                from_output = self._stage_outputs[from_stage]
                to_output = self._stage_outputs[to_stage]

                # Link known ID fields
                id_map = {
                    (StageName.SACCADE, StageName.EVIDENCE): ("problem_id", "problem_id"),
                    (StageName.EVIDENCE, StageName.INTERPRETATION): ("finding_id", "interpretation_refs"),  # interpretation output has interpretation_refs
                    (StageName.INTERPRETATION, StageName.STRATEGY): ("finding_id", "interpretation_ref"),  # Use finding_id from evidence
                    (StageName.STRATEGY, StageName.OUTPUT): ("strategy_id", "strategy_ref"),
                    (StageName.OUTPUT, StageName.DECK): ("output_id", "output_ref"),
                    (StageName.OUTPUT, StageName.OUTCOME): ("output_id", "output_ref"),
                    (StageName.OUTCOME, StageName.LEARNING): ("outcome_id", "outcome_check"),
                }

                if (from_stage, to_stage) in id_map:
                    from_field, to_field = id_map[(from_stage, to_stage)]
                    from_val = from_output.get(from_field)
                    to_val = to_output.get(to_field)

                    # Also try to get from stored artifact IDs if not in current output
                    if not from_val:
                        artifact_key = f"{from_stage.value}:{from_field}"
                        from_val = self._artifact_ids.get(artifact_key)
                    if not to_val:
                        artifact_key = f"{to_stage.value}:{to_field}"
                        to_val = self._artifact_ids.get(artifact_key)

                    # DECK special case - if DECK output has 'deck_id', use that; if error, still link
                    if from_stage == StageName.OUTPUT and to_stage == StageName.DECK:
                        # Try deck_id from to_output, or from artifact_ids
                        if not to_val:
                            to_val = to_output.get("deck_id") or self._artifact_ids.get("deck:deck_id")

                    # OUTCOME special case - uses output_ref which should be in output
                    if from_stage == StageName.OUTPUT and to_stage == StageName.OUTCOME:
                        if not to_val:
                            to_val = to_output.get("output_ref") or self._artifact_ids.get("output:output_id")

                    # LEARNING special case - uses outcome_check which maps to outcome_id
                    if from_stage == StageName.OUTCOME and to_stage == StageName.LEARNING:
                        if not to_val:
                            to_val = to_output.get("outcome_check") or self._artifact_ids.get("outcome:outcome_id")

                    if from_val and to_val:
                        self.add_causal_link(
                            source_type=from_stage.value,
                            source_id=from_val,
                            target_type=to_stage.value,
                            target_id=to_val if isinstance(to_val, str) else (to_val[0] if to_val else None),
                            relationship="informs",
                        )

    def finalize(self, dispatch_id: str) -> CausalChain:
        """Finalize the chain and return it."""
        self.chain.completed_at = datetime.utcnow().isoformat() + "Z"
        self.auto_link_stages()

        # Set final artifact IDs
        saccade_out = self._stage_outputs.get(StageName.SACCADE, {})
        output_out = self._stage_outputs.get(StageName.OUTPUT, {})
        learning_out = self._stage_outputs.get(StageName.LEARNING, {})

        if saccade_out.get("problem_id"):
            self.chain.final_problem_id = saccade_out["problem_id"]
        if output_out.get("output_id"):
            self.chain.final_output_id = output_out["output_id"]
        if learning_out.get("learning_id"):
            self.chain.final_learning_id = learning_out["learning_id"]

        return self.chain


# Integration with runner
class CausalChainRunner:
    """Mixin for runners to automatically build causal chains."""

    def __init__(self, dispatch_id: str, key_manager=None):
        self.chain_builder = CausalChainBuilder(dispatch_id, key_manager=key_manager)

    def record_stage(
        self,
        stage: StageName,
        input_data: Dict,
        output_data: Dict,
        agent_id: str,
        model_call_id: Optional[str] = None,
        tools_used: List[str] = None,
    ) -> str:
        """Record a stage transition and return output hash."""
        # Determine from_stage from previous stages
        if self.chain_builder._stage_outputs:
            from_stage = list(self.chain_builder._stage_outputs.keys())[-1]
        else:
            from_stage = None

        return self.chain_builder.record_stage_transition(
            from_stage=from_stage,
            to_stage=stage,
            input_data=input_data,
            output_data=output_data,
            agent_id=agent_id,
            model_call_id=model_call_id,
            tools_used=tools_used,
        )

    def add_causal_link(
        self,
        source_type: str,
        source_id: str,
        target_type: str,
        target_id: str,
        relationship: str = "derives_from",
    ):
        """Add a causal link between artifacts."""
        return self.chain_builder.add_causal_link(
            source_type=source_type,
            source_id=source_id,
            target_type=target_type,
            target_id=target_id,
            relationship=relationship,
        )

    def finalize(self, dispatch_id: str):
        """Finalize the chain and return it."""
        return self.chain_builder.finalize(dispatch_id)