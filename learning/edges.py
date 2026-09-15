# Edges component for EVIDENCE stage
# Typed relationships between records (depends_on, contradicts, supersedes)

# Example relationships
example_relationships = {
    'campaign_1': {
        'depends_on': ['campaign_2'],
        'contradicts': ['campaign_3'],
        'supersedes': ['campaign_4'],
    },
    'campaign_2': {
        'depends_on': ['campaign_1'],
    }
}

# Function to create and store the relationships
import json
import os

def create_and_store_relationships(relationships):
    relationships_dir = os.path.join('learning', 'relationships')
    os.makedirs(relationships_dir, exist_ok=True)
    relationships_path = os.path.join(relationships_dir, 'relationships.json')
    with open(relationships_path, 'w') as f:
        json.dump(relationships, f)
    return relationships_path

# Example usage
relationships_path = create_and_store_relationships(example_relationships)
print(f'Relationships created at: {relationships_path}')
