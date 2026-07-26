import boto3

from app.core.config import settings
from botocore.client import BaseClient
from botocore.exceptions import BotoCoreError, ClientError


def get_s3_client() -> BaseClient:
    return boto3.client(
        "s3",
        endpoint_url=settings.s3_endpoint_url,
        aws_access_key_id=settings.s3_access_key,
        aws_secret_access_key=settings.s3_secret_key,
        region_name=settings.aws_region,
    )


def generate_presigned_url(upload_id: int, org_id: int, filename: str) -> str:
    try:
        s3 = get_s3_client()
        key = f"bronze/org_id={org_id}/upload_id={upload_id}/filename={filename}"
        url = s3.generate_presigned_url(
            "put_object",
            Params={"Bucket": settings.s3_bucket_name, "Key": key},
            ExpiresIn=3600,
        )
        return url
    except (BotoCoreError, ClientError) as e:
        raise Exception(f"Failed to generate presigned URL: {str(e)}")
