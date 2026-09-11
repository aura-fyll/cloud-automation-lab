"""
System information task.

Collects non-sensitive information about the temporary GitHub Actions VM.
This task requires no credentials and works on any Ubuntu runner.
"""

import os
import platform
import shutil
import subprocess

from src.tasks import register_task
from src.logger import get_logger

logger = get_logger(__name__)


@register_task(
    name="system_info",
    description="Collect non-sensitive VM system information"
)
def run():
    """Collect and display system information from the runner VM."""
    logger.info("System information task started.")

    info = {
        "operating_system": platform.system(),
        "os_release": platform.release(),
        "os_version": platform.version(),
        "hostname": platform.node(),
        "architecture": platform.machine(),
        "processor": platform.processor(),
        "python_version": platform.python_version(),
        "python_implementation": platform.python_implementation(),
    }

    logger.info(f"OS: {info['operating_system']} {info['os_release']}")
    logger.info(f"Architecture: {info['architecture']}")
    logger.info(f"Python: {info['python_version']} ({info['python_implementation']})")
    logger.info(f"Hostname: {info['hostname']}")

    # Disk usage (non-sensitive, general paths only)
    try:
        disk = shutil.disk_usage("/")
        info["disk_total_gb"] = round(disk.total / (1024 ** 3), 2)
        info["disk_free_gb"] = round(disk.free / (1024 ** 3), 2)
        info["disk_used_gb"] = round(disk.used / (1024 ** 3), 2)
        logger.info(f"Disk: {info['disk_free_gb']} GB free of {info['disk_total_gb']} GB")
    except Exception as e:
        logger.warning(f"Could not retrieve disk info: {e}")

    # Memory info (summary only, no process-level details)
    try:
        result = subprocess.run(
            ["free", "-h"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            info["memory_summary"] = result.stdout.strip()
            logger.info(f"Memory:\n{result.stdout}")
    except Exception as e:
        logger.warning(f"Could not retrieve memory info: {e}")

    # Current working directory
    cwd = os.getcwd()
    info["current_directory"] = cwd
    logger.info(f"Working directory: {cwd}")

    # Environment info (safe, non-sensitive vars only)
    logger.info(f"USER: {os.environ.get('USER', 'unknown')}")
    logger.info(f"SHELL: {os.environ.get('SHELL', 'unknown')}")

    logger.info("System information task completed successfully.")
    return {"status": "success", "system_info": info}