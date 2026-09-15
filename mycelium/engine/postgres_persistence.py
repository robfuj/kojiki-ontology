#!/usr/bin/env python3
"""
PostgreSQL Persistence Layer for Kojiki Decision System.

Replaces JSON file storage with proper relational database.
Supports all MYCELIUM engines: Registry, Propagate, Reinforcement, Sentinel, Kaizen.
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from contextlib import contextmanager
import psycopg2
from psycopg2.extras import RealDictCursor, Json
from psycopg2.pool import SimpleConnectionPool

# Connection pool
_pool: Optional[SimpleConnectionPool] = None
_pool_dsn: Optional[str] = None


def init_pool(dsn: str = None, minconn: int = 1, maxconn: int = 10) -> SimpleConnectionPool:
    """Initialize global connection pool."""
    global _pool, _pool_dsn
    dsn = dsn or os.environ.get("KOJIKI_DSN", "postgresql://localhost/kojiki")
    _pool = SimpleConnectionPool(minconn, maxconn, dsn)
    _pool_dsn = dsn
    return _pool


def get_pool(dsn: str = None) -> SimpleConnectionPool:
    """Get global connection pool, initializing if needed."""
    global _pool, _pool_dsn
    if _pool is None:
        dsn = dsn or os.environ.get("KOJIKI_DSN", "postgresql://localhost/kojiki")
        _pool = init_pool(dsn)
    return _pool


@contextmanager
def get_conn():
    """Get a connection from the pool."""
    pool = get_pool()
    conn = pool.getconn()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        pool.putconn(conn)


@contextmanager
def get_cursor(commit: bool = True):
    """Get a cursor with automatic commit/rollback."""
    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            try:
                yield cur
                if commit:
                    conn.commit()
            except Exception:
                conn.rollback()
                raise


# =============================================================================
# SCHEMA DEFINITIONS
# =============================================================================

SCHEMA_SQL = """
-- ============================================================
-- KOJIKI DECISION SYSTEM - POSTGRESQL SCHEMA
-- ============================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================
-- MYCELIUM REGISTRY
-- ============================================================

CREATE TABLE IF NOT EXISTS mycelium_nodes (
    id VARCHAR(255) PRIMARY KEY,
    domain VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL DEFAULT 'agent',
    status VARCHAR(50) NOT NULL DEFAULT 'active',
    pipeline_manifest_ref VARCHAR(500),
    pipeline_validated BOOLEAN DEFAULT FALSE,
    public_key TEXT NOT NULL,
    key_status VARCHAR(50) NOT NULL DEFAULT 'active',
    key_issued_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    key_revoked_at TIMESTAMPTZ,
    parent_id VARCHAR(255) REFERENCES mycelium_nodes(id),
    decision_rights JSONB,
    decision_right VARCHAR(255),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_nodes_parent ON mycelium_nodes(parent_id);
CREATE INDEX IF NOT EXISTS idx_nodes_decision_right ON mycelium_nodes(decision_right);
CREATE INDEX IF NOT EXISTS idx_nodes_status ON mycelium_nodes(status);

-- Node lifecycle audit log
CREATE TABLE IF NOT EXISTS mycelium_node_audit (
    id BIGSERIAL PRIMARY KEY,
    event_type VARCHAR(50) NOT NULL,
    node_id VARCHAR(255) NOT NULL REFERENCES mycelium_nodes(id),
    actor VARCHAR(255) NOT NULL,
    detail JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_node_audit_node ON mycelium_node_audit(node_id);
CREATE INDEX IF NOT EXISTS idx_node_audit_event ON mycelium_node_audit(event_type);

-- ============================================================
-- MYCELIUM EDGES (PROPAGATE/REINFORCEMENT)
-- ============================================================

CREATE TABLE IF NOT EXISTS mycelium_edges (
    id BIGSERIAL PRIMARY KEY,
    from_kr VARCHAR(255) NOT NULL REFERENCES mycelium_nodes(id),
    to_kr VARCHAR(255) NOT NULL REFERENCES mycelium_nodes(id),
    weight DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    reciprocal_exchanges INTEGER NOT NULL DEFAULT 0,
    one_directional_exchanges INTEGER NOT NULL DEFAULT 0,
    last_reinforced TIMESTAMPTZ,
    trigger_event VARCHAR(255),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(from_kr, to_kr)
);

CREATE INDEX IF NOT EXISTS idx_edges_from ON mycelium_edges(from_kr);
CREATE INDEX IF NOT EXISTS idx_edges_to ON mycelium_edges(to_kr);
CREATE INDEX IF NOT EXISTS idx_edges_weight ON mycelium_edges(weight);

-- Edge exchange log (for reinforcement history)
CREATE TABLE IF NOT EXISTS mycelium_edge_exchanges (
    id BIGSERIAL PRIMARY KEY,
    edge_id BIGINT REFERENCES mycelium_edges(id),
    from_kr VARCHAR(255) NOT NULL,
    to_kr VARCHAR(255) NOT NULL,
    exchange_type VARCHAR(50) NOT NULL, -- 'reciprocal' or 'one_directional'
    signal_id VARCHAR(255),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================
-- MYCELIUM SIGNALS (PROPAGATE)
-- ============================================================

CREATE TABLE IF NOT EXISTS mycelium_signals (
    id VARCHAR(255) PRIMARY KEY,
    origin_kr VARCHAR(255) NOT NULL REFERENCES mycelium_nodes(id),
    event VARCHAR(100) NOT NULL,
    signal_kind VARCHAR(50) NOT NULL, -- 'failure', 'request'
    new_status VARCHAR(50),
    diagnosed_cause TEXT,
    diagnosed_cause_category VARCHAR(100),
    status VARCHAR(50) NOT NULL DEFAULT 'ROUTED',
    subgraph JSONB NOT NULL DEFAULT '[]',
    signature TEXT NOT NULL,
    fired_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_signals_origin ON mycelium_signals(origin_kr);
CREATE INDEX IF NOT EXISTS idx_signals_kind ON mycelium_signals(signal_kind);
CREATE INDEX IF NOT EXISTS idx_signals_fired ON mycelium_signals(fired_at);

-- ============================================================
-- SENTINEL PROVENANCE
-- ============================================================

CREATE TABLE IF NOT EXISTS sentinel_experiences (
    id VARCHAR(255) PRIMARY KEY,
    problem_id VARCHAR(255),
    hypothesis TEXT NOT NULL,
    agents TEXT[] NOT NULL,
    action TEXT NOT NULL,
    expected TEXT NOT NULL,
    observed TEXT NOT NULL,
    error_classification VARCHAR(100),
    escalation JSONB,
    redefinition JSONB,
    learning_ref VARCHAR(255),
    propagation_targets TEXT[],
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS sentinel_provenance_tokens (
    id VARCHAR(255) PRIMARY KEY,
    payload_hash VARCHAR(64) NOT NULL,
    prev_entry_id VARCHAR(255),
    signer VARCHAR(255) NOT NULL,
    signature TEXT NOT NULL,
    payload JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_tokens_prev ON sentinel_provenance_tokens(prev_entry_id);
CREATE INDEX IF NOT EXISTS idx_tokens_signer ON sentinel_provenance_tokens(signer);

CREATE TABLE IF NOT EXISTS sentinel_gate_evidence (
    id BIGSERIAL PRIMARY KEY,
    gate_request_id VARCHAR(255) NOT NULL,
    experience_id VARCHAR(255) NOT NULL REFERENCES sentinel_experiences(id),
    signer VARCHAR(255) NOT NULL,
    signature TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(gate_request_id, experience_id, signer)
);

CREATE TABLE IF NOT EXISTS sentinel_gate_requests (
    id VARCHAR(255) PRIMARY KEY,
    experience_id VARCHAR(255) NOT NULL REFERENCES sentinel_experiences(id),
    problem_id VARCHAR(255) NOT NULL,
    layer VARCHAR(20) NOT NULL, -- L0, L1, L2, L3, L4
    status VARCHAR(50) NOT NULL DEFAULT 'PENDING',
    decided_by VARCHAR(255),
    decided_at TIMESTAMPTZ,
    decision VARCHAR(50),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS sentinel_node_lifecycle (
    id BIGSERIAL PRIMARY KEY,
    event_type VARCHAR(50) NOT NULL,
    node_id VARCHAR(255) NOT NULL,
    actor VARCHAR(255) NOT NULL,
    detail JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================
-- NEURAXIS ESCALATION
-- ============================================================

CREATE TABLE IF NOT EXISTS neuraxis_escalations (
    id VARCHAR(255) PRIMARY KEY,
    problem_id VARCHAR(255) NOT NULL,
    experience_id VARCHAR(255) REFERENCES sentinel_experiences(id),
    error_class VARCHAR(20) NOT NULL, -- L0, L1, L2, L3, L4
    repetition_count INTEGER NOT NULL DEFAULT 0,
    sla_deadline TIMESTAMPTZ,
    status VARCHAR(50) NOT NULL DEFAULT 'OPEN',
    gate_request_id VARCHAR(255) REFERENCES sentinel_gate_requests(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    resolved_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_escalations_problem ON neuraxis_escalations(problem_id);
CREATE INDEX IF NOT EXISTS idx_escalations_status ON neuraxis_escalations(status);

-- ============================================================
-- SYNAPSIS PIPELINE RECORDS
-- ============================================================

CREATE TABLE IF NOT EXISTS synapsis_problems (
    problem_id VARCHAR(255) PRIMARY KEY,
    dispatch_id VARCHAR(255) NOT NULL,
    goal TEXT NOT NULL,
    context JSONB,
    assumptions TEXT[],
    constraints TEXT[],
    unknowns TEXT[],
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS synapsis_evidence (
    finding_id VARCHAR(255) PRIMARY KEY,
    problem_id VARCHAR(255) REFERENCES synapsis_problems(problem_id),
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    source VARCHAR(255),
    confidence DOUBLE PRECISION,
    retrieval_state VARCHAR(50),
    coverage_limits TEXT,
    sufficiency VARCHAR(50),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS synapsis_interpretations (
    interpretation_id VARCHAR(255) PRIMARY KEY,
    problem_id VARCHAR(255) REFERENCES synapsis_problems(problem_id),
    synthesis TEXT NOT NULL,
    confidence DOUBLE PRECISION,
    key_drivers TEXT[],
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS synapsis_strategies (
    strategy_id VARCHAR(255) PRIMARY KEY,
    problem_id VARCHAR(255) REFERENCES synapsis_problems(problem_id),
    interpretation_ref VARCHAR(255) REFERENCES synapsis_interpretations(interpretation_id),
    objective TEXT NOT NULL,
    rationale TEXT NOT NULL,
    timeline TEXT,
    success_criteria JSONB NOT NULL,
    escalation_conditions TEXT[],
    decision_rights JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS synapsis_outputs (
    output_id VARCHAR(255) PRIMARY KEY,
    strategy_id VARCHAR(255) REFERENCES synapsis_strategies(strategy_id),
    content JSONB NOT NULL,
    measurement_window JSONB,
    confidence DOUBLE PRECISION,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS synapsis_decks (
    deck_id VARCHAR(255) PRIMARY KEY,
    output_id VARCHAR(255) REFERENCES synapsis_outputs(output_id),
    deck_ref VARCHAR(255),
    mode VARCHAR(50),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS synapsis_outcomes (
    outcome_id VARCHAR(255) PRIMARY KEY,
    output_id VARCHAR(255) REFERENCES synapsis_outputs(output_id),
    actuals JSONB NOT NULL,
    evaluations JSONB NOT NULL,
    outcome_score DOUBLE PRECISION,
    target_met BOOLEAN,
    converged BOOLEAN,
    iteration_count INTEGER,
    guardrail_violations JSONB,
    deviation_analysis TEXT,
    confidence DOUBLE PRECISION,
    kaizen_iteration INTEGER,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS synapsis_learning (
    learning_id VARCHAR(255) PRIMARY KEY,
    cycle_timestamp TIMESTAMPTZ NOT NULL,
    experiences JSONB NOT NULL,
    patterns TEXT[],
    reusable_insights TEXT[],
    redefinitions JSONB,
    outcome_score DOUBLE PRECISION,
    guardrail_violations JSONB,
    confidence DOUBLE PRECISION,
    kaizen_iteration INTEGER,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================
-- KAIZEN LOOP
-- ============================================================

CREATE TABLE IF NOT EXISTS kaizen_iterations (
    id BIGSERIAL PRIMARY KEY,
    problem_id VARCHAR(255) REFERENCES synapsis_problems(problem_id),
    iteration INTEGER NOT NULL,
    phase VARCHAR(20) NOT NULL,
    started_at TIMESTAMPTZ NOT NULL,
    completed_at TIMESTAMPTZ,
    input_data JSONB,
    output_data JSONB,
    guardrail_violations JSONB,
    learning_generated BOOLEAN DEFAULT FALSE,
    experience_refs TEXT[],
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_kaizen_problem ON kaizen_iterations(problem_id);

-- ============================================================
-- CAUSAL CHAIN
-- ============================================================

CREATE TABLE IF NOT EXISTS causal_chains (
    chain_id VARCHAR(255) PRIMARY KEY,
    dispatch_id VARCHAR(255) NOT NULL,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    total_tokens BIGINT DEFAULT 0,
    total_latency_ms BIGINT DEFAULT 0,
    final_problem_id VARCHAR(255),
    final_output_id VARCHAR(255),
    final_learning_id VARCHAR(255),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS causal_nodes (
    id VARCHAR(255) PRIMARY KEY,
    chain_id VARCHAR(255) REFERENCES causal_chains(chain_id),
    stage VARCHAR(50) NOT NULL,
    artifact_type VARCHAR(50) NOT NULL,
    artifact_id VARCHAR(255) NOT NULL,
    content_hash VARCHAR(64) NOT NULL,
    content JSONB NOT NULL,
    agent_id VARCHAR(255),
    tools TEXT[],
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_causal_chain ON causal_nodes(chain_id);

CREATE TABLE IF NOT EXISTS causal_transitions (
    id BIGSERIAL PRIMARY KEY,
    chain_id VARCHAR(255) REFERENCES causal_chains(chain_id),
    from_stage VARCHAR(50) NOT NULL,
    to_stage VARCHAR(50) NOT NULL,
    input_hash VARCHAR(64) NOT NULL,
    output_hash VARCHAR(64) NOT NULL,
    agent_id VARCHAR(255) NOT NULL,
    signer VARCHAR(255),
    signature TEXT,
    public_key TEXT,
    input_summary TEXT,
    output_summary TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================
-- UPDATED_AT TRIGGER
-- ============================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS update_nodes_updated_at ON mycelium_nodes;
CREATE TRIGGER update_nodes_updated_at
    BEFORE UPDATE ON mycelium_nodes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_edges_updated_at ON mycelium_edges;
CREATE TRIGGER update_edges_updated_at
    BEFORE UPDATE ON mycelium_edges
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
"""


def apply_schema(dsn: str = None):
    """Apply the schema to the database."""
    dsn = dsn or os.environ.get("KOJIKI_DSN", "postgresql://localhost/kojiki")
    conn = psycopg2.connect(dsn)
    conn.autocommit = True
    try:
        with conn.cursor() as cur:
            cur.execute(SCHEMA_SQL)
        print("Schema applied successfully")
    finally:
        conn.close()


if __name__ == "__main__":
    apply_schema()