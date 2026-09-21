#!/usr/bin/env python3
"""Patch all 141 runners to include KeyManager for causal chain signing."""

import sys
from pathlib import Path

# Find all runner.py files
base = Path("/Users/Fujita/Documents/AI Filing System/decision-systems")
runners = list(base.glob("*/bots/*/runner.py"))

print(f"Found {len(runners)} runners to patch")

for runner_path in runners:
    content = runner_path.read_text()
    
    # Skip if already has KeyManager import
    if "KeyManager = sentinel_module.KeyManager" in content:
        print(f"  ⏭️  {runner_path.relative_to(base)} - already patched")
        continue
    
    # 1. Add SENTINEL KeyManager import after Causal Chain import
    old_import = """# Import Causal Chain
CAUSAL_CHAIN_PATH = Path(__file__).parent.parent.parent.parent / "00-kojiki-ontology" / "synapsis" / "causal_chain.py"
if CAUSAL_CHAIN_PATH.exists():
    spec = importlib.util.spec_from_file_location("causal_chain", CAUSAL_CHAIN_PATH)
    causal_chain_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(causal_chain_module)
    CausalChainRunner = causal_chain_module.CausalChainRunner
    StageName = causal_chain_module.StageName
else:
    CausalChainRunner = None
    StageName = None"""

    new_import = """# Import Causal Chain
CAUSAL_CHAIN_PATH = Path(__file__).parent.parent.parent.parent / "00-kojiki-ontology" / "synapsis" / "causal_chain.py"
if CAUSAL_CHAIN_PATH.exists():
    spec = importlib.util.spec_from_file_location("causal_chain", CAUSAL_CHAIN_PATH)
    causal_chain_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(causal_chain_module)
    CausalChainRunner = causal_chain_module.CausalChainRunner
    StageName = causal_chain_module.StageName
else:
    CausalChainRunner = None
    StageName = None

# Import SENTINEL KeyManager for signing
SENTINEL_PATH = Path(__file__).parent.parent.parent.parent / "00-kojiki-ontology" / "mycelium" / "engine" / "sentinel.py"
if SENTINEL_PATH.exists():
    spec = importlib.util.spec_from_file_location("sentinel", SENTINEL_PATH)
    sentinel_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(sentinel_module)
    KeyManager = sentinel_module.KeyManager
else:
    KeyManager = None"""

    if old_import in content:
        content = content.replace(old_import, new_import)
    else:
        # Try alternative format
        alt_old = """# Import Causal Chain
CAUSAL_CHAIN_PATH = Path(__file__).parent.parent.parent.parent / "00-kojiki-ontology" / "synapsis" / "causal_chain.py"
if CAUSAL_CHAIN_PATH.exists():
    spec = importlib.util.spec_from_file_location("causal_chain", CAUSAL_CHAIN_PATH)
    causal_chain_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(causal_chain_module)
    CausalChainRunner = causal_chain_module.CausalChainRunner
    StageName = causal_chain_module.StageName
else:
    CausalChainRunner = None
    StageName = None

# Import evidence compression"""
        if alt_old in content:
            content = content.replace(alt_old, new_import + "\n\n# Import evidence compression")
        else:
            print(f"  ⚠️  {runner_path.relative_to(base)} - import pattern not found")
            continue
    
    # 2. Update chain_builder initialization to include key_manager
    old_init = """    # Initialize causal chain builder
    chain_builder = None
    if CausalChainRunner:
        chain_builder = CausalChainRunner(dispatch.get("task_id", "unknown"))"""

    new_init = """    # Initialize SENTINEL KeyManager for signing
    key_manager = None
    if KeyManager:
        key_manager = KeyManager()
    
    # Initialize causal chain builder
    chain_builder = None
    if CausalChainRunner:
        chain_builder = CausalChainRunner(dispatch.get("task_id", "unknown"), key_manager=key_manager)"""

    if old_init in content:
        content = content.replace(old_init, new_init)
    else:
        # Try alternative
        alt_old2 = """    # Initialize causal chain builder
    chain_builder = None
    if CausalChainRunner:
        chain_builder = CausalChainRunner(dispatch.get("task_id", "unknown"))"""
        if alt_old2 in content:
            content = content.replace(alt_old2, new_init)
        else:
            print(f"  ⚠️  {runner_path.relative_to(base)} - init pattern not found")
            continue
    
    # Write back
    runner_path.write_text(content)
    print(f"  ✅ {runner_path.relative_to(base)}")

print("\nDone!")