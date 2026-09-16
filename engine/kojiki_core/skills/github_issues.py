#!/usr/bin/env python3
"""
GitHub Issues Tool
Uses gh CLI for issue operations.
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


def create_issue(repo: str, title: str, body: str = "", labels: List[str] = None, assignees: List[str] = None) -> Dict[str, Any]:
    """Create a GitHub issue."""
    args = ["issue", "create", "--repo", repo, "--title", title]
    if body:
        args.extend(["--body", body])
    if labels:
        for label in labels:
            args.extend(["--label", label])
    if assignees:
        for assignee in assignees:
            args.extend(["--assignee", assignee])
    args.extend(["--json", "number,title,url,state"])
    return run_gh(args)


def list_issues(repo: str, state: str = "open", limit: int = 30, labels: List[str] = None) -> Dict[str, Any]:
    """List issues in a repository."""
    args = ["issue", "list", "--repo", repo, "--state", state, "--limit", str(limit), "--json", "number,title,state,labels,assignees,createdAt"]
    if labels:
        for label in labels:
            args.extend(["--label", label])
    return run_gh(args)


def update_issue(repo: str, issue_number: int, updates: Dict[str, Any]) -> Dict[str, Any]:
    """Update an issue."""
    args = ["issue", "edit", str(issue_number), "--repo", repo]
    if "title" in updates:
        args.extend(["--title", updates["title"]])
    if "body" in updates:
        args.extend(["--body", updates["body"]])
    if "state" in updates:
        args.extend(["--state", updates["state"]])
    if "labels" in updates:
        for label in updates["labels"]:
            if label.startswith("+"):
                args.extend(["--add-label", label[1:]])
            elif label.startswith("-"):
                args.extend(["--remove-label", label[1:]])
    if "assignees" in updates:
        for assignee in updates["assignees"]:
            if assignee.startswith("+"):
                args.extend(["--add-assignee", assignee[1:]])
            elif assignee.startswith("-"):
                args.extend(["--remove-assignee", assignee[1:]])
    return run_gh(args)