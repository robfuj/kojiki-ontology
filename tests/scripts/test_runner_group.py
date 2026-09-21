#!/usr/bin/env python3
"""Test all runners grouped for parallel CI execution."""

import sys
import os
from pathlib import Path
import subprocess

# Group runners by department for parallel execution
RUNNER_GROUPS = {
    "group1": [
        "01-executive-strategy/bots/strategic-planning",
        "01-executive-strategy/bots/competitive-intelligence",
        "02-finance/bots/accounting",
        "02-finance/bots/treasury",
        "02-finance/bots/fpna",
    ],
    "group2": [
        "02-finance/bots/tax",
        "02-finance/bots/audit",
        "03-marketing/bots/brand",
        "03-marketing/bots/growth",
        "03-marketing/bots/content",
    ],
    "group3": [
        "03-marketing/bots/performance",
        "03-marketing/bots/events",
        "03-marketing/bots/analytics",
        "04-sales/bots/account-management",
        "04-sales/bots/outbound",
    ],
    "group4": [
        "04-sales/bots/sales-operations",
        "04-sales/bots/channel-partnerships",
        "05-business-development/bots/partnerships",
        "05-business-development/bots/m-a",
        "05-business-development/bots/ecosystem",
    ],
    "group5": [
        "06-customer-success/bots/onboarding",
        "06-customer-success/bots/renewals",
        "06-customer-success/bots/expansion",
        "06-customer-success/bots/support",
        "07-product/bots/product-management",
    ],
    "group6": [
        "07-product/bots/product-design",
        "07-product/bots/user-research",
        "07-product/bots/launch",
        "08-engineering-technology/bots/architecture",
        "08-engineering-technology/bots/platform",
    ],
    "group7": [
        "08-engineering-technology/bots/devops",
        "08-engineering-technology/bots/security",
        "08-engineering-technology/bots/data",
        "09-operations/bots/supply-chain",
        "09-operations/bots/facilities",
    ],
}

def run_runner(runner_path):
    """Run a single runner and return success/failure."""
    runner_file = Path(runner_path) / "runner.py"
    if not runner_file.exists():
        return False, f"Runner not found: {runner_file}"
    
    # Create test dispatch
    test_dispatch = {
        "task_id": f"ci-test-{runner_path.replace('/', '-')}",
        "raw_record": {"test": "data"},
        "raw_source": {},
        "prior_accepted_evidence": []
    }
    
    # Write test dispatch to temp file
    import json
    dispatch_file = f"/tmp/dispatch_{runner_path.replace('/', '_')}.json"
    with open(dispatch_file, 'w') as f:
        json.dump(test_dispatch, f)
    
    # Run the runner
    try:
        result = subprocess.run(
            [sys.executable, str(runner_file), dispatch_file],
            capture_output=True,
            text=True,
            timeout=60,
            cwd="/Users/Fujita/Documents/AI Filing System/decision-systems"
        )
        if result.returncode == 0 and "PIPELINE COMPLETE" in result.stdout:
            return True, f"OK: {runner_path}"
        else:
            return False, f"FAIL: {runner_path} - {result.stdout[-500:]}"
    except subprocess.TimeoutExpired:
        return False, f"TIMEOUT: {runner_path}"
    except Exception as e:
        return False, f"ERROR: {runner_path} - {e}"

def main():
    if len(sys.argv) < 2:
        print("Usage: python test_runner_group.py <group_name>")
        sys.exit(1)
    
    group_name = sys.argv[1]
    if group_name not in RUNNER_GROUPS:
        print(f"Unknown group: {group_name}")
        print(f"Available groups: {list(RUNNER_GROUPS.keys())}")
        sys.exit(1)
    
    runners = RUNNER_GROUPS[group_name]
    print(f"Testing group {group_name}: {len(runners)} runners")
    
    results = []
    for runner in runners:
        success, msg = run_runner(runner)
        results.append((success, msg))
        print(msg)
    
    failed = [r for r in results if not r[0]]
    if failed:
        print(f"\n{len(failed)}/{len(runners)} FAILED:")
        for success, msg in failed:
            print(f"  {msg}")
        sys.exit(1)
    else:
        print(f"\nAll {len(runners)} runners PASSED")
        sys.exit(0)

if __name__ == "__main__":
    main()