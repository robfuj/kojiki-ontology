#!/usr/bin/env python3
"""
Schema Validator for SYNAPSIS Pipeline Stages.

Validates stage outputs against JSON schemas. Used by runners to enforce
structured output compliance.
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
from jsonschema import validate, ValidationError, Draft7Validator


class SchemaValidator:
    """Validates SYNAPSIS stage outputs against schemas."""
    
    def __init__(self, schema_root: Path = None):
        if schema_root is None:
            # Default to synapsis/schemas in the ontology
            schema_root = Path(__file__).parent.parent.parent / "00-kojiki-ontology" / "synapsis" / "schemas"
        
        self.schema_root = Path(schema_root)
        self._schemas: Dict[str, Dict] = {}
        self._validators: Dict[str, Draft7Validator] = {}
        self._load_schemas()
    
    def _load_schemas(self):
        """Load all JSON schemas from the schema directory."""
        schema_files = {
            "saccade": "saccade_problem.json",
            "evidence": "evidence_findings.json",
            "interpretation": "interpretation.json",
            "strategy": "strategy.json",
            "output": "output.json",
            "deck": "deck.json",
        }
        
        for stage, filename in schema_files.items():
            path = self.schema_root / filename
            if path.exists():
                with open(path) as f:
                    self._schemas[stage] = json.load(f)
                    self._validators[stage] = Draft7Validator(self._schemas[stage])
            else:
                print(f"Warning: Schema not found: {path}")
        
        # Also check for Kaizen schemas in brand bot
        # Try multiple possible locations
        possible_kaizen_roots = [
            Path(__file__).parent.parent / "03-marketing" / "bots" / "brand" / "schema",
            Path(__file__).parent.parent.parent / "03-marketing" / "bots" / "brand" / "schema",
            Path.cwd() / "03-marketing" / "bots" / "brand" / "schema",
        ]
        
        kaizen_root = None
        for root in possible_kaizen_roots:
            if root.exists():
                kaizen_root = root
                break
        
        if kaizen_root:
            for stage, filename in [("outcome", "outcome.json"), ("learning", "learning.json")]:
                path = kaizen_root / filename
                if path.exists():
                    with open(path) as f:
                        self._schemas[stage] = json.load(f)
                        self._validators[stage] = Draft7Validator(self._schemas[stage])
                    print(f"Loaded Kaizen schema: {stage} from {path}")
                else:
                    print(f"Warning: Kaizen schema not found: {path}")
        else:
            print("Warning: Kaizen schema root not found in any expected location")
    
    def validate(self, stage: str, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate data against stage schema.
        
        Returns:
            (is_valid, error_messages)
        """
        if stage not in self._validators:
            return False, [f"No schema loaded for stage: {stage}"]
        
        validator = self._validators[stage]
        errors = []
        
        for error in validator.iter_errors(data):
            # Format error path
            path = " -> ".join(str(p) for p in error.absolute_path)
            path_str = f" at {path}" if path else ""
            errors.append(f"{error.message}{path_str}")
        
        return len(errors) == 0, errors
    
    def validate_or_raise(self, stage: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and raise on failure, return data on success."""
        valid, errors = self.validate(stage, data)
        if not valid:
            raise ValidationError(f"Stage '{stage}' validation failed:\n" + "\n".join(errors))
        return data
    
    def get_schema(self, stage: str) -> Optional[Dict]:
        """Get raw schema for a stage."""
        return self._schemas.get(stage)
    
    def list_stages(self) -> List[str]:
        """List available stage schemas."""
        return list(self._schemas.keys())


# Stage-specific prompt templates that enforce structured output
STAGE_PROMPTS = {
    "saccade": """You are the SACCADE engine. Frame the problem as structured JSON.

OUTPUT SCHEMA (must match exactly):
{
  "problem_id": "P-XXXXXXXX",
  "goal": "Single sentence goal",
  "constraints": ["constraint 1", "constraint 2"],
  "assumptions": ["assumption 1", "assumption 2"],
  "unknowns": ["unknown 1", "unknown 2"],
  "supersedes": "P-XXXXXXXX-v2",
  "reason": "Why this supersedes previous problem"
}

RULES:
- problem_id: P- + 8 uppercase alphanumeric
- goal: 10-500 chars, one sentence
- constraints: 1-7 items, max 200 chars each
- assumptions: 0-7 items, max 200 chars each  
- unknowns: 0-7 items, max 200 chars each
- NO extra fields, NO markdown, NO explanation

Input: {raw_record}""",

    "evidence": """You are the EVIDENCE engine. Extract findings as structured JSON.

OUTPUT SCHEMA (must match exactly):
{
  "findings": [
    {
      "finding_id": "FE-001",
      "question": "Specific question answered",
      "answer": "Concise one-sentence answer",
      "source": "Source system/document",
      "confidence": 0.9,
      "retrieval_state": "RETRIEVED",
      "coverage_limits": "Known limitations",
      "sufficiency": "SUFFICIENT"
    }
  ]
}

RULES:
- finding_id: FE- + 3 digits
- question: 5-300 chars
- answer: 1-500 chars, ONE SENTENCE
- source: max 200 chars
- confidence: 0.0-1.0
- retrieval_state: RETRIEVED|PARTIAL|MISSING
- sufficiency: SUFFICIENT|INSUFFICIENT|CONTRADICTED
- NO extra fields, NO markdown, NO explanation

Input: {raw_source}, {prior_accepted_evidence}""",

    "interpretation": """You are the INTERPRETATION engine. Synthesize evidence as structured JSON.

OUTPUT SCHEMA (must match exactly):
{
  "synthesis": "Integrated interpretation of all evidence",
  "confidence": 0.85,
  "key_insights": ["insight 1", "insight 2"],
  "contradictions": [
    {
      "finding_ids": ["FE-001", "FE-002"],
      "description": "Nature of contradiction",
      "resolution": "How resolved"
    }
  ],
  "evidence_gaps": ["unanswered question 1"]
}

RULES:
- synthesis: 10-800 chars
- confidence: 0.0-1.0
- key_insights: 1-5 items, max 300 chars each
- contradictions: 0-3 items, finding_ids must be FE-XXX format
- evidence_gaps: 0-5 items
- NO extra fields, NO markdown, NO explanation

Input: {accepted_evidence}""",

    "strategy": """You are the STRATEGY engine. Produce structured JSON.

OUTPUT SCHEMA (must match exactly):
{
  "objective": "Single measurable objective",
  "owner": "Department.Role",
  "actions": [
    {
      "action_id": "ACT-001",
      "description": "Action description",
      "owner": "Department.Role",
      "due_date": "2026-12-31",
      "dependencies": ["ACT-002"]
    }
  ],
  "success_criteria": [
    {
      "name": "criterion_name",
      "metric": "metric_name",
      "target": 0.15,
      "operator": ">=",
      "weight": 1.0
    }
  ],
  "risks": [
    {
      "risk_id": "RSK-001",
      "description": "Risk description",
      "likelihood": 0.3,
      "impact": 0.7,
      "mitigation": "Mitigation plan"
    }
  ],
  "decision_rights": {
    "own": "Department.Role",
    "consult": ["Department.Role"],
    "inform": ["Department.Role"]
  }
}

RULES:
- owner format: Capitalized.Word (e.g., Marketing.Growth)
- action_id: ACT- + 3 digits
- due_date: YYYY-MM-DD
- success_criteria: 1-5 items, operator: >=|<=|==|>|<
- risk_id: RSK- + 3 digits
- likelihood/impact: 0.0-1.0
- decision_rights: own/consult/inform with valid role format
- NO extra fields, NO markdown, NO explanation

Input: {accepted_interpretation}""",

    "output": """You are the OUTPUT engine. Produce structured deliverable as JSON.

OUTPUT SCHEMA (must match exactly):
{
  "output_id": "OUT-001",
  "content": { ...structured content... },
  "confidence": 0.9,
  "format": "json|markdown|deck_plan|email|report",
  "validated_against": "schema_name",
  "trace": {
    "problem_id": "P-XXXXXXXX",
    "evidence_ids": ["FE-001", "FE-002"],
    "strategy_id": "strategy_ref"
  }
}

RULES:
- output_id: OUT- + 3 digits
- content: any valid JSON object
- confidence: 0.0-1.0
- format: one of the enum values
- trace: required fields with correct patterns
- NO extra fields, NO markdown, NO explanation

Input: {accepted_strategy}""",

    "deck": """You are the DECK engine. Plan deck as structured JSON.

OUTPUT SCHEMA (must match exactly):
{
  "deck_id": "DECK-001",
  "mode": "native",
  "status": "planned",
  "plan": {
    "slides": [
      {
        "slide_id": "S-01",
        "title": "Slide Title",
        "layout": "answer_first|mece_grouped|scq_ordered|storyboard|charlie_hills",
        "content_keys": ["key1", "key2"]
      }
    ],
    "framework": "Pyramid Principle|MECE|SCQ|Storyboarding|Charlie Hills",
    "narrative": "High-level narrative arc"
  },
  "dna_ref": "dna-sheet.json",
  "validation": {
    "pyramid_passed": true,
    "mece_passed": true,
    "scq_passed": true,
    "violations": []
  },
  "outputs": {
    "dna_file": "dna-sheet.json",
    "plan_file": "plan.json",
    "draft_pptx": "draft.pptx",
    "final_pptx": "final.pptx",
    "qa_report": "qa-report.json"
  }
}

RULES:
- deck_id: DECK- + 3 digits
- mode: one of 5 enum values
- status: planned|dna_extracted|drafted|qa_passed|finalized
- slides: 3-20 items, slide_id S-XX, layout from enum
- framework: one of 5 consultant frameworks
- validation: all three booleans required
- NO extra fields, NO markdown, NO explanation

Input: {output_content}, {dna_references}, {audience}""",
}


def main():
    """Test validator with sample data."""
    validator = SchemaValidator()
    print(f"Loaded schemas for: {validator.list_stages()}")
    
    # Test saccade schema
    test_problem = {
        "problem_id": "P-ABCDEF12",
        "goal": "Increase referral pipeline by 15% QoQ",
        "constraints": ["2-week deadline", "Use existing CRM fields"],
        "assumptions": ["CRM data accurate", "Good faith engagement"],
        "unknowns": ["Current conversion by source", "Sales definition of quality"]
    }
    
    valid, errors = validator.validate("saccade", test_problem)
    print(f"\nSACCADE test: {'PASS' if valid else 'FAIL'}")
    for e in errors:
        print(f"  - {e}")
    
    # Test evidence schema
    test_evidence = {
        "findings": [{
            "finding_id": "FE-001",
            "question": "What is current lead-to-opportunity conversion by source?",
            "answer": "Q3 2026: organic=12%, paid=8%, referral=23%, email=5%",
            "source": "CRM export",
            "confidence": 0.95,
            "retrieval_state": "RETRIEVED",
            "coverage_limits": "Q3 2026 only",
            "sufficiency": "SUFFICIENT"
        }]
    }
    
    valid, errors = validator.validate("evidence", test_evidence)
    print(f"\nEVIDENCE test: {'PASS' if valid else 'FAIL'}")
    for e in errors:
        print(f"  - {e}")
    
    # Test strategy schema
    test_strategy = {
        "objective": "Double referral pipeline in Q4",
        "owner": "Marketing.Growth",
        "actions": [{
            "action_id": "ACT-001",
            "description": "Launch referral incentive program",
            "owner": "Marketing.Growth",
            "due_date": "2026-10-15",
            "dependencies": []
        }],
        "success_criteria": [{
            "name": "pipeline_growth",
            "metric": "referral_pipeline_qoq",
            "target": 0.15,
            "operator": ">=",
            "weight": 1.0
        }],
        "risks": [{
            "risk_id": "RSK-001",
            "description": "Incentive cost exceeds budget",
            "likelihood": 0.3,
            "impact": 0.6,
            "mitigation": "Cap incentives at $500/referral"
        }],
        "decision_rights": {
            "own": "Marketing.Growth",
            "consult": ["Sales.Outbound"],
            "inform": ["Finance"]
        }
    }
    
    valid, errors = validator.validate("strategy", test_strategy)
    print(f"\nSTRATEGY test: {'PASS' if valid else 'FAIL'}")
    for e in errors:
        print(f"  - {e}")


if __name__ == "__main__":
    main()