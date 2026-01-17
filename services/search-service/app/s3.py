import os
import boto3
from botocore.config import Config

S3_BUCKET = os.getenv("S3_BUCKET", "campus-media")
S3_ENDPOINT = os.getenv("S3_ENDPOINT")  # inside docker: http://minio:9000
S3_PUBLIC_BASE_URL = os.getenv("S3_PUBLIC_BASE_URL")  # browser: http://localhost:9000
S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY", "")
S3_SECRET_KEY = os.getenv("S3_SECRET_KEY", "")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")


def _client():
    kwargs = {
        "service_name": "s3",
        "region_name": AWS_REGION,
        "config": Config(signature_version="s3v4"),
    }

    # Local MinIO
    if S3_ENDPOINT:
        kwargs["endpoint_url"] = S3_ENDPOINT
        kwargs["aws_access_key_id"] = S3_ACCESS_KEY
        kwargs["aws_secret_access_key"] = S3_SECRET_KEY

    return boto3.client(**kwargs)


def _to_public(url: str) -> str:
    # Replace internal endpoint with public base URL for the browser
    if S3_PUBLIC_BASE_URL and S3_ENDPOINT and url.startswith(S3_ENDPOINT):
        return S3_PUBLIC_BASE_URL + url[len(S3_ENDPOINT):]
    return url


def presign_get(key: str, expires_in: int = 900) -> str:
    s3 = _client()
    url = s3.generate_presigned_url(
        ClientMethod="get_object",
        Params={"Bucket": S3_BUCKET, "Key": key},
        ExpiresIn=expires_in,
    )
    return _to_public(url)
