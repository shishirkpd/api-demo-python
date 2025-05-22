from logger import get_logger
from s3_utils import upload_to_s3
from datetime import datetime
import os

logger = get_logger("cron_script")

def run():
    logger.info(f"script started")
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    filename = f"{output_dir}/data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(filename, "w") as f:
        f.write(f"Sample data created at {datetime.now()}\n")

    logger.info(f"File created: {filename}")

    s3_key = f"cron_output/{os.path.basename(filename)}"
    upload_to_s3(filename, s3_key)
    logger.info(f"File uploaded to S3 as: {s3_key}")

    return None