#!/usr/bin/env python3
"""
GitHub Auth Tool
Manages GitHub authentication tokens.
"""

import subprocess
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, List


def run_gh(args: List[str]) -> Dict[str, Any]:
    """Run gh CLI command and return parsed JSON."""
    try:
        result = subprocess.run(
            ["gh"] + args,
            capture_output=True,
            text=True,
            timeout=30
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


def get_auth_status() -> Dict[str, Any]:
    """Get current auth status."""
    return run_gh(["auth", "status"])


def get_auth_token(scopes: List[str] = None) -> Dict[str, Any]:
    """Get auth token for specified scopes."""
    args = ["auth", "token"]
    if scopes:
        for scope in scopes:
            args.extend(["--scopes", scope])
    return run_gh(args)


def login_with_token(token: str) -> Dict[str, Any]:
    """Login with a personal access token."""
    # Write token to stdin for gh auth login
    try:
        result = subprocess.run(
            ["gh", "auth", "login", "--with-token"],
            input=token,
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode != 0:
            return {"error": result.stderr}
        return {"success": True}
    except Exception as e:
        return {"error": str(e)}


def logout() -> Dict[str, Any]:
    """Logout from GitHub."""
    return run_gh(["auth", "logout"])


def refresh_token() -> Dict[str, Any]:
    """Refresh the auth token."""
    return run_gh(["auth", "refresh", "--hostname", "github.com"])