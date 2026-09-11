"""
Authenticated API template task.

Template for accessing an authorized third-party API using credentials
stored in GitHub Secrets. This task demonstrates secure handling of
environment variables without exposing sensitive values.

Required environment variables:
  - SERVICE_API_TOKEN: API token for the authorized service
  - SERVICE_BASE_URL: Base URL for the API (e.g., https://api.example.com/v1)

This task will fail gracefully if the required secrets are not configured.
"""

import requests

from src.tasks import register_task
from src.config import TaskConfig
from src.logger import get_logger

logger = get_logger(__name__)

# Define required environment variables for this task
REQUIRED_VARS = ["SERVICE_API_TOKEN", "SERVICE_BASE_URL"]


@register_task(
    name="authed_api",
    description="Template for accessing an authorized API with credentials from GitHub Secrets"
)
def run():
    """Template demonstrating authenticated API access.

    Replace the endpoint and logic below with your actual automation logic.
    """
    logger.info("Authenticated API template task started.")

    # Validate required credentials are available
    config = TaskConfig("authed_api", required_vars=REQUIRED_VARS)

    if not config.is_valid:
        logger.error(
            "Required environment variables are missing. "
            "Please configure SERVICE_API_TOKEN and SERVICE_BASE_URL in GitHub Secrets."
        )
        return {
            "status": "skipped",
            "message": "Required secrets not configured. See README for setup instructions.",
        }

    # Retrieve credentials (values are never logged)
    token = config.get("SERVICE_API_TOKEN")
    base_url = config.get("SERVICE_BASE_URL")

    logger.info(f"Using API base URL: {base_url}")
    logger.info("Authenticating with provided credentials...")

    # Build authenticated request
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "User-Agent": "cloud-automation-lab/1.0",
    }

    try:
        # Example: API health check endpoint
        url = f"{base_url}/health"
        logger.info(f"Calling: {url}")

        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        data = response.json()
        logger.info(f"API responded with status: {response.status_code}")

        # Log the response status but NOT the full response if it contains auth info
        if response.status_code == 200:
            logger.info("Authentication successful. API is responsive.")

        return {
            "status": "success",
            "status_code": response.status_code,
            "endpoint": "/health",
        }

    except requests.exceptions.HTTPError as e:
        if response.status_code == 401:
            logger.error("Authentication failed. Check your SERVICE_API_TOKEN.")
        elif response.status_code == 403:
            logger.error("Access forbidden. Token may lack required permissions.")
        elif response.status_code == 404:
            logger.error(f"Endpoint not found: {url}")
        else:
            logger.error(f"HTTP error: {response.status_code}")
        return {"status": "error", "message": f"HTTP {response.status_code}"}

    except requests.exceptions.ConnectionError:
        logger.error(f"Could not connect to {base_url}. Check SERVICE_BASE_URL.")
        return {"status": "error", "message": "Connection failed"}

    except requests.exceptions.Timeout:
        logger.error(f"Request timed out for {base_url}.")
        return {"status": "error", "message": "Request timed out"}

    except Exception as e:
        logger.error(f"Unexpected error: {type(e).__name__}")
        return {"status": "error", "message": "An unexpected error occurred"}