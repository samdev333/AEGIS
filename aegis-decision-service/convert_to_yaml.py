#!/usr/bin/env python3
"""Convert OpenAPI JSON to YAML format"""
import json
import yaml

# Read JSON
with open('aegis-openapi.json', 'r') as f:
    openapi_data = json.load(f)

# Write YAML
with open('aegis-openapi.yaml', 'w') as f:
    yaml.dump(openapi_data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

print("Converted aegis-openapi.json to aegis-openapi.yaml")
