---
name: specialist-github-autodiscovery
category: software-development
description: Use when specialist has gap. Finds and secures GitHub repo.
---

# Specialist GitHub Auto-Discovery with Security Audit

Each specialist continuously discovers, evaluates, and securely integrates GitHub repositories.

## Trigger
- Capability gap detected during execution
- Scheduled weekly discovery run
- New requirement from Chief of Staff decomposition

## Auto-Discovery Loop with Security Gate

```python
class GitHubAutoDiscovery:
    def __init__(self, specialist_name: str, domain_keywords: List[str]):
        self.specialist = specialist_name
        self.keywords = domain_keywords
    
    def discover(self) -> List[RepoCandidate]:
        pass
    
    def evaluate(self, repo: RepoCandidate) -> RepoScore:
        pass
    
    def security_audit(self, repo: RepoCandidate) -> SecurityReport:
        pass
    
    def integrate(self, repo: RepoCandidate) -> ToolWrapper:
        pass
```

## Security Gate Criteria

| Severity | Action |
|----------|--------|
| CRITICAL | Block integration |
| HIGH | Require manual review |
| MEDIUM | Warn, allow with monitoring |
| LOW | Allow |

## Capability Manifest

Each specialist maintains `capability_manifest.json`:
```json
{
  "specialist": "marketing-brand",
  "capabilities": [
    {
      "name": "meta_ads_management",
      "source": "github.com/facebook/facebook-python-business-sdk",
      "version": "18.0.0",
      "security_audit": {
        "scan_date": "2026-09-11",
        "critical": 0, "high": 0, "medium": 2, "low": 5
      },
      "tools": ["create_campaign", "get_insights"],
      "pinned_version": "18.0.0"
    }
  ],
  "gaps": ["tiktok_ads_api"],
  "last_discovery_run": "2026-09-11T10:00:00Z"
}
```

## Security Tools Used
- Static: bandit, semgrep, codeql
- Dependencies: pip-audit, npm audit, cargo audit, osv-scanner
- Secrets: trufflehog, gitleaks
- Supply chain: sigstore verify, SLSA verifier
- License: clearlydefined, licensee

## Integration with Mycelium
- Specialist publishes new capabilities as signals
- Security audit results shared via Mycelium edges
- Chief of Staff queries capabilities + audit status for decomposition