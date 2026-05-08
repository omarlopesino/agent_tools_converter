"""Data models for agent artifacts (skills, agents, commands)."""

from dataclasses import dataclass, field
from pathlib import Path

from agent_tools_converter.utils.frontmatter import parse_frontmatter


@dataclass
class Artifact:
    """Base artifact with frontmatter and body."""
    name: str
    description: str
    frontmatter: dict = field(default_factory=dict)
    body: str = field(default="")

    def to_markdown(self) -> str:
        """Serialize back to markdown with frontmatter."""
        from agent_tools_converter.utils.frontmatter import write_frontmatter
        return write_frontmatter(self.frontmatter, self.body)


@dataclass
class Skill(Artifact):
    """An agent skill artifact."""
    license: str = field(default="")
    compatibility: str = field(default="")


@dataclass
class Agent(Artifact):
    """An agent/subagent artifact."""
    mode: str = field(default="")
    model: str = field(default="")
    temperature: float = field(default=0.0)
    steps: int = field(default=0)
    prompt: str = field(default="")
    permission: dict = field(default_factory=dict)
    hidden: bool = field(default=False)
    top_p: float = field(default=0.0)


@dataclass
class Command(Artifact):
    """A command artifact."""
    agent: str = field(default="")
    model: str = field(default="")
    template: str = field(default="")


def from_file(type_: str, path: str) -> object:
    """Parse a markdown file and return the appropriate model instance.

    Args:
        type_: One of 'skill', 'agent', 'command'.
        path: Path to the markdown file.

    Returns:
        A Skill, Agent, or Command instance.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file has no frontmatter or invalid YAML.
    """
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    text = file_path.read_text(encoding="utf-8")
    frontmatter, body = parse_frontmatter(text)

    name = frontmatter.get("name", file_path.stem)
    description = frontmatter.get("description", "")
    fm = dict(frontmatter)

    if type_ == "skill":
        return Skill(
            name=name,
            description=description,
            frontmatter=fm,
            body=body,
            license=fm.get("license", ""),
            compatibility=fm.get("compatibility", ""),
        )
    elif type_ == "agent":
        return Agent(
            name=name,
            description=description,
            frontmatter=fm,
            body=body,
            mode=fm.get("mode", ""),
            model=fm.get("model", ""),
            temperature=float(fm.get("temperature", 0.0)),
            steps=int(fm.get("steps", fm.get("maxTurns", 0))),
            prompt=body,
            permission=fm.get("permission", {}),
            hidden=bool(fm.get("hidden", False)),
            top_p=float(fm.get("top_p", 0.0)),
        )
    elif type_ == "command":
        return Command(
            name=name,
            description=description,
            frontmatter=fm,
            body=body,
            agent=fm.get("agent", ""),
            model=fm.get("model", ""),
            template=fm.get("template", body),
        )
    else:
        raise ValueError(f"Unknown type: {type_}. Must be one of: skill, agent, command")
