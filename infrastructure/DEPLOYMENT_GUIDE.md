# RegulaAI Infrastructure Deployment Guide

## 🎯 Overview

This guide provides complete instructions for deploying the RegulaAI infrastructure on AWS using Terraform. The infrastructure includes a production-ready EKS cluster, VPC with proper networking, S3 storage, and security configurations.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        AWS Cloud                            │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐    ┌─────────────────┐                │
│  │   Public Subnet │    │  Private Subnet │                │
│  │   (AZ-1)        │    │   (AZ-1)        │                │
│  │                 │    │                 │                │
│  │ ┌─────────────┐ │    │ ┌─────────────┐ │                │
│  │ │   NAT GW    │ │    │ │ EKS Nodes   │ │                │
│  │ │             │ │    │ │             │ │                │
│  │ └─────────────┘ │    │ └─────────────┘ │                │
│  └─────────────────┘    └─────────────────┘                │
│           │                       │                        │
│  ┌─────────────────┐    ┌─────────────────┐                │
│  │   Public Subnet │    │  Private Subnet │                │
│  │   (AZ-2)        │    │   (AZ-2)        │                │
│  │                 │    │                 │                │
│  │ ┌─────────────┐ │    │ ┌─────────────┐ │                │
│  │ │ Internet GW │ │    │ │ EKS Nodes   │ │                │
│  │ │             │ │    │ │             │ │                │
│  │ └─────────────┘ │    │ └─────────────┘ │                │
│  └─────────────────┘    └─────────────────┘                │
│           │                       │                        │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                    EKS Cluster                          │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │ │
│  │  │   API Pod   │  │ Scanner Pod│  │  Worker Pod │     │ │
│  │  │             │  │             │  │             │     │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘     │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                    S3 Storage                           │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │ │
│  │  │ Scan Results│  │  Logs       │  │  Reports    │     │ │
│  │  │             │  │             │  │             │     │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘     │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## 📋 Prerequisites

### Required Tools
- **AWS CLI** (v2.x) - [Install Guide](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
- **Terraform** (>= 1.0) - [Install Guide](https://developer.hashicorp.com/terraform/downloads)
- **kubectl** - [Install Guide](https://kubernetes.io/docs/tasks/tools/)
- **Helm** (>= 3.0) - [Install Guide](https://helm.sh/docs/intro/install/)

### AWS Requirements
- AWS Account with appropriate permissions
- AWS credentials configured (`aws configure`)
- Sufficient quota for EKS clusters and EC2 instances

### Required IAM Permissions
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "eks:*",
                "ec2:*",
                "iam:*",
                "s3:*",
                "kms:*",
                "elasticloadbalancing:*"
            ],
            "Resource": "*"
        }
    ]
}
```

## 🚀 Quick Deployment

### 1. Clone and Navigate
```bash
cd infrastructure
```

### 2. Configure Variables
```bash
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your preferences
```

### 3. Deploy Infrastructure
```bash
./deploy.sh deploy
```

### 4. Deploy Application
```bash
# Configure kubectl (done automatically by deploy.sh)
kubectl get nodes

# Deploy RegulaAI application
helm install regulaai ../helm/regulaai
```

## 📁 File Structure

```
infrastructure/
├── main.tf                 # Main Terraform configuration
├── variables.tf            # Variable definitions
├── outputs.tf              # Output values
├── terraform.tfvars.example # Example variable values
├── deploy.sh               # Deployment automation script
├── validate.sh             # Configuration validation script
├── README.md               # Detailed documentation
├── .gitignore              # Git ignore rules
├── eks-cluster/            # EKS cluster module
│   ├── main.tf            # EKS cluster configuration
│   └── outputs.tf         # EKS module outputs
└── DEPLOYMENT_GUIDE.md    # This guide
```

## ⚙️ Configuration Options

### Environment Variables
| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `aws_region` | AWS region | `us-west-2` | `us-east-1` |
| `vpc_cidr` | VPC CIDR block | `10.0.0.0/16` | `172.16.0.0/16` |
| `cluster_name` | EKS cluster name | `regulaai-eks` | `my-regulaai-cluster` |
| `environment` | Environment name | `production` | `development` |
| `node_group_instance_types` | EC2 instance types | `["t3.large"]` | `["m5.large"]` |
| `node_group_desired_size` | Desired nodes | `2` | `3` |
| `node_group_max_size` | Maximum nodes | `4` | `6` |
| `node_group_min_size` | Minimum nodes | `1` | `1` |

### Cost Optimization
- **Development**: Use `t3.medium` instances, 1-2 nodes
- **Production**: Use `m5.large` or `c5.large` instances, 2-4 nodes
- **High Performance**: Use `m5.xlarge` or `c5.xlarge` instances

## 🔒 Security Features

### Network Security
- **Private subnets** for EKS nodes
- **NAT Gateway** for controlled internet access
- **Security groups** with minimal required access
- **VPC isolation** with custom CIDR blocks

### Data Security
- **KMS encryption** for S3 bucket
- **Server-side encryption** enabled
- **Versioning** enabled for data protection
- **IAM roles** with least privilege

### Access Control
- **IRSA (IAM Roles for Service Accounts)** for pod-level permissions
- **EKS OIDC provider** for secure authentication
- **RBAC** enabled for Kubernetes access control

## 📊 Monitoring and Logging

### CloudWatch Integration
- **Container Insights** enabled on EKS cluster
- **VPC Flow Logs** for network monitoring
- **S3 access logs** for storage monitoring

### Kubernetes Monitoring
```bash
# Check cluster health
kubectl get nodes
kubectl get pods --all-namespaces

# View cluster metrics
kubectl top nodes
kubectl top pods
```

## 🛠️ Troubleshooting

### Common Issues

#### 1. Insufficient IAM Permissions
```bash
# Check current identity
aws sts get-caller-identity

# Verify EKS permissions
aws eks list-clusters
```

#### 2. VPC/Subnet Issues
```bash
# Check VPC status
aws ec2 describe-vpcs --vpc-ids <vpc-id>

# Verify subnet availability
aws ec2 describe-subnets --subnet-ids <subnet-id>
```

#### 3. EKS Cluster Issues
```bash
# Check cluster status
aws eks describe-cluster --name <cluster-name> --region <region>

# View cluster logs
aws logs describe-log-groups --log-group-name-prefix "/aws/eks/<cluster-name>"
```

#### 4. Node Group Issues
```bash
# Check node group status
aws eks describe-nodegroup --cluster-name <cluster-name> --nodegroup-name default

# View node group logs
aws logs describe-log-streams --log-group-name "/aws/eks/<cluster-name>/cluster"
```

### Useful Commands

```bash
# Get cluster credentials
aws eks update-kubeconfig --region <region> --name <cluster-name>

# Check cluster connectivity
kubectl cluster-info

# View all resources
kubectl get all --all-namespaces

# Check node resources
kubectl describe nodes
```

## 🔄 Maintenance

### Updates and Upgrades

#### EKS Cluster Updates
```bash
# Check available versions
aws eks describe-addon-versions --addon-name vpc-cni

# Update cluster version
aws eks update-cluster-version --name <cluster-name> --kubernetes-version <version>
```

#### Node Group Updates
```bash
# Update node group
aws eks update-nodegroup-version --cluster-name <cluster-name> --nodegroup-name default
```

### Backup and Recovery

#### S3 Backup
```bash
# Create backup bucket
aws s3 mb s3://regulaai-backup-$(date +%Y%m%d)

# Sync data
aws s3 sync s3://regulaai-storage s3://regulaai-backup-$(date +%Y%m%d)
```

#### EKS Backup
```bash
# Export cluster configuration
kubectl get all --all-namespaces -o yaml > cluster-backup-$(date +%Y%m%d).yaml
```

## 🧹 Cleanup

### Destroy Infrastructure
```bash
# Destroy all resources
./deploy.sh destroy

# Or manually
terraform destroy -auto-approve
```

### Manual Cleanup
```bash
# Delete EKS cluster
aws eks delete-cluster --name <cluster-name> --region <region>

# Delete S3 bucket
aws s3 rb s3://<bucket-name> --force

# Delete VPC
aws ec2 delete-vpc --vpc-id <vpc-id>
```

## 📞 Support

### Getting Help
1. Check the [README.md](README.md) for detailed documentation
2. Review the [Terraform documentation](https://www.terraform.io/docs)
3. Check [AWS EKS documentation](https://docs.aws.amazon.com/eks/)
4. Review logs and error messages for specific issues

### Useful Resources
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [EKS Best Practices](https://aws.github.io/aws-eks-best-practices/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)

---

**Note**: This infrastructure is designed for production use. Always test in a development environment first and ensure you have proper backup and monitoring in place. 