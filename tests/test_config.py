"""Tests for the configuration module."""

import os

import pytest

from src.config import (
    get_env,
    validate_required_vars,
    TaskConfig,
)


class TestGetEnv:
    """Tests for get_env() function."""

    def test_returns_value_when_set(self):
        os.environ["TEST_VAR"] = "hello"
        assert get_env("TEST_VAR") == "hello"

    def test_returns_default_when_not_set(self):
        assert get_env("NONEXISTENT_VAR", default="fallback") == "fallback"

    def test_raises_error_when_required_and_missing(self):
        with pytest.raises(ValueError, match="Required environment variable"):
            get_env("MISSING_REQUIRED_VAR", required=True)

    def test_returns_none_when_not_set_and_no_default(self):
        assert get_env("NONEXISTENT_VAR") is None


class TestValidateRequiredVars:
    """Tests for validate_required_vars() function."""

    def test_passes_when_all_vars_set(self):
        os.environ["TEST_VAR_A"] = "value_a"
        os.environ["TEST_VAR_B"] = "value_b"
        validate_required_vars(["TEST_VAR_A", "TEST_VAR_B"])

    def test_raises_error_when_var_missing(self):
        with pytest.raises(ValueError, match="Missing required"):
            validate_required_vars(["TEST_VAR_A", "MISSING_VAR"])


class TestTaskConfig:
    """Tests for TaskConfig class."""

    def test_is_valid_when_all_required_present(self):
        os.environ["CONFIG_TEST_VAR"] = "value"
        config = TaskConfig("test", required_vars=["CONFIG_TEST_VAR"])
        assert config.is_valid is True

    def test_is_invalid_when_required_missing(self):
        config = TaskConfig("test", required_vars=["MISSING_CONFIG_VAR"])
        assert config.is_valid is False

    def test_get_returns_value(self):
        os.environ["GET_TEST_VAR"] = "test_value"
        config = TaskConfig("test")
        assert config.get("GET_TEST_VAR") == "test_value"

    def test_get_returns_default(self):
        config = TaskConfig("test")
        assert config.get("NONEXISTENT_CONFIG", default="fallback") == "fallback"