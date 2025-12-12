#!/usr/bin/env python3
"""Script to validate FastAPI OpenAPI schema against TypeSpec-generated schema."""

import json
import sys
from pathlib import Path
from typing import Dict, Any
import yaml


def load_yaml(file_path: Path) -> Dict[str, Any]:
    """Load YAML file."""
    with open(file_path, "r") as f:
        return yaml.safe_load(f)


def load_json(file_path: Path) -> Dict[str, Any]:
    """Load JSON file."""
    with open(file_path, "r") as f:
        return json.load(f)


def compare_schemas(typespec_schema: Dict[str, Any], fastapi_schema: Dict[str, Any]) -> bool:
    """Compare two OpenAPI schemas and report differences."""
    differences = []
    
    # Compare basic info
    if typespec_schema.get("info", {}).get("title") != fastapi_schema.get("info", {}).get("title"):
        differences.append("Title mismatch")
    
    # Compare paths
    typespec_paths = set(typespec_schema.get("paths", {}).keys())
    fastapi_paths = set(fastapi_schema.get("paths", {}).keys())
    
    if typespec_paths != fastapi_paths:
        missing_in_fastapi = typespec_paths - fastapi_paths
        extra_in_fastapi = fastapi_paths - typespec_paths
        
        if missing_in_fastapi:
            differences.append(f"Paths in TypeSpec but not in FastAPI: {missing_in_fastapi}")
        if extra_in_fastapi:
            differences.append(f"Paths in FastAPI but not in TypeSpec: {extra_in_fastapi}")
    
    if differences:
        print("Schema differences found:")
        for diff in differences:
            print(f"  - {diff}")
        return False
    
    print("✓ Schemas match!")
    return True


def main():
    """Main validation function."""
    project_root = Path(__file__).parent.parent
    typespec_dir = project_root / "typespec"
    typespec_schema_path = typespec_dir / "openapi.yaml"
    fastapi_schema_path = project_root / "fastapi-openapi.json"
    
    # Check if TypeSpec schema exists
    if not typespec_schema_path.exists():
        print(f"Error: TypeSpec schema not found at {typespec_schema_path}")
        print("Please run 'npm run build' in the typespec directory first.")
        sys.exit(1)
    
    # Check if FastAPI schema exists
    if not fastapi_schema_path.exists():
        print(f"Error: FastAPI schema not found at {fastapi_schema_path}")
        print("Please fetch it from the running API: curl http://localhost:8000/openapi.json > fastapi-openapi.json")
        sys.exit(1)
    
    # Load schemas
    print("Loading schemas...")
    typespec_schema = load_yaml(typespec_schema_path)
    fastapi_schema = load_json(fastapi_schema_path)
    
    # Compare
    print("\nComparing schemas...")
    if compare_schemas(typespec_schema, fastapi_schema):
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()

