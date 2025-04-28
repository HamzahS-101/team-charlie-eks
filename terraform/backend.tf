terraform {
  backend "s3" {
    bucket       = "charlie-eks-project"
    key          = "terraform.tfstate"
    region       = "eu-west-2"
    encrypt      = true
    use_lockfile = true
  }
}