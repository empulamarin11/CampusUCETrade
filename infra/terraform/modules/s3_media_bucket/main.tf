
# 1. Random suffix to ensure unique bucket name globally
resource "random_id" "suffix" {
  byte_length = 4
}

# 2. The Bucket itself
resource "aws_s3_bucket" "this" {
  bucket = "${var.name}-media-${random_id.suffix.hex}"
  
  # CRITICAL FOR DEV/ACADEMY:
  # Allows Terraform to delete the bucket even if it contains files.
  force_destroy = true 

  tags = merge(var.tags, {
    Name = "${var.name}-media"
  })
}

# 3. Enable Versioning (Optional, good for backup)
resource "aws_s3_bucket_versioning" "this" {
  bucket = aws_s3_bucket.this.id
  versioning_configuration {
    status = "Enabled"
  }
}

# 4. Security: Block Public Access (Make it private by default)
resource "aws_s3_bucket_public_access_block" "this" {
  bucket = aws_s3_bucket.this.id

  block_public_acls       = true
  ignore_public_acls      = true
  block_public_policy     = true
  restrict_public_buckets = true
}