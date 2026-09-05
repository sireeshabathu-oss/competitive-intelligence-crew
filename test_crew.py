"""
Tests for crew.py.

These tests mock out `crewai` and `crewai_tools` entirely, so they run fast
and don't require installing the real (heavy) crewai package or making any
network/API calls — they test our own logic (validation, error handling),
not CrewAI's internals.
"""

import os
import sys
import types
import unittest
from unittest.mock import MagicMock, patch


def _install_crewai_mocks():
    crewai_mock = types.ModuleType("crewai")
    crewai_mock.Agent = MagicMock(side_effect=lambda **kwargs: MagicMock(**kwargs))
    crewai_mock.Task = MagicMock(side_effect=lambda **kwargs: MagicMock(**kwargs))
    crewai_mock.Crew = MagicMock(side_effect=lambda **kwargs: MagicMock(**kwargs))
    crewai_mock.Process = MagicMock()
    crewai_mock.Process.sequential = "sequential"

    crewai_tools_mock = types.ModuleType("crewai_tools")
    crewai_tools_mock.SerperDevTool = MagicMock(return_value=MagicMock())

    sys.modules["crewai"] = crewai_mock
    sys.modules["crewai_tools"] = crewai_tools_mock
    return crewai_mock, crewai_tools_mock


_crewai_mock, _crewai_tools_mock = _install_crewai_mocks()

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import importlib
import crew as crew_module

importlib.reload(crew_module)


class TestBuildCrew(unittest.TestCase):
    def setUp(self):
        # Reset the mock's side effect before each test
        _crewai_tools_mock.SerperDevTool.side_effect = None
        _crewai_tools_mock.SerperDevTool.return_value = MagicMock()

    def test_build_crew_succeeds_with_required_keys(self):
        with patch.dict(os.environ, {"SERPER_API_KEY": "fake-key"}, clear=True):
            result = crew_module.build_crew("Notion", "pricing, AI features")
        self.assertIsNotNone(result)

    def test_build_crew_raises_without_serper_key(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(RuntimeError):
                crew_module.build_crew("Notion", "pricing")

    def test_build_crew_wraps_tool_init_failure(self):
        _crewai_tools_mock.SerperDevTool.side_effect = Exception("boom")
        with patch.dict(os.environ, {"SERPER_API_KEY": "fake-key"}, clear=True):
            with self.assertRaises(RuntimeError):
                crew_module.build_crew("Notion", "pricing")

    def test_build_crew_rejects_empty_company_name(self):
        with patch.dict(os.environ, {"SERPER_API_KEY": "fake-key"}, clear=True):
            with self.assertRaises(ValueError):
                crew_module.build_crew("", "pricing")

    def test_build_crew_rejects_whitespace_only_company_name(self):
        with patch.dict(os.environ, {"SERPER_API_KEY": "fake-key"}, clear=True):
            with self.assertRaises(ValueError):
                crew_module.build_crew("   ", "pricing")


if __name__ == "__main__":
    unittest.main()
