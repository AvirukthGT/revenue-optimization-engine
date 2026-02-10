# I create the main Data Lake bucket
resource "aws_s3_bucket" "raw_data_lake" {
  bucket = "de-project-${var.project_name}-raw-source"

  tags = {
    Project     = "Revenue Optimization Engine"
    Environment = "Production"
    ManagedBy   = "Terraform"
  }
}

# I enable versioning so I never accidentally lose training data
resource "aws_s3_bucket_versioning" "raw_data_lake_ver" {
  bucket = aws_s3_bucket.raw_data_lake.id
  versioning_configuration {
    status = "Enabled"
  }
}

# I create folders (prefixes) for organization
resource "aws_s3_object" "folder_olist" {
  bucket = aws_s3_bucket.raw_data_lake.id
  key    = "olist/"
}

resource "aws_s3_object" "folder_weather" {
  bucket = aws_s3_bucket.raw_data_lake.id
  key    = "weather/"
}

resource "aws_s3_object" "folder_competitors" {
  bucket = aws_s3_bucket.raw_data_lake.id
  key    = "competitors/"
}