#!/usr/bin/env python3
"""Add servers section to OpenAPI spec"""
import json

# Read JSON
with open('aegis-openapi.json', 'r') as f:
    openapi_data = json.load(f)

# Add servers section
openapi_data['servers'] = [{
    'url': 'https://your-aegis-service-url.codeengine.appdomain.cloud',
    'description': 'A.E.G.I.S. Decision Service - Production (IBM Cloud Code Engine)'
}]

# Write back with proper formatting
with open('aegis-openapi.json', 'w') as f:
    json.dump(openapi_data, f, indent=2)

print("Added servers section to aegis-openapi.json")
