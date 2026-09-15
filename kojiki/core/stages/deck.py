#!/usr/bin/env python3
"""
Stage 6: DECK - Deck Generation (via deck-builder skill)
"""

from typing import Dict, Any, Optional, List
from kojiki.core import ScopedContext, StageName
from pathlib import Path
import sys
import json

async def run_deck_stage(
    runner,
    dispatch: Dict[str, Any],
    context: ScopedContext,
    department: str
) -> Dict[str, Any]:
    """Execute DECK stage using deck-builder skill."""
    print("\n--- STAGE 6: DECK ---")
    
    # Import deck-builder bridge - check both locations
    SKILL_DIRS = [
        Path(__file__).parent.parent.parent.parent / ".hermes" / "skills" / "deck-builder",  # User home
        Path(__file__).parent.parent.parent.parent / "00-kojiki-ontology" / "mycelium" / "skills" / "deck-builder",  # Project mycelium
    ]
    
    deck_result = {"error": "deck-builder skill not found"}
    
    for SKILL_DIR in SKILL_DIRS:
        if SKILL_DIR.exists():
            sys.path.insert(0, str(SKILL_DIR))
            try:
                from bridge import run_deck_stage as run_deck
                
                # Collect all context for deck building
                intervention_context = {
                    "accepted_strategy": context.stage_outputs.get("strategy", {}),
                    "accepted_output": context.stage_outputs.get("output", {}),
                    "accepted_interpretation": context.stage_outputs.get("interpretation", {}),
                    "accepted_evidence": dispatch.get("full_evidence", context.stage_outputs.get("evidence", {})),
                    "deck_ref": dispatch.get("accepted_deck"),
                }
                
                deck_result = run_deck(
                    accepted_output=intervention_context,
                    accepted_outcome=dispatch.get("accepted_outcome"),
                    accepted_learning=dispatch.get("accepted_learning"),
                    department=department,
                    mode="native",
                )
                break
            except Exception as e:
                print(f"  Deck builder error: {e}")
                deck_result = {"error": str(e)}
    else:
        deck_result = {"error": "deck-builder skill not found in any known location"}
    
    context.set_stage_output("deck", deck_result)
    
    if runner.chain_builder:
        agent_id = f"{runner.specialist.agent_prefix}.Deck"
        runner.chain_builder.record_stage(
            stage=StageName.DECK,
            input_data=deck_result if isinstance(deck_result, dict) else {},
            output_data=deck_result,
            agent_id=agent_id,
        )
    
    print(f"  Deck result: {deck_result}")
    return deck_result