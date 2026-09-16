#!/usr/bin/env python3
"""
Mycelium Signal Propagation Stage
Propagates signals through the MYCELIUM canopy layer after OUTCOME stage.
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional, Set
from datetime import datetime

from engine.kojiki_core import ScopedContext, StageName
# PipelineRunner imported locally to avoid circular import

# Add mycelium to path
MYCELIUM_PATH = Path(__file__).parent.parent.parent.parent / "00-kojiki-ontology" / "mycelium"
sys.path.insert(0, str(MYCELIUM_PATH / "engine"))

try:
    from propagate import SignalPropagator
    from registry import NodeRegistry
    from sentinel import KeyManager
    MYCELIUM_AVAILABLE = True
except ImportError as e:
    MYCELIUM_AVAILABLE = False
    MYCELIUM_ERROR = str(e)


class MyceliumSignalPropagator:
    """Manages signal propagation through MYCELIUM layer."""
    
    def __init__(self, department: str, dispatch: Dict[str, Any]):
        self.department = department
        self.dispatch = dispatch
        
        # Paths
        base_path = Path(__file__).parent.parent.parent.parent / "00-kojiki-ontology" / "mycelium"
        self.edge_store = base_path / "graph" / "edges.json"
        self.signal_log = base_path / "log" / "signals.jsonl"
        self.registry_path = base_path / "registry" / "nodes.json"
        
        # Initialize propagator
        self.propagator = None
        if MYCELIUM_AVAILABLE:
            try:
                registry = NodeRegistry(str(self.registry_path)) if self.registry_path.exists() else None
                self.propagator = SignalPropagator(
                    edge_store_path=str(self.edge_store),
                    log_path=str(self.signal_log),
                    registry=registry
                )
            except Exception:
                self.propagator = None
    
    def extract_signals_from_outcome(self, outcome: Dict[str, Any], context: ScopedContext) -> List[Dict[str, Any]]:
        """Extract signals from OUTCOME stage result."""
        signals = []
        
        # Get evaluation results
        evaluations = outcome.get("evaluations", [])
        
        for eval in evaluations:
            metric = eval.get("metric")
            actual = eval.get("actual")
            target = eval.get("target")
            operator = eval.get("operator", ">=")
            weight = eval.get("weight", 1.0)
            
            # Determine if target met
            met = False
            if actual is not None and target is not None:
                if operator == ">=":
                    met = actual >= target
                elif operator == "<=":
                    met = actual <= target
                elif operator == "==":
                    met = actual == target
                elif operator == ">":
                    met = actual > target
                elif operator == "<":
                    met = actual < target
            
            # Generate signal if target not met (failure) or for significant events
            if not met or eval.get("signal_on_success", False):
                # Create signal
                kr_id = f"{self.department}.{metric}"
                signal = {
                    "id": f"sig-{datetime.now().strftime('%Y%m%d%H%M%S')}-{metric}",
                    "origin_kr": kr_id,
                    "event": "evaluation",
                    "new_status": "FAILURE" if not met else "SUCCESS",
                    "diagnosed_cause": eval.get("diagnosed_cause", f"{metric} {'missed' if not met else 'met'} target"),
                    "diagnosed_cause_category": eval.get("diagnosed_cause_category", "Threshold"),
                    "status": "ROUTED",
                    "fired_at": datetime.now().isoformat(),
                    "signal_kind": "failure" if not met else "request",
                    "subgraph": [],  # Will be computed by propagator
                    "evaluation": eval,
                }
                signals.append(signal)
        
        return signals
    
    def sign_signal(self, signal: Dict[str, Any]) -> Dict[str, Any]:
        """Sign signal with SENTINEL key."""
        if not MYCELIUM_AVAILABLE:
            return signal
        
        try:
            key_manager = KeyManager()
            # Sign the signal (excluding subgraph which is computed by receiver)
            signal_to_sign = {k: v for k, v in signal.items() if k != 'subgraph'}
            
            from sentinel import canonical_json
            data = canonical_json(signal_to_sign)
            signature = key_manager.sign(data)
            
            signal['signature'] = signature
            signal['signer'] = key_manager.get_public_key()
        except Exception:
            pass
        
        return signal
    
    def propagate_signals(self, signals: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Propagate signals through MYCELIUM layer."""
        if not MYCELIUM_AVAILABLE or not self.propagator:
            return [{"error": "Mycelium not available", "signal": s} for s in signals]
        
        results = []
        for signal in signals:
            # Sign signal
            signed_signal = self.sign_signal(signal)
            
            # Propagate
            result = self.propagator.propagate(signed_signal)
            results.append({
                "signal_id": signal.get("id"),
                "result": result
            })
        
        return results


async def run_mycelium_stage(
    runner,
    dispatch: Dict[str, Any],
    context: ScopedContext,
    department: str
) -> Dict[str, Any]:
    """
    Execute MYCELIUM stage - propagate signals through canopy layer.
    Runs after OUTCOME stage.
    """
    print("\n--- STAGE 7.5: MYCELIUM SIGNAL PROPAGATION ---")
    
    # Check if mycelium is enabled for this specialist
    specialist = runner.specialist
    mycelium_config = specialist.stages.get("mycelium")
    if not mycelium_config or not getattr(mycelium_config, "enabled", True):
        print("  Mycelium stage disabled")
        return {"mycelium_skipped": True, "reason": "Disabled in config"}
    
    # Get OUTCOME stage result
    outcome = context.get_stage_output("outcome")
    if not outcome:
        print("  No OUTCOME result found, skipping mycelium")
        return {"mycelium_skipped": True, "reason": "No OUTCOME result"}
    
    if not MYCELIUM_AVAILABLE:
        print("  Mycelium engine not available")
        return {"mycelium_skipped": True, "reason": f"Mycelium not available: {MYCELIUM_ERROR}"}
    
    # Initialize propagator
    propagator = MyceliumSignalPropagator(department, dispatch)
    
    # Extract signals from outcome
    signals = propagator.extract_signals_from_outcome(outcome, context)
    print(f"  Extracted {len(signals)} signal(s) from outcome")
    
    if not signals:
        print("  No signals to propagate")
        return {"signals_propagated": 0, "results": []}
    
    # Propagate signals
    print(f"  Propagating {len(signals)} signal(s) through MYCELIUM...")
    propagation_results = propagator.propagate_signals(signals)
    
    # Store in context
    context.set_stage_output("mycelium", {
        "signals_generated": len(signals),
        "propagation_results": propagation_results,
    })
    
    successful = sum(1 for r in propagation_results if r.get("result", {}).get("success"))
    print(f"  Mycelium propagation complete: {successful}/{len(signals)} successful")
    
    return {
        "signals_generated": len(signals),
        "propagation_results": propagation_results,
        "successful": successful
    }