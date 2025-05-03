provider "aws" {
  region = var.aws_region
}

resource "aws_iam_role" "lambda_exec_role" {
  name = "tree_api_lambda_exec"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_logs" {
  role       = aws_iam_role.lambda_exec_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "lambda_dynamo" {
  role       = aws_iam_role.lambda_exec_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess"
}

resource "aws_lambda_function" "tree_api" {
  function_name = "tree-api-handler"
  role          = aws_iam_role.lambda_exec_role.arn
  runtime       = "python3.10"
  handler       = "handler.lambda_handler"
  filename      = "${path.module}/../lambda.zip"
  source_code_hash = filebase64sha256("${path.module}/../lambda.zip")

  environment {
    variables = {
      TABLE_NAME = aws_dynamodb_table.tree.name
    }
  }
}

resource "aws_dynamodb_table" "tree" {
  name         = "TreeNodes"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "id"

  attribute {
    name = "id"
    type = "S"
  }
}

resource "aws_apigatewayv2_api" "api" {
  name          = "TreeApiHTTP"
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_integration" "lambda_integration" {
  api_id                = aws_apigatewayv2_api.api.id
  integration_type      = "AWS_PROXY"
  integration_uri       = aws_lambda_function.tree_api.invoke_arn
  integration_method    = "POST"
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "get_tree" {
  api_id    = aws_apigatewayv2_api.api.id
  route_key = "GET /api/tree"
  target    = "integrations/${aws_apigatewayv2_integration.lambda_integration.id}"
}

resource "aws_apigatewayv2_route" "post_tree" {
  api_id    = aws_apigatewayv2_api.api.id
  route_key = "POST /api/tree"
  target    = "integrations/${aws_apigatewayv2_integration.lambda_integration.id}"
}

resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.api.id
  name        = "$default"
  auto_deploy = true
}

resource "aws_lambda_permission" "api_gateway" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.tree_api.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.api.execution_arn}/*/*"
}
