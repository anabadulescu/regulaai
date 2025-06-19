#!/bin/bash

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check if AWS CLI is installed
    if ! command -v aws &> /dev/null; then
        print_error "AWS CLI is not installed. Please install it first."
        exit 1
    fi
    
    # Check if Terraform is installed
    if ! command -v terraform &> /dev/null; then
        print_error "Terraform is not installed. Please install it first."
        exit 1
    fi
    
    # Check if kubectl is installed
    if ! command -v kubectl &> /dev/null; then
        print_error "kubectl is not installed. Please install it first."
        exit 1
    fi
    
    # Check AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        print_error "AWS credentials are not configured. Please run 'aws configure' first."
        exit 1
    fi
    
    print_status "All prerequisites are satisfied."
}

# Initialize Terraform
init_terraform() {
    print_status "Initializing Terraform..."
    terraform init
}

# Plan Terraform deployment
plan_deployment() {
    print_status "Planning Terraform deployment..."
    terraform plan
}

# Apply Terraform deployment
apply_deployment() {
    print_status "Applying Terraform deployment..."
    terraform apply -auto-approve
}

# Configure kubectl
configure_kubectl() {
    print_status "Configuring kubectl..."
    
    # Get cluster name and region from Terraform output
    CLUSTER_NAME=$(terraform output -raw eks_cluster_name)
    REGION=$(terraform output -raw aws_region 2>/dev/null || echo "us-west-2")
    
    aws eks update-kubeconfig --region "$REGION" --name "$CLUSTER_NAME"
    
    print_status "kubectl configured for cluster: $CLUSTER_NAME"
}

# Show deployment summary
show_summary() {
    print_status "Deployment completed successfully!"
    echo
    echo "=== Deployment Summary ==="
    echo "EKS Cluster: $(terraform output -raw eks_cluster_name)"
    echo "Cluster Endpoint: $(terraform output -raw eks_cluster_endpoint)"
    echo "S3 Bucket: $(terraform output -raw s3_bucket_name)"
    echo "VPC ID: $(terraform output -raw vpc_id)"
    echo
    echo "=== Next Steps ==="
    echo "1. Deploy the RegulaAI application:"
    echo "   helm install regulaai ../helm/regulaai"
    echo
    echo "2. Check cluster status:"
    echo "   kubectl get nodes"
    echo
    echo "3. View cluster information:"
    echo "   kubectl cluster-info"
}

# Main deployment function
deploy() {
    print_status "Starting RegulaAI infrastructure deployment..."
    
    check_prerequisites
    init_terraform
    plan_deployment
    
    print_warning "This will create AWS resources that may incur costs."
    read -p "Do you want to continue? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        apply_deployment
        configure_kubectl
        show_summary
    else
        print_status "Deployment cancelled."
        exit 0
    fi
}

# Destroy function
destroy() {
    print_warning "This will destroy ALL AWS resources created by Terraform."
    print_warning "This action cannot be undone!"
    read -p "Are you sure you want to continue? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Destroying infrastructure..."
        terraform destroy -auto-approve
        print_status "Infrastructure destroyed successfully."
    else
        print_status "Destruction cancelled."
    fi
}

# Show usage
usage() {
    echo "Usage: $0 [deploy|destroy|plan]"
    echo
    echo "Commands:"
    echo "  deploy   - Deploy the complete infrastructure"
    echo "  destroy  - Destroy all infrastructure"
    echo "  plan     - Show deployment plan without applying"
    echo
    echo "Examples:"
    echo "  $0 deploy"
    echo "  $0 destroy"
    echo "  $0 plan"
}

# Main script logic
case "${1:-deploy}" in
    deploy)
        deploy
        ;;
    destroy)
        destroy
        ;;
    plan)
        check_prerequisites
        init_terraform
        plan_deployment
        ;;
    *)
        usage
        exit 1
        ;;
esac 