"""Tests for the Reddit browser automation task."""


class TestRedditTaskRegistration:
    """Tests for Reddit task registration."""

    def test_reddit_task_is_registered(self):
        """Verify the reddit_automation task is discoverable after import."""
        # Importing the module triggers the @register_task decorator
        import src.tasks.reddit_task  # noqa: F401
        from src.tasks import get_task
        task_func = get_task("reddit_automation")
        assert task_func is not None, "reddit_automation task should be registered"

    def test_reddit_task_returns_dict(self):
        """Verify the task returns a dict even when failing gracefully."""
        from src.tasks.reddit_task import run
        result = run()
        assert isinstance(result, dict)
        assert "status" in result

    def test_reddit_task_skipped_without_credentials(self):
        """Verify graceful skip when secrets are missing."""
        import os
        os.environ.pop("REDDIT_USERNAME", None)
        os.environ.pop("REDDIT_PASSWORD", None)

        from src.tasks.reddit_task import run
        result = run()
        assert result.get("status") == "skipped"
        assert "Required secrets" in result.get("message", "")