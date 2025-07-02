import json
from deepdiff import DeepDiff

def compare_results(generated, expected):
    return DeepDiff(
        generated, 
        expected,
        ignore_order=True,
        exclude_paths=["root['id']", "root['timestamp']"]
    )