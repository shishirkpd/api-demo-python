import os
import tempfile
import pytest
from unittest.mock import patch
from app import app as flask_app


@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as client:
        yield client


def test_download_url_success(client):
    test_url = "https://example.com/testfile.txt"
    filename = "testfile.txt"
    dummy_file_content = b"Hello, this is test data!"

    with patch("app.requests.get") as mock_get, \
            patch("app.upload_to_s3") as mock_upload:
        mock_response = mock_get.return_value
        mock_response.iter_content.return_value = [dummy_file_content]
        mock_response.__enter__.return_value = mock_response
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None

        mock_upload.return_value = f"s3://dummy-bucket/uploaded/{filename}"

        response = client.post("/download-url", json={"url": test_url})
        assert response.status_code == 200
        assert "s3_key" in response.json
        assert response.json["s3_key"] == f"uploaded/{filename}"


def test_download_url_missing_url(client):
    response = client.post("/download-url", json={})
    assert response.status_code == 400
    assert response.json["error"] == "URL is required"


def test_fetch_from_s3_success(client):
    s3_key = "uploaded/testfile.txt"
    dummy_data = b"Dummy file content"

    with patch("app.download_from_s3") as mock_download, \
            patch("app.send_file") as mock_send_file:
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        temp_file.write(dummy_data)
        temp_file.close()

        mock_download.return_value = temp_file.name
        mock_send_file.return_value = "sending dummy file"

        response = client.get(f"/fetch-from-s3?s3_key={s3_key}")
        assert response.status_code == 200
        assert b"sending dummy file" in response.data or response.data == b""

        os.remove(temp_file.name)


def test_fetch_from_s3_missing_key(client):
    response = client.get("/fetch-from-s3")
    assert response.status_code == 400
    assert response.json["error"] == "s3_key is required"
