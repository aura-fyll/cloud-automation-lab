"""
Browser automation module (optional).

Use this module for authorized browser-based automation tasks when:
- There is no suitable official API available
- The account owner explicitly authorizes the automation
- The automation follows the service's terms of service
- No security controls are bypassed (CAPTCHA, MFA, bot detection, etc.)

All credentials must be provided via environment variables (GitHub Secrets).
Screenshots for debugging must never contain sensitive information.

IMPORTANT:
- Never attempt to bypass CAPTCHA, two-factor authentication, or MFA
- Never bypass rate limits or anti-bot protections
- Never upload screenshots containing credentials or sensitive data
- Always close browser processes properly in cleanup/error handlers
"""

from src.logger import get_logger

logger = get_logger(__name__)


def is_available() -> bool:
    """Check if browser automation dependencies are installed.

    Returns:
        True if playwright or selenium is available
    """
    try:
        import playwright  # noqa: F401
        return True
    except ImportError:
        pass

    try:
        import selenium  # noqa: F401
        return True
    except ImportError:
        pass

    return False


SUPPORTED_TASKS = {
    # Future browser-based tasks can be registered here
    # Example:
    # "browser_example": "Example browser automation (requires credentials)"
}


def list_tasks() -> dict:
    """List available browser automation tasks.

    Returns:
        Dictionary of task_name -> description
    """
    return dict(SUPPORTED_TASKS)