# agent-tools-converter

Convert Claude Code and OpenCode skills, agents, and commands between formats.

## What it does

Transfers skills, agents, and commands between [Claude Code](https://docs.anthropic.com/en/docs/claude-code/overview) and [OpenCode](https://github.com/anthropics/skills-converter) by mapping YAML frontmatter fields to their closest equivalents. Markdown body content is preserved unchanged.

### Supported artifact types

| Type | Claude Code location | OpenCode location |
|---|---|---|
| Skills | `.claude/skills/<name>/SKILL.md` | `.opencode/skills/<name>/SKILL.md` |
| Agents | `.claude/agents/<name>.md` | `.opencode/agents/<name>.md` |
| Commands | `.claude/commands/<name>.md` | `.opencode/commands/<name>.md` |

### Supported directions

- `claude → opencode`
- `opencode → claude`

No other directions are supported.

## Installation

### Prerequisites

- Python 3.9+
- [pip](https://pip.pypa.io/)

### Install from source

```bash
git clone <repo-url>
cd skills-converter
pip install -e .
```

### Install from PyPI (when published)

```bash
pip install agent-tools-converter
```

The only runtime dependency is `pyyaml`. The CLI uses Python's built-in `argparse`.

## Usage

### CLI signature

```bash
python -m agent_tools_converter <type> <from> <to> <folder-from> <folder-to>
```

Or with the console script entry point:

```bash
agent-tools-converter <type> <from> <to> <folder-from> <folder-to>
```

### Arguments

| Argument | Values | Description |
|---|---|---|
| `type` | `skill`, `agent`, `command` | Artifact type to convert |
| `from` | `claude`, `opencode` | Source format |
| `to` | `claude`, `opencode` | Destination format |
| `folder-from` | path | Source folder path |
| `folder-to` | path | Destination folder path |

### Optional arguments (agents only)

| Argument | Values | Description |
|---|---|---|
| `--model` | string | Model to apply to all agents (e.g. `opus`, `sonnet`) |
| `--steps` | integer | Steps to apply to all agents |

### Examples

Convert all skills from Claude Code to OpenCode:

```bash
python -m agent_tools_converter skill claude opencode \
  ~/.claude/skills ~/.opencode/skills
```

Convert all agents from OpenCode to Claude Code, applying `opus` as the model and `5` as steps to every agent (no interactive prompts):

```bash
python -m agent_tools_converter agent opencode claude \
  ~/.opencode/agents ~/.claude/agents --model opus --steps 5
```

Convert a single agent from Claude Code to OpenCode with interactive prompts for model and steps:

```bash
python -m agent_tools_converter agent claude opencode \
  ~/.claude/agents ~/.opencode/agents
```

Convert commands from OpenCode to Claude Code:

```bash
python -m agent_tools_converter command opencode claude \
  ~/.opencode/commands ~/.claude/commands
```

### Agent conversion prompts

When converting agents from Claude Code to OpenCode, the converter needs `model` and `steps` values that have no direct equivalent in Claude Code agents.

| Scenario | Behavior |
|---|---|
| `--model` and `--steps` both provided | No prompts. All agents get the same model and steps. |
| Only `--model` provided | Prompts for steps for each agent. |
| Only `--steps` provided | Prompts for model for each agent. |
| Neither provided | Prompts for both model and steps for each agent. |

Model input is required (empty input is rejected). Steps defaults to `1` if left empty.

## Field mappings

### Skills

| Claude Code | OpenCode |
|---|---|
| `name` | `name` |
| `description` | `description` |
| (all other fields) | `metadata` (preserved) |
| — | `license` (empty string) |
| — | `compatibility` (empty string) |

Unmapped Claude Code fields are collected under `metadata`. When converting back, `metadata` fields are expanded to top-level keys.

### Agents

| Claude Code | OpenCode |
|---|---|
| `name` | `name` |
| `description` | `description` |
| `model` | `model` |
| `maxTurns` | `steps` |
| `tools` (comma-separated) | `permission.{tool}: allow` |
| `disallowedTools` (comma-separated) | `permission.{tool}: deny` |
| (all other fields) | `metadata` (preserved) |

Claude Code `tools` are comma-separated strings like `"Glob, Grep, Read"`. These are converted to an OpenCode `permission` object:

```yaml
permission:
  glob: allow
  grep: allow
  read: allow
```

The reverse conversion reconstructs the comma-separated string.

### Commands

| Claude Code | OpenCode |
|---|---|
| `description` | `description` |
| `agent` | `agent` |
| `model` | `model` |
| body content | `template` |

When converting back, the OpenCode `template` field is merged into the Claude Code body.

## Output structure

The output directory mirrors the input directory structure:

- Skills: `folder-from/my-skill/SKILL.md` → `folder-to/my-skill/SKILL.md`
- Agents: `folder-from/my-agent.md` → `folder-to/my-agent.md`
- Commands: `folder-from/my-cmd.md` → `folder-to/my-cmd.md`

## Conversion summary

After conversion, the CLI prints a summary:

```
Conversion complete: 6 files processed, 6 converted, 0 skipped
  OK: /path/to/agent1.md -> /dest/agent1.md
  OK: /path/to/agent2.md -> /dest/agent2.md
  SKIP: /path/to/bad.md (No valid frontmatter)
```

## Limitations

- **Only two directions**: `claude → opencode` and `opencode → claude`. Conversions to/from other platforms (Cursor, Copilot, etc.) are not supported.
- **Skills**: The `license` and `compatibility` fields are always set to empty strings when converting to OpenCode. There is no automatic way to derive these from Claude Code skills.
- **Agents**: When converting from Claude Code to OpenCode, `model` and `steps` must be provided (via CLI or interactive prompts). Claude Code agents do not have an equivalent `steps` field.
- **Commands**: The body content of Claude Code commands is moved to the OpenCode `template` field. The reverse merges `template` into the body.
- **No merge**: Destination files are overwritten. Existing destination files are not merged with source content.
- **No validation**: The converter does not validate that the destination format's required fields are semantically meaningful — it only ensures the YAML is well-formed.
- **Body content preserved**: The markdown body after the frontmatter is never modified. If a field mapping loses semantic meaning (e.g., `effort` → `metadata`), the information is preserved but not interpreted.

## Future steps

- [ ] Support conversions to/from other platforms (Cursor, Copilot, etc.)
- [ ] Diff reporting: show what changed between source and destination
- [ ] Merge strategy: option to merge destination content with source content
- [ ] Dry-run mode: preview changes without writing files
- [ ] Batch agent conversion without prompts: support `--default-model` and `--default-steps` as global defaults
- [ ] CI integration: test against real Claude Code and OpenCode agent files
- [ ] Documentation: generate field mapping reference from converter source code

## Architecture

The project uses SOLID OOP principles:

- **BaseConverter**: Abstract base class defining `convert_file()` and `convert_folder()` interfaces.
- **Concrete converters**: `SkillConverter`, `AgentConverter`, `CommandConverter` implement type-specific mapping logic.
- **ConverterFactory**: Maps `(type, from, to)` tuples to the correct converter instance.
- **Frontmatter utilities**: `parse_frontmatter()` and `write_frontmatter()` use `yaml.safe_load()` exclusively for security.
- **File walker**: `list_skill_dirs()` and `list_md_files()` discover files at the top level only.

## Development

### Run tests

```bash
pip install -e ".[dev]"
pytest
```

### Add a new converter

1. Create a new class inheriting from `BaseConverter` in `agent_tools_converter/converters/`.
2. Implement `claude_to_opencode()` and `opencode_to_claude()` methods.
3. Register the converter in `ConverterFactory._registry`.

## Build breakdown

- **80% OpenSpec**: Structured specification-driven development with proposal, design docs, formal specs, and task breakdown
- **20% Vibecoding**: Implementation of converter logic, CLI, and tests based on intuition and domain knowledge

