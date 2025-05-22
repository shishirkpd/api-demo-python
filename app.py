from flask import Flask, request, send_file, jsonify
import os
import requests

from logger import get_logger
from s3_utils import upload_to_s3, download_from_s3

from apscheduler.schedulers.background import BackgroundScheduler
import script.script_1 as cron_job  # <-- import your script

app = Flask(__name__)
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)
logger = get_logger("app")

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
        logger.info(f"s3_key is required")
        return {"error": "s3_key is required"}, 400

    local_path = os.path.join(DOWNLOAD_DIR, s3_key.replace("/", "_"))

    try:
        logger.info(f"API triggered: to {s3_key}")
        download_from_s3(s3_key, local_path)
        return send_file(local_path, as_attachment=True)
    except Exception as e:
        logger.exception("Download failed")
        return {"error": str(e)}, 500

def start_cron():
    scheduler = BackgroundScheduler()
    scheduler.add_job(cron_job.run, 'cron', minute='*/1')  # runs every 5 min
    scheduler.start()
    logger.info("Cron job scheduled")

if __name__ == '__main__':
    start_cron()
    app.run(host='0.0.0.0', port=5005)
