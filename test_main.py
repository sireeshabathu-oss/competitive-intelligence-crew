import os
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from main import validate_environment, parse_args


class TestValidateEnvironment(unittest.TestCase):
    def test_missing_all_keys(self):
        with patch.dict(os.environ, {}, clear=True):
            missing = validate_environment()
        self.assertIn("OPENAI_API_KEY, ANTHROPIC_API_KEY, or GEMINI_API_KEY", missing)
        self.assertIn("SERPER_API_KEY", missing)

    def test_openai_and_serper_present_is_valid(self):
        env = {"OPENAI_API_KEY": "fake-key", "SERPER_API_KEY": "fake-key"}
        with patch.dict(os.environ, env, clear=True):
            missing = validate_environment()
        self.assertEqual(missing, [])

    def test_anthropic_key_also_satisfies_llm_requirement(self):
        env = {"ANTHROPIC_API_KEY": "fake-key", "SERPER_API_KEY": "fake-key"}
        with patch.dict(os.environ, env, clear=True):
            missing = validate_environment()
        self.assertEqual(missing, [])

    def test_gemini_key_also_satisfies_llm_requirement(self):
        env = {"GEMINI_API_KEY": "fake-key", "SERPER_API_KEY": "fake-key"}
        with patch.dict(os.environ, env, clear=True):
            missing = validate_environment()
        self.assertEqual(missing, [])

    def test_missing_only_serper_key(self):
        env = {"OPENAI_API_KEY": "fake-key"}
        with patch.dict(os.environ, env, clear=True):
            missing = validate_environment()
        self.assertEqual(missing, ["SERPER_API_KEY"])


class TestParseArgs(unittest.TestCase):
    def test_default_company_comes_from_env(self):
        with patch.dict(os.environ, {"COMPANY_NAME": "Figma"}, clear=True):
            with patch.object(sys, "argv", ["main.py"]):
                args = parse_args()
        self.assertEqual(args.company, "Figma")

    def test_cli_company_overrides_env(self):
        with patch.dict(os.environ, {"COMPANY_NAME": "Figma"}, clear=True):
            with patch.object(sys, "argv", ["main.py", "Slack"]):
                args = parse_args()
        self.assertEqual(args.company, "Slack")

    def test_default_output_filename(self):
        with patch.object(sys, "argv", ["main.py"]):
            args = parse_args()
        self.assertEqual(args.output, "report.md")

    def test_custom_focus_flag(self):
        with patch.object(sys, "argv", ["main.py", "Slack", "--focus", "pricing only"]):
            args = parse_args()
        self.assertEqual(args.focus, "pricing only")


if __name__ == "__main__":
    unittest.main()
