def check_artifact(artifact):
    # Check if artifact is valid
    if 'content' not in artifact:
        return False
    if not isinstance(artifact['content'], str):
        return False
    if not artifact['content']:
        return False
    return True
