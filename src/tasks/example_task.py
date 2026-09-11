"""
Example automation task.

This is a minimal demonstration task showing the task interface.
Use this as a template when creating new tasks.
"""

from src.tasks import register_task
from src.logger import get_logger

logger = get_logger(__name__)


@register_task(name="example", description="Demonstration task that prints a message")
def run():
    """Run the example task."""
    logger.info("Example task started.")

    message = "Hello from cloud-automation-lab! This is a demonstration task."
    logger.info(f"Message: {message}")

    logger.info("Example task completed successfully.")
    return {"status": "success", "message": message}