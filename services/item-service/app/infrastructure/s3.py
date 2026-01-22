import os
import boto3
from botocore.config import Config

S3_ENDPOINT = os.getenv("S3_ENDPOINT")  # e.g. http://minio:9000 (local) or empty for AWS
S3_PUBLIC_ENDPOINT = os.getenv("S3_PUBLIC_ENDPOINT", S3_ENDPOINT)
S3_BUCKET = os.getenv("S3_BUCKET", "campus-media")
S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY", "")
S3_SECRET_KEY = os.getenv("S3_SECRET_KEY", "")
S3_REGION = os.getenv("S3_REGION", "us-east-1")


def get_s3_client(for_presign: bool = False):
    public_endpoint = os.getenv("S3_PUBLIC_ENDPOINT", "").strip()
    endpoint = S3_ENDPOINT

    # For presigned URLs we must sign with the same host the client will call.
    if for_presign and public_endpoint:
        endpoint = public_endpoint

    kwargs = {
        "region_name": S3_REGION,
        "config": Config(signature_version="s3v4"),
    }

    if endpoint:
        kwargs["endpoint_url"] = endpoint
        kwargs["aws_access_key_id"] = S3_ACCESS_KEY
        kwargs["aws_secret_access_key"] = S3_SECRET_KEY

    return boto3.client("s3", **kwargs)


def presign_put(key: str, content_type: str, expires_in: int = 900) -> str:
    s3 = get_s3_client(for_presign=True)
    return s3.generate_presigned_url(
        "put_object",
        Params={"Bucket": S3_BUCKET, "Key": key, "ContentType": content_type},
        ExpiresIn=expires_in,
    )


def presign_get(key: str, expires_in: int = 900) -> str:
    s3 = get_s3_client(for_presign=True)
    return s3.generate_presigned_url(
        "get_object",
        Params={"Bucket": S3_BUCKET, "Key": key},
        ExpiresIn=expires_in,
    )
