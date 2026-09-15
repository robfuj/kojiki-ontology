# Index component for EVIDENCE stage
# Creates one-line entries per case/finding in learning/ directory, with entity tags and a short summary, scored for relevance

# Example case/finding
example_case = {
    'case_id': 'campaign_1',
    'tags': ['marketing', 'campaign'],
    'summary': 'Summary of campaign_1',
    'score': 0.85,
}

# Function to create one-line entry
import json

def create_one_line_entry(case):
    entry = {
        'case_id': case['case_id'],
        'tags': case['tags'],
        'summary': case['summary'],
        'score': case['score'],
    }
    return json.dumps(entry)

# Example usage
entry = create_one_line_entry(example_case)
print(entry)
