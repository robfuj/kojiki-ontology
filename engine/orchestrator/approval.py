#!/usr/bin/env python3
"""
Approval Channel — Pluggable approval mechanism for Phase 7 gate.

Supports:
- CLI interactive approval
- Webhook callback (for Vercel UI)
- Auto-approval (test mode)
- Fail-closed default
"""

import asyncio
import json
import os
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass, asdict


@dataclass
class ApprovalRequest:
    """Request for user approval."""
    orchestration_id: str
    raw_goal: str
    execution_results: Dict[str, Any]
    retry_count: int
    created_at: str
    expires_at: Optional[str] = None


@dataclass
class ApprovalDecision:
    """User's decision on approval request."""
    approved: bool
    feedback: str
    decided_at: str
    decided_by: str


class ApprovalChannel(ABC):
    """Abstract base for approval channels."""

    @abstractmethod
    async def request_approval(self, request: ApprovalRequest) -> ApprovalDecision:
        """Request approval and return decision."""
        pass


class CLIApprovalChannel(ApprovalChannel):
    """Interactive CLI approval (for local development)."""

    def __init__(self, timeout_seconds: int = 300):
        self.timeout_seconds = timeout_seconds

    async def request_approval(self, request: ApprovalRequest) -> ApprovalDecision:
        print(f"\n{'='*60}")
        print(f"APPROVAL REQUEST: {request.orchestration_id}")
        print(f"{'='*60}")
        print(f"Goal: {request.raw_goal}")
        print(f"Retry: {request.retry_count}/{3}")
        print("\nExecution Results:")
        for dept, result in request.execution_results.items():
            outcome = result.get("outcome", {})
            print(f"  {dept}: score={outcome.get('outcome_score', 0):.2f}, converged={outcome.get('converged', False)}")

        print("\nOptions:")
        print("  [a] Approve - continue to completion")
        print("  [r] Reject - re-loop with feedback")
        print("  [f] Fail - return unapproved result")

        # Use asyncio to add timeout
        try:
            choice = await asyncio.wait_for(
                asyncio.get_event_loop().run_in_executor(None, input, "\nDecision [a/r/f]: "),
                timeout=self.timeout_seconds
            )
        except asyncio.TimeoutError:
            print(f"\nTimeout after {self.timeout_seconds}s — FAILING CLOSED")
            return ApprovalDecision(
                approved=False,
                feedback="Timeout — no response",
                decided_at=datetime.utcnow().isoformat() + "Z",
                decided_by="system_timeout"
            )

        choice = choice.strip().lower()
        if choice == "a":
            return ApprovalDecision(
                approved=True,
                feedback="Approved via CLI",
                decided_at=datetime.utcnow().isoformat() + "Z",
                decided_by="cli_user"
            )
        elif choice == "r":
            feedback = input("Feedback for re-loop: ").strip() or "Rejected via CLI"
            return ApprovalDecision(
                approved=False,
                feedback=feedback,
                decided_at=datetime.utcnow().isoformat() + "Z",
                decided_by="cli_user"
            )
        else:
            return ApprovalDecision(
                approved=False,
                feedback="Failed via CLI",
                decided_at=datetime.utcnow().isoformat() + "Z",
                decided_by="cli_user"
            )


class WebhookApprovalChannel(ApprovalChannel):
    """Webhook-based approval for Vercel UI integration.

    Flow:
    1. Orchestrator POSTs approval request to webhook URL
    2. Webhook stores request and returns immediately
    3. Vercel UI polls /api/approval/status or receives push
    4. User clicks Approve/Reject in UI
    4. UI POSTs decision to /api/approval/decide
    5. Channel resolves the pending future
    """

    def __init__(
        self,
        webhook_url: str,
        decision_callback_url: str,
        secret: str,
        timeout_seconds: int = 3600,
        poll_interval: int = 5
    ):
        self.webhook_url = webhook_url
        self.decision_callback_url = decision_callback_url
        self.secret = secret
        self.timeout_seconds = timeout_seconds
        self.poll_interval = poll_interval
        self._pending: Dict[str, asyncio.Future] = {}

    async def request_approval(self, request: ApprovalRequest) -> ApprovalDecision:
        # Create future to wait for decision
        future = asyncio.get_event_loop().create_future()
        self._pending[request.orchestration_id] = future

        # Send webhook notification
        await self._send_webhook(request)

        try:
            # Wait for decision with timeout
            decision = await asyncio.wait_for(future, timeout=self.timeout_seconds)
            return decision
        except asyncio.TimeoutError:
            print(f"Approval timeout for {request.orchestration_id} — FAILING CLOSED")
            return ApprovalDecision(
                approved=False,
                feedback=f"Approval timeout after {self.timeout_seconds}s",
                decided_at=datetime.utcnow().isoformat() + "Z",
                decided_by="webhook_timeout"
            )
        finally:
            self._pending.pop(request.orchestration_id, None)

    async def _send_webhook(self, request: ApprovalRequest):
        """Send approval request to webhook."""
        try:
            import aiohttp
            payload = {
                "type": "approval_request",
                "orchestration_id": request.orchestration_id,
                "raw_goal": request.raw_goal,
                "execution_results": request.execution_results,
                "retry_count": request.retry_count,
                "callback_url": self.decision_callback_url,
                "secret": self.secret
            }
            async with aiohttp.ClientSession() as session:
                async with session.post(self.webhook_url, json=payload) as resp:
                    if resp.status != 200:
                        print(f"Webhook failed: {resp.status}")
        except Exception as e:
            print(f"Webhook error: {e}")

    def receive_decision(self, orchestration_id: str, approved: bool, feedback: str, decided_by: str):
        """Called by webhook handler when UI posts decision."""
        future = self._pending.get(orchestration_id)
        if future and not future.done():
            decision = ApprovalDecision(
                approved=approved,
                feedback=feedback,
                decided_at=datetime.utcnow().isoformat() + "Z",
                decided_by=decided_by
            )
            future.set_result(decision)


class AutoApprovalChannel(ApprovalChannel):
    """Auto-approval for test mode - approves if all converged."""

    def __init__(self, require_all_converged: bool = True):
        self.require_all_converged = require_all_converged

    async def request_approval(self, request: ApprovalRequest) -> ApprovalDecision:
        all_converged = all(
            r.get("outcome", {}).get("converged", False)
            for r in request.execution_results.values()
        )

        if self.require_all_converged and all_converged:
            return ApprovalDecision(
                approved=True,
                feedback="Auto-approved: all departments converged",
                decided_at=datetime.utcnow().isoformat() + "Z",
                decided_by="auto_test_mode"
            )

        return ApprovalDecision(
            approved=False,
            feedback="Auto-rejected: not all converged" if self.require_all_converged else "Auto-approved (lenient)",
            decided_at=datetime.utcnow().isoformat() + "Z",
            decided_by="auto_test_mode"
        )


class FailClosedApprovalChannel(ApprovalChannel):
    """Fail-closed approval - always rejects unless explicitly configured."""

    async def request_approval(self, request: ApprovalRequest) -> ApprovalDecision:
        return ApprovalDecision(
            approved=False,
            feedback="No approval channel configured — FAILING CLOSED for safety",
            decided_at=datetime.utcnow().isoformat() + "Z",
            decided_by="fail_closed"
        )


def create_approval_channel(channel_type: Optional[str] = None) -> ApprovalChannel:
    """Factory function to create approval channel based on config."""
    channel_type = channel_type or os.environ.get("KOJIKI_APPROVAL_CHANNEL", "fail_closed")

    if channel_type == "cli":
        return CLIApprovalChannel()
    elif channel_type == "webhook":
        return WebhookApprovalChannel(
            webhook_url=os.environ.get("KOJIKI_WEBHOOK_URL", ""),
            decision_callback_url=os.environ.get("KOJIKI_DECISION_CALLBACK_URL", ""),
            secret=os.environ.get("KOJIKI_WEBHOOK_SECRET", ""),
            timeout_seconds=int(os.environ.get("KOJIKI_APPROVAL_TIMEOUT", "3600"))
        )
    elif channel_type == "auto":
        return AutoApprovalChannel(require_all_converged=True)
    elif channel_type == "auto_lenient":
        return AutoApprovalChannel(require_all_converged=False)
    else:
        return FailClosedApprovalChannel()


# Webhook handler for Vercel API routes
async def handle_approval_webhook(request_data: Dict[str, Any], channel: WebhookApprovalChannel) -> Dict[str, Any]:
    """Handle incoming approval webhook from orchestrator."""
    # Verify secret
    if request_data.get("secret") != channel.secret:
        return {"error": "Invalid secret", "status": 401}

    orchestration_id = request_data.get("orchestration_id")
    if not orchestration_id:
        return {"error": "Missing orchestration_id", "status": 400}

    # Store for polling
    # In production, use Redis or database
    approval_requests[orchestration_id] = request_data

    return {"status": "received", "orchestration_id": orchestration_id}


async def handle_decision_webhook(
    orchestration_id: str,
    decision_data: Dict[str, Any],
    channel: WebhookApprovalChannel
) -> Dict[str, Any]:
    """Handle decision from Vercel UI."""
    if orchestration_id not in approval_requests:
        return {"error": "Unknown orchestration_id", "status": 404}

    approved = decision_data.get("approved", False)
    feedback = decision_data.get("feedback", "")
    decided_by = decision_data.get("decided_by", "vercel_ui")

    channel.receive_decision(orchestration_id, approved, feedback, decided_by)

    return {"status": "decided", "orchestration_id": orchestration_id}


# In-memory store for demo (use Redis in production)
approval_requests: Dict[str, Dict] = {}


def get_pending_approvals() -> Dict[str, Any]:
    """Get all pending approval requests."""
    return approval_requests