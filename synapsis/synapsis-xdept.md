# SYNAPSIS Cross-Department Handoff (optional, with fallback)

This document specifies how SYNAPSIS transformations cross department boundaries
**without breaking the standalone-install guarantee**. Read `SYNAPSIS.md` first.

## The rule
> Every SYNAPSIS transformation MUST be executable locally. Cross-department inputs
> are OPTIONAL accelerators. If the producing sibling is absent, the bot
> synthesizes the input itself and tags it `state_provenance: self-generated`.
> Absence of a sibling NEVER breaks the chain.

This is what keeps a single `kojiki-marketing-department` install fully functional
with zero other packages downloaded.

## Why no package download is needed
- The **schema** for every transformation lives in `00-kojiki-ontology/synapsis/`
  (already installed with every department via `install.sh` / the installer).
- Live sibling outputs are exchanged **peer-to-peer** as typed JSON objects via the
  Agent Inbox / `handoffs/registry.json` — not by cloning another repo.
- So "connecting to another department" means *messaging a registered sibling*, not
  *installing its code*.

## The handoff protocol
1. A transformation declares `optional_inputs` (which sibling outputs would improve it).
2. The department **Brain** checks `handoffs/registry.json` for the producer.
3. **If registered:** request the typed output; on receipt, tag the consumed input
   `state_provenance: sibling-verified`.
4. **If absent:** synthesize the input locally; tag it `state_provenance: self-generated`.
5. The consuming transformation proceeds either way. The `state_provenance` tag travels
   with the record so auditors know which inputs were independently verified.

## Provenance tags (enforced by validate.py)
| Tag | Meaning |
|---|---|
| `sibling-verified` | Input came from a registered sibling's typed transformation output. |
| `self-generated` | Input was synthesized locally because the sibling was absent (or unavailable). |

A record that tags an input `sibling-verified` for a producer **not in the registry**
FAILS validation — that means the bot claimed verification it couldn't have. The correct
behavior is to fall back to `self-generated`.

## Worked cross-department couplings (illustrative)
| Consumer | Optional input | Fallback when absent |
|---|---|---|
| `sales.STRATEGY` | `marketing.INTERPRETATION` | synthesize segment interpretation locally |
| `*.STRATEGY` | `legal.AUDIT` | proceed; tag decision `unaudited` |
| `finance.EVIDENCE` | `sales.OUTCOME` | use internal forecast assumptions |
| `product.STRATEGY` | `engineering.INTERPRETATION` | use product's own technical read |
| `every dept` | `risk-compliance.AUDIT` | proceed without independent risk audit |

## Org-level Brain (Executive Strategy)
`01-executive-strategy` runs the **meta-Brain**: it can set decision barriers that span
multiple departments (e.g. "do not synthesize the Q3 plan until `marketing.INTERPRETATION`
+ `finance.EVIDENCE` + `risk-compliance.AUDIT` are present"), without originating any
department's specialist analysis. When siblings are installed, the meta-Brain upgrades
fidelity by waiting for `sibling-verified` inputs; when they are not, it accepts
`self-generated` ones.

## Validator usage
```bash
# standalone mode (no registry): only hard invariants checked
python3 synapsis/validate.py my-record.json

# with a sibling registry: flags any 'sibling-verified' claim whose producer is absent
python3 synapsis/validate.py --registry registry.json my-record.json
# registry.json: {"marketing.INTERPRETATION": true, "legal.AUDIT": false}
```
