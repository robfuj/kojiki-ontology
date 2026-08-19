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

Usage: python3 validate.py [--registry reg.json] <record.json> [record2.json ...]
  --registry: JSON mapping of which sibling producers are installed/registered,
              e.g. {"marketing.INTERPRETATION": true}. If omitted, all inputs are
              treated as self-generated (standalone mode) and only the hard
              invariants are checked.
"""
import json, sys, os, argparse

HERE = os.path.dirname(os.path.abspath(__file__))
TRANSFORMATIONS = json.load(open(os.path.join(HERE, "transformations.json")))["transformations"]

LEGAL_STATE_KINDS = set(t.get("state_kind") for t in TRANSFORMATIONS.values())
INDEPENDENT = {"AUDIT", "BRAIN"}

def err(m):
    print("FAIL: " + m)
    return False

def validate(path, registry):
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
    return ok

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--registry", help="JSON file mapping producer keys -> bool (installed?)")
    ap.add_argument("records", nargs="*")
    args = ap.parse_args()
    registry = None
    if args.registry:
        registry = json.load(open(args.registry))
    targets = args.records or [os.path.join(HERE, "example-synapsis-record.json")]
    all_ok = True
    for t in targets:
        print("== " + t)
        try:
            all_ok &= validate(t, registry)
        except Exception as e:
            print("FAIL: " + str(e)); all_ok = False
    print("ALL VALID" if all_ok else "VALIDATION FAILED")
    sys.exit(0 if all_ok else 1)

if __name__ == "__main__":
    main()

