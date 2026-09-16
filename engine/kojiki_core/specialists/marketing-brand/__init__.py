#!/usr/bin/env python3
"""
Marketing Brand Specialist - Domain-specific configuration.

Provides: prompts, tools, validators, adapters, schemas for marketing brand decisions.
"""

from engine.kojiki_core import Specialist, StageConfig, Tool, Validator, Adapter
from typing import Dict, Any, List
from pathlib import Path
import importlib.util

# Import shared tools
from engine.kojiki_core.skills.github_tool import github, specialist_github_autodiscovery

# ============================================================
# SUB-SPECIALIST LOADER
# ============================================================

def load_sub_specialist(sub_agent_name: str) -> Specialist:
    """Dynamically load a sub-specialist module."""
    sub_path = Path(__file__).parent / "sub-agents" / sub_agent_name / "__init__.py"
    if not sub_path.exists():
        raise ValueError(f"Sub-specialist not found: {sub_agent_name}")
    
    spec = importlib.util.spec_from_file_location(f"sub_specialist_{sub_agent_name}", sub_path)
    if spec is None or spec.loader is None:
        raise ValueError(f"Could not load spec for {sub_agent_name}")
    
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    # Find Specialist subclass
    for attr_name in dir(module):
        attr = getattr(module, attr_name)
        if isinstance(attr, type) and issubclass(attr, Specialist) and attr is not Specialist:
            return attr()
    
    raise ValueError(f"No Specialist subclass found in {sub_agent_name}")

# ============================================================
# SPECIALIST TOOLS
# ============================================================

class CRMQuery(Tool):
    """Query CRM for marketing metrics."""
    
    @property
    def name(self) -> str:
        return "crm_query"
    
    def execute(self, context: Any, params: Dict[str, Any]) -> Any:
        # In production: query actual CRM
        return {
            "conversion_by_source": {
                "organic": 0.12,
                "paid": 0.08,
                "referral": 0.23,
                "email": 0.05
            },
            "period": "Q3 2026"
        }


class SEOAudit(Tool):
    """Run SEO audit for content optimization."""
    
    @property
    def name(self) -> str:
        return "seo_audit"
    
    def execute(self, context: Any, params: Dict[str, Any]) -> Any:
        return {
            "technical_score": 87,
            "content_score": 72,
            "backlink_profile": "strong",
            "top_keywords": ["lead generation", "B2B marketing", "conversion optimization"]
        }


class CompetitorIntel(Tool):
    """Gather competitive intelligence."""
    
    @property
    def name(self) -> str:
        return "competitor_intel"
    
    def execute(self, context: Any, params: Dict[str, Any]) -> Any:
        return {
            "competitors": ["CompetitorA", "CompetitorB"],
            "their_channels": ["paid", "content", "events"],
            "gap_analysis": "We underinvest in referral vs competitors"
        }


# ============================================================
# SPECIALIST VALIDATORS
# ============================================================

class BrandVoiceCheck(Validator):
    """Validate output matches brand voice guidelines."""
    
    @property
    def name(self) -> str:
        return "brand_voice_check"
    
    def validate(self, output: Dict[str, Any], context: Any) -> List[Dict[str, Any]]:
        violations = []
        
        # Check for forbidden terms
        forbidden = ["cheap", "discount", "bargain", "low-cost"]
        output_str = str(output).lower()
        
        for term in forbidden:
            if term in output_str:
                violations.append({
                    "validator": self.name,
                    "severity": "warning",
                    "message": f"Brand voice violation: '{term}' not allowed",
                    "suggested_fix": f"Replace with 'value-oriented' or 'accessible'"
                })
        
        return violations


class VarianceCheck(Validator):
    """Validate metrics variance within acceptable bounds."""
    
    @property
    def name(self) -> str:
        return "variance_check"
    
    def validate(self, output: Dict[str, Any], context: Any) -> List[Dict[str, Any]]:
        violations = []
        
        # Check outcome metrics variance
        if "evaluations" in output:
            for eval in output["evaluations"]:
                if "actual" in eval and "target" in eval:
                    actual = eval["actual"]
                    target = eval["target"]
                    if target != 0:
                        variance = abs((actual - target) / target)
                        if variance > 0.15:  # 15% threshold
                            violations.append({
                                "validator": self.name,
                                "severity": "warning",
                                "message": f"High variance on {eval.get('metric')}: {variance:.1%} from target",
                                "suggested_fix": "Investigate root cause: measurement error or real deviation?"
                            })
        
        return violations


# ============================================================
# SPECIALIST ADAPTERS
# ============================================================

class HubSpotAdapter(Adapter):
    """HubSpot measurement adapter for marketing metrics."""
    
    @property
    def name(self) -> str:
        return "hubspot"
    
    def fetch_metrics(self, metrics: List[str], window: Dict[str, str]) -> Dict[str, float]:
        # In production: query HubSpot API
        mock_data = {
            "referral_pipeline_qoq": 0.18,
            "paid_cac_delta_pct": -0.18,
            "referral_to_opp_conversion": 0.24,
            "email_open_rate": 0.22,
            "landing_page_conversion": 0.15,
        }
        return {m: mock_data.get(m, 0.0) for m in metrics}


class GA4Adapter(Adapter):
    """Google Analytics 4 adapter."""
    
    @property
    def name(self) -> str:
        return "ga4"
    
    def fetch_metrics(self, metrics: List[str], window: Dict[str, str]) -> Dict[str, float]:
        mock_data = {
            "organic_traffic": 12500,
            "paid_traffic": 8200,
            "conversion_rate": 0.032,
        }
        return {m: mock_data.get(m, 0.0) for m in metrics}


# ============================================================
# SPECIALIST DEFINITION
# ============================================================

class MarketingBrandSpecialist(Specialist):
    """Marketing Brand specialist - handles brand, campaigns, lead quality."""
    
    @property
    def name(self) -> str:
        return "marketing-brand"
    
    @property
    def agent_prefix(self) -> str:
        return "marketing"
    
    @property
    def decision_rights_node(self) -> str:
        return "Marketing.Growth"
    
    @property
    def stages(self) -> Dict[str, StageConfig]:
        base_path = Path(__file__).parent
        
        return {
            "saccade": StageConfig(
                name="saccade",
                prompt=str(base_path / "prompts" / "01-saccade.md"),
                tools=[],
                schema=str(base_path / "schemas" / "saccade_problem.json"),
            ),
            "evidence": StageConfig(
                name="evidence",
                prompt=str(base_path / "prompts" / "02-evidence.md"),
                tools=[CRMQuery(), SEOAudit(), CompetitorIntel(), github, specialist_github_autodiscovery],
                schema=str(base_path / "schemas" / "evidence_findings.json"),
            ),
            "interpretation": StageConfig(
                name="interpretation",
                prompt=str(base_path / "prompts" / "03-interpretation.md"),
                tools=[],
                schema=str(base_path / "schemas" / "interpretation.json"),
            ),
            "strategy": StageConfig(
                name="strategy",
                prompt=str(base_path / "prompts" / "04-strategy.md"),
                tools=[],
                schema=str(base_path / "schemas" / "strategy.json"),
                inputs_allowed=["problem", "evidence", "interpretation", "dept_objective", "team_nodes", "dept_head"],
            ),
            "output": StageConfig(
                name="output",
                prompt=str(base_path / "prompts" / "05-output.md"),
                tools=[],
                schema=str(base_path / "schemas" / "output.json"),
            ),
            "delegation": StageConfig(
                name="delegation",
                prompt=str(base_path / "prompts" / "05-delegation.md"),
                tools=[],
                schema=str(base_path / "schemas" / "delegation.json"),
                inputs_allowed=["output", "strategy", "interpretation"],
                enabled=True,
            ),
            "deck": StageConfig(
                name="deck",
                prompt=str(base_path / "prompts" / "06-deck.md"),
                tools=[],
                schema=str(base_path / "schemas" / "deck.json"),
            ),
            "outcome": StageConfig(
                name="outcome",
                prompt=str(base_path / "prompts" / "07-outcome.md"),
                tools=["measurement_retrieval", "tracking"],
                schema=str(base_path / "schemas" / "outcome.json"),
                validators=[BrandVoiceCheck(), VarianceCheck()],
                adapter=HubSpotAdapter(),
            ),
            "learning": StageConfig(
                name="learning",
                prompt=str(base_path / "prompts" / "08-learning.md"),
                tools=["pattern_extraction", "experience_synthesis"],
                schema=str(base_path / "schemas" / "learning.json"),
            ),
        }


# Register specialist
specialist = MarketingBrandSpecialist()