def cross_check_artifacts(artifacts):
    # Cross-check artifacts for consistency
    for i, artifact1 in enumerate(artifacts):
        for j, artifact2 in enumerate(artifacts):
            if i != j:
                if 'content' in artifact1 and 'content' in artifact2:
                    if artifact1['content'] == artifact2['content']:
                        return False
    return True
