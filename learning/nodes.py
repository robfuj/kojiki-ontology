# Nodes component for EVIDENCE stage
# Small, specific records that can be read completely in one shot

# Example record
example_record = {
    'case_id': 'campaign_1',
    'record_type': 'verified_extract',
    'content': 'Content of verified extract for campaign_1',
    'summary': 'Summary of verified extract for campaign_1',
    'score': 0.9,
}

# Function to create and store the record
import json
import os

def create_and_store_record(record):
    record_dir = os.path.join('learning', record['case_id'])
    os.makedirs(record_dir, exist_ok=True)
    record_path = os.path.join(record_dir, 'record.json')
    with open(record_path, 'w') as f:
        json.dump(record, f)
    return record_path

# Example usage
record_path = create_and_store_record(example_record)
print(f'Record created at: {record_path}')
