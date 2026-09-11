"""
Configuration module for cloud-automation-lab.

All sensitive configuration values must be provided via environment variables.
Never hardcode credentials, tokens, or secrets in this file or anywhere in the codebase.
"""

import os
from typing import Dict, Optional


# Environment variable prefixes used across tasks
ENV_PREFIX = "AUTOMATION_"


def get_env(name: str, default: Optional[str] = None, required: bool = False) -> Optional[str]:
    """Retrieve an environment variable safely.

    Args:
        name: Environment variable name
        default: Default value if not set
        required: If True, raise ValueError when variable is missing

    Returns:
        Environment variable value or default

    Raises:
        ValueError: If required is True and variable is not set
    """
    value = os.environ.get(name, default)

    if required and value is None:
        raise ValueError(f"Required environment variable '{name}' is not set.")

    return value


def get_all_env(prefix: str = "") -> Dict[str, str]:
    """Retrieve all environment variables matching an optional prefix.

    Args:
        prefix: Optional prefix filter

    Returns:
        Dictionary of matching environment variables
    """
    if prefix:
        return {k: v for k, v in os.environ.items() if k.startswith(prefix)}

    return dict(os.environ)


def validate_required_vars(required_vars: list) -> None:
    """Validate that all required environment variables are set.

    Args:
        required_vars: List of environment variable names

    Raises:
        ValueError: If any required variable is missing
    """
    missing = []

    for var in required_vars:
        if not os.environ.get(var):
            missing.append(var)

    if missing:
        raise ValueError(
            f"Missing required environment variable(s): {', '.join(missing)}. "
            "Please set them in GitHub Secrets or your local .env file."
        )


class TaskConfig:
    """Configuration wrapper for individual tasks.

    Tasks receive a TaskConfig instance containing only the configuration
    values they explicitly request, avoiding broad access to all secrets.
    """

    def __init__(self, task_name: str, required_vars: Optional[list] = None):
        """Initialize task configuration.

        Args:
            task_name: Name of the task
            required_vars: List of required environment variables for this task
        """
        self.task_name = task_name
        self._required_vars = required_vars or []

    def get(self, name: str, default: Optional[str] = None) -> Optional[str]:
        """Get a configuration value from the environment.

        Args:
            name: Environment variable name
            default: Default value if not set

        Returns:
            Configuration value or default
        """
        return get_env(name, default)

    @property
    def is_valid(self) -> bool:
        """Check if all required variables are present."""
        for var in self._required_vars:
            if not os.environ.get(var):
                return False
        return True