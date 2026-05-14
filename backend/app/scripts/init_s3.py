from app.core.s3 import get_s3_client


def init_buckets():
    s3 = get_s3_client()  #  uses centralized config

    buckets = ["plozeus-data"]

    for bucket in buckets:
        try:
            s3.create_bucket(Bucket=bucket)
            print(f"✓ Created {bucket}")
        except s3.exceptions.BucketAlreadyOwnedByYou:
            print(f"✓ {bucket} exists")


if __name__ == "__main__":
    init_buckets()
