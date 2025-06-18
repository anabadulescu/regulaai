import os
import json
import glob
import pytest
from jsonschema import validate, ValidationError

SCHEMA_PATH = "community_rule_pack_schema.json"
RULES_DIR = "community-rules"

with open(SCHEMA_PATH) as f:
    schema = json.load(f)

@pytest.mark.parametrize("rule_file", glob.glob(os.path.join(RULES_DIR, "*.json")))
def test_rule_pack_schema(rule_file):
    with open(rule_file) as f:
        data = json.load(f)
    try:
        validate(instance=data, schema=schema)
    except ValidationError as e:
        pytest.fail(f"Schema validation failed for {rule_file}: {e.message}") 