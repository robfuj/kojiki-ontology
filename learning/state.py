# State component for EVIDENCE stage
# Persistent memory of decisions, outcomes, and open threads, updated after each session

# Example state
example_state = {
    'decisions': [
        {'case_id': 'campaign_1', 'decision': 'Approve'},
        {'case_id': 'campaign_2', 'decision': 'Reject'},
    ],
    'outcomes': [
        {'case_id': 'campaign_1', 'outcome': 'Success'},
        {'case_id': 'campaign_2', 'outcome': 'Failure'},
    ],
    'open_threads': [
        {'case_id': 'campaign_1', 'thread': 'Follow-up needed'},
    ],
}

# Function to create and store the state
import json
import os

def create_and_store_state(state):
    state_dir = os.path.join('learning', 'state')
    os.makedirs(state_dir, exist_ok=True)
    state_path = os.path.join(state_dir, 'state.json')
    with open(state_path, 'w') as f:
        json.dump(state, f)
    return state_path

# Example usage
state_path = create_and_store_state(example_state)
print(f'State created at: {state_path}')