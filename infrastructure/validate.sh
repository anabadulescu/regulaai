#!/bin/bash

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if required files exist
check_files() {
    print_status "Checking required files..."
    
    required_files=(
        "main.tf"
        "variables.tf"
        "outputs.tf"
        "eks-cluster/main.tf"
        "eks-cluster/outputs.tf"
        "terraform.tfvars.example"
        "README.md"
    )
    
    for file in "${required_files[@]}"; do
        if [[ -f "$file" ]]; then
            print_status "✓ $file exists"
        else
            print_error "✗ $file is missing"
            exit 1
        fi
    done
}

# Validate Terraform syntax (basic checks)
validate_syntax() {
    print_status "Validating Terraform syntax..."
    
    # Check for basic Terraform blocks
    if grep -q "terraform {" main.tf; then
        print_status "✓ terraform block found"
    else
        print_error "✗ terraform block missing in main.tf"
        exit 1
    fi
    
    if grep -q "provider \"aws\"" main.tf; then
        print_status "✓ AWS provider found"
    else
        print_error "✗ AWS provider missing in main.tf"
        exit 1
    fi
    
    # Check for required resources
    required_resources=(
        "aws_vpc"
        "aws_subnet"
        "aws_eks_cluster"
        "aws_s3_bucket"
    )
    
    for resource in "${required_resources[@]}"; do
        if grep -q "resource \"$resource\"" main.tf; then
            print_status "✓ $resource resource found"
        else
            print_warning "⚠ $resource resource not found in main.tf"
        fi
    done
    
    # Check eks-cluster module
    if grep -q "module \"eks_cluster\"" main.tf; then
        print_status "✓ eks_cluster module found"
    else
        print_error "✗ eks_cluster module missing in main.tf"
        exit 1
    fi
}

# Check variable definitions
validate_variables() {
    print_status "Validating variables..."
    
    # Check if variables.tf exists and has content
    if [[ -s variables.tf ]]; then
        print_status "✓ variables.tf has content"
    else
        print_error "✗ variables.tf is empty or missing"
        exit 1
    fi
    
    # Check for required variables
    required_vars=(
        "aws_region"
        "vpc_cidr"
        "cluster_name"
    )
    
    for var in "${required_vars[@]}"; do
        if grep -q "variable \"$var\"" variables.tf; then
            print_status "✓ variable $var defined"
        else
            print_warning "⚠ variable $var not found"
        fi
    done
}

# Check outputs
validate_outputs() {
    print_status "Validating outputs..."
    
    if [[ -s outputs.tf ]]; then
        print_status "✓ outputs.tf has content"
    else
        print_warning "⚠ outputs.tf is empty or missing"
    fi
}

# Check eks-cluster module
validate_eks_module() {
    print_status "Validating eks-cluster module..."
    
    if [[ -d "eks-cluster" ]]; then
        print_status "✓ eks-cluster directory exists"
        
        if [[ -f "eks-cluster/main.tf" ]]; then
            print_status "✓ eks-cluster/main.tf exists"
        else
            print_error "✗ eks-cluster/main.tf missing"
            exit 1
        fi
        
        if [[ -f "eks-cluster/outputs.tf" ]]; then
            print_status "✓ eks-cluster/outputs.tf exists"
        else
            print_warning "⚠ eks-cluster/outputs.tf missing"
        fi
    else
        print_error "✗ eks-cluster directory missing"
        exit 1
    fi
}

# Main validation function
main() {
    print_status "Starting infrastructure validation..."
    
    check_files
    validate_syntax
    validate_variables
    validate_outputs
    validate_eks_module
    
    print_status "Validation completed successfully!"
    echo
    print_status "Infrastructure configuration appears to be valid."
    print_status "To deploy, run: ./deploy.sh"
    print_status "To see the plan, run: ./deploy.sh plan"
}

main 