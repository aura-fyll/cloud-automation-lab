"""
File processing automation task.

Downloads or reads a file, processes it, and produces output.
Demonstrates artifact generation for GitHub Actions.
"""

import json
import os
from datetime import datetime, timezone

import requests

from src.tasks import register_task
from src.logger import get_logger

logger = get_logger(__name__)

# Path for output artifacts
OUTPUT_DIR = "/tmp/automation-outputs"


@register_task(
    name="file_processing",
    description="Download a public file, process it, and produce output artifacts"
)
def run():
    """Process a file and generate output artifacts."""
    logger.info("File processing task started.")

    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Fetch a public JSON file (placeholder API data, no auth needed)
    url = "https://jsonplaceholder.typicode.com/posts"

    try:
        logger.info(f"Fetching data from: {url}")
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        data = response.json()
        logger.info(f"Downloaded {len(data)} records ({len(response.content)} bytes)")

        # Process: generate summary statistics
        user_ids = {}
        for post in data:
            uid = post.get("userId", 0)
            user_ids[uid] = user_ids.get(uid, 0) + 1

        summary = {
            "processed_at": datetime.now(timezone.utc).isoformat(),
            "total_records": len(data),
            "unique_users": len(user_ids),
            "posts_per_user": user_ids,
            "sample_records": data[:3],
        }

        logger.info(f"Summary: {summary['total_records']} records from "
                     f"{summary['unique_users']} unique users")

        # Write summary as JSON artifact
        summary_path = os.path.join(OUTPUT_DIR, "processing_summary.json")
        with open(summary_path, "w") as f:
            json.dump(summary, f, indent=2)
        logger.info(f"Summary written to: {summary_path}")

        # Write a simple CSV report
        csv_path = os.path.join(OUTPUT_DIR, "posts_per_user.csv")
        with open(csv_path, "w") as f:
            f.write("user_id,post_count\n")
            for uid, count in sorted(user_ids.items()):
                f.write(f"{uid},{count}\n")
        logger.info(f"CSV report written to: {csv_path}")

        # Write processing log
        log_path = os.path.join(OUTPUT_DIR, "processing.log")
        with open(log_path, "w") as f:
            f.write(f"[INFO] File processing task completed at {summary['processed_at']}\n")
            f.write(f"[INFO] Total records processed: {summary['total_records']}\n")
            f.write(f"[INFO] Output files: summary.json, posts_per_user.csv\n")
        logger.info(f"Processing log written to: {log_path}")

        logger.info("File processing task completed successfully.")
        return {
            "status": "success",
            "output_dir": OUTPUT_DIR,
            "files": ["processing_summary.json", "posts_per_user.csv", "processing.log"],
            "summary": summary,
        }

    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch data: {e}")
        return {"status": "error", "message": str(e)}
    except Exception as e:
        logger.error(f"Unexpected error: {type(e).__name__}")
        return {"status": "error", "message": "An unexpected error occurred"}