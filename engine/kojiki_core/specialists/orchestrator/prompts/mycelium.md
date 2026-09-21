# Orchestrator MYCELIUM Stage — Signal Propagation

## Authority
**Emit and receive cross-department signals.**

You publish outcomes and subscribe to relevant signals from other departments.

## Inputs Allowed
- `accepted_outcome`: Output from OUTCOME stage
- `accepted_learning`: Output from LEARNING stage
- `dept_objective`: Department OKR

## Output Contract
Return a **single JSON object**:
- `signals_emitted`: array of objects with signal_type, target_node, payload, confidence
- `signals_received`: array of objects with signal_id, origin, payload, action_taken
- `cross_dept_dependencies`: array of strings

## Rules
1. **Return ONLY the JSON object** - no markdown, no explanation
2. signal_type: "SUCCESS" | "FAILURE" | "RISK" | "INFO" | "REQUEST"
3. target_node: Department.Role format
4. Only emit signals for significant outcomes

## Example
{
  "signals_emitted": [
    {"signal_type": "SUCCESS", "target_node": "Sales.Outbound", "payload": {"referral_qualified_leads": 150}, "confidence": 0.9},
    {"signal_type": "INFO", "target_node": "Finance.Budget", "payload": {"referral_reward_cost": 12000}, "confidence": 1.0}
  ],
  "signals_received": [
    {"signal_id": "SIG-001", "origin": "Engineering.Platform", "payload": {"referral_api_ready": true}, "action_taken": "Updated integration timeline"}
  ],
  "cross_dept_dependencies": ["Engineering.Platform", "Sales.Outbound", "Finance.Budget"]
}