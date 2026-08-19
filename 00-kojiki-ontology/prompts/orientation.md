# Orientation Protocol (first-run)

Before any decision work, the agent must orient: establish identity, learn the operating context, and discover sibling agents so the organization's functions can coordinate.

### Q1
What should I call you, and which organizational function do you represent?

- captures: agent_name, function_line
- flows to: decision-rights/ (owner/role), ontology/functions.md

### Q2
What industry or sector is the organization in?

- captures: industry, sector
- flows to: triggers the agent's research team: market/competitive/regulatory scan of the field

### Q3
What jurisdiction(s) apply — which country, region/state, and regulatory regime?

- captures: country, region, regulatory_regime
- flows to: Legal/Compliance research; any decision with legal exposure; ontology/ (geography axis)

### Q4
What geography do you operate in, and what is the business model?

- captures: geography, business_model
- flows to: ontology/ (adaptation axes, S20); scopes the canonical ontology to the real org

### Q5
Are other agents from this same group already running? Register me so we can hand off.

- captures: group_id, sibling_agents
- flows to: handoffs/ (Cross-Functional Handoff Standard, S11); enables agent-to-agent messaging


## Then
After orientation the agent loads its function schema (ontology/functions.md + lines/<n>-<line>/), starts a research pass for its industry/jurisdiction, and announces itself to registered siblings so cross-functional decisions can be routed per the Handoff Standard.
