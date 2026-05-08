"""Tests for converters."""

from unittest.mock import patch
import pytest
from pathlib import Path
from agent_tools_converter.converters.skill_converter import SkillConverter
from agent_tools_converter.converters.agent_converter import AgentConverter
from agent_tools_converter.converters.command_converter import CommandConverter
from agent_tools_converter.converters.factory import create_converter


class TestSkillConverterClaudeToOpencode:
    def test_convert_skill_claude_to_opencode(self, tmp_path):
        source = tmp_path / "test_skill" / "SKILL.md"
        source.parent.mkdir()
        source.write_text("---\nname: my-skill\ndescription: A skill\nwhen_to_use: testing\n---\nBody\n")

        dest = tmp_path / "dest"
        converter = SkillConverter()
        converter._set_direction("claude_to_opencode")
        result = converter.convert_file(str(source), str(dest / "test_skill" / "SKILL.md"))

        assert result["success"] is True
        assert not result["skipped"]
        output = (dest / "test_skill" / "SKILL.md").read_text()
        assert "name: my-skill" in output
        assert "description: A skill" in output
        assert "license: ''" in output
        assert "compatibility: ''" in output
        assert "metadata:" in output
        assert "when_to_use: testing" in output
        assert "Body\n" in output

    def test_convert_skill_opencode_to_claude(self, tmp_path):
        source = tmp_path / "test_skill" / "SKILL.md"
        source.parent.mkdir()
        source.write_text("---\nname: my-skill\ndescription: A skill\nlicense: MIT\nmetadata:\n  when_to_use: testing\n---\nBody\n")

        dest = tmp_path / "dest"
        converter = SkillConverter()
        converter._set_direction("opencode_to_claude")
        result = converter.convert_file(str(source), str(dest / "test_skill" / "SKILL.md"))

        assert result["success"] is True
        output = (dest / "test_skill" / "SKILL.md").read_text()
        assert "name: my-skill" in output
        assert "description: A skill" in output
        assert "when_to_use: testing" in output
        assert "metadata:" not in output

    def test_convert_skill_no_frontmatter(self, tmp_path):
        source = tmp_path / "test_skill" / "SKILL.md"
        source.parent.mkdir()
        source.write_text("No frontmatter\n")

        dest = tmp_path / "dest"
        converter = SkillConverter()
        converter._set_direction("claude_to_opencode")
        result = converter.convert_file(str(source), str(dest / "test_skill" / "SKILL.md"))

        assert result["success"] is False
        assert result["skipped"] is True


class TestAgentConverterClaudeToOpencode:
    @patch("agent_tools_converter.converters.agent_converter.input")
    def test_convert_agent_claude_to_opencode(self, mock_input, tmp_path):
        mock_input.side_effect = ["opus", "5"]
        source = tmp_path / "test-agent.md"
        source.write_text("---\nname: my-agent\ndescription: An agent\nmaxTurns: 10\n---\nPrompt\n")

        dest = tmp_path / "dest"
        converter = AgentConverter()
        converter._set_direction("claude_to_opencode")
        result = converter.convert_file(str(source), str(dest / "test-agent.md"))

        assert result["success"] is True
        output = (dest / "test-agent.md").read_text()
        assert "name: my-agent" in output
        assert "description: An agent" in output
        assert "model: opus" in output
        assert "steps: 5" in output
        assert "Prompt\n" in output

    @patch("agent_tools_converter.converters.agent_converter.input")
    def test_convert_agent_with_tools(self, mock_input, tmp_path):
        mock_input.side_effect = ["sonnet", ""]
        source = tmp_path / "test-agent.md"
        source.write_text("---\nname: my-agent\ndescription: An agent\ntools: read, write\n---\nPrompt\n")

        dest = tmp_path / "dest"
        converter = AgentConverter()
        converter._set_direction("claude_to_opencode")
        result = converter.convert_file(str(source), str(dest / "test-agent.md"))

        assert result["success"] is True
        output = (dest / "test-agent.md").read_text()
        assert "name: my-agent" in output
        assert "model: sonnet" in output
        assert "steps: 1" in output
        assert "permission:" in output
        assert "read: allow" in output
        assert "write: allow" in output

    def test_convert_agent_opencode_to_claude(self, tmp_path):
        source = tmp_path / "test-agent.md"
        source.write_text("---\nname: my-agent\ndescription: An agent\nsteps: 5\npermission:\n  read: allow\n---\nPrompt\n")

        dest = tmp_path / "dest"
        converter = AgentConverter()
        converter._set_direction("opencode_to_claude")
        result = converter.convert_file(str(source), str(dest / "test-agent.md"))

        assert result["success"] is True
        output = (dest / "test-agent.md").read_text()
        assert "maxTurns: 5" in output
        assert "tools: Read" in output

    @patch("agent_tools_converter.converters.agent_converter.input")
    def test_convert_agent_tools_with_spaces(self, mock_input, tmp_path):
        mock_input.side_effect = ["opus", "3"]
        source = tmp_path / "test-agent.md"
        source.write_text("---\nname: spaced-agent\ndescription: A spaced agent\ntools: glob, grep, read\n---\nBody\n")

        dest = tmp_path / "dest"
        converter = AgentConverter()
        converter._set_direction("claude_to_opencode")
        result = converter.convert_file(str(source), str(dest / "test-agent.md"))

        assert result["success"] is True
        output = (dest / "test-agent.md").read_text()
        assert "glob: allow" in output
        assert "grep: allow" in output
        assert "read: allow" in output

    @patch("agent_tools_converter.converters.agent_converter.input")
    def test_convert_agent_disallowed_tools(self, mock_input, tmp_path):
        mock_input.side_effect = ["sonnet", ""]
        source = tmp_path / "test-agent.md"
        source.write_text("---\nname: restricted-agent\ndescription: A restricted agent\ndisallowedTools: bash, edit\n---\nBody\n")

        dest = tmp_path / "dest"
        converter = AgentConverter()
        converter._set_direction("claude_to_opencode")
        result = converter.convert_file(str(source), str(dest / "test-agent.md"))

        assert result["success"] is True
        output = (dest / "test-agent.md").read_text()
        assert "bash: deny" in output
        assert "edit: deny" in output

    def test_convert_agent_opencode_deny_tools(self, tmp_path):
        source = tmp_path / "test-agent.md"
        source.write_text("---\nname: my-agent\ndescription: An agent\nsteps: 3\npermission:\n  bash: deny\n  read: allow\n---\nPrompt\n")

        dest = tmp_path / "dest"
        converter = AgentConverter()
        converter._set_direction("opencode_to_claude")
        result = converter.convert_file(str(source), str(dest / "test-agent.md"))

        assert result["success"] is True
        output = (dest / "test-agent.md").read_text()
        assert "tools: Read" in output
        assert "disallowedTools: Bash" in output


class TestAgentToolsParsing:
    def test_parse_tools_string_simple(self):
        tools = AgentConverter._parse_tools_string("read, write, edit")
        assert tools == ["read", "write", "edit"]

    def test_parse_tools_string_no_spaces(self):
        tools = AgentConverter._parse_tools_string("read,write,edit")
        assert tools == ["read", "write", "edit"]

    def test_parse_tools_string_empty(self):
        tools = AgentConverter._parse_tools_string("")
        assert tools == []

    def test_format_tools_string(self):
        result = AgentConverter._format_tools_string(["read", "write", "edit"])
        assert result == "Read, Write, Edit"

    @patch("agent_tools_converter.converters.agent_converter.input")
    def test_roundtrip_claude_to_opencode_to_claude(self, mock_input, tmp_path):
        mock_input.side_effect = ["opus", "5"]
        original = "---\nname: roundtrip\ndescription: Test agent\ntools: glob, grep, read\nmaxTurns: 10\n---\nBody\n"
        source = tmp_path / "test-agent.md"
        source.write_text(original)

        dest1 = tmp_path / "dest1"
        converter_to = AgentConverter()
        converter_to._set_direction("claude_to_opencode")
        converter_to.convert_file(str(source), str(dest1 / "test-agent.md"))

        opencode_output = (dest1 / "test-agent.md").read_text()
        assert "glob: allow" in opencode_output
        assert "grep: allow" in opencode_output
        assert "read: allow" in opencode_output

        dest2 = tmp_path / "dest2"
        converter_from = AgentConverter()
        converter_from._set_direction("opencode_to_claude")
        converter_from.convert_file(str(dest1 / "test-agent.md"), str(dest2 / "test-agent.md"))

        claude_output = (dest2 / "test-agent.md").read_text()
        assert "tools: Glob, Grep, Read" in claude_output


class TestCommandConverterClaudeToOpencode:
    def test_convert_command_claude_to_opencode(self, tmp_path):
        source = tmp_path / "test-cmd.md"
        source.write_text("---\ndescription: A command\nagent: default\n---\necho hello\n")

        dest = tmp_path / "dest"
        converter = CommandConverter()
        converter._set_direction("claude_to_opencode")
        result = converter.convert_file(str(source), str(dest / "test-cmd.md"))

        assert result["success"] is True
        output = (dest / "test-cmd.md").read_text()
        assert "description: A command" in output
        assert "agent: default" in output
        assert "template:" in output
        assert "echo hello" in output

    def test_convert_command_opencode_to_claude(self, tmp_path):
        source = tmp_path / "test-cmd.md"
        source.write_text("---\ndescription: A command\nagent: default\ntemplate: echo hello\n---\nBody\n")

        dest = tmp_path / "dest"
        converter = CommandConverter()
        converter._set_direction("opencode_to_claude")
        result = converter.convert_file(str(source), str(dest / "test-cmd.md"))

        assert result["success"] is True
        output = (dest / "test-cmd.md").read_text()
        assert "description: A command" in output
        assert "agent: default" in output
        assert "echo hello" in output


class TestConverterFactory:
    def test_create_skill_converter(self):
        converter = create_converter("skill", "claude_to_opencode")
        assert isinstance(converter, SkillConverter)

    def test_create_agent_converter(self):
        converter = create_converter("agent", "claude_to_opencode")
        assert isinstance(converter, AgentConverter)

    def test_create_command_converter(self):
        converter = create_converter("command", "claude_to_opencode")
        assert isinstance(converter, CommandConverter)

    def test_create_invalid_converter(self):
        converter = create_converter("invalid", "claude_to_opencode")
        assert converter is None

    def test_converter_direction_set(self):
        converter = create_converter("skill", "claude_to_opencode")
        assert converter is not None
        assert converter._direction == "claude_to_opencode"

        converter2 = create_converter("skill", "opencode_to_claude")
        assert converter2 is not None
        assert converter2._direction == "opencode_to_claude"


class TestSkillConverterFolder:
    def test_convert_folder(self, tmp_path):
        skill1 = tmp_path / "skill1" / "SKILL.md"
        skill1.parent.mkdir()
        skill1.write_text("---\nname: skill1\n---\nBody1\n")
        skill2 = tmp_path / "skill2" / "SKILL.md"
        skill2.parent.mkdir()
        skill2.write_text("---\nname: skill2\n---\nBody2\n")

        dest = tmp_path / "dest"
        converter = SkillConverter()
        converter._set_direction("claude_to_opencode")
        results = converter.convert_folder(str(tmp_path), str(dest))

        assert len(results) == 2
        assert all(r["success"] for r in results)
        assert (dest / "skill1" / "SKILL.md").exists()
        assert (dest / "skill2" / "SKILL.md").exists()
        assert "name: skill1" in (dest / "skill1" / "SKILL.md").read_text()
        assert "name: skill2" in (dest / "skill2" / "SKILL.md").read_text()


class TestAgentConverterFolder:
    @patch("agent_tools_converter.converters.agent_converter.input")
    def test_convert_folder(self, mock_input, tmp_path):
        mock_input.side_effect = ["opus", "1", "sonnet", "2"]
        agent1 = tmp_path / "agent1.md"
        agent1.write_text("---\nname: agent1\n---\nPrompt1\n")
        agent2 = tmp_path / "agent2.md"
        agent2.write_text("---\nname: agent2\n---\nPrompt2\n")
        (tmp_path / "readme.txt").write_text("Not an agent\n")

        dest = tmp_path / "dest"
        converter = AgentConverter()
        converter._set_direction("claude_to_opencode")
        results = converter.convert_folder(str(tmp_path), str(dest))

        assert len(results) == 2
        assert all(r["success"] for r in results)
        assert (dest / "agent1.md").exists()
        assert (dest / "agent2.md").exists()
        output1 = (dest / "agent1.md").read_text()
        assert "name: agent1" in output1
        assert "model: opus" in output1
        output2 = (dest / "agent2.md").read_text()
        assert "name: agent2" in output2
        assert "model: sonnet" in output2


class TestCommandConverterFolder:
    def test_convert_folder(self, tmp_path):
        cmd1 = tmp_path / "cmd1.md"
        cmd1.write_text("---\ndescription: cmd1\n---\nTemplate1\n")
        cmd2 = tmp_path / "cmd2.md"
        cmd2.write_text("---\ndescription: cmd2\n---\nTemplate2\n")
        (tmp_path / "readme.txt").write_text("Not a command\n")

        dest = tmp_path / "dest"
        converter = CommandConverter()
        converter._set_direction("claude_to_opencode")
        results = converter.convert_folder(str(tmp_path), str(dest))

        assert len(results) == 2
        assert all(r["success"] for r in results)
        assert (dest / "cmd1.md").exists()
        assert (dest / "cmd2.md").exists()
