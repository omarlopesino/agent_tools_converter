"""Tests for data models."""

import pytest
from agent_tools_converter.models import Skill, Agent, Command, from_file


class TestFromSkillFile:
    def test_parse_skill(self, tmp_path):
        skill_md = tmp_path / "test_skill" / "SKILL.md"
        skill_md.parent.mkdir()
        skill_md.write_text("---\nname: my-skill\ndescription: A skill\n---\nBody\n")

        skill = from_file("skill", str(skill_md))
        assert isinstance(skill, Skill)
        assert skill.name == "my-skill"
        assert skill.description == "A skill"
        assert skill.body == "Body\n"
        assert skill.frontmatter["name"] == "my-skill"

    def test_parse_skill_missing_frontmatter(self, tmp_path):
        skill_md = tmp_path / "test_skill" / "SKILL.md"
        skill_md.parent.mkdir()
        skill_md.write_text("No frontmatter\n")

        with pytest.raises(ValueError):
            from_file("skill", str(skill_md))


class TestFromAgentFile:
    def test_parse_agent(self, tmp_path):
        agent_md = tmp_path / "test-agent.md"
        agent_md.write_text("---\nname: my-agent\ndescription: An agent\nmaxTurns: 5\n---\nPrompt\n")

        agent = from_file("agent", str(agent_md))
        assert isinstance(agent, Agent)
        assert agent.name == "my-agent"
        assert agent.description == "An agent"
        assert agent.steps == 5
        assert agent.body == "Prompt\n"

    def test_parse_agent_with_permission(self, tmp_path):
        agent_md = tmp_path / "test-agent.md"
        agent_md.write_text("---\nname: my-agent\ndescription: An agent\npermission:\n  tools:\n    - read\n---\nPrompt\n")

        agent = from_file("agent", str(agent_md))
        assert agent.permission["tools"] == ["read"]


class TestFromCommandFile:
    def test_parse_command(self, tmp_path):
        cmd_md = tmp_path / "test-cmd.md"
        cmd_md.write_text("---\ndescription: A command\nagent: default\n---\nTemplate\n")

        cmd = from_file("command", str(cmd_md))
        assert isinstance(cmd, Command)
        assert cmd.description == "A command"
        assert cmd.agent == "default"
        assert cmd.template == "Template\n"

    def test_parse_command_with_template(self, tmp_path):
        cmd_md = tmp_path / "test-cmd.md"
        cmd_md.write_text("---\ndescription: A command\ntemplate: echo hello\n---\nBody\n")

        cmd = from_file("command", str(cmd_md))
        assert cmd.template == "echo hello"


class TestFromFileInvalidType:
    def test_invalid_type(self, tmp_path):
        md_file = tmp_path / "test.md"
        md_file.write_text("---\nname: test\n---\n")

        with pytest.raises(ValueError, match="Unknown type"):
            from_file("invalid", str(md_file))


class TestFileNotFound:
    def test_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            from_file("skill", "/nonexistent/file.md")


class TestToMarkdown:
    def test_skill_to_markdown(self):
        skill = Skill(name="test", description="A test", frontmatter={"name": "test"}, body="Body\n")
        result = skill.to_markdown()
        assert result.startswith("---\n")
        assert "name: test" in result
