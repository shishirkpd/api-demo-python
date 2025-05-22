import boto3
import os
import tempfile
from moto import mock_s3
import pytest
from s3_utils import upload_to_s3, download_from_s3

BUCKET_NAME = "test-bucket"

@pytest.fixture(scope="function")
def s3_mock():
    with mock_s3():
        s3 = boto3.client("s3", region_name="us-east-1")
        s3.create_bucket(Bucket=BUCKET_NAME)
        yield

def test_upload_and_download_to_s3(s3_mock, monkeypatch):
    # Patch environment variables
    monkeypatch.setenv("S3_BUCKET_NAME", BUCKET_NAME)
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "testing")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "testing")
    monkeypatch.setenv("AWS_REGION", "us-east-1")

    # Create a dummy file
    file_content = b"Test content"
    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.write(file_content)
        f_path = f.name

    s3_key = "test/testfile.txt"
    upload_to_s3(f_path, s3_key)

    # Download file back
    output_file = f_path + "_downloaded"
    download_from_s3(s3_key, output_file)

    with open(output_file, "rb") as f:
        assert f.read() == file_content

    os.remove(f_path)
    os.remove(output_file)
