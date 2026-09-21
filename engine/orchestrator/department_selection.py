#!/usr/bin/env python3
"""
Department Selection module for Orchestrator — transparent reasoning for which departments handle a goal.
"""

from typing import Dict, List, Any
from dataclasses import dataclass


@dataclass
class DepartmentChoice:
    """Why a department was selected for a goal."""
    department: str
    specialist_name: str
    reason: str
    okr_alignment: str
    confidence: float
    dependencies: List[str]


def select_departments(problem: Dict[str, Any], orientation: Dict[str, Any]) -> List[DepartmentChoice]:
    """
    Phase 3: Department Selection with transparent reasoning.
    
    Maps problem domain to departments with keyword matching and adds cross-department dependencies.
    """
    print("\n--- PHASE 3: DEPARTMENT SELECTION ---")

    # Map problem domain to departments with reasoning
    dept_mapping = {
        "marketing-brand": {
            "keywords": ["brand", "campaign", "lead", "growth", "referral", "paid", "seo", "content"],
            "scope": "Brand, growth, referral, paid media"
        },
        "sales-outbound": {
            "keywords": ["outbound", "bizdev", "corpdev", "pipeline", "conversion", "deal"],
            "scope": "Outbound, growth, Biz Dev, Corp Dev"
        },
        "finance-accounting": {
            "keywords": ["budget", "cac", "roi", "fp&a", "treasury", "revenue", "cost"],
            "scope": "Budget, CAC, ROI, FP&A, treasury"
        },
        "engineering-platform": {
            "keywords": ["product", "tech", "platform", "infrastructure", "referral tech", "api"],
            "scope": "Product, Customer Success, Technology, Referral tech"
        },
        "operations-ops": {
            "keywords": ["supply", "procurement", "ops", "logistics", "fulfillment"],
            "scope": "Supply chain, procurement, day-to-day ops"
        },
        "legal-compliance": {
            "keywords": ["compliance", "risk", "contract", "regulatory", "legal", "gdpr"],
            "scope": "Compliance, Risk, contracts, regulatory"
        },
        "people-hr": {
            "keywords": ["hr", "hiring", "team", "culture", "comms", "internal"],
            "scope": "HR, Internal comms, Public Affairs"
        },
        "ai-intelligence": {
            "keywords": ["ai", "model", "governance", "infosec", "identity", "tools", "ml"],
            "scope": "AI strategy, models, governance, InfoSec, identity, tools"
        }
    }

    problem_text = (problem.get("goal", "") + " " + " ".join(problem.get("constraints", [])) + " " + " ".join(problem.get("assumptions", []))).lower()

    choices = []
    for dept_name, dept_info in dept_mapping.items():
        matches = sum(1 for kw in dept_info["keywords"] if kw in problem_text)
        if matches > 0:
            confidence = min(matches / len(dept_info["keywords"]) * 2, 1.0)
            choice = DepartmentChoice(
                department=dept_name.replace("-", " ").title(),
                specialist_name=dept_name,
                reason=f"Matched {matches}/{len(dept_info['keywords'])} domain keywords: {[kw for kw in dept_info['keywords'] if kw in problem_text]}",
                okr_alignment=f"Aligns with {dept_info['scope']}",
                confidence=confidence,
                dependencies=[]
            )
            choices.append(choice)
            print(f"  ✅ {dept_name} (confidence: {confidence:.1%}) - {choice.reason}")

    # Sort by confidence
    choices.sort(key=lambda c: c.confidence, reverse=True)

    # Add cross-department dependencies
    for i, choice in enumerate(choices):
        if choice.specialist_name == "marketing-brand" and any(c.specialist_name == "sales-outbound" for c in choices):
            choice.dependencies.append("sales-outbound")
        if choice.specialist_name == "sales-outbound" and any(c.specialist_name == "engineering-platform" for c in choices):
            choice.dependencies.append("engineering-platform")
        if choice.specialist_name == "engineering-platform" and any(c.specialist_name == "finance-accounting" for c in choices):
            choice.dependencies.append("finance-accounting")

    return choices