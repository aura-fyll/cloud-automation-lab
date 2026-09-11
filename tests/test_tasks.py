"""Tests for the task system."""

import pytest

from src.tasks import (
    register_task,
    get_task,
    list_tasks,
    get_task_names,
    discover_tasks,
)


# Test task registry directly (not via decorator)
@register_task(name="_test_task", description="Test task for unit tests")
def _test_run():
    return {"status": "success"}


class TestTaskRegistry:
    """Tests for task registration and discovery."""

    def test_register_task_decorator(self):
        """Test that @register_task works."""
        func = get_task("_test_task")
        assert func is not None
        assert func() == {"status": "success"}

    def test_get_task_returns_none_for_unknown(self):
        """Test that unknown tasks return None."""
        assert get_task("nonexistent_task") is None

    def test_list_tasks_includes_registered(self):
        """Test that tasks appear in listing."""
        tasks = list_tasks()
        assert "_test_task" in tasks
        assert tasks["_test_task"] == "Test task for unit tests"

    def test_get_task_names(self):
        """Test that get_task_names returns list of names."""
        names = get_task_names()
        assert "_test_task" in names


class TestTaskDiscovery:
    """Tests for task auto-discovery."""

    def test_discover_tasks_does_not_raise(self):
        """Test that discover_tasks runs without error."""
        discover_tasks()

    def test_known_tasks_are_registered(self):
        """Test that built-in tasks are registered after discovery."""
        discover_tasks()
        for task_name in ["example", "system_info", "public_api", "authed_api", "file_processing"]:
            assert get_task(task_name) is not None, f"Task '{task_name}' not found after discovery"


class TestTaskExecution:
    """Tests for task execution behavior."""

    def test_example_task_returns_dict(self):
        from src.tasks.example_task import run
        result = run()
        assert isinstance(result, dict)
        assert result.get("status") == "success"

    def test_system_info_task_returns_system_data(self):
        from src.tasks.system_info_task import run
        result = run()
        assert isinstance(result, dict)
        assert result.get("status") == "success"
        assert "system_info" in result

    def test_public_api_task_returns_status(self):
        from src.tasks.public_api_task import run
        result = run()
        assert isinstance(result, dict)
        # May be "success" or "error" depending on network availability, but must return a dict
        assert "status" in result

    def test_file_processing_task_returns_status(self):
        from src.tasks.file_processing_task import run
        result = run()
        assert isinstance(result, dict)
        assert "status" in result