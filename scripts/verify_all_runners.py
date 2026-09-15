#!/usr/bin/env python3
"""Verify all specialists pass."""

import sys
from pathlib import Path
import subprocess

def find_all_specialists():
    """Find all specialist directories (those with __init__.py directly under specialists/)."""
    base = Path("/Users/Fujita/Documents/AI Filing System/decision-systems/kojiki/specialists")
    specialists = []
    for spec_dir in base.iterdir():
        if spec_dir.is_dir() and not spec_dir.name.startswith('.') and (spec_dir / "__init__.py").exists():
            specialists.append(spec_dir.name)
    return specialists

def run_specialist(specialist_name):
    """Run a single specialist and return success/failure."""
    test_dispatch = {
        "task_id": f"verify-{specialist_name}",
        "raw_record": "Test goal for verification",
        "raw_source": {},
        "prior_accepted_evidence": []
    }
    
    import json
    dispatch_file = f"/tmp/dispatch_{specialist_name}.json"
    with open(dispatch_file, 'w') as f:
        json.dump(test_dispatch, f)
    
    try:
        result = subprocess.run(
            [sys.executable, "-m", "kojiki.core.runner", specialist_name, dispatch_file],
            capture_output=True,
            text=True,
            timeout=60,
            cwd="/Users/Fujita/Documents/AI Filing System/decision-systems"
        )
        if result.returncode == 0 and "PIPELINE COMPLETE" in result.stdout:
            return True, None
        else:
            return False, result.stdout[-500:]
    except subprocess.TimeoutExpired:
        return False, "TIMEOUT"
    except Exception as e:
        return False, str(e)

def main():
    specialists = find_all_specialists()
    print(f"Found {len(specialists)} specialists")
    
    results = []
    for specialist in specialists:
        success, error = run_specialist(specialist)
        results.append((specialist, success, error))
        status = "✅" if success else "❌"
        print(f"{status} {specialist}")
        if not success:
            print(f"    Error: {error}")
    
    passed = sum(1 for r in results if r[1])
    failed = len(results) - passed
    
    print(f"\n{'='*50}")
    print(f"PASSED: {passed}/{len(specialists)}")
    print(f"FAILED: {failed}/{len(specialists)}")
    
    if failed > 0:
        print("\nFailures:")
        for specialist, success, error in results:
            if not success:
                print(f"  {specialist}: {error}")
        sys.exit(1)
    else:
        print("\n✅ ALL SPECIALISTS PASSED")
        sys.exit(0)

if __name__ == "__main__":
    main()