"""Tests for CLI module."""

from unittest.mock import patch
import pytest
from argparse import ArgumentTypeError
from agent_tools_converter.cli import build_parser, validate_args, print_summary, run_conversion


class TestBuildParser:
    def test_parser_returns_argument_parser(self):
        parser = build_parser()
        assert parser is not None

    def test_parser_has_all_arguments(self):
        parser = build_parser()
        # Should be able to parse valid arguments
        args = parser.parse_args(["skill", "claude", "opencode", "/src", "/dst"])
        assert args.type == "skill"
        assert args.direction_from == "claude"
        assert args.direction_to == "opencode"
        assert args.folder_from == "/src"
        assert args.folder_to == "/dst"

    def test_parser_rejects_invalid_type(self):
        parser = build_parser()
        with pytest.raises(SystemExit):
            parser.parse_args(["invalid", "claude", "opencode", "/src", "/dst"])

    def test_parser_rejects_invalid_direction(self):
        parser = build_parser()
        with pytest.raises(SystemExit):
            parser.parse_args(["skill", "invalid", "opencode", "/src", "/dst"])


class TestValidateArgs:
    def test_validate_valid_args(self, tmp_path):
        args = type("Args", (), {
            "direction_from": "claude",
            "direction_to": "opencode",
            "folder_from": str(tmp_path),
        })()
        assert validate_args(args) is True

    def test_validate_same_direction(self):
        args = type("Args", (), {
            "direction_from": "claude",
            "direction_to": "claude",
            "folder_from": "/tmp",
        })()
        assert validate_args(args) is False

    def test_validate_missing_source_folder(self):
        args = type("Args", (), {
            "direction_from": "claude",
            "direction_to": "opencode",
            "folder_from": "/nonexistent/path",
        })()
        assert validate_args(args) is False


class TestPrintSummary:
    def test_print_summary_all_converted(self, capsys):
        results = [
            {"success": True, "source": "a.md", "dest": "b.md", "skipped": False},
        ]
        print_summary(results)
        captured = capsys.readouterr()
        assert "1 converted" in captured.out
        assert "0 skipped" in captured.out

    def test_print_summary_with_skipped(self, capsys):
        results = [
            {"success": False, "source": "a.md", "dest": "b.md", "skipped": True, "reason": "No frontmatter"},
            {"success": True, "source": "c.md", "dest": "d.md", "skipped": False},
        ]
        print_summary(results)
        captured = capsys.readouterr()
        assert "2 files processed" in captured.out
        assert "1 converted" in captured.out
        assert "1 skipped" in captured.out
        assert "SKIP:" in captured.out
        assert "No frontmatter" in captured.out


class TestBuildParserWithModelSteps:
    def test_parser_has_model_argument(self):
        parser = build_parser()
        args = parser.parse_args(["agent", "claude", "opencode", "/src", "/dst", "--model", "opus"])
        assert args.model == "opus"
        assert args.steps is None

    def test_parser_has_steps_argument(self):
        parser = build_parser()
        args = parser.parse_args(["agent", "claude", "opencode", "/src", "/dst", "--steps", "5"])
        assert args.model is None
        assert args.steps == 5

    def test_parser_has_both_model_and_steps(self):
        parser = build_parser()
        args = parser.parse_args(["agent", "claude", "opencode", "/src", "/dst", "--model", "sonnet", "--steps", "10"])
        assert args.model == "sonnet"
        assert args.steps == 10


class TestRunConversionWithModelSteps:
    @patch("agent_tools_converter.converters.agent_converter.input")
    def test_conversion_with_model_only_prompts_for_steps(self, mock_input, tmp_path):
        mock_input.side_effect = ["5"]
        agent = tmp_path / "test-agent.md"
        agent.write_text("---\nname: test-agent\ndescription: Test\n---\nBody\n")

        dest = tmp_path / "dest"
        results = run_conversion("agent", "claude_to_opencode", str(tmp_path), str(dest),
                                model="opus", steps=None)

        assert len(results) == 1
        assert results[0]["success"] is True
        output = (dest / "test-agent.md").read_text()
        assert "model: opus" in output
        assert "steps: 5" in output

    @patch("agent_tools_converter.converters.agent_converter.input")
    def test_conversion_with_steps_only_prompts_for_model(self, mock_input, tmp_path):
        mock_input.side_effect = ["sonnet", ""]
        agent = tmp_path / "test-agent.md"
        agent.write_text("---\nname: test-agent\ndescription: Test\n---\nBody\n")

        dest = tmp_path / "dest"
        results = run_conversion("agent", "claude_to_opencode", str(tmp_path), str(dest),
                                model=None, steps=7)

        assert len(results) == 1
        assert results[0]["success"] is True
        output = (dest / "test-agent.md").read_text()
        assert "model: sonnet" in output
        assert "steps: 7" in output

    def test_conversion_with_both_model_and_steps_no_prompts(self, tmp_path):
        agent = tmp_path / "test-agent.md"
        agent.write_text("---\nname: test-agent\ndescription: Test\n---\nBody\n")

        dest = tmp_path / "dest"
        results = run_conversion("agent", "claude_to_opencode", str(tmp_path), str(dest),
                                model="opus", steps=10)

        assert len(results) == 1
        assert results[0]["success"] is True
        output = (dest / "test-agent.md").read_text()
        assert "model: opus" in output
        assert "steps: 10" in output

    @patch("agent_tools_converter.converters.agent_converter.input")
    def test_conversion_without_model_or_steps_prompts_for_both(self, mock_input, tmp_path):
        mock_input.side_effect = ["opus", "5"]
        agent = tmp_path / "test-agent.md"
        agent.write_text("---\nname: test-agent\ndescription: Test\n---\nBody\n")

        dest = tmp_path / "dest"
        results = run_conversion("agent", "claude_to_opencode", str(tmp_path), str(dest),
                                model=None, steps=None)

        assert len(results) == 1
        assert results[0]["success"] is True
        output = (dest / "test-agent.md").read_text()
        assert "model: opus" in output
        assert "steps: 5" in output
