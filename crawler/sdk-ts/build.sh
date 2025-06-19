#!/bin/bash

# RegulaAI TypeScript SDK Build Script

set -e

echo "🔨 Building RegulaAI TypeScript SDK..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js first."
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm first."
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
npm install

# Clean previous build
echo "🧹 Cleaning previous build..."
npm run clean

# Build the SDK
echo "🔨 Building TypeScript SDK..."
npm run build

# Check if build was successful
if [ ! -d "dist" ]; then
    echo "❌ Build failed - dist directory not found"
    exit 1
fi

# Check if main files exist
if [ ! -f "dist/index.js" ] || [ ! -f "dist/index.d.ts" ]; then
    echo "❌ Build failed - missing main files"
    exit 1
fi

echo "✅ Build completed successfully!"

# Run tests if available
if [ -f "test-sdk.js" ]; then
    echo "🧪 Running SDK tests..."
    node test-sdk.js
fi

echo "🎉 SDK is ready for publishing!"
echo ""
echo "To publish to npm:"
echo "  npm publish"
echo ""
echo "To test locally:"
echo "  npm link"
echo "  # In another project: npm link @regulaai/sdk" 