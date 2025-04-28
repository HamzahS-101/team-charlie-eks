resource "aws_route53_zone" "route53_zone" {
  name = var.domain_name
  vpc {
    vpc_id = var.vpc_id
  }
}