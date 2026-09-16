#!/usr/bin/env python3
"""
GitHub Code Review Tool
Uses gh CLI for code review operations.
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


def create_review(repo: str, pr_number: int, body: str, event: str = "COMMENT", comments: List[Dict] = None) -> Dict[str, Any]:
    """Create a code review."""
    args = ["pr", "review", str(pr_number), "--repo", repo, "--body", body, f"--{event.lower()}"]
    if comments:
        # Write comments to temp file for gh
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(comments, f)
            comment_file = f.name
        args.extend(["--comments-file", comment_file])
    args.extend(["--json", "id,state,body,author,submittedAt"])
    return run_gh(args)


def submit_review(repo: str, pr_number: int, review_id: int, event: str = "APPROVE") -> Dict[str, Any]:
    """Submit a pending review."""
    args = ["pr", "review", str(pr_number), "--repo", repo, "--review-id", str(review_id), f"--{event.lower()}"]
    args.extend(["--json", "id,state,body,author,submittedAt"])
    return run_gh(args)


def list_reviews(repo: str, pr_number: int) -> Dict[str, Any]:
    """List reviews on a PR."""
    args = ["pr", "review", "list", str(pr_number), "--repo", repo, "--json", "id,state,body,author,submittedAt"]
    return run_gh(args)


def get_pr_files(repo: str, pr_number: int) -> Dict[str, Any]:
    """Get files changed in a PR."""
    args = ["pr", "view", str(pr_number), "--repo", repo, "--json", "files"]
    return run_gh(args)