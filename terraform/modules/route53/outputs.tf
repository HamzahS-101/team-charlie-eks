output "zone_id" {
  description = "ID of hosted zone."
  value       = aws_route53_zone.route53_zone.zone_id
}

output "zone_arn" {
  description = "ARN of hosted Zone."
  value       = aws_route53_zone.route53_zone.arn
}