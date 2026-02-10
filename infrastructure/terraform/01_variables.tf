variable "aws_region" {
  description = "AWS Region for S3 Buckets"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Base name for resources"
  type        = string
  default     = "dynamic-pricing"
}

variable "snowflake_account" {
  description = "Snowflake Account Identifier"
  type        = string
}

variable "snowflake_user" {
  description = "Snowflake Username"
  type        = string
}

variable "snowflake_password" {
  description = "Snowflake Password"
  type        = string
  sensitive   = true
}