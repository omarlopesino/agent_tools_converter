"""Factory for creating converter instances."""

from typing import Union

from agent_tools_converter.converters.agent_converter import AgentConverter
from agent_tools_converter.converters.base import BaseConverter
from agent_tools_converter.converters.command_converter import CommandConverter
from agent_tools_converter.converters.skill_converter import SkillConverter

CONVERTER_REGISTRY = {
    "skill": SkillConverter,
    "agent": AgentConverter,
    "command": CommandConverter,
}


def create_converter(
    type_: str,
    direction: str,
) -> Union[SkillConverter, AgentConverter, CommandConverter, None]:
    """Create a converter instance for the given type and direction.

    Args:
        type_: One of 'skill', 'agent', 'command'.
        direction: One of 'claude_to_opencode', 'opencode_to_claude'.

    Returns:
        A converter instance, or None if the type is not supported.
    """
    converter_class = CONVERTER_REGISTRY.get(type_)
    if converter_class is None:
        return None

    converter = converter_class()
    converter._set_direction(direction)
    return converter
