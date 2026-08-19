# Cross-Functional Handoff Standard

A handoff is complete only when the receiving function can act. For agent-to-agent handoffs, register in `registry.json`.

## Sender
Who is responsible for producing the input?
## Receiver
Who is responsible for acting on it?
## Trigger
What event initiates the handoff?
## Required data
What minimum information is needed?
## Acceptance criteria
What makes the handoff usable?
## SLA / timing
When must the receiving function act?
## Exception
What happens when requirements are not met?
## Feedback
How does the receiver report outcome back to sender?
## Learning
What should change in the handoff based on outcomes?

## registry.json
A JSON array of registered agents:
```json
[
 {"agent_name": "...", "function_line": "...", "group_id": "...", "endpoint": "...", "registered_at": "..."}
]
```
