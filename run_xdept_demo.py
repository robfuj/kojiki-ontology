#!/usr/bin/env python3
"""
Cross-department SYNAPSIS proof on local Ollama (qwen2.5:14b).
Scenario: Marketing INTERPRETATION feeds Sales STRATEGY.

Two runs of the Sales bot:
  (A) sibling-present: consumes marketing.INTERPRETATION as 'sibling-verified'
  (B) standalone: marketing absent -> synthesizes interpretation, tags 'self-generated'

Proves the standalone guarantee + provenance enforcement at runtime.
Outputs + validator results saved to 00-kojiki-ontology/evaluations/run-xdept-001/.
"""
import json, os, re, subprocess, sys, urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))
SYN = os.path.join(ROOT, "synapsis")
VALIDATOR = os.path.join(SYN, "validate.py")
MODEL = "qwen2.5:14b"
OUT = os.path.join(ROOT, "evaluations", "run-xdept-001")
os.makedirs(OUT, exist_ok=True)

def ollama(system, user, temperature=0.2):
    payload = {"model": MODEL, "messages": [
        {"role": "system", "content": system},
        {"role": "user", "content": user}], "temperature": temperature, "stream": False}
    req = urllib.request.Request("http://127.0.0.1:11434/api/chat",
        data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=300) as r:
        return json.loads(r.read().decode())["message"]["content"]

def extract_json(text):
    m = re.search(r"\{.*\}", text, re.DOTALL)
    return json.loads(m.group(0)) if m else None

# ---- Marketing bot: INTERPRETATION ----
print("=== Marketing bot: RECORD -> EVIDENCE -> INTERPRETATION ===")
mkt_sys = """You are the Marketing department agent (Kojiki Decision System, SYNAPSIS substrate).
Run transformations RECORD, EVIDENCE, then INTERPRETATION for this signal:
'SaaS benchmark report shows our category's buyers now shortlist 3 vendors in week 1 and decide by week 3; they distrust vendor-written ROI claims.'
Output ONE json: {"record":..., "evidence":..., "interpretation":...}. Interpretation answers:
what does accepted evidence mean for Marketing's segmentation/messaging question? Output only JSON."""
mkt = ollama(mkt_sys, "Produce the three transformation outputs now.", temperature=0.2)
mkt_obj = extract_json(mkt)
print(json.dumps(mkt_obj, indent=2)[:900])
open(os.path.join(OUT, "marketing-interpretation.json"), "w").write(json.dumps(mkt_obj, indent=2))

# ---- Sales bot: STRATEGY, sibling-present ----
print("\n=== Sales bot: STRATEGY (sibling-present, marketing.INTERPRETATION = sibling-verified) ===")
sales_sys_verified = """You are the Sales department agent (Kojiki SYNAPSIS). Produce a STRATEGY transformation.
You have received a sibling-verified input: marketing.INTERPRETATION = """ + json.dumps(mkt_obj.get("interpretation")) + """
Produce ONE json: {"strategy":"...", "consumes":[{"producer":"marketing.INTERPRETATION","state_provenance":"sibling-verified"}]}.
Strategy answers: what is the binding constraint and next customer commitment to seek, given that interpretation? Output only JSON."""
sales_verified = ollama(sales_sys_verified, "Produce STRATEGY now.", temperature=0.2)
sv = extract_json(sales_verified)
record_verified = {
    "synapsis": {"conclusion": sv.get("strategy"), "transformations": [
        {"name": "RECORD", "state_kind": "record", "output": "Category buyer behavior from benchmark report."},
        {"name": "EVIDENCE", "state_kind": "evidence", "output": mkt_obj.get("evidence"), "consumes": [{"producer": "marketing.EVIDENCE", "state_provenance": "sibling-verified"}]},
        {"name": "INTERPRETATION", "state_kind": "interpretation", "output": mkt_obj.get("interpretation"), "consumes": [{"producer": "marketing.INTERPRETATION", "state_provenance": "sibling-verified"}]},
        {"name": "STRATEGY", "state_kind": "strategy", "output": sv.get("strategy"), "consumes": sv.get("consumes", [])},
        {"name": "BRAIN", "state_kind": "coordination", "no_origination": True, "output": "Route to INTERACTION."}
    ]}
}
json.dump(record_verified, open(os.path.join(OUT, "sales-strategy-verified.json"), "w"), indent=2)
print(json.dumps(sv, indent=2)[:600])

# ---- Sales bot: STRATEGY, standalone (marketing absent) ----
print("\n=== Sales bot: STRATEGY (standalone, marketing ABSENT -> self-generated) ===")
sales_sys_standalone = """You are the Sales department agent (Kojiki SYNAPSIS), running STANDALONE (no Marketing sibling installed).
You must synthesize the needed segmentation interpretation yourself, then produce STRATEGY.
Produce ONE json: {"interpretation_self":"...", "strategy":"...", "consumes":[{"producer":"marketing.INTERPRETATION","state_provenance":"self-generated"}]}.
Tag the interpretation input 'self-generated' because the sibling is absent. Output only JSON."""
sales_standalone = ollama(sales_sys_standalone, "Produce STRATEGY from local synthesis now.", temperature=0.2)
sa = extract_json(sales_standalone)
record_standalone = {
    "synapsis": {"conclusion": sa.get("strategy"), "transformations": [
        {"name": "RECORD", "state_kind": "record", "output": "Category buyer behavior (local assumption)."},
        {"name": "EVIDENCE", "state_kind": "evidence", "output": "Local market assumptions (no sibling evidence available).", "consumes": [{"producer": "marketing.EVIDENCE", "state_provenance": "self-generated"}]},
        {"name": "INTERPRETATION", "state_kind": "interpretation", "output": sa.get("interpretation_self"), "consumes": [{"producer": "marketing.INTERPRETATION", "state_provenance": "self-generated"}]},
        {"name": "STRATEGY", "state_kind": "strategy", "output": sa.get("strategy"), "consumes": sa.get("consumes", [])},
        {"name": "BRAIN", "state_kind": "coordination", "no_origination": True, "output": "Route to INTERACTION."}
    ]}
}
json.dump(record_standalone, open(os.path.join(OUT, "sales-strategy-standalone.json"), "w"), indent=2)
print(json.dumps(sa, indent=2)[:600])

# ---- Validate both ----
print("\n=== VALIDATION ===")
reg = os.path.join(OUT, "registry.json")
json.dump({"marketing.INTERPRETATION": True, "marketing.EVIDENCE": True}, open(reg, "w"))
r1 = subprocess.run([sys.executable, VALIDATOR, "--registry", reg, os.path.join(OUT, "sales-strategy-verified.json")], capture_output=True, text=True)
print("[verified mode]"); print(r1.stdout.strip()); print(r1.stderr.strip())
r2 = subprocess.run([sys.executable, VALIDATOR, os.path.join(OUT, "sales-strategy-standalone.json")], capture_output=True, text=True)
print("[standalone mode]"); print(r2.stdout.strip()); print(r2.stderr.strip())

summary = {
    "model": MODEL, "scenario": "marketing.INTERPRETATION -> sales.STRATEGY",
    "sibling_present_valid": "ALL VALID" in r1.stdout,
    "standalone_valid": "ALL VALID" in r2.stdout,
    "marketing_interpretation": mkt_obj.get("interpretation"),
    "sales_strategy_verified": sv.get("strategy"),
    "sales_strategy_standalone": sa.get("strategy"),
}
json.dump(summary, open(os.path.join(OUT, "summary.json"), "w"), indent=2)
print("\nSUMMARY:", json.dumps(summary, indent=2))
