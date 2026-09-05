#!/usr/bin/env python3
"""
SYNAPSIS invariant validator (stdlib only). Checks that a transformation record
preserves the SYNAPSIS epistemic boundaries:
  - each transformation carries an explicit state_kind
  - no transformation overwrites an upstream state_kind
  - AUDIT / BRAIN are independent (no_origination) and do not re-implement the
    specialist transformation they review
  - LEARNING proposals are separate from doctrine (never auto-applied)
  - cross-department inputs carry state_provenance; a 'sibling-verified' input
    whose producer is NOT in the supplied registry is flagged (should have fallen
    back to 'self-generated' per the standalone guarantee)
  - MYCELIUM naming/lineage validation (additive hook): non-root node IDs must
    start with parent_id + ".", orphan nodes rejected, 20 root departments unchanged

Usage: python3 validate.py [--registry reg.json] [--mycelium-registry reg.json] <record.json> [record2.json ...]
  --registry: JSON file mapping producer keys -> bool (installed?)
  --mycelium-registry: JSON file mapping node IDs -> {parent, public_key, ...} for lineage validation
"""
import json, sys, os, argparse

HERE = os.path.dirname(os.path.abspath(__file__))
TRANSFORMATIONS = json.load(open(os.path.join(HERE, "transformations.json")))["transformations"]

LEGAL_STATE_KINDS = set(t.get("state_kind") for t in TRANSFORMATIONS.values())
INDEPENDENT = {"AUDIT", "BRAIN"}

# 20 canonical root departments (from Hermes Organizational Decision System Specification)
ROOT_DEPARTMENTS = {
    "Executive.Strategy", "Finance", "Marketing", "Sales", "Business.Development",
    "Customer.Success", "Product", "Engineering.Technology", "Operations",
    "Supply.Chain.Procurement", "Data.Analytics", "AI.Intelligence", "IT",
    "Security", "Legal", "Compliance.Risk", "People.HR", "Corporate.Development",
    "Communications.Public.Affairs", "Executive.Office.Chief.of.Staff"
}

def err(m):
    print("FAIL: " + m)
    return False

def validate_mycelium_naming(mycelium_registry):
    """Validate MYCELIUM node naming and lineage conventions.
    
    This is an additive, separately-callable check per §IV.9 of the thesis.
    """
    ok = True
    if not mycelium_registry:
        return True
    
    for node in mycelium_registry:
        node_id = node.get("id")
        parent_id = node.get("parent")
        
        if not node_id:
            ok = err("MYCELIUM node missing 'id'")
            continue
        
        # Root departments: no parent, must be in canonical set
        if parent_id is None:
            if node_id not in ROOT_DEPARTMENTS:
                ok = err(f"MYCELIUM root node '{node_id}' not in canonical 20 departments")
            continue
        
        # Non-root: must have parent, parent must exist, ID must follow lineage
        if parent_id not in [n.get("id") for n in mycelium_registry]:
            ok = err(f"MYCELIUM node '{node_id}': parent '{parent_id}' not in registry")
            continue
        
        expected_prefix = parent_id + "."
        if not node_id.startswith(expected_prefix) or node_id == parent_id:
            ok = err(f"MYCELIUM node '{node_id}': invalid lineage — must start with '{expected_prefix}'")
    
    # Check for orphan nodes (non-root with no parent)
    for node in mycelium_registry:
        node_id = node.get("id")
        parent_id = node.get("parent")
        if node_id not in ROOT_DEPARTMENTS and parent_id is None:
            ok = err(f"MYCELIUM node '{node_id}': orphan non-root node (missing parent)")
    
    return ok

def validate(path, registry, mycelium_registry=None):
    ok = True
    rec = json.load(open(path))
    steps = rec.get("synapsis", {}).get("transformations", rec.get("transformations", []))
    if not isinstance(steps, list) or not steps:
        return err("no synapsis.transformations array")

    seen_kinds = {}
    for i, step in enumerate(steps):
        name = step.get("name", f"step{i}")
        sk = step.get("state_kind")
        if sk not in LEGAL_STATE_KINDS:
            ok = err(f"{name}: illegal state_kind '{sk}'")
        if step.get("overwrites_upstream_state"):
            ok = err(f"{name}: overwrites an upstream state_kind (invariant violation)")
        seen_kinds[sk] = name
        if name in INDEPENDENT and step.get("reimplements_specialist_transformation"):
            ok = err(f"{name}: re-implements specialist transformation it should only review")
        if name == "LEARNING" and step.get("applied_to_doctrine_directly"):
            ok = err("LEARNING applied a rule change directly to doctrine (must be proposed)")
        # evidence grounding: verifiable evidence MUST cite a source (anti-hallucination)
        spec = TRANSFORMATIONS.get(name, {})
        if spec.get("requires_source_citation") and sk == "evidence":
            etype = step.get("evidence_type")
            if etype == "interaction-derived":
                # v2 reflective step handles this; allowed in v1 but flagged for tracking
                print(f"WARN: {name}: interaction-derived evidence (client-scoped) — reflective step deferred to v2 (ROADMAP.md)")
            else:
                cite = step.get("source_citation") or step.get("citation") or step.get("source")
                if not cite:
                    ok = err(f"{name}: evidence requires_source_citation but has no source_citation/citation/source (cannot verify — hallucination risk)")

        # cross-department provenance enforcement
        for cons in step.get("consumes", []):
            prov = cons.get("state_provenance")
            prod = cons.get("producer")
            if prov not in ("sibling-verified", "self-generated", None):
                ok = err(f"{name}: consumed input '{prod}' has illegal state_provenance '{prov}'")
            if prov == "sibling-verified" and registry is not None and not registry.get(prod):
                ok = err(f"{name}: claims 'sibling-verified' from '{prod}' but producer not in registry (should fall back to self-generated)")

    concl = rec.get("synapsis", {}).get("conclusion")
    if concl:
        if "record" not in seen_kinds:
            ok = err("conclusion has no RECORD origin")
        if "evidence" not in seen_kinds:
            ok = err("conclusion has no EVIDENCE basis")
    
    # MYCELIUM naming/lineage validation (additive hook)
    if mycelium_registry is not None:
        ok &= validate_mycelium_naming(mycelium_registry)
    
    return ok

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--registry", help="JSON file mapping producer keys -> bool (installed?)")
    ap.add_argument("--mycelium-registry", help="JSON file with MYCELIUM node registry for lineage validation")
    ap.add_argument("records", nargs="*")
    args = ap.parse_args()
    registry = None
    if args.registry:
        registry = json.load(open(args.registry))
    mycelium_registry = None
    if args.mycelium_registry:
        mycelium_registry = json.load(open(args.mycelium_registry))
    targets = args.records or [os.path.join(HERE, "example-synapsis-record.json")]
    all_ok = True
    for t in targets:
        print("== " + t)
        try:
            all_ok &= validate(t, registry, mycelium_registry)
        except Exception as e:
            print("FAIL: " + str(e)); all_ok = False
    print("ALL VALID" if all_ok else "VALIDATION FAILED")
    sys.exit(0 if all_ok else 1)

if __name__ == "__main__":
    main()