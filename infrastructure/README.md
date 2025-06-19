# RegulaAI Infrastructure

This directory contains the Terraform configuration for deploying the RegulaAI infrastructure on AWS.

## Architecture

The infrastructure includes:

- **VPC** with public and private subnets across 2 availability zones
- **EKS Cluster** with managed node groups
- **S3 Bucket** with KMS encryption for storage
- **NAT Gateway** for private subnet internet access
- **IRSA (IAM Roles for Service Accounts)** for secure S3 access

## Prerequisites

1. **AWS CLI** configured with appropriate credentials
2. **Terraform** >= 1.0
3. **kubectl** for Kubernetes management
4. **AWS IAM permissions** for EKS, VPC, S3, and IAM

## Quick Start

1. **Copy the example variables file:**
   ```bash
   cp terraform.tfvars.example terraform.tfvars
   ```

2. **Customize the variables** in `terraform.tfvars`:
   - Set your preferred AWS region
   - Adjust cluster size and instance types
   - Customize the S3 bucket name

3. **Initialize Terraform:**
   ```bash
   terraform init
   ```

4. **Plan the deployment:**
   ```bash
   terraform plan
   ```

5. **Deploy the infrastructure:**
   ```bash
   terraform apply
   ```

6. **Configure kubectl:**
   ```bash
   aws eks update-kubeconfig --region <region> --name <cluster-name>
   ```

## Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `aws_region` | AWS region to deploy resources | `us-west-2` |
| `vpc_cidr` | CIDR block for the VPC | `10.0.0.0/16` |
| `cluster_name` | EKS cluster name | `regulaai-eks` |
| `environment` | Environment name | `production` |
| `node_group_instance_types` | Instance types for EKS node group | `["t3.large"]` |
| `node_group_desired_size` | Desired number of nodes | `2` |
| `node_group_max_size` | Maximum number of nodes | `4` |
| `node_group_min_size` | Minimum number of nodes | `1` |
| `s3_bucket_name` | S3 bucket name | Auto-generated |

## Outputs

After deployment, Terraform will output:

- VPC and subnet IDs
- EKS cluster information (name, endpoint, version)
- S3 bucket details
- KMS key ARN
- kubectl configuration command

## Security Features

- **KMS encryption** for S3 bucket
- **Private subnets** for EKS nodes
- **IRSA** for secure S3 access from pods
- **Security groups** with minimal required access
- **IAM roles** with least privilege

## Cost Optimization

- Use `t3.large` instances for development
- Consider using Spot instances for cost savings
- Monitor NAT Gateway costs (consider NAT instances for dev)
- Use appropriate node group sizing

## Cleanup

To destroy all resources:

```bash
terraform destroy
```

**Warning:** This will delete all resources including the EKS cluster, VPC, and S3 bucket.

## Troubleshooting

### Common Issues

1. **Insufficient IAM permissions**: Ensure your AWS user/role has permissions for EKS, VPC, S3, and IAM
2. **Subnet availability**: Ensure the selected region has enough subnets available
3. **Instance type availability**: Verify the selected instance types are available in your region

### Useful Commands

```bash
# Check cluster status
aws eks describe-cluster --name <cluster-name> --region <region>

# List node groups
aws eks list-nodegroups --cluster-name <cluster-name> --region <region>

# Get cluster credentials
aws eks get-token --cluster-name <cluster-name> --region <region>
```

## Next Steps

After infrastructure deployment:

1. Deploy the RegulaAI application using the Helm chart
2. Configure monitoring and logging
3. Set up CI/CD pipelines
4. Configure backup and disaster recovery 