#!/usr/bin/env python3
"""
GitHub Repository Management Tool
Uses gh CLI for repo operations.
"""

import subprocess
import json
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


def clone_repo(url: str, path: Optional[str] = None) -> Dict[str, Any]:
    """Clone a GitHub repository."""
    args = ["repo", "clone", url]
    if path:
        args.append(path)
    return run_gh(args)


def create_repo(name: str, private: bool = False, description: str = "") -> Dict[str, Any]:
    """Create a new GitHub repository."""
    args = ["repo", "create", name]
    if private:
        args.append("--private")
    else:
        args.append("--public")
    if description:
        args.extend(["--description", description])
    args.append("--json")
    args.append("name,url,sshUrl")
    return run_gh(args)


def fork_repo(owner: str, repo: str) -> Dict[str, Any]:
    """Fork a repository."""
    args = ["repo", "fork", f"{owner}/{repo}", "--json", "name,url,sshUrl"]
    return run_gh(args)


def list_repos(org: Optional[str] = None, limit: int = 30) -> Dict[str, Any]:
    """List repositories."""
    args = ["repo", "list", "--limit", str(limit), "--json", "name,url,description,isPrivate,updatedAt"]
    if org:
        args.insert(2, org)
    return run_gh(args)