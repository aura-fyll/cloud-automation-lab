"""Tests for the logging module."""

import logging

from src.logger import (
    setup_logger,
    get_logger,
    sanitize_message,
    safe_log,
)


class TestSetupLogger:
    """Tests for setup_logger()."""

    def test_creates_logger_with_correct_name(self):
        logger = setup_logger("test_logger")
        assert logger.name == "test_logger"

    def test_sets_correct_level(self):
        logger = setup_logger("test_level", level=logging.DEBUG)
        assert logger.level == logging.DEBUG

    def test_does_not_add_duplicate_handlers(self):
        logger = setup_logger("test_no_duplicate")
        initial_count = len(logger.handlers)
        logger = setup_logger("test_no_duplicate")
        assert len(logger.handlers) == initial_count


class TestGetLogger:
    """Tests for get_logger()."""

    def test_returns_logger_by_name(self):
        logger = get_logger("named_logger")
        assert logger.name == "named_logger"

    def test_returns_default_logger(self):
        logger = get_logger()
        assert logger.name == "automation"


class TestSanitizeMessage:
    """Tests for sanitize_message()."""

    def test_passes_safe_messages(self):
        msg = "System information collected successfully"
        assert sanitize_message(msg) == msg

    def test_redacts_password(self):
        msg = "Password is: mysecretpassword"
        result = sanitize_message(msg)
        assert "mysecretpassword" not in result
        assert "LOG REDACTED" in result

    def test_redacts_token(self):
        msg = "Token: ghp_abc123def456"
        result = sanitize_message(msg)
        assert "ghp_abc123def456" not in result
        assert "LOG REDACTED" in result

    def test_redacts_api_key(self):
        msg = "API key is sk-12345678"
        result = sanitize_message(msg)
        assert "sk-12345678" not in result
        assert "LOG REDACTED" in result

    def test_redacts_authorization_header(self):
        msg = "Authorization: Bearer token123"
        result = sanitize_message(msg)
        assert "token123" not in result
        assert "LOG REDACTED" in result

    def test_case_insensitive_redaction(self):
        msg = "API_KEY=secret_value"
        result = sanitize_message(msg)
        assert "secret_value" not in result
        assert "LOG REDACTED" in result


class TestSafeLog:
    """Tests for safe_log()."""

    def test_logs_safe_message(self):
        logger = setup_logger("test_safe_log")
        logger.info("Task completed successfully")

    def test_redacts_sensitive_message(self):
        logger = setup_logger("test_redact_log")

        # Create a custom handler that captures output for testing
        import io
        stream = io.StringIO()
        handler = logging.StreamHandler(stream)
        handler.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(handler)

        safe_log(logger, logging.INFO, "The token is abc123")
        output = stream.getvalue()
        assert "abc123" not in output
        assert "LOG REDACTED" in output

        logger.removeHandler(handler)