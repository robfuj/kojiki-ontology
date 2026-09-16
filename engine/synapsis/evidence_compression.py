"""
Evidence Compression - Reduces token usage in EVIDENCE stage while preserving verified extracts.

Compression strategies:
1. Field selection - only include essential fields for downstream stages
2. Answer truncation - keep core answer, drop qualifiers
3. Deduplication - merge findings answering same question
4. Template compression - use standardized formats
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import json


class CompressionLevel(str, Enum):
    NONE = "none"           # Full finding objects
    MINIMAL = "minimal"     # finding_id, question, answer only
    REFERENCE = "reference" # finding_id + reference to full evidence store
    SUMMARY = "summary"     # Aggregated answers by question theme


@dataclass
class EvidenceCompressor:
    """Compresses evidence findings for token-efficient downstream consumption."""
    
    compression_level: CompressionLevel = CompressionLevel.MINIMAL
    max_answer_length: int = 120  # chars
    max_findings: int = 10
    
    def compress(self, evidence_output: Dict[str, Any]) -> Dict[str, Any]:
        """Compress evidence findings based on configured level."""
        findings = evidence_output.get("findings", [])
        
        if self.compression_level == CompressionLevel.NONE:
            return evidence_output
        
        elif self.compression_level == CompressionLevel.MINIMAL:
            return self._compress_minimal(findings)
        
        elif self.compression_level == CompressionLevel.REFERENCE:
            return self._compress_reference(findings)
        
        elif self.compression_level == CompressionLevel.SUMMARY:
            return self._compress_summary(findings)
        
        return evidence_output
    
    def _compress_minimal(self, findings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Keep only essential fields: finding_id, question, answer (truncated)."""
        compressed = []
        for f in findings[:self.max_findings]:
            compressed.append({
                "finding_id": f.get("finding_id"),
                "question": f.get("question"),
                "answer": self._truncate_answer(f.get("answer", "")),
            })
        return {"findings": compressed}
    
    def _compress_reference(self, findings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Return finding IDs only - full objects stored in evidence store."""
        compressed = []
        for f in findings[:self.max_findings]:
            compressed.append({
                "finding_id": f.get("finding_id"),
                "question": f.get("question"),
            })
        return {"findings": compressed, "_reference": "full_evidence_store"}
    
    def _compress_summary(self, findings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Group by question theme, aggregate answers."""
        # Simple grouping by first keyword of question
        themes = {}
        for f in findings:
            q = f.get("question", "").lower()
            # Extract theme from question
            theme = self._extract_theme(q)
            if theme not in themes:
                themes[theme] = []
            themes[theme].append(f)
        
        summary = []
        for theme, findings_in_theme in themes.items():
            answers = [f.get("answer", "") for f in findings_in_theme]
            summary.append({
                "theme": theme,
                "finding_count": len(findings_in_theme),
                "combined_answer": " | ".join(answers[:3]),  # Max 3 answers
                "finding_ids": [f.get("finding_id") for f in findings_in_theme],
            })
        
        return {"themes": summary, "total_findings": len(findings)}
    
    def _extract_theme(self, question: str) -> str:
        """Extract theme from question for grouping."""
        keywords = ["conversion", "revenue", "cost", "pipeline", "cac", "ltv", "churn", "retention", "source", "channel"]
        for kw in keywords:
            if kw in question:
                return kw
        # Fallback: first noun-like word
        words = question.split()
        for w in words:
            if len(w) > 4:
                return w
        return "general"
    
    def _truncate_answer(self, answer: str) -> str:
        """Truncate answer to max length, preserving key numbers."""
        if len(answer) <= self.max_answer_length:
            return answer
        # Try to truncate at sentence boundary
        truncated = answer[:self.max_answer_length]
        last_period = truncated.rfind(".")
        if last_period > self.max_answer_length * 0.5:
            return truncated[:last_period + 1]
        return truncated + "..."


# Integration helper for runner
def compress_evidence_for_stage(evidence_output: Dict[str, Any], 
                                 target_stage: str,
                                 level: CompressionLevel = CompressionLevel.MINIMAL) -> Dict[str, Any]:
    """
    Compress evidence for a specific downstream stage.
    
    Args:
        evidence_output: Full evidence output from EVIDENCE stage
        target_stage: "interpretation", "strategy", "output", "deck"
        level: Compression level
    """
    compressor = EvidenceCompressor(compression_level=level)
    compressed = compressor.compress(evidence_output)
    
    # Add metadata for downstream
    compressed["_compression"] = {
        "level": level.value,
        "original_count": len(evidence_output.get("findings", [])),
        "target_stage": target_stage,
    }
    
    return compressed


if __name__ == "__main__":
    # Test compression
    sample_evidence = {
        "findings": [
            {
                "finding_id": "FE-001",
                "question": "What is the current lead-to-opportunity conversion rate by source?",
                "answer": "Q3 2026: organic=12%, paid=8%, referral=23%, email=5%",
                "source": "CRM export",
                "confidence": 0.95,
                "retrieval_state": "RETRIEVED",
                "coverage_limits": "Q3 2026 only",
                "sufficiency": "SUFFICIENT"
            },
            {
                "finding_id": "FE-002", 
                "question": "What is the referral pipeline QoQ growth?",
                "answer": "Referral pipeline grew +18% QoQ after incentive program launch in Q3",
                "source": "Analytics Dashboard",
                "confidence": 0.9,
                "retrieval_state": "RETRIEVED",
                "coverage_limits": "Q3 2026",
                "sufficiency": "SUFFICIENT"
            },
            {
                "finding_id": "FE-003",
                "question": "What is the paid CAC delta vs target?",
                "answer": "Paid CAC reduced -18% vs -20% target, within 10% of goal",
                "source": "Finance Reports",
                "confidence": 0.85,
                "retrieval_state": "RETRIEVED",
                "coverage_limits": "Q3 2026",
                "sufficiency": "INSUFFICIENT"
            }
        ]
    }
    
    for level in CompressionLevel:
        print(f"\n=== {level.value.upper()} ===")
        compressor = EvidenceCompressor(compression_level=level)
        result = compressor.compress(sample_evidence)
        print(json.dumps(result, indent=2))
    
    # Test helper
    print("\n=== HELPER (INTERPRETATION) ===")
    result = compress_evidence_for_stage(sample_evidence, "interpretation", CompressionLevel.MINIMAL)
    print(json.dumps(result, indent=2))