data "archive_file" "trigger" {
  type        = "zip"
  source_file = "${path.module}/lambda/trigger.py"
  output_path = "${path.module}/.build/trigger.zip"
}

resource "aws_iam_role" "trigger" {
  name = "candlefree-trigger-lambda"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy" "trigger" {
  name = "candlefree-trigger-policy"
  role = aws_iam_role.trigger.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = "bedrock-agentcore:InvokeAgentRuntime"
        Resource = [var.agent_runtime_arn, "${var.agent_runtime_arn}/*"]
      },
      {
        Effect   = "Allow"
        Action   = ["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"]
        Resource = "arn:aws:logs:*:*:*"
      }
    ]
  })
}

resource "aws_lambda_function" "trigger" {
  function_name    = "candlefree-scheduled-trigger"
  role             = aws_iam_role.trigger.arn
  handler          = "trigger.handler"
  runtime          = "python3.13"
  timeout          = 300
  filename         = data.archive_file.trigger.output_path
  source_code_hash = data.archive_file.trigger.output_base64sha256

  environment {
    variables = {
      AGENT_RUNTIME_ARN = var.agent_runtime_arn
      AGENT_REGION      = var.aws_region
    }
  }
}

resource "aws_iam_role" "scheduler" {
  name = "candlefree-scheduler"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "scheduler.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy" "scheduler" {
  name = "candlefree-scheduler-policy"
  role = aws_iam_role.scheduler.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = "lambda:InvokeFunction"
      Resource = aws_lambda_function.trigger.arn
    }]
  })
}

resource "aws_scheduler_schedule" "candlefree" {
  name                = "candlefree-background-pass"
  schedule_expression = var.schedule_expression

  flexible_time_window {
    mode = "OFF"
  }

  target {
    arn      = aws_lambda_function.trigger.arn
    role_arn = aws_iam_role.scheduler.arn
  }
}

resource "aws_budgets_budget" "candlefree" {
  name         = "candlefree-monthly"
  budget_type  = "COST"
  limit_amount = var.budget_limit_usd
  limit_unit   = "USD"
  time_unit    = "MONTHLY"

  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                  = 80
    threshold_type             = "PERCENTAGE"
    notification_type          = "ACTUAL"
    subscriber_email_addresses = [var.alert_email]
  }
}

output "lambda_function" {
  value = aws_lambda_function.trigger.function_name
}

output "schedule" {
  value = aws_scheduler_schedule.candlefree.name
}
