#!/usr/bin/env python3
"""
GitHub PR Workflow Tool
Uses gh CLI for PR operations.
"""

import subprocess
import json
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


def create_pr(repo: str, title: str, head: str, base: str = "main", body: str = "", draft: bool = False) -> Dict[str, Any]:
    """Create a pull request."""
    args = ["pr", "create", "--repo", repo, "--title", title, "--head", head, "--base", base]
    if body:
        args.extend(["--body", body])
    if draft:
        args.append("--draft")
    args.extend(["--json", "number,title,url,state,headRefName,baseRefName"])
    return run_gh(args)


def merge_pr(repo: str, pr_number: int, merge_method: str = "squash", delete_branch: bool = True) -> Dict[str, Any]:
    """Merge a pull request."""
    args = ["pr", "merge", str(pr_number), "--repo", repo, "--merge" if merge_method == "merge" else f"--{merge_method}"]
    if delete_branch:
        args.append("--delete-branch")
    args.extend(["--json", "merged,mergeCommit"])
    return run_gh(args)


def list_prs(repo: str, state: str = "open", limit: int = 30) -> Dict[str, Any]:
    """List pull requests."""
    args = ["pr", "list", "--repo", repo, "--state", state, "--limit", str(limit), "--json", "number,title,state,headRefName,baseRefName,author,createdAt"]
    return run_gh(args)


def get_pr(repo: str, pr_number: int) -> Dict[str, Any]:
    """Get PR details."""
    args = ["pr", "view", str(pr_number), "--repo", repo, "--json", "number,title,body,state,headRefName,baseRefName,author,files,commits,reviews"]
    return run_gh(args)


def checkout_pr(repo: str, pr_number: int) -> Dict[str, Any]:
    """Checkout a PR locally."""
    args = ["pr", "checkout", str(pr_number), "--repo", repo]
    return run_gh(args)