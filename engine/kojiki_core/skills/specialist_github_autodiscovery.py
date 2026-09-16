#!/usr/bin/env python3
"""
Specialist GitHub Autodiscovery Tool
Discovers relevant GitHub repositories for specialist domains.
"""

import subprocess
import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional


def run_gh(args: List[str]) -> Dict[str, Any]:
    """Run gh CLI command and return parsed JSON."""
    try:
        result = subprocess.run(
            ["gh"] + args,
            capture_output=True,
            text=True,
            timeout=60
        )
        if result.returncode != 0:
            return {"error": result.stderr}
        try:
            return json.loads(result.stdout) if result.stdout.strip() else {}
        except json.JSONDecodeError:
            return {"output": result.stdout}
    except subprocess.TimeoutExpired:
        return {"error": "Command timed out"}
    except FileNotFoundError:
        return {"error": "gh CLI not found. Install: brew install gh"}


# Domain-specific search keywords
DOMAIN_KEYWORDS = {
    "finance": ["financial-modeling", "accounting", "treasury", "fp&A", "budgeting", "cfo", "investment"],
    "marketing": ["marketing-automation", "analytics", "seo", "social-media", "email-marketing", "brand", "growth"],
    "sales": ["crm", "outreach", "lead-generation", "sales-automation", "pipeline", "proposal"],
    "engineering": ["ci-cd", "infrastructure", "kubernetes", "microservices", "api", "devops", "platform"],
    "operations": ["supply-chain", "procurement", "workflow", "automation", "logistics", "vendor"],
    "legal": ["compliance", "contracts", "policy", "risk", "privacy", "gdpr", "legal-tech"],
    "people": ["hris", "recruiting", "onboarding", "engagement", "payroll", "benefits", "culture"],
    "ai": ["mlops", "llm", "rag", "model-serving", "ai-governance", "ml-pipeline", "vector-db"],
}


def search_repos(query: str, limit: int = 10) -> Dict[str, Any]:
    """Search GitHub repositories."""
    args = ["api", "/search/repositories", "-f", f"q={query}", "-f", f"per_page={limit}"]
    return run_gh(args)


def discover_specialist_repos(domain: str, keywords: List[str] = None, limit: int = 10) -> Dict[str, Any]:
    """Discover GitHub repos relevant to a specialist domain."""
    # Build search query
    domain_keywords = DOMAIN_KEYWORDS.get(domain.lower(), [])
    if keywords:
        search_terms = keywords + domain_keywords
    else:
        search_terms = domain_keywords

    if not search_terms:
        return {"error": f"Unknown domain: {domain}", "available_domains": list(DOMAIN_KEYWORDS.keys())}

    # Build query: topic:keyword1 OR topic:keyword2 ...
    query_parts = [f"topic:{term}" for term in search_terms[:5]]  # Limit to 5 terms
    query = " ".join(query_parts)
    query += " stars:>100"  # Filter for quality

    result = search_repos(query, limit)
    if "error" in result:
        return result

    # Format results
    repos = result.get("items", [])
    formatted = []
    for repo in repos:
        formatted.append({
            "name": repo.get("full_name"),
            "description": repo.get("description"),
            "url": repo.get("html_url"),
            "stars": repo.get("stargazers_count"),
            "language": repo.get("language"),
            "topics": repo.get("topics", []),
            "updated": repo.get("updated_at"),
        })

    return {
        "domain": domain,
        "keywords_used": search_terms[:5],
        "repos_found": len(formatted),
        "repositories": formatted
    }


def discover_by_topic(topics: List[str], limit: int = 10) -> Dict[str, Any]:
    """Discover repos by specific topics."""
    query = " ".join([f"topic:{topic}" for topic in topics])
    query += " stars:>50"
    result = search_repos(query, limit)

    if "error" in result:
        return result

    repos = result.get("items", [])
    formatted = []
    for repo in repos:
        formatted.append({
            "name": repo.get("full_name"),
            "description": repo.get("description"),
            "url": repo.get("html_url"),
            "stars": repo.get("stargazers_count"),
            "language": repo.get("language"),
            "topics": repo.get("topics", []),
        })

    return {
        "topics": topics,
        "repos_found": len(formatted),
        "repositories": formatted
    }


def get_repo_details(owner: str, repo: str) -> Dict[str, Any]:
    """Get detailed information about a repository."""
    args = ["api", f"/repos/{owner}/{repo}"]
    return run_gh(args)


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python specialist_github_autodiscovery.py <domain> [keywords...]")
        sys.exit(1)

    domain = sys.argv[1]
    keywords = sys.argv[2:] if len(sys.argv) > 2 else None
    result = discover_specialist_repos(domain, keywords)
    print(json.dumps(result, indent=2))