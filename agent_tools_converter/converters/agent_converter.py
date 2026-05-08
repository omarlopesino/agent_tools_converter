"""Convert agents between Claude Code and OpenCode formats."""

import sys
from pathlib import Path
from typing import Optional

from agent_tools_converter.converters.base import BaseConverter
from agent_tools_converter.models import Agent
from agent_tools_converter.utils.file_walker import list_md_files
from agent_tools_converter.utils.frontmatter import write_frontmatter


def _prompt_agent_fields(agent_name: str, description: str, model: str, max_turns: str,
                         provided_model: Optional[str] = None, provided_steps: Optional[int] = None) -> dict:
    """Prompt user for model and steps when converting agent to OpenCode.

    Args:
        agent_name: Name of the agent.
        description: Description of the agent.
        model: Current model value (may be empty).
        max_turns: Current maxTurns value (may be empty).
        provided_model: Model value provided via CLI (may be None).
        provided_steps: Steps value provided via CLI (may be None).

    Returns:
        Dict with 'model' and 'steps' keys.
    """
    needs_model_prompt = provided_model is None
    needs_steps_prompt = provided_steps is None

    print(f"\n  Agent: {agent_name}", file=sys.stderr)
    if description:
        print(f"  Description: {description}", file=sys.stderr)

    if needs_model_prompt:
        print(f"  Model: {model if model else '(empty)'}", file=sys.stderr)
        model_input = input("  Enter model (required, e.g. opus, sonnet): ").strip()
        while not model_input:
            print("  Model is required. Please enter a value.", file=sys.stderr)
            model_input = input("  Enter model: ").strip()
    else:
        model_input = provided_model

    if needs_steps_prompt:
        print(f"  Steps (maxTurns): {max_turns if max_turns else '(empty, default 1)'}", file=sys.stderr)
        steps_input = input("  Enter steps (press Enter for 1): ").strip()
        if steps_input:
            try:
                steps = int(steps_input)
            except ValueError:
                print("  Invalid number, using default 1", file=sys.stderr)
                steps = 1
        else:
            steps = 1
    else:
        try:
            steps = int(provided_steps)
        except (ValueError, TypeError):
            print("  Invalid number, using default 1", file=sys.stderr)
            steps = 1

    return {"model": model_input, "steps": steps}


class AgentConverter(BaseConverter):
    """Convert agents between Claude Code and OpenCode formats.

    Claude Code fields: name, description, tools, disallowedTools, model,
        permissionMode, maxTurns, skills, mcpServers, memory, hooks,
        background, effort, isolation, color, initialPrompt
    OpenCode fields: name, description, mode, model, temperature, steps,
        prompt, permission, hidden, top_p

    Mapping (claude -> opencode):
        name -> name
        description -> description
        model -> model
        maxTurns -> steps
        tools (comma-separated) -> permission {tool: allow}
        disallowedTools (comma-separated) -> permission {tool: deny}
        everything else -> metadata

    Mapping (opencode -> claude):
        name -> name
        description -> description
        model -> model
        steps -> maxTurns
        permission {tool: allow} -> tools (comma-separated)
        permission {tool: deny} -> disallowedTools (comma-separated)
        everything else -> metadata
    """

    source_fields = {"name", "description", "model"}
    destination_fields = {"name", "description", "mode", "model", "temperature",
                          "steps", "prompt", "permission", "hidden", "top_p"}

    def __init__(self):
        self._direction = ""
        self._model = None
        self._steps = None

    @staticmethod
    def _parse_tools_string(tools_value) -> list:
        """Parse comma-separated tools string into a list of lowercase tool names."""
        if isinstance(tools_value, str):
            return [t.strip().lower() for t in tools_value.split(",") if t.strip()]
        return []

    @staticmethod
    def _format_tools_string(tools_list: list) -> str:
        """Format a list of tool names into a comma-separated string."""
        return ", ".join(t.capitalize() for t in tools_list)

    def claude_to_opencode(self, agent: Agent) -> Agent:
        """Convert a Claude Code agent to OpenCode format."""
        dest_fm = {
            "name": agent.frontmatter.get("name", agent.name),
            "description": agent.frontmatter.get("description", agent.description),
            "model": agent.frontmatter.get("model", ""),
            "steps": int(agent.frontmatter.get("maxTurns", 0)),
            "permission": {},
        }

        tools = agent.frontmatter.get("tools", [])
        if isinstance(tools, str):
            tools = self._parse_tools_string(tools)
        if tools:
            for tool in tools:
                dest_fm["permission"][tool] = "allow"

        disallowed_tools = agent.frontmatter.get("disallowedTools", [])
        if isinstance(disallowed_tools, str):
            disallowed_tools = self._parse_tools_string(disallowed_tools)
        if disallowed_tools:
            for tool in disallowed_tools:
                dest_fm["permission"][tool] = "deny"

        known_cc = {"name", "description", "model", "maxTurns", "tools", "disallowedTools"}
        for key, value in agent.frontmatter.items():
            if key not in known_cc:
                dest_fm.setdefault("metadata", {})[key] = value

        return Agent(
            name=dest_fm["name"],
            description=dest_fm["description"],
            frontmatter=dest_fm,
            body=agent.body,
            mode="",
            temperature=0.0,
            steps=int(dest_fm["steps"]),
            prompt=agent.body,
            permission=dest_fm["permission"],
            hidden=False,
            top_p=0.0,
        )

    def opencode_to_claude(self, agent: Agent) -> Agent:
        """Convert an OpenCode agent to Claude Code format."""
        dest_fm = {
            "name": agent.frontmatter.get("name", agent.name),
            "description": agent.frontmatter.get("description", agent.description),
            "model": agent.frontmatter.get("model", ""),
            "maxTurns": int(agent.frontmatter.get("steps", 0)),
        }

        permission = agent.frontmatter.get("permission", {})
        if isinstance(permission, dict):
            allow_tools = [k for k, v in permission.items() if v == "allow"]
            deny_tools = [k for k, v in permission.items() if v == "deny"]
            if allow_tools:
                dest_fm["tools"] = self._format_tools_string(allow_tools)
            if deny_tools:
                dest_fm["disallowedTools"] = self._format_tools_string(deny_tools)

        known_oc = {"name", "description", "model", "steps", "permission"}
        for key, value in agent.frontmatter.items():
            if key not in known_oc:
                dest_fm.setdefault("metadata", {})[key] = value

        return Agent(
            name=dest_fm["name"],
            description=dest_fm["description"],
            frontmatter=dest_fm,
            body=agent.body,
            mode=agent.mode,
            temperature=agent.temperature,
            steps=int(agent.frontmatter.get("steps", 0)),
            prompt=agent.prompt,
            permission=agent.permission,
            hidden=agent.hidden,
            top_p=agent.top_p,
        )

    def convert_file(self, source_path: str, dest_path: str) -> dict:
        """Convert a single agent file.

        Args:
            source_path: Path to the source .md file.
            dest_path: Path to write the converted .md file.

        Returns:
            Dict with conversion result info.
        """
        text = Path(source_path).read_text(encoding="utf-8")
        agent_name = Path(source_path).stem

        from agent_tools_converter.utils.frontmatter import parse_frontmatter
        try:
            fm, body = parse_frontmatter(text)
        except ValueError:
            return {"success": False, "source": source_path, "dest": dest_path, "skipped": True, "reason": "No valid frontmatter"}

        agent = Agent(
            name=fm.get("name", agent_name),
            description=fm.get("description", ""),
            frontmatter=fm,
            body=body,
            mode=fm.get("mode", ""),
            model=fm.get("model", ""),
            temperature=float(fm.get("temperature", 0.0)),
            steps=int(fm.get("steps", 0)),
            prompt=body,
            permission=fm.get("permission", {}),
            hidden=bool(fm.get("hidden", False)),
            top_p=float(fm.get("top_p", 0.0)),
        )

        dest_fm = {}
        if self._direction == "claude_to_opencode":
            prompt_result = _prompt_agent_fields(
                agent.name,
                agent.description,
                agent.frontmatter.get("model", ""),
                agent.frontmatter.get("maxTurns", ""),
                self._model,
                self._steps,
            )
            agent = self.claude_to_opencode(agent)
            agent.frontmatter["model"] = prompt_result["model"]
            agent.frontmatter["steps"] = prompt_result["steps"]
        else:
            agent = self.opencode_to_claude(agent)

        dest_fm = agent.frontmatter
        output = write_frontmatter(dest_fm, agent.body)

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
        """Convert all agents in a source directory.

        Args:
            source_dir: Path to the source agents directory.
            dest_dir: Path to write converted agents.

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

    def _set_model(self, model: Optional[str]):
        """Set the model value. Called by CLI."""
        self._model = model

    def _set_steps(self, steps: Optional[int]):
        """Set the steps value. Called by CLI."""
        self._steps = steps
