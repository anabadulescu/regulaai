import argparse
import json
import shutil
import os
from jsonschema import validate, ValidationError

SCHEMA_PATH = "community_rule_pack_schema.json"
COMMUNITY_DIR = "rule_packs/community"

def add_rule_pack(pack_path):
    with open(SCHEMA_PATH) as f:
        schema = json.load(f)
    with open(pack_path) as f:
        data = json.load(f)
    try:
        validate(instance=data, schema=schema)
    except ValidationError as e:
        print(f"❌ Validation failed: {e.message}")
        return
    os.makedirs(COMMUNITY_DIR, exist_ok=True)
    dest = os.path.join(COMMUNITY_DIR, os.path.basename(pack_path))
    shutil.copy(pack_path, dest)
    print(f"✅ Rule pack added: {dest}")
    # Optionally reload rule_engine here

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")
    add_parser = subparsers.add_parser("rules")
    add_parser.add_argument("add")
    add_parser.add_argument("pack_path")
    args = parser.parse_args()
    if args.command == "rules" and args.add == "add":
        add_rule_pack(args.pack_path) 