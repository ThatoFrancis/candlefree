terraform {
  required_version = ">= 1.5"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.4"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

variable "aws_region" {
  description = "Region where the AgentCore runtime lives"
  type        = string
  default     = "us-east-1"
}

variable "agent_runtime_arn" {
  description = "ARN of the deployed CandleFree AgentCore runtime"
  type        = string
}

variable "schedule_expression" {
  description = "How often CandleFree runs its background pass"
  type        = string
  default     = "rate(30 minutes)"
}

variable "budget_limit_usd" {
  description = "Monthly cost budget alert threshold"
  type        = string
  default     = "10"
}

variable "alert_email" {
  description = "Email for budget alerts"
  type        = string
}
