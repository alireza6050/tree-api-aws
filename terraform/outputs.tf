output "api_url" {
  description = "The URL of the API Gateway endpoint"
  value       = aws_apigatewayv2_api.api.api_endpoint
}
