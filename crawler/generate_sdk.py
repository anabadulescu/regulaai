#!/usr/bin/env python3
"""
Script to generate TypeScript SDK from OpenAPI spec
"""

import subprocess
import sys
import os
import json
import requests
from pathlib import Path

def install_dependencies():
    """Install required npm packages for SDK generation"""
    print("Installing openapi-typescript-codegen...")
    try:
        subprocess.run([
            "npm", "install", "-g", "openapi-typescript-codegen"
        ], check=True, capture_output=True)
        print("✓ openapi-typescript-codegen installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install openapi-typescript-codegen: {e}")
        return False
    return True

def get_openapi_spec(base_url="http://localhost:8000"):
    """Fetch OpenAPI spec from the running API server"""
    try:
        response = requests.get(f"{base_url}/openapi.json", timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"✗ Failed to fetch OpenAPI spec from {base_url}: {e}")
        print("Make sure the API server is running on the specified URL")
        return None

def generate_sdk(openapi_spec, output_dir="sdk-ts"):
    """Generate TypeScript SDK from OpenAPI spec"""
    # Save spec to temporary file
    spec_file = "temp_openapi.json"
    with open(spec_file, 'w') as f:
        json.dump(openapi_spec, f, indent=2)
    
    try:
        print(f"Generating TypeScript SDK in {output_dir}...")
        
        # Remove existing generated files
        if os.path.exists(output_dir):
            subprocess.run(["rm", "-rf", output_dir], check=True)
        
        # Generate SDK using openapi-typescript-codegen
        subprocess.run([
            "openapi", "--input", spec_file, "--output", output_dir
        ], check=True, capture_output=True)
        
        print("✓ TypeScript SDK generated successfully")
        
        # Clean up temporary file
        os.remove(spec_file)
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to generate SDK: {e}")
        if os.path.exists(spec_file):
            os.remove(spec_file)
        return False

def customize_sdk():
    """Customize the generated SDK with our specific requirements"""
    sdk_dir = Path("sdk-ts")
    
    # Update package.json
    package_json = sdk_dir / "package.json"
    if package_json.exists():
        with open(package_json, 'r') as f:
            pkg = json.load(f)
        
        # Update package details
        pkg.update({
            "name": "@regulaai/sdk",
            "version": "0.1.0",
            "description": "TypeScript SDK for RegulaAI - GDPR compliance scanning API",
            "main": "dist/index.js",
            "types": "dist/index.d.ts",
            "files": ["dist", "README.md"],
            "scripts": {
                "build": "tsc",
                "dev": "tsc --watch",
                "clean": "rm -rf dist",
                "prepublishOnly": "npm run clean && npm run build",
                "test": "jest",
                "lint": "eslint src --ext .ts",
                "format": "prettier --write src/**/*.ts"
            },
            "keywords": [
                "gdpr", "compliance", "scanning", "api", "typescript", "sdk", "regulaai"
            ],
            "author": "RegulaAI <support@regulaai.com>",
            "license": "MIT",
            "repository": {
                "type": "git",
                "url": "https://github.com/regulaai/regulaai-sdk-typescript.git"
            },
            "bugs": {
                "url": "https://github.com/regulaai/regulaai-sdk-typescript/issues"
            },
            "homepage": "https://github.com/regulaai/regulaai-sdk-typescript#readme",
            "dependencies": {
                "axios": "^1.6.0"
            },
            "devDependencies": {
                "@types/node": "^20.0.0",
                "@typescript-eslint/eslint-plugin": "^6.0.0",
                "@typescript-eslint/parser": "^6.0.0",
                "eslint": "^8.0.0",
                "jest": "^29.0.0",
                "prettier": "^3.0.0",
                "typescript": "^5.0.0"
            },
            "engines": {
                "node": ">=16.0.0"
            },
            "publishConfig": {
                "access": "public"
            }
        })
        
        with open(package_json, 'w') as f:
            json.dump(pkg, f, indent=2)
        
        print("✓ Package.json updated")

def main():
    """Main function"""
    print("RegulaAI TypeScript SDK Generator")
    print("=" * 40)
    
    # Check if npm is available
    try:
        subprocess.run(["npm", "--version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("✗ npm is not available. Please install Node.js and npm first.")
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Get API server URL from command line or use default
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    
    # Fetch OpenAPI spec
    print(f"Fetching OpenAPI spec from {base_url}...")
    openapi_spec = get_openapi_spec(base_url)
    if not openapi_spec:
        sys.exit(1)
    
    print("✓ OpenAPI spec fetched successfully")
    
    # Generate SDK
    if not generate_sdk(openapi_spec):
        sys.exit(1)
    
    # Customize SDK
    customize_sdk()
    
    print("\n🎉 TypeScript SDK generated successfully!")
    print("\nNext steps:")
    print("1. cd sdk-ts")
    print("2. npm install")
    print("3. npm run build")
    print("4. npm publish")

if __name__ == "__main__":
    main() 