from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    database_url: str
    database_url_sync: str
    postgres_password: str

    # S3/MinIO
    s3_endpoint_url: str
    s3_access_key: str
    s3_secret_key: str
    s3_bucket_name: str
    aws_region: str

    # Clerk
    clerk_secret_key: str
    clerk_publishable_key: str
    clerk_jwks_url: str
    clerk_jwks_public_key: str
    clerk_webhook_signing_secret: str

    class Config:
        env_file = "/app/.env"


settings = Settings()
