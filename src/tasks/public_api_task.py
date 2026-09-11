"""
Public API automation task.

Demonstrates HTTP requests, error handling, JSON parsing, and logging.
This task requires no credentials and calls a public API.
"""

import json

import requests

from src.tasks import register_task
from src.logger import get_logger

logger = get_logger(__name__)


@register_task(
    name="public_api",
    description="Call a public API to demonstrate HTTP requests and JSON parsing"
)
def run():
    """Call a public API and display results."""
    logger.info("Public API task started.")

    # Public JSON placeholder API (no auth required)
    url = "https://jsonplaceholder.typicode.com/posts/1"

    try:
        logger.info(f"Calling public API: {url}")
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        data = response.json()
        logger.info(f"API responded with status: {response.status_code}")
        logger.info(f"Content-Type: {response.headers.get('Content-Type', 'unknown')}")
        logger.info(f"Response size: {len(response.content)} bytes")

        # Log non-sensitive fields only
        logger.info(f"Post ID: {data.get('id')}")
        logger.info(f"User ID: {data.get('userId')}")
        logger.info(f"Title: {data.get('title')}")

        return {
            "status": "success",
            "data": data,
        }

    except requests.exceptions.Timeout:
        logger.error(f"Request timed out for {url}")
        return {"status": "error", "message": "Request timed out"}

    except requests.exceptions.ConnectionError:
        logger.error(f"Connection failed for {url}")
        return {"status": "error", "message": "Connection failed"}

    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error: {e}")
        return {"status": "error", "message": str(e)}

    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing error: {e}")
        return {"status": "error", "message": "Invalid JSON response"}

    except Exception as e:
        logger.error(f"Unexpected error: {type(e).__name__}")
        return {"status": "error", "message": "An unexpected error occurred"}