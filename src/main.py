#!/usr/bin/env python3
"""
Main entry point for cloud-automation-lab.

Usage:
    python src/main.py --task <task_name>
    python src/main.py --list-tasks
    python src/main.py --help

The application discovers tasks automatically from src/tasks/ and executes
the selected task. All sensitive configuration must come from environment
variables (GitHub Secrets).
"""

import argparse
import sys
import os

# Ensure the project root is on sys.path for both:
#   python src/main.py
#   python -m src.main
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.logger import setup_logger, get_logger
from src.config import get_env
from src.tasks import discover_tasks, get_task, list_tasks, get_task_names


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="cloud-automation-lab — a secure, modular automation platform",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python src/main.py --task example\n"
            "  python src/main.py --task system_info\n"
            "  python src/main.py --task public_api\n"
            "  python src/main.py --list-tasks\n"
        ),
    )

    parser.add_argument(
        "--task",
        type=str,
        default=None,
        help="Name of the automation task to execute",
    )

    parser.add_argument(
        "--list-tasks",
        action="store_true",
        help="List all available automation tasks and exit",
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose (debug) logging",
    )

    return parser.parse_args()


def main():
    """Application entry point."""
    # Parse arguments
    args = parse_args()

    # Setup logging
    level = "DEBUG" if args.verbose else "INFO"
    import logging
    setup_logger(level=getattr(logging, level))
    logger = get_logger()

    # Discover and register tasks
    discover_tasks()

    available_tasks = get_task_names()

    # Handle --list-tasks
    if args.list_tasks:
        print("\nAvailable automation tasks:\n")
        tasks = list_tasks()
        for name in sorted(tasks.keys()):
            desc = tasks[name]
            print(f"  {name:20s} {desc}")
        print()
        return 0

    # Handle --task
    if args.task:
        task_name = args.task
        logger.info(f"cloud-automation-lab starting...")
        logger.info(f"Selected task: {task_name}")

        # Validate task exists
        task_func = get_task(task_name)
        if task_func is None:
            logger.error(f"Unknown task: '{task_name}'")
            logger.error(f"Available tasks: {', '.join(available_tasks)}")
            return 1

        # Execute task
        try:
            result = task_func()
            logger.info("Task execution completed.")
            if result and isinstance(result, dict):
                status = result.get("status", "unknown")
                logger.info(f"Result status: {status}")
            return 0 if result and isinstance(result, dict) and result.get("status") == "success" else 1
        except Exception as e:
            logger.error(f"Task failed with unexpected error: {e}")
            return 1

    # No task specified
    logger.error("No task specified. Use --task <task_name> or --list-tasks.")
    print(f"\nAvailable tasks: {', '.join(available_tasks)}\n")
    return 1


if __name__ == "__main__":
    sys.exit(main())