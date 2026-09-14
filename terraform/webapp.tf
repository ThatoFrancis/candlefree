# Public live demo — FastAPI dashboard on Lambda + Function URL

resource "aws_iam_role" "webapp" {
  name = "candlefree-webapp"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy" "webapp" {
  name = "candlefree-webapp"
  role = aws_iam_role.webapp.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        # Lets the "Run CandleFree now" button invoke Claude on Bedrock
        Action   = ["bedrock:InvokeModel", "bedrock:InvokeModelWithResponseStream"]
        Effect   = "Allow"
        Resource = "*"
      },
      {
        Action   = ["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"]
        Effect   = "Allow"
        Resource = "arn:aws:logs:*:*:*"
      }
    ]
  })
}

resource "aws_lambda_function" "webapp" {
  function_name    = "candlefree-webapp"
  role             = aws_iam_role.webapp.arn
  runtime          = "python3.12"
  handler          = "candlefree.api.lambda_handler.handler"
  filename         = "${path.module}/webapp.zip"
  source_code_hash = filebase64sha256("${path.module}/webapp.zip")
  timeout          = 120
  memory_size      = 1024

  environment {
    variables = {
      CANDLEFREE_DEMO_MODE     = "true"
      CANDLEFREE_BEDROCK_REGION = "us-east-1"
      TZ                       = "Africa/Johannesburg"
    }
  }
}

resource "aws_lambda_function_url" "webapp" {
  function_name      = aws_lambda_function.webapp.function_name
  authorization_type = "NONE"
}

output "live_demo_url" {
  value = aws_lambda_function_url.webapp.function_url
}
