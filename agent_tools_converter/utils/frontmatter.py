"""Parse and write YAML frontmatter in markdown files.

Uses yaml.safe_load() exclusively for security.
"""

import re
import yaml
from typing import Tuple


def parse_frontmatter(text: str) -> Tuple[dict, str]:
    """Extract YAML frontmatter from a markdown string.

    Frontmatter is delimited by `---` markers at the start of the file.
    Everything after the closing `---` is the body.

    Args:
        text: The full markdown file content.

    Returns:
        A tuple of (frontmatter_dict, body_string).

    Raises:
        ValueError: If no frontmatter block is found or YAML is invalid.
    """
    if not text.startswith("---"):
        raise ValueError("No frontmatter block found: file must start with '---'")

    remaining = text[3:]

    close_match = re.match(r"^(.*?)\n---\s*(.*)$", remaining, re.DOTALL)

    if not close_match:
        raise ValueError("No closing '---' found for frontmatter block")

    yaml_content = close_match.group(1)
    body = close_match.group(2)

    try:
        frontmatter = yaml.safe_load(yaml_content)
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML in frontmatter: {e}")

    if frontmatter is None:
        frontmatter = {}

    return frontmatter, body


def write_frontmatter(frontmatter: dict, body: str) -> str:
    """Serialize a dictionary to YAML frontmatter and prepend it to the body.

    Args:
        frontmatter: Dictionary of frontmatter fields.
        body: The markdown body content.

    Returns:
        The complete markdown string with frontmatter prepended.
    """
    yaml_content = yaml.dump(
        frontmatter,
        default_flow_style=False,
        allow_unicode=True,
        sort_keys=False,
    )
    result = f"---\n{yaml_content}---\n{body}"
    return result
