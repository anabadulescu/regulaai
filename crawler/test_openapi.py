#!/usr/bin/env python3
"""
Test script for OpenAPI spec generation
"""

import json
import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_openapi_generation():
    """Test that the OpenAPI spec can be generated"""
    try:
        # Import the app
        from app import app
        
        # Generate OpenAPI spec
        openapi_spec = app.openapi()
        
        # Validate the spec has required fields
        required_fields = ['openapi', 'info', 'paths', 'components']
        for field in required_fields:
            if field not in openapi_spec:
                print(f"❌ Missing required field: {field}")
                return False
        
        # Check that we have the expected tags
        expected_tags = ['Auth', 'Scans', 'Billing', 'Integrations', 'Settings', 'Monitoring']
        spec_tags = [tag['name'] for tag in openapi_spec.get('tags', [])]
        
        for tag in expected_tags:
            if tag not in spec_tags:
                print(f"❌ Missing expected tag: {tag}")
                return False
        
        # Check that we have some paths
        paths = openapi_spec.get('paths', {})
        if not paths:
            print("❌ No paths found in OpenAPI spec")
            return False
        
        print(f"✅ OpenAPI spec generated successfully!")
        print(f"   Version: {openapi_spec.get('openapi', 'unknown')}")
        print(f"   Title: {openapi_spec.get('info', {}).get('title', 'unknown')}")
        print(f"   Paths: {len(paths)}")
        print(f"   Tags: {spec_tags}")
        
        # Save spec to file for inspection
        with open('test_openapi_spec.json', 'w') as f:
            json.dump(openapi_spec, f, indent=2)
        print("   Spec saved to test_openapi_spec.json")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to generate OpenAPI spec: {e}")
        return False

if __name__ == "__main__":
    success = test_openapi_generation()
    sys.exit(0 if success else 1) 