variable "region" {
  description = "AWS Region"
  type        = string
  default     = "eu-west-2"
}

# VPC

variable "vpc_cidr" {
  type        = string
  description = "CIDR block for the VPC."
  default     = "10.0.0.0/16"
}

variable "vpc_name" {
  type        = string
  description = "Name of the VPC."
  default     = "team-charlie-eks"
}

variable "public_subnet_cidrs" {
  type        = list(string)
  description = "List of CIDR blocks for public subnets."
  default     = ["10.0.0.0/24", "10.0.1.0/24"]
}

variable "private_subnet_cidrs" {
  type        = list(string)
  description = "List of CIDR blocks for private subnets."
  default     = ["10.0.2.0/24", "10.0.3.0/24"]
}

variable "availability_zones" {
  type        = list(string)
  description = "List of availability zones to use."
  default     = ["eu-west-2a", "eu-west-2b"]
}

variable "cluster_name" {
  description = "Name of the EKS cluster"
  type        = string
  default     = "team-charlie"
}

#Route 53

variable "domain_name" {
  description = "Name of the domain"
  type        = string
  default     = "domain.com"
}