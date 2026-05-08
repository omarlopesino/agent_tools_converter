"""Tests for file_walker utility."""

from pathlib import Path
from agent_tools_converter.utils.file_walker import list_skill_dirs, list_md_files


class TestListSkillDirs:
    def test_list_skill_dirs_returns_paths(self, tmp_path):
        skill_dir = tmp_path / "my_skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("---\nname: my_skill\n---\nBody\n")
        other_dir = tmp_path / "not_a_skill"
        other_dir.mkdir()

        result = list_skill_dirs(str(tmp_path))
        assert len(result) == 1
        assert result[0].name == "my_skill"

    def test_list_skill_dirs_skips_no_skill_md(self, tmp_path):
        skill_dir = tmp_path / "bad_skill"
        skill_dir.mkdir()
        (skill_dir / "README.md").write_text("No SKILL.md here\n")

        result = list_skill_dirs(str(tmp_path))
        assert len(result) == 0

    def test_list_skill_dirs_no_subdirs(self, tmp_path):
        result = list_skill_dirs(str(tmp_path))
        assert result == []

    def test_list_skill_dirs_multiple_skills(self, tmp_path):
        skill1 = tmp_path / "skill1"
        skill1.mkdir()
        (skill1 / "SKILL.md").write_text("---\nname: skill1\n---\n")
        skill2 = tmp_path / "skill2"
        skill2.mkdir()
        (skill2 / "SKILL.md").write_text("---\nname: skill2\n---\n")

        result = list_skill_dirs(str(tmp_path))
        assert len(result) == 2
        names = {r.name for r in result}
        assert names == {"skill1", "skill2"}


class TestListMdFiles:
    def test_list_md_files_returns_files(self, tmp_path):
        (tmp_path / "agent1.md").write_text("---\nname: agent1\n---\n")
        (tmp_path / "agent2.md").write_text("---\nname: agent2\n---\n")
        (tmp_path / "readme.txt").write_text("Not a markdown file\n")

        result = list_md_files(str(tmp_path))
        assert len(result) == 2
        names = {r.stem for r in result}
        assert names == {"agent1", "agent2"}

    def test_list_md_files_no_md_files(self, tmp_path):
        (tmp_path / "readme.txt").write_text("Not a markdown file\n")

        result = list_md_files(str(tmp_path))
        assert result == []

    def test_list_md_files_empty_dir(self, tmp_path):
        result = list_md_files(str(tmp_path))
        assert result == []
