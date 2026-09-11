"""
Reddit browser automation task.

Uses Playwright to automate Reddit in a browser. This approach is used
because there is no suitable official API for the specific automation needed.

All credentials must come from environment variables (GitHub Secrets).
Never bypass CAPTCHA, MFA, rate limits, or anti-bot protections.

Required environment variables:
  - REDDIT_USERNAME: Reddit account username
  - REDDIT_PASSWORD: Reddit account password
"""

import os
import shutil
from pathlib import Path

from src.tasks import register_task
from src.config import TaskConfig
from src.logger import get_logger

logger = get_logger(__name__)

REQUIRED_VARS = ["REDDIT_USERNAME", "REDDIT_PASSWORD"]


@register_task(
    name="reddit_automation",
    description="Browser automation for Reddit (uses Playwright, credentials from Secrets)"
)
def run():
    """Run Reddit browser automation task."""
    logger.info("Reddit browser automation task started.")

    config = TaskConfig("reddit_automation", required_vars=REQUIRED_VARS)

    if not config.is_valid:
        logger.error(
            "Required environment variables are missing. "
            "Please configure REDDIT_USERNAME and REDDIT_PASSWORD in GitHub Secrets."
        )
        return {
            "status": "skipped",
            "message": "Required secrets not configured.",
        }

    username = config.get("REDDIT_USERNAME")
    password = config.get("REDDIT_PASSWORD")

    logger.info(f"Authenticating Reddit user: {username}")

    try:
        from playwright.sync_api import sync_playwright, TimeoutError as PwTimeout
    except ImportError:
        logger.error(
            "Playwright is not installed. "
            "Run: pip install playwright && playwright install chromium"
        )
        return {"status": "error", "message": "Playwright not installed"}

    browser = None
    try:
        with sync_playwright() as pw:
            # Launch headless Chromium browser
            browser = pw.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",
                ],
            )

            context = browser.new_context(
                viewport={"width": 1280, "height": 720},
                user_agent=(
                    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                ),
            )

            page = context.new_page()
            logger.info("Browser launched successfully.")

            # Step 1: Navigate to Reddit login page
            logger.info("Navigating to Reddit login page...")
            page.goto("https://www.reddit.com/login/", timeout=30000, wait_until="networkidle")
            logger.info(f"Page loaded: {page.title()}")

            # Step 2: Fill in login credentials
            logger.info("Filling in login credentials...")

            # Wait for the login form to load
            page.wait_for_selector("#login-username", timeout=15000)
            page.fill("#login-username", username)

            page.wait_for_selector("#login-password", timeout=5000)
            page.fill("#login-password", password)

            # Step 3: Submit login
            logger.info("Submitting login form...")
            page.click("button[type='submit']")

            # Wait for login to complete (wait for homepage elements)
            try:
                page.wait_for_url("https://www.reddit.com/?*", timeout=20000)
                page.wait_for_timeout(3000)
                logger.info("Login appears successful.")
            except PwTimeout:
                # Check current URL to see if we ended up somewhere unexpected
                current_url = page.url
                logger.warning(f"Login timeout. Current URL: {current_url}")

                # Check for error messages
                error_elements = page.query_selector_all(".error, .notification, [role='alert']")
                if error_elements:
                    for el in error_elements:
                        text = el.text_content()
                        if text:
                            logger.warning(f"Page notification: {text[:100]}")

                logger.error("Login may have failed. Check your credentials.")
                return {
                    "status": "error",
                    "message": "Login failed. Verify credentials in GitHub Secrets.",
                }

            # Step 4: Take a non-sensitive screenshot
            screenshot_dir = "/tmp/automation-outputs"
            os.makedirs(screenshot_dir, exist_ok=True)
            screenshot_path = os.path.join(screenshot_dir, "reddit_homepage.png")

            # Only screenshot the top portion (safe area — no private messages or user details)
            page.screenshot(path=screenshot_path, full_page=False)
            logger.info(f"Non-sensitive screenshot saved to: {screenshot_path}")

            # Step 5: Check for user indicator (logged in state)
            user_menu = page.query_selector("shreddit-logged-in-user-menu")
            if user_menu:
                logger.info("Logged-in user menu detected. Session is active.")
            else:
                # Try alternative indicators
                feed_present = page.query_selector("shreddit-feed")
                if feed_present:
                    logger.info("Feed detected. Session appears active.")

            # Step 6: Clean up
            logger.info("Closing browser...")
            context.close()
            browser.close()
            browser = None

            logger.info("Reddit browser automation task completed successfully.")
            return {
                "status": "success",
                "username": username,
                "action": "login_verified",
            }

    except Exception as e:
        logger.error(f"Browser automation failed: {type(e).__name__}")
        return {"status": "error", "message": f"Unexpected error: {type(e).__name__}"}

    finally:
        # Ensure browser is closed even on failure
        if browser:
            try:
                browser.close()
                logger.info("Browser closed in cleanup.")
            except Exception:
                pass