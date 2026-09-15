"""
SQLAlchemy models for Kojiki Decision System PostgreSQL schema.
Used by Alembic for autogenerate migrations.
"""

from sqlalchemy import (
    Column, String, Text, Boolean, DateTime, Integer, BigInteger, 
    ForeignKey, UniqueConstraint, Index, JSON, ARRAY, func
)
from sqlalchemy.dialects.postgresql import JSONB, UUID, TIMESTAMP, INET
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

# ============================================================
# MYCELIUM REGISTRY
# ============================================================

class MyceliumNode(Base):
    __tablename__ = 'mycelium_nodes'
    
    id = Column(String(255), primary_key=True)
    domain = Column(String(255), nullable=False)
    type = Column(String(50), nullable=False, default='agent')
    status = Column(String(50), nullable=False, default='active')
    pipeline_manifest_ref = Column(String(500))
    pipeline_validated = Column(Boolean, default=False)
    public_key = Column(Text, nullable=False)
    key_status = Column(String(50), nullable=False, default='active')
    key_issued_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    key_revoked_at = Column(DateTime(timezone=True))
    parent_id = Column(String(255), ForeignKey('mycelium_nodes.id'))
    decision_rights = Column(JSONB)
    decision_right = Column(String(255))
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, default=func.now(), onupdate=func.now())
    
    # Relationships
    parent = relationship("MyceliumNode", remote_side=[id], backref="children")
    edges_from = relationship("MyceliumEdge", foreign_keys="MyceliumEdge.from_kr", back_populates="from_node")
    edges_to = relationship("MyceliumEdge", foreign_keys="MyceliumEdge.to_kr", back_populates="to_node")
    signals = relationship("MyceliumSignal", back_populates="origin_node")
    
    __table_args__ = (
        Index('idx_nodes_parent', 'parent_id'),
        Index('idx_nodes_decision_right', 'decision_right'),
        Index('idx_nodes_status', 'status'),
    )


class MyceliumNodeAudit(Base):
    __tablename__ = 'mycelium_node_audit'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    event_type = Column(String(50), nullable=False)
    node_id = Column(String(255), ForeignKey('mycelium_nodes.id'), nullable=False)
    actor = Column(String(255), nullable=False)
    detail = Column(JSONB)
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    
    __table_args__ = (
        Index('idx_node_audit_node', 'node_id'),
        Index('idx_node_audit_event', 'event_type'),
    )


# ============================================================
# MYCELIUM EDGES (PROPAGATE/REINFORCEMENT)
# ============================================================

class MyceliumEdge(Base):
    __tablename__ = 'mycelium_edges'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    from_kr = Column(String(255), ForeignKey('mycelium_nodes.id'), nullable=False)
    to_kr = Column(String(255), ForeignKey('mycelium_nodes.id'), nullable=False)
    weight = Column(String(50), nullable=False, default='0.0')  # Stored as string for precision
    reciprocal_exchanges = Column(Integer, nullable=False, default=0)
    one_directional_exchanges = Column(Integer, nullable=False, default=0)
    last_reinforced = Column(DateTime(timezone=True))
    trigger_event = Column(String(255))
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, default=func.now(), onupdate=func.now())
    
    # Relationships
    from_node = relationship("MyceliumNode", foreign_keys=[from_kr], back_populates="edges_from")
    to_node = relationship("MyceliumNode", foreign_keys=[to_kr], back_populates="edges_to")
    exchanges = relationship("MyceliumEdgeExchange", back_populates="edge")
    
    __table_args__ = (
        UniqueConstraint('from_kr', 'to_kr', name='uq_edge_from_to'),
        Index('idx_edges_from', 'from_kr'),
        Index('idx_edges_to', 'to_kr'),
        Index('idx_edges_weight', 'weight'),
    )


class MyceliumEdgeExchange(Base):
    __tablename__ = 'mycelium_edge_exchanges'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    edge_id = Column(BigInteger, ForeignKey('mycelium_edges.id'))
    from_kr = Column(String(255), nullable=False)
    to_kr = Column(String(255), nullable=False)
    exchange_type = Column(String(50), nullable=False)  # 'reciprocal' or 'one_directional'
    signal_id = Column(String(255))
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    
    edge = relationship("MyceliumEdge", back_populates="exchanges")


# ============================================================
# MYCELIUM SIGNALS (PROPAGATE)
# ============================================================

class MyceliumSignal(Base):
    __tablename__ = 'mycelium_signals'
    
    id = Column(String(255), primary_key=True)
    origin_kr = Column(String(255), ForeignKey('mycelium_nodes.id'), nullable=False)
    event = Column(String(100), nullable=False)
    signal_kind = Column(String(50), nullable=False)  # 'failure', 'request'
    new_status = Column(String(50))
    diagnosed_cause = Column(Text)
    diagnosed_cause_category = Column(String(100))
    status = Column(String(50), nullable=False, default='ROUTED')
    subgraph = Column(JSONB, nullable=False, default=[])
    signature = Column(Text, nullable=False)
    fired_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    
    origin_node = relationship("MyceliumNode", back_populates="signals")
    
    __table_args__ = (
        Index('idx_signals_origin', 'origin_kr'),
        Index('idx_signals_kind', 'signal_kind'),
        Index('idx_signals_fired', 'fired_at'),
    )


# ============================================================
# SENTINEL PROVENANCE
# ============================================================

class SentinelExperience(Base):
    __tablename__ = 'sentinel_experiences'
    
    id = Column(String(255), primary_key=True)
    problem_id = Column(String(255))
    hypothesis = Column(Text, nullable=False)
    agents = Column(ARRAY(Text), nullable=False)
    action = Column(Text, nullable=False)
    expected = Column(Text, nullable=False)
    observed = Column(Text, nullable=False)
    error_classification = Column(String(100))
    escalation = Column(JSONB)
    redefinition = Column(JSONB)
    learning_ref = Column(String(255))
    propagation_targets = Column(ARRAY(Text))
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())


class SentinelProvenanceToken(Base):
    __tablename__ = 'sentinel_provenance_tokens'
    
    id = Column(String(255), primary_key=True)
    payload_hash = Column(String(64), nullable=False)
    prev_entry_id = Column(String(255))
    signer = Column(String(255), nullable=False)
    signature = Column(Text, nullable=False)
    payload = Column(JSONB, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    
    __table_args__ = (
        Index('idx_tokens_prev', 'prev_entry_id'),
        Index('idx_tokens_signer', 'signer'),
    )


class SentinelGateEvidence(Base):
    __tablename__ = 'sentinel_gate_evidence'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    gate_request_id = Column(String(255), nullable=False)
    experience_id = Column(String(255), ForeignKey('sentinel_experiences.id'), nullable=False)
    signer = Column(String(255), nullable=False)
    signature = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    
    __table_args__ = (
        UniqueConstraint('gate_request_id', 'experience_id', 'signer', name='uq_gate_evidence'),
    )


class SentinelGateRequest(Base):
    __tablename__ = 'sentinel_gate_requests'
    
    id = Column(String(255), primary_key=True)
    experience_id = Column(String(255), ForeignKey('sentinel_experiences.id'), nullable=False)
    problem_id = Column(String(255), nullable=False)
    layer = Column(String(20), nullable=False)  # L0, L1, L2, L3, L4
    status = Column(String(50), nullable=False, default='PENDING')
    decided_by = Column(String(255))
    decided_at = Column(DateTime(timezone=True))
    decision = Column(String(50))
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())


class SentinelNodeLifecycle(Base):
    __tablename__ = 'sentinel_node_lifecycle'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    event_type = Column(String(50), nullable=False)
    node_id = Column(String(255), nullable=False)
    actor = Column(String(255), nullable=False)
    detail = Column(JSONB)
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())


# ============================================================
# NEURAXIS ESCALATION
# ============================================================

class NeuraxisEscalation(Base):
    __tablename__ = 'neuraxis_escalations'
    
    id = Column(String(255), primary_key=True)
    problem_id = Column(String(255), nullable=False)
    experience_id = Column(String(255), ForeignKey('sentinel_experiences.id'))
    error_class = Column(String(20), nullable=False)  # L0, L1, L2, L3, L4
    repetition_count = Column(Integer, nullable=False, default=0)
    sla_deadline = Column(DateTime(timezone=True))
    status = Column(String(50), nullable=False, default='OPEN')
    gate_request_id = Column(String(255), ForeignKey('sentinel_gate_requests.id'))
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    resolved_at = Column(DateTime(timezone=True))
    
    __table_args__ = (
        Index('idx_escalations_problem', 'problem_id'),
        Index('idx_escalations_status', 'status'),
    )


# ============================================================
# SYNAPSIS PIPELINE RECORDS
# ============================================================

class SynapsisProblem(Base):
    __tablename__ = 'synapsis_problems'
    
    problem_id = Column(String(255), primary_key=True)
    dispatch_id = Column(String(255), nullable=False)
    goal = Column(Text, nullable=False)
    context = Column(JSONB)
    assumptions = Column(ARRAY(Text))
    constraints = Column(ARRAY(Text))
    unknowns = Column(ARRAY(Text))
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())


class SynapsisEvidence(Base):
    __tablename__ = 'synapsis_evidence'
    
    finding_id = Column(String(255), primary_key=True)
    problem_id = Column(String(255), ForeignKey('synapsis_problems.problem_id'))
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    source = Column(String(255))
    confidence = Column(String(50))
    retrieval_state = Column(String(50))
    coverage_limits = Column(Text)
    sufficiency = Column(String(50))
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())


class SynapsisInterpretation(Base):
    __tablename__ = 'synapsis_interpretations'
    
    interpretation_id = Column(String(255), primary_key=True)
    problem_id = Column(String(255), ForeignKey('synapsis_problems.problem_id'))
    synthesis = Column(Text, nullable=False)
    confidence = Column(String(50))
    key_drivers = Column(ARRAY(Text))
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())


class SynapsisStrategy(Base):
    __tablename__ = 'synapsis_strategies'
    
    strategy_id = Column(String(255), primary_key=True)
    problem_id = Column(String(255), ForeignKey('synapsis_problems.problem_id'))
    interpretation_ref = Column(String(255), ForeignKey('synapsis_interpretations.interpretation_id'))
    objective = Column(Text, nullable=False)
    rationale = Column(Text, nullable=False)
    timeline = Column(Text)
    success_criteria = Column(JSONB, nullable=False)
    escalation_conditions = Column(ARRAY(Text))
    decision_rights = Column(JSONB, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())


class SynapsisOutput(Base):
    __tablename__ = 'synapsis_outputs'
    
    output_id = Column(String(255), primary_key=True)
    strategy_id = Column(String(255), ForeignKey('synapsis_strategies.strategy_id'))
    content = Column(JSONB, nullable=False)
    measurement_window = Column(JSONB)
    confidence = Column(String(50))
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())


class SynapsisDeck(Base):
    __tablename__ = 'synapsis_decks'
    
    deck_id = Column(String(255), primary_key=True)
    output_id = Column(String(255), ForeignKey('synapsis_outputs.output_id'))
    deck_ref = Column(String(255))
    mode = Column(String(50))
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())


class SynapsisOutcome(Base):
    __tablename__ = 'synapsis_outcomes'
    
    outcome_id = Column(String(255), primary_key=True)
    output_id = Column(String(255), ForeignKey('synapsis_outputs.output_id'))
    actuals = Column(JSONB, nullable=False)
    evaluations = Column(JSONB, nullable=False)
    outcome_score = Column(String(50))
    target_met = Column(Boolean)
    converged = Column(Boolean)
    iteration_count = Column(Integer)
    guardrail_violations = Column(JSONB)
    deviation_analysis = Column(Text)
    confidence = Column(String(50))
    kaizen_iteration = Column(Integer)
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())


class SynapsisLearning(Base):
    __tablename__ = 'synapsis_learning'
    
    learning_id = Column(String(255), primary_key=True)
    cycle_timestamp = Column(DateTime(timezone=True), nullable=False)
    experiences = Column(JSONB, nullable=False)
    patterns = Column(ARRAY(Text))
    reusable_insights = Column(ARRAY(Text))
    redefinitions = Column(JSONB)
    outcome_score = Column(String(50))
    guardrail_violations = Column(JSONB)
    confidence = Column(String(50))
    kaizen_iteration = Column(Integer)
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())


# ============================================================
# KAIZEN LOOP
# ============================================================

class KaizenIteration(Base):
    __tablename__ = 'kaizen_iterations'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    problem_id = Column(String(255), ForeignKey('synapsis_problems.problem_id'))
    iteration = Column(Integer, nullable=False)
    phase = Column(String(20), nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=False)
    completed_at = Column(DateTime(timezone=True))
    input_data = Column(JSONB)
    output_data = Column(JSONB)
    guardrail_violations = Column(JSONB)
    learning_generated = Column(Boolean, default=False)
    experience_refs = Column(ARRAY(Text))
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    
    __table_args__ = (
        Index('idx_kaizen_problem', 'problem_id'),
    )


# ============================================================
# CAUSAL CHAIN
# ============================================================

class CausalChain(Base):
    __tablename__ = 'causal_chains'
    
    chain_id = Column(String(255), primary_key=True)
    dispatch_id = Column(String(255), nullable=False)
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    total_tokens = Column(BigInteger, default=0)
    total_latency_ms = Column(BigInteger, default=0)
    final_problem_id = Column(String(255))
    final_output_id = Column(String(255))
    final_learning_id = Column(String(255))
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    
    transitions = relationship("CausalTransition", back_populates="chain", order_by="CausalTransition.created_at")
    nodes = relationship("CausalNode", back_populates="chain")


class CausalNode(Base):
    __tablename__ = 'causal_nodes'
    
    id = Column(String(255), primary_key=True)
    chain_id = Column(String(255), ForeignKey('causal_chains.chain_id'))
    stage = Column(String(50), nullable=False)
    artifact_type = Column(String(50), nullable=False)
    artifact_id = Column(String(255), nullable=False)
    content_hash = Column(String(64), nullable=False)
    content = Column(JSONB, nullable=False)
    agent_id = Column(String(255))
    tools = Column(ARRAY(Text))
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    
    chain = relationship("CausalChain", back_populates="nodes")
    
    __table_args__ = (
        Index('idx_causal_chain', 'chain_id'),
    )


class CausalTransition(Base):
    __tablename__ = 'causal_transitions'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    chain_id = Column(String(255), ForeignKey('causal_chains.chain_id'))
    from_stage = Column(String(50), nullable=False)
    to_stage = Column(String(50), nullable=False)
    input_hash = Column(String(64), nullable=False)
    output_hash = Column(String(64), nullable=False)
    agent_id = Column(String(255), nullable=False)
    signer = Column(String(255))
    signature = Column(Text)
    public_key = Column(Text)
    input_summary = Column(Text)
    output_summary = Column(Text)
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    
    chain = relationship("CausalChain", back_populates="transitions")


# ============================================================
# GOVERNANCE CHANGES
# ============================================================

class GovernanceChange(Base):
    __tablename__ = 'governance_changes'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    change_type = Column(String(50), nullable=False)  # add_node, update_decision_rights, etc.
    target = Column(String(255), nullable=False)
    payload = Column(JSONB, nullable=False)
    reason = Column(Text)
    gate_id = Column(String(255))
    approver = Column(String(255))
    timestamp = Column(DateTime(timezone=True), nullable=False, default=func.now())


# ============================================================
# DECK DNA CACHE (Priority 2)
# ============================================================

class DeckDNACache(Base):
    __tablename__ = 'deck_dna_cache'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    cache_key = Column(String(255), nullable=False, unique=True)
    department = Column(String(50), nullable=False)
    mode = Column(String(50), nullable=False)
    template_data = Column(JSONB, nullable=False)
    slides = Column(JSONB)
    hit_count = Column(Integer, default=0)
    last_accessed = Column(DateTime(timezone=True), default=func.now())
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    expires_at = Column(DateTime(timezone=True))
    
    __table_args__ = (
        Index('idx_deck_dna_dept', 'department'),
        Index('idx_deck_dna_expires', 'expires_at'),
    )