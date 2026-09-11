"""Tests for the main entry point."""

import sys
from unittest.mock import patch

import pytest

from src.main import parse_args


class TestArgParsing:
    """Tests for command-line argument parsing."""

    def test_parse_task_argument(self):
        test_args = ["program", "--task", "example"]
        with patch.object(sys, "argv", test_args):
            args = parse_args()
            assert args.task == "example"
            assert args.list_tasks is False
            assert args.verbose is False

    def test_parse_list_tasks(self):
        test_args = ["program", "--list-tasks"]
        with patch.object(sys, "argv", test_args):
            args = parse_args()
            assert args.task is None
            assert args.list_tasks is True

    def test_parse_verbose(self):
        test_args = ["program", "--task", "system_info", "--verbose"]
        with patch.object(sys, "argv", test_args):
            args = parse_args()
            assert args.task == "system_info"
            assert args.verbose is True

    def test_no_arguments(self):
        test_args = ["program"]
        with patch.object(sys, "argv", test_args):
            args = parse_args()
            assert args.task is None
            assert args.list_tasks is False