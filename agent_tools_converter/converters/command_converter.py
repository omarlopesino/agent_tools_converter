"""Convert commands between Claude Code and OpenCode formats."""

from pathlib import Path

from agent_tools_converter.converters.base import BaseConverter
from agent_tools_converter.models import Command
from agent_tools_converter.utils.file_walker import list_md_files
from agent_tools_converter.utils.frontmatter import write_frontmatter


class CommandConverter(BaseConverter):
    """Convert commands between Claude Code and OpenCode formats.

    Claude Code fields: description, agent, model
    OpenCode fields: description, agent, model, template

    Mapping (claude -> opencode):
        description -> description
        agent -> agent
        model -> model
        body -> template

    Mapping (opencode -> claude):
        description -> description
        agent -> agent
        model -> model
        template -> merged into body
    """

    source_fields = {"description", "agent", "model"}
    destination_fields = {"description", "agent", "model", "template"}

    def claude_to_opencode(self, command: Command) -> Command:
        """Convert a Claude Code command to OpenCode format."""
        dest_fm = {
            "description": command.frontmatter.get("description", command.description),
            "agent": command.frontmatter.get("agent", ""),
            "model": command.frontmatter.get("model", ""),
            "template": command.body,
        }

        known_cc = {"description", "agent", "model"}
        for key, value in command.frontmatter.items():
            if key not in known_cc:
                dest_fm.setdefault("metadata", {})[key] = value

        return Command(
            name=command.name,
            description=dest_fm["description"],
            frontmatter=dest_fm,
            body=command.body,
            agent=dest_fm["agent"],
            model=dest_fm["model"],
            template=dest_fm["template"],
        )

    def opencode_to_claude(self, command: Command) -> Command:
        """Convert an OpenCode command to Claude Code format."""
        dest_fm = {
            "description": command.frontmatter.get("description", command.description),
            "agent": command.frontmatter.get("agent", ""),
            "model": command.frontmatter.get("model", ""),
        }

        template = command.frontmatter.get("template", "")
        body = command.body
        if template:
            if body:
                body = body.rstrip("\n") + "\n\n" + template
            else:
                body = template

        known_oc = {"description", "agent", "model", "template"}
        for key, value in command.frontmatter.items():
            if key not in known_oc:
                dest_fm.setdefault("metadata", {})[key] = value

        return Command(
            name=command.name,
            description=dest_fm["description"],
            frontmatter=dest_fm,
            body=body,
            agent=command.agent,
            model=command.model,
            template=command.template,
        )

    def convert_file(self, source_path: str, dest_path: str) -> dict:
        """Convert a single command file.

        Args:
            source_path: Path to the source .md file.
            dest_path: Path to write the converted .md file.

        Returns:
            Dict with conversion result info.
        """
        text = Path(source_path).read_text(encoding="utf-8")
        command_name = Path(source_path).stem

        from agent_tools_converter.utils.frontmatter import parse_frontmatter
        try:
            fm, body = parse_frontmatter(text)
        except ValueError:
            return {"success": False, "source": source_path, "dest": dest_path, "skipped": True, "reason": "No valid frontmatter"}

        command = Command(
            name=fm.get("name", command_name),
            description=fm.get("description", ""),
            frontmatter=fm,
            body=body,
            agent=fm.get("agent", ""),
            model=fm.get("model", ""),
            template=fm.get("template", ""),
        )

        if self._direction == "claude_to_opencode":
            command = self.claude_to_opencode(command)
        else:
            command = self.opencode_to_claude(command)

        dest_fm = command.frontmatter
        output = write_frontmatter(dest_fm, command.body)

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
        """Convert all commands in a source directory.

        Args:
            source_dir: Path to the source commands directory.
            dest_dir: Path to write converted commands.

        Returns:
            List of result dicts.
        """
        results = []
        md_files = list_md_files(source_dir)

        for md_file in md_files:
            dest_path = str(Path(dest_dir) / md_file.name)
            result = self.convert_file(str(md_file), dest_path)
            results.append(result)

        return results

    def _set_direction(self, direction: str):
        """Set the conversion direction. Called by factory."""
        self._direction = direction
