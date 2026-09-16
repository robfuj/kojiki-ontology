#!/usr/bin/env python3
"""
GitHub Tools for SYNAPSIS Pipeline
Wraps all GitHub skill modules for use as tools.
"""

import sys
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add skills directory to path
SKILLS_DIR = Path(__file__).parent.parent.parent.parent / "skills" / "github-autodiscovery"
sys.path.insert(0, str(SKILLS_DIR))
sys.path.insert(0, str(Path(__file__).parent))

# Import all github modules
try:
    from github_repo_management import clone_repo, create_repo, fork_repo, list_repos
    from github_issues import create_issue, list_issues, update_issue
    from github_pr_workflow import create_pr, merge_pr, list_prs, get_pr, checkout_pr
    from github_code_review import create_review, submit_review, list_reviews, get_pr_files
    from github_auth import get_auth_status, get_auth_token, login_with_token, logout, refresh_token
    from specialist_github_autodiscovery import discover_specialist_repos, discover_by_topic, get_repo_details
    GITHUB_AVAILABLE = True
    GITHUB_ERROR = ""
except ImportError as e:
    GITHUB_AVAILABLE = False
    GITHUB_ERROR = str(e)


class GitHubTool:
    """Tool wrapper for GitHub operations."""

    @property
    def name(self) -> str:
        return "github"

    def execute(self, context: Any, params: Dict[str, Any]) -> Any:
        """Execute GitHub operation."""
        if not GITHUB_AVAILABLE:
            return {"error": f"GitHub skills not available: {GITHUB_ERROR}"}

        action = params.get("action", "list_repos")

        try:
            if action == "clone_repo":
                return clone_repo(params.get("url"), params.get("path"))
            elif action == "create_repo":
                return create_repo(params.get("name"), params.get("private", False), params.get("description", ""))
            elif action == "fork_repo":
                return fork_repo(params.get("owner"), params.get("repo"))
            elif action == "list_repos":
                return list_repos(params.get("org"), params.get("limit", 30))
            elif action == "create_issue":
                return create_issue(params.get("repo"), params.get("title"), params.get("body", ""), params.get("labels"), params.get("assignees"))
            elif action == "list_issues":
                return list_issues(params.get("repo"), params.get("state", "open"), params.get("limit", 30), params.get("labels"))
            elif action == "update_issue":
                return update_issue(params.get("repo"), params.get("issue_number"), params.get("updates", {}))
            elif action == "create_pr":
                return create_pr(params.get("repo"), params.get("title"), params.get("head"), params.get("base", "main"), params.get("body", ""), params.get("draft", False))
            elif action == "merge_pr":
                return merge_pr(params.get("repo"), params.get("pr_number"), params.get("merge_method", "squash"), params.get("delete_branch", True))
            elif action == "list_prs":
                return list_prs(params.get("repo"), params.get("state", "open"), params.get("limit", 30))
            elif action == "get_pr":
                return get_pr(params.get("repo"), params.get("pr_number"))
            elif action == "checkout_pr":
                return checkout_pr(params.get("repo"), params.get("pr_number"))
            elif action == "create_review":
                return create_review(params.get("repo"), params.get("pr_number"), params.get("body"), params.get("event", "COMMENT"), params.get("comments"))
            elif action == "submit_review":
                return submit_review(params.get("repo"), params.get("pr_number"), params.get("review_id"), params.get("event", "APPROVE"))
            elif action == "list_reviews":
                return list_reviews(params.get("repo"), params.get("pr_number"))
            elif action == "get_pr_files":
                return get_pr_files(params.get("repo"), params.get("pr_number"))
            elif action == "get_auth_status":
                return get_auth_status()
            elif action == "get_auth_token":
                return get_auth_token(params.get("scopes"))
            elif action == "login_with_token":
                return login_with_token(params.get("token"))
            elif action == "logout":
                return logout()
            elif action == "refresh_token":
                return refresh_token()
            else:
                return {"error": f"Unknown GitHub action: {action}"}
        except Exception as e:
            return {"error": str(e)}


class SpecialistGitHubAutodiscoveryTool:
    """Tool for auto-discovering specialist repositories."""

    @property
    def name(self) -> str:
        return "specialist_github_autodiscovery"

    def execute(self, context: Any, params: Dict[str, Any]) -> Any:
        """Discover GitHub repos for a specialist domain."""
        if not GITHUB_AVAILABLE:
            return {"error": f"GitHub skills not available: {GITHUB_ERROR}"}

        domain = params.get("domain", context.get("department", "").lower())
        keywords = params.get("keywords", [])
        limit = params.get("limit", 10)

        return discover_specialist_repos(domain, keywords, limit)


class GitHubTopicDiscoveryTool:
    """Tool for discovering repos by topics."""

    @property
    def name(self) -> str:
        return "github_topic_discovery"

    def execute(self, context: Any, params: Dict[str, Any]) -> Any:
        """Discover GitHub repos by topics."""
        if not GITHUB_AVAILABLE:
            return {"error": f"GitHub skills not available: {GITHUB_ERROR}"}

        topics = params.get("topics", [])
        limit = params.get("limit", 10)

        return discover_by_topic(topics, limit)


class GitHubRepoDetailsTool:
    """Tool for getting repo details."""

    @property
    def name(self) -> str:
        return "github_repo_details"

    def execute(self, context: Any, params: Dict[str, Any]) -> Any:
        """Get repository details."""
        if not GITHUB_AVAILABLE:
            return {"error": f"GitHub skills not available: {GITHUB_ERROR}"}

        owner = params.get("owner")
        repo = params.get("repo")

        return get_repo_details(owner, repo)


# Export for direct import
github = GitHubTool()
specialist_github_autodiscovery = SpecialistGitHubAutodiscoveryTool()
github_topic_discovery = GitHubTopicDiscoveryTool()
github_repo_details = GitHubRepoDetailsTool()