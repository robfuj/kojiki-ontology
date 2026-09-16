#!/usr/bin/env python3
"""
Kojiki Core Runner - Slim orchestrator (500 lines)

Executes the 8-stage SYNAPSIS pipeline for any specialist.
All stage logic extracted to engine/kojiki_core/stages/
"""

import json
import sys
import importlib.util
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent))

from engine.kojiki_core import (
    Specialist, ScopedContext, load_specialist
)

# Import KeyManager from sentinel
SENTINEL_PATH = Path(__file__).parent.parent.parent / "engine" / "sentinel" / "sentinel.py"
if SENTINEL_PATH.exists():
    spec = importlib.util.spec_from_file_location("sentinel", SENTINEL_PATH)
    sentinel_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(sentinel_module)
    KeyManager = sentinel_module.KeyManager
else:
    KeyManager = None

# Import StageName from core module (single source of truth)
from . import StageName, CausalChainRunner

# Import stage executors
from engine.kojiki_core.stages import (
    run_saccade_stage,
    run_evidence_stage,
    run_interpretation_stage,
    run_strategy_stage,
    run_output_stage,
    run_delegation_stage,
    run_handoff_stage,
    run_mycelium_stage,
    run_deck_stage,
    run_outcome_stage,
    run_learning_stage,
    finalize_causal_chain,
    adjudicate
)

# Import registry
POSTGRES_REGISTRY_PATH = Path(__file__).parent.parent.parent / "engine" / "mycelium" / "postgres_registry.py"
PostgresNodeRegistry = None
if POSTGRES_REGISTRY_PATH.exists():
    try:
        spec = importlib.util.spec_from_file_location("postgres_registry", POSTGRES_REGISTRY_PATH)
        postgres_registry_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(postgres_registry_module)
        PostgresNodeRegistry = postgres_registry_module.PostgresNodeRegistry
    except Exception:
        PostgresNodeRegistry = None

REGISTRY_PATH = Path(__file__).parent.parent.parent / "engine" / "mycelium" / "registry.py"
NodeRegistry = None
if REGISTRY_PATH.exists():
    try:
        spec = importlib.util.spec_from_file_location("registry", REGISTRY_PATH)
        registry_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(registry_module)
        NodeRegistry = registry_module.NodeRegistry
    except Exception:
        NodeRegistry = None


class PipelineRunner:
    """Slim pipeline orchestrator - executes stages in order."""
    
    STAGE_EXECUTORS = [
        ("saccade", run_saccade_stage),
        ("evidence", run_evidence_stage),
        ("interpretation", run_interpretation_stage),
        ("strategy", run_strategy_stage),
        ("output", run_output_stage),
        ("delegation", run_delegation_stage),
        ("handoff", run_handoff_stage),
        ("mycelium", run_mycelium_stage),
        ("deck", run_deck_stage),
        ("outcome", run_outcome_stage),
        ("learning", run_learning_stage),
    ]
    
    def __init__(self, specialist: Specialist, dispatch: Dict[str, Any]):
        self.specialist = specialist
        self.dispatch = dispatch
        self.department = specialist.name.split("-")[0] if "-" in specialist.name else specialist.name
        
        # SENTINEL KeyManager for signing
        self.key_manager = KeyManager() if KeyManager else None
        
        # Causal chain builder
        self.chain_builder = None
        if StageName and CausalChainRunner:
            self.chain_builder = CausalChainRunner(
                dispatch.get("task_id", "unknown"), 
                key_manager=self.key_manager
            )
        
        # Registry for Decision Rights
        self.registry = None
        if PostgresNodeRegistry:
            self.registry = PostgresNodeRegistry()
        elif NodeRegistry:
            REGISTRY_FILE = Path(__file__).parent.parent.parent / "engine" / "mycelium" / "registry" / "nodes.json"
            if REGISTRY_FILE.parent.exists():
                self.registry = NodeRegistry(str(REGISTRY_FILE))
        
        # Schema validator
        self.schema_validator = None
        VALIDATOR_PATH = Path(__file__).parent.parent.parent / "engine" / "synapsis" / "schema_validator.py"
        if VALIDATOR_PATH.exists():
            spec = importlib.util.spec_from_file_location("schema_validator", VALIDATOR_PATH)
            validator_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(validator_module)
            SchemaValidator = validator_module.SchemaValidator
            self.schema_validator = SchemaValidator()
        
        # Context management
        self.context = ScopedContext(dispatch)
    
    async def run(self) -> Dict[str, Any]:
        """Execute the full 8-stage pipeline."""
        print(f"=== {self.specialist.name.upper()} PIPELINE EXECUTION ===")
        print(f"Dispatch: {self.dispatch.get('task_id', 'unknown')}")
        
        # Execute each stage
        for stage_name, executor in self.STAGE_EXECUTORS:
            try:
                await executor(self, self.dispatch, self.context, self.department)
            except Exception as e:
                print(f"  ERROR in {stage_name}: {e}")
                raise
        
        # Finalize causal chain
        await finalize_causal_chain(self, self.dispatch)
        
        # Adjudication
        return await adjudicate(self, self.dispatch, self.department)


def run_pipeline(specialist_name: str, dispatch: Dict[str, Any]) -> Dict[str, Any]:
    """Entry point: load specialist and run pipeline."""
    specialist = load_specialist(specialist_name)
    runner = PipelineRunner(specialist, dispatch)
    
    # Run async pipeline
    import asyncio
    return asyncio.run(runner.run())


def main():
    """CLI entry point: python -m engine.kojiki_core.runner <specialist> <dispatch.json>"""
    if len(sys.argv) < 3:
        print("Usage: python -m engine.kojiki_core.runner <specialist_name> <dispatch_json_file>")
        sys.exit(1)
    
    specialist_name = sys.argv[1]
    dispatch_file = sys.argv[2]
    
    with open(dispatch_file) as f:
        dispatch = json.load(f)
    
    result = run_pipeline(specialist_name, dispatch)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()