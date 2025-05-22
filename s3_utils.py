import boto3
import os
from dotenv import load_dotenv

load_dotenv()

s3 = boto3.client(
    's3',
    region_name=os.getenv("AWS_REGION"),
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
)

BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

def upload_to_s3(file_path, s3_key):
    s3.upload_file(file_path, BUCKET_NAME, s3_key)
    return f"s3://{BUCKET_NAME}/{s3_key}"

def download_from_s3(s3_key, local_path):
    s3.download_file(BUCKET_NAME, s3_key, local_path)
    return local_path
