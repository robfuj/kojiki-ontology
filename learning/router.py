# Router component for EVIDENCE stage
# Generates a tiny, per-dispatch map scoping what this specific EVIDENCE call is allowed to touch

# Example dispatch contract
example_dispatch_contract = {
    'scope': 'marketing',
    'allowed_cases': ['campaign_1', 'campaign_2'],
    'allowed_transformations': ['summary', 'analysis'],
}

# Function to generate the router
def generate_router(dispatch_contract):
    router = {
        'scope': dispatch_contract['scope'],
        'allowed_cases': dispatch_contract['allowed_cases'],
        'allowed_transformations': dispatch_contract['allowed_transformations'],
    }
    return router

# Example usage
router = generate_router(example_dispatch_contract)
print(router)
