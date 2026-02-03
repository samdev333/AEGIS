"""
Export OpenAPI specification from FastAPI app

This script generates a static openapi.yaml file that can be imported
into watsonx Orchestrate.

Usage:
    python scripts/export_openapi.py
"""

import json
import yaml
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.aegis_service.main import app


def export_openapi():
    """Export OpenAPI spec to YAML file"""
    # Get OpenAPI schema from FastAPI
    openapi_schema = app.openapi()

    # Update servers for deployment
    openapi_schema["servers"] = [
        {
            "url": "https://your-code-engine-url.us-south.codeengine.appdomain.cloud",
            "description": "IBM Code Engine Deployment (UPDATE THIS URL)"
        },
        {
            "url": "http://localhost:5000",
            "description": "Local Development"
        }
    ]

    # Write to YAML file
    output_path = Path(__file__).parent.parent / "openapi.yaml"
    with open(output_path, "w") as f:
        yaml.dump(openapi_schema, f, sort_keys=False, default_flow_style=False)

    print(f"✅ OpenAPI spec exported to: {output_path}")
    print(f"📝 Total paths: {len(openapi_schema.get('paths', {}))}")
    print(f"📦 Schemas: {len(openapi_schema.get('components', {}).get('schemas', {}))}")
    print()
    print("Next steps:")
    print("1. Deploy your service to IBM Code Engine")
    print("2. Update the 'servers' section in openapi.yaml with your actual URL")
    print("3. Import openapi.yaml into watsonx Orchestrate")

    # Also export as JSON for reference
    json_path = Path(__file__).parent.parent / "openapi.json"
    with open(json_path, "w") as f:
        json.dump(openapi_schema, f, indent=2)

    print(f"📄 Also exported JSON version to: {json_path}")


if __name__ == "__main__":
    export_openapi()
