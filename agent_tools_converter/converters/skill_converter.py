"""Convert skills between Claude Code and OpenCode formats."""

from pathlib import Path

from agent_tools_converter.converters.base import BaseConverter
from agent_tools_converter.models import Skill
from agent_tools_converter.utils.file_walker import list_skill_dirs
from agent_tools_converter.utils.frontmatter import write_frontmatter


class SkillConverter(BaseConverter):
    """Convert skills between Claude Code and OpenCode formats.

    Claude Code fields: name, description, when_to_use, arguments,
        allowed-tools, context, hooks, shell, disable-model-invocation,
        user-invocable, model, effort, paths, agent
    OpenCode fields: name, description, license, compatibility, metadata

    Mapping (claude -> opencode):
        name -> name
        description -> description
        everything else -> metadata
        license = ""
        compatibility = ""

    Mapping (opencode -> claude):
        name -> name
        description -> description
        metadata expanded to top-level fields
    """

    source_fields = {"name", "description"}
    destination_fields = {"name", "description", "license", "compatibility", "metadata"}

    def claude_to_opencode(self, skill: Skill) -> Skill:
        """Convert a Claude Code skill to OpenCode format."""
        dest_fm = {
            "name": skill.frontmatter.get("name", skill.name),
            "description": skill.frontmatter.get("description", skill.description),
            "license": "",
            "compatibility": "",
        }
        # Collect unmapped Claude Code fields into metadata
        known_cc = {"name", "description"}
        for key, value in skill.frontmatter.items():
            if key not in known_cc:
                dest_fm.setdefault("metadata", {})[key] = value

        return Skill(
            name=dest_fm["name"],
            description=dest_fm["description"],
            frontmatter=dest_fm,
            body=skill.body,
            license="",
            compatibility="",
        )

    def opencode_to_claude(self, skill: Skill) -> Skill:
        """Convert an OpenCode skill to Claude Code format."""
        dest_fm = {
            "name": skill.frontmatter.get("name", skill.name),
            "description": skill.frontmatter.get("description", skill.description),
        }
        # Expand metadata back to top-level fields
        if "metadata" in skill.frontmatter:
            for key, value in skill.frontmatter["metadata"].items():
                dest_fm[key] = value

        # license and compatibility have no CC equivalent, skip them
        return Skill(
            name=dest_fm["name"],
            description=dest_fm["description"],
            frontmatter=dest_fm,
            body=skill.body,
            license=skill.license,
            compatibility=skill.compatibility,
        )

    def convert_file(self, source_path: str, dest_path: str) -> dict:
        """Convert a single skill file.

        Args:
            source_path: Path to the source SKILL.md file.
            dest_path: Path to write the converted SKILL.md file.

        Returns:
            Dict with conversion result info.
        """
        text = Path(source_path).read_text(encoding="utf-8")
        skill = Skill(
            name=self._extract_name(source_path),
            description="",
            frontmatter={},
            body=text,
        )

        # Parse frontmatter from the raw text
        from agent_tools_converter.utils.frontmatter import parse_frontmatter
        try:
            fm, body = parse_frontmatter(text)
        except ValueError:
            return {"success": False, "source": source_path, "dest": dest_path, "skipped": True, "reason": "No valid frontmatter"}

        skill.frontmatter = fm
        skill.body = body

        dest_fm = {}
        if self._direction == "claude_to_opencode":
            skill = self.claude_to_opencode(skill)
        else:
            skill = self.opencode_to_claude(skill)

        dest_fm = skill.frontmatter
        output = write_frontmatter(dest_fm, skill.body)

        dest_p = Path(dest_path)
        dest_p.parent.mkdir(parents=True, exist_ok=True)
        dest_p.write_text(output, encoding="utf-8")

        return {
            "success": True,
            "source": source_path,
            "dest": dest_path,
            "skipped": False,
        }

    def convert_folder(self, source_dir: str, dest_dir: str) -> list:
        """Convert all skills in a source directory.

        Args:
            source_dir: Path to the source skills directory.
            dest_dir: Path to write converted skills.

        Returns:
            List of result dicts.
        """
        results = []
        skill_dirs = list_skill_dirs(source_dir)

        for skill_dir in skill_dirs:
            source_path = str(skill_dir / "SKILL.md")
            dest_path = str(Path(dest_dir) / skill_dir.name / "SKILL.md")
            result = self.convert_file(source_path, dest_path)
            results.append(result)

        return results

    def _extract_name(self, path: str) -> str:
        """Extract skill name from directory structure."""
        p = Path(path)
        # Skill name is the parent directory name
        return p.parent.name

    def _set_direction(self, direction: str):
        """Set the conversion direction. Called by factory."""
        self._direction = direction
