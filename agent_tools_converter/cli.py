"""CLI entry point for agent-tools-converter."""

import argparse
import sys
from pathlib import Path
from typing import Optional, cast

from agent_tools_converter.converters.factory import create_converter
from agent_tools_converter.converters.agent_converter import AgentConverter


VALID_TYPES = ("skill", "agent", "command")
VALID_DIRECTIONS = ("claude", "opencode")


def build_parser() -> argparse.ArgumentParser:
    """Build and return the argument parser."""
    parser = argparse.ArgumentParser(
        prog="agent-tools-converter",
        description="Convert skills, agents, and commands between Claude Code and OpenCode formats.",
    )
    parser.add_argument(
        "type",
        choices=VALID_TYPES,
        help="Artifact type: skill, agent, or command",
    )
    parser.add_argument(
        "direction_from",
        choices=VALID_DIRECTIONS,
        help="Source format: claude or opencode",
    )
    parser.add_argument(
        "direction_to",
        choices=VALID_DIRECTIONS,
        help="Destination format: claude or opencode",
    )
    parser.add_argument(
        "folder_from",
        help="Source folder path",
    )
    parser.add_argument(
        "folder_to",
        help="Destination folder path",
    )
    parser.add_argument(
        "--model",
        help="Model to use for all agents (only valid with type=agent)",
    )
    parser.add_argument(
        "--steps",
        type=int,
        help="Steps to use for all agents (only valid with type=agent)",
    )
    return parser


def validate_args(args: argparse.Namespace) -> bool:
    """Validate parsed arguments. Returns True if valid."""
    if args.direction_from == args.direction_to:
        print(f"Error: Source and destination formats must be different "
              f"(got {args.direction_from}→{args.direction_to})", file=sys.stderr)
        return False

    source_dir = Path(args.folder_from)
    if not source_dir.exists():
        print(f"Error: Source folder not found: {args.folder_from}", file=sys.stderr)
        return False

    return True


def run_conversion(type_: str, direction: str, folder_from: str, folder_to: str,
                   model: Optional[str] = None, steps: Optional[int] = None) -> list:
    """Run the conversion and return results."""
    converter = create_converter(type_, direction)
    if converter is None:
        print(f"Error: Unsupported type: {type_}", file=sys.stderr)
        return []

    if isinstance(converter, AgentConverter) and (model is not None or steps is not None):
        agent_converter = cast(AgentConverter, converter)
        agent_converter._set_model(model)
        agent_converter._set_steps(steps)

    return converter.convert_folder(folder_from, folder_to)


def print_summary(results: list) -> None:
    """Print a summary of the conversion results."""
    total = len(results)
    converted = sum(1 for r in results if not r.get("skipped", False))
    skipped = sum(1 for r in results if r.get("skipped", False))

    print(f"\nConversion complete: {total} files processed, "
          f"{converted} converted, {skipped} skipped")

    for result in results:
        if result.get("skipped"):
            print(f"  SKIP: {result['source']} ({result.get('reason', 'unknown')})")
        else:
            print(f"  OK: {result['source']} -> {result['dest']}")


def main() -> None:
    """Main entry point."""
    parser = build_parser()
    args = parser.parse_args()

    if not validate_args(args):
        sys.exit(1)

    direction_map = {
        ("claude", "opencode"): "claude_to_opencode",
        ("opencode", "claude"): "opencode_to_claude",
    }
    direction = direction_map.get((args.direction_from, args.direction_to))

    if direction is None:
        print(f"Error: Unsupported direction {args.direction_from}→{args.direction_to}", file=sys.stderr)
        sys.exit(1)

    results = run_conversion(args.type, direction, args.folder_from, args.folder_to,
                             args.model, args.steps)
    print_summary(results)


if __name__ == "__main__":
    main()
