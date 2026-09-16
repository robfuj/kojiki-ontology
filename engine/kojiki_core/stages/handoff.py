#!/usr/bin/env python3
"""
Handoff Runtime Engine
Executes cross-department handoffs defined in specialist configs.
"""

import json
import importlib.util
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from engine.kojiki_core import load_specialist, ScopedContext
# PipelineRunner imported locally to avoid circular import


@dataclass
class HandoffPayload:
    """A handoff payload between departments."""
    source_dept: str
    target_dept: str
    trigger: str
    payload: Dict[str, Any]
    schema: str


class HandoffEngine:
    """Manages cross-department handoff execution."""
    
    def __init__(self, dispatch: Dict[str, Any]):
        self.dispatch = dispatch
        self.specialists_dir = Path(__file__).parent.parent.parent / "specialists"
        self.handoff_history: List[Dict] = []
    
    def discover_handoffs(self, specialist_name: str) -> List[Dict[str, Any]]:
        """Discover handoffs defined in a specialist's config."""
        specialist = load_specialist(specialist_name)
        config = specialist.config if hasattr(specialist, 'config') else {}
        handoffs = config.get('handoffs', [])
        return handoffs
    
    def validate_payload(self, payload: Dict[str, Any], schema_path: str) -> bool:
        """Validate handoff payload against schema."""
        schema_file = self.specialists_dir / schema_path
        if not schema_file.exists():
            return True  # No schema = skip validation
        
        import jsonschema
        try:
            schema = json.loads(schema_file.read_text())
            jsonschema.validate(payload, schema)
            return True
        except Exception:
            return False
    
    def execute_handoff(self, handoff: Dict[str, Any], source_output: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single handoff to target department."""
        source_dept = handoff.get('source_dept', self.dispatch.get('department', 'unknown'))
        target_dept = handoff.get('target')
        trigger = handoff.get('trigger')
        schema_path = handoff.get('payload_schema')
        
        if not target_dept:
            return {"error": "No target department specified"}
        
        # Map target department to specialist name
        target_specialist_map = {
            "finance-accounting": "finance-accounting",
            "marketing-brand": "marketing-brand",
            "sales-outbound": "sales-outbound",
            "engineering-platform": "engineering-platform",
            "operations-ops": "operations-ops",
            "legal-compliance": "legal-compliance",
            "people-hr": "people-hr",
            "ai-intelligence": "ai-intelligence",
            "Finance": "finance-accounting",
            "Marketing": "marketing-brand",
            "Sales": "sales-outbound",
            "Engineering": "engineering-platform",
            "Operations": "operations-ops",
            "Legal": "legal-compliance",
            "People & Comms": "people-hr",
            "Technology Platform": "ai-intelligence",
            "AI Intelligence": "ai-intelligence",
        }
        
        target_specialist = target_specialist_map.get(target_dept)
        if not target_specialist:
            return {"error": f"Unknown target department: {target_dept}"}
        
        # Build handoff payload from source output
        payload = self._build_payload(handoff, source_output)
        
        # Validate against schema if provided
        if schema_path and not self.validate_payload(payload, schema_path):
            return {"error": f"Payload validation failed for schema: {schema_path}"}
        
        # Execute target specialist with handoff payload
        handoff_dispatch = {
            **self.dispatch,
            "task_id": f"{self.dispatch.get('task_id', 'handoff')}.{target_specialist}",
            "handoff": {
                "source": source_dept,
                "target": target_dept,
                "trigger": trigger,
                "payload": payload
            },
            "raw_record": payload.get("description", f"Handoff from {source_dept}: {trigger}"),
            "raw_source": payload,
            "prior_accepted_evidence": [],
        }
        
        try:
            target_specialist_obj = load_specialist(target_specialist)
            from kojiki.core.runner import PipelineRunner
            runner = PipelineRunner(target_specialist_obj, handoff_dispatch)
            
            import asyncio
            result = asyncio.run(runner.run())
            
            # Record handoff
            self.handoff_history.append({
                "source": source_dept,
                "target": target_dept,
                "trigger": trigger,
                "status": "completed",
                "result_summary": self._summarize_result(result)
            })
            
            return {
                "status": "completed",
                "target_specialist": target_specialist,
                "result": result
            }
            
        except Exception as e:
            self.handoff_history.append({
                "source": source_dept,
                "target": target_dept,
                "trigger": trigger,
                "status": "failed",
                "error": str(e)
            })
            return {"error": str(e)}
    
    def _build_payload(self, handoff: Dict[str, Any], source_output: Dict[str, Any]) -> Dict[str, Any]:
        """Build handoff payload from source output and handoff config."""
        trigger = handoff.get('trigger', '')
        
        # Default payload includes key source output fields
        payload = {
            "trigger": trigger,
            "source_department": handoff.get('source_dept', 'unknown'),
            "description": f"Handoff triggered by {trigger}",
        }
        
        # Add relevant source output data based on trigger type
        if 'strategy' in source_output:
            payload['strategy'] = source_output['strategy']
        if 'output' in source_output:
            payload['output'] = source_output['output']
        if 'interpretation' in source_output:
            payload['interpretation'] = source_output['interpretation']
        if 'evidence' in source_output:
            payload['evidence'] = source_output['evidence']
        
        return payload
    
    def _summarize_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Summarize handoff result."""
        return {
            "adjudication": result.get("adjudication"),
            "has_output": "output" in result,
            "has_delegation": "delegation" in result,
        }
    
    def execute_all_handoffs(self, source_specialist: str, source_output: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute all handoffs for a source specialist."""
        handoffs = self.discover_handoffs(source_specialist)
        results = []
        
        for handoff in handoffs:
            result = self.execute_handoff(handoff, source_output)
            results.append(result)
        
        return results
    
    def get_handoff_history(self) -> List[Dict[str, Any]]:
        """Get handoff execution history."""
        return self.handoff_history


async def run_handoff_stage(
    runner,
    dispatch: Dict[str, Any],
    context: ScopedContext,
    department: str
) -> Dict[str, Any]:
    """
    Execute HANDOFF stage - process cross-department handoffs.
    Runs after DELEGATION stage.
    """
    print("\n--- STAGE 5.7: HANDOFF ---")
    
    specialist = runner.specialist
    handoff_config = specialist.stages.get("handoff")
    if not handoff_config or not getattr(handoff_config, "enabled", True):
        print("  Handoff stage disabled")
        return {"handoff_skipped": True, "reason": "Disabled in config"}
    
    # Check if this specialist has handoffs
    handoffs = getattr(specialist, 'config', {}).get('handoffs', [])
    if not handoffs:
        print("  No handoffs configured for this specialist")
        return {"handoff_skipped": True, "reason": "No handoffs defined"}
    
    # Get source output (from OUTPUT or DELEGATION stage)
    source_output = {}
    for stage in ["delegation", "output", "strategy", "interpretation"]:
        stage_output = context.stage_outputs.get(stage, {})
        if stage_output:
            source_output.update(stage_output)
    
    if not source_output:
        print("  No source output available for handoffs")
        return {"handoff_skipped": True, "reason": "No source output"}
    
    # Execute handoffs
    engine = HandoffEngine(dispatch)
    print(f"  Executing {len(handoffs)} handoff(s)...")
    
    results = engine.execute_all_handoffs(specialist.name, source_output)
    
    # Store in context
    context.set_stage_output("handoff", {
        "handoffs_executed": len(results),
        "results": results,
        "history": engine.get_handoff_history()
    })
    
    print(f"  Handoff complete: {len(results)} executed")
    
    return {
        "handoffs_executed": len(results),
        "results": results
    }