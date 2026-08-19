# Bootstrap — install the Kojiki Decision System

Two ways to install.

## A) The whole package (recommended for first run)
Clone the ontology + all 20 line departments + the two meta agents in one command:
```bash
bash install-all.sh            # -> ./kojiki-decision-system/ with everything
```
This always includes `kojiki-ontology` (the shared standard) so every department can
reference canonical schemas and register siblings.

## B) One department + the ontology it needs
Every department repo ships its own `install.sh` that installs the ontology sibling if
it is missing, then the department:
```bash
git clone https://github.com/robfuj/kojiki-marketing-department.git
cd kojiki-marketing-department
bash install.sh                # clones kojiki-ontology sibling if absent, then this dept
```
(After orientation + research, the department installs its own working bots via
`bots/install_bots.py <slugs>` — see its AGENT.md.)

## Why both?
`kojiki-ontology` is the shared standard (schemas, taxonomy, decision-rights, handoff).
Every department assumes it is present. The installer and `install.sh` guarantee that.
