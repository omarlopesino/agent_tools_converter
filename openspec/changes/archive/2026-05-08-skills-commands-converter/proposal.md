# agent-tools-converter

## Why

Developers using both Claude Code and OpenCode need to transfer skills, agents, and commands between the two platforms. Each tool uses a similar but incompatible YAML frontmatter schema for these artifacts. A converter eliminates manual rewriting and ensures frontmatter fields are correctly mapped while preserving markdown body content.

## What Changes

- Python CLI application installed via `pip install -e .`
- Converts Claude Code ↔ OpenCode skills, agents, and commands
- CLI signature: `<type> <from> <to> <folder-from> <folder-to>` where type is `skill|agent|command`, from/to is `claude|opencode`
- Only `claude→opencode` and `opencode→claude` directions supported in MVP
- Frontmatter fields unmapped in the destination format preserved under a `metadata` key
- Only top-level files processed, not recursive
- SOLID OOP design with abstract base converter, concrete converters per type, and factory pattern

## Capabilities

### New Capabilities
- `tool-conversion` - Core conversion logic for skills, agents, and commands between Claude Code and OpenCode formats
- `frontmatter-parsing` - Parse and write YAML frontmatter with metadata preservation for unmapped fields
- `cli-interface` - Command-line interface with argparse for type/from/to/folder-from/folder-to arguments

### Modified Capabilities
- (none)

## Impact

- New Python package `agent_tools_converter` with CLI entry point
- Dependencies: `pyyaml` for frontmatter parsing, `argparse` (stdlib) for CLI
- No external APIs or network calls needed
- File discovery limited to top-level of source folder
