# Kojiki Core Stages
# Stage executors for the 8-stage SYNAPSIS pipeline

from .saccade import run_saccade_stage
from .evidence import run_evidence_stage
from .interpretation import run_interpretation_stage
from .strategy import run_strategy_stage
from .output import run_output_stage
from .deck import run_deck_stage
from .outcome import run_outcome_stage
from .learning import run_learning_stage, finalize_causal_chain, adjudicate

__all__ = [
    "run_saccade_stage",
    "run_evidence_stage", 
    "run_interpretation_stage",
    "run_strategy_stage",
    "run_output_stage",
    "run_deck_stage",
    "run_outcome_stage",
    "run_learning_stage",
    "finalize_causal_chain",
    "adjudicate",
]