from flask import Flask, request, send_file, jsonify
import os
import requests
from s3_utils import upload_to_s3, download_from_s3

app = Flask(__name__)
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

@app.route('/download-url', methods=['POST'])
def download_url():
    data = request.json
    url = data.get("url")
    if not url:
        return {"error": "URL is required"}, 400

    filename = url.split("/")[-1]
    local_path = os.path.join(DOWNLOAD_DIR, filename)

    # Download the file
    try:
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(local_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
    except Exception as e:
        return {"error": str(e)}, 500

    # Upload to S3
    try:
        s3_key = f"uploaded/{filename}"
        upload_to_s3(local_path, s3_key)
        return {"message": "File downloaded and uploaded to S3", "s3_key": s3_key}
    except Exception as e:
        return {"error": str(e)}, 500

@app.route('/fetch-from-s3', methods=['GET'])
def fetch_from_s3():
    s3_key = request.args.get("s3_key")
    if not s3_key:
        return {"error": "s3_key is required"}, 400

    local_path = os.path.join(DOWNLOAD_DIR, s3_key.replace("/", "_"))

    try:
        download_from_s3(s3_key, local_path)
        return send_file(local_path, as_attachment=True)
    except Exception as e:
        return {"error": str(e)}, 500

if __name__ == '__main__':
    app.run(debug=True)
