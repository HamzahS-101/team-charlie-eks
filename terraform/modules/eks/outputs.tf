output "oidc_provider_arn" {
  description = "OIDC provider ARN for the EKS cluster"
  value       = module.eks.oidc_provider_arn
}

output "cluster_endpoint" {
  description = "EKS cluster endpoint"
  value       = module.eks.cluster_endpoint
}

output "cluster_certificate_authority_data" {
  description = "EKS cluster certificate authority data"
  value       = module.eks.cluster_certificate_authority_data
}




