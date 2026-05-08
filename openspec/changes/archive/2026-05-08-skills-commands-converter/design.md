# Design: agent-tools-converter

## Context

Developers using both Claude Code and OpenCode need to transfer skills, agents, and commands between the two platforms. Both tools use YAML frontmatter in markdown files to define these artifacts, but their frontmatter schemas differ significantly:

- **Claude Code skills** (`.claude/skills/<name>/SKILL.md`): frontmatter fields include `name`, `description`, `when_to_use`, `arguments`, `allowed-tools`, `context`, `hooks`, `shell`, `disable-model-invocation`, `user-invocable`, `model`, `effort`, `paths`, `agent`.
- **OpenCode skills** (`.opencode/skills/<name>/SKILL.md`): frontmatter fields include `name`, `description`, `license`, `compatibility`, `metadata` (string-to-string map).
- **Claude Code agents** (`.claude/agents/<name>.md`): frontmatter fields include `tools`, `disallowedTools`, `model`, `permissionMode`, `maxTurns`, `skills`, `mcpServers`, `memory`, `hooks`, `background`, `effort`, `isolation`, `color`, `initialPrompt`.
- **OpenCode agents** (`.opencode/agents/<name>.md`): frontmatter fields include `description`, `mode`, `model`, `temperature`, `steps`, `prompt`, `tools` (deprecated), `permission`, `hidden`, `top_p`, `additional`.
- **Claude Code commands** (`.claude/commands/<name>.md`): frontmatter fields include `description`, `agent`, `model`.
- **OpenCode commands** (`.opencode/commands/<name>.md`): frontmatter fields include `description`, `agent`, `model`, `template`.

The markdown body content remains unchanged during conversion.

## Goals / Non-Goals

**Goals:**
- Convert skills, agents, and commands between Claude Code and OpenCode formats
- Map frontmatter fields to their closest equivalents in the target format
- Preserve unmapped frontmatter fields under a `metadata` key in the destination
- Preserve markdown body content unchanged
- Process only top-level files (not recursive)
- Provide a CLI with argparse: `<type> <from> <to> <folder-from> <folder-to>`
- Support only `claude→opencode` and `opencode→claude` directions in MVP
- Installable via `pip install -e .`

**Non-Goals:**
- Recursive file discovery (only top-level)
- Conversion to/from other agent platforms (Cursor, Copilot, etc.)
- Bidirectional conversion validation or diff reporting
- Merging existing destination files
- Network calls or API integrations

## Decisions

### D1: Use abstract base class with concrete converters (Strategy pattern)

**Decision:** Define a `BaseConverter` abstract class with `convert_file()` and `convert_folder()` methods. Each converter type (skill, agent, command) implements its own direction mappings.

**Rationale:** Each artifact type has different frontmatter fields and conversion logic. An abstract base ensures a uniform interface while allowing type-specific behavior. New artifact types can be added without modifying existing converters (OCP).

**Alternatives considered:**
- Dictionary-based field mapping: Simpler but harder to extend, mixes all logic in one place.
- Function-based approach: Loses the ability to share common frontmatter parsing logic between converters.

### D2: Frontmatter parsing via PyYAML

**Decision:** Use `pyyaml` for parsing and writing YAML frontmatter.

**Rationale:** PyYAML is the de facto standard for YAML in Python, handles complex nested structures, and is lightweight. Markdown body is everything after the closing `---` delimiter.

**Alternatives considered:**
- `toml` + manual YAML: Adds unnecessary dependency.
- Regex-based parsing: Fragile, doesn't handle YAML edge cases (multiline strings, anchors).

### D3: Unmapped fields preserved in `metadata`

**Decision:** Any frontmatter field present in the source format that has no equivalent in the destination format is collected into a `metadata` key in the output.

**Rationale:** Preserves information losslessly. The consumer can inspect metadata for fields that weren't mapped. Direction matters — a field unmapped in `claude→opencode` may have an equivalent in `opencode→claude`.

**Alternatives considered:**
- Warn and drop unmapped fields: Information loss.
- Append unmapped fields as sibling keys: Inconsistent output format, harder to parse.

### D4: Factory pattern for converter selection

**Decision:** A `ConverterFactory` class maps `(type, from, to)` tuples to the appropriate converter instance.

**Rationale:** Decouples CLI from concrete converter classes (DIP). The CLI asks the factory for the right converter without knowing about individual implementations.

**Alternatives considered:**
- Conditional branching in CLI: Harder to extend, violates DIP.
- Registry pattern: More complex than needed for 3 converter types.

### D5: argparse (stdlib) for CLI

**Decision:** Use Python's built-in `argparse` instead of `click` or `typer`.

**Rationale:** No external dependency for CLI parsing. The only external dependency is `pyyaml`. Keeps the package minimal.

**Alternatives considered:**
- `click`: More ergonomic but adds a dependency.
- `sys.argv` manual parsing: Fragile, no help/usage generation.

### D6: Output directory structure mirrors input

**Decision:** The output folder structure mirrors the input structure. For skills, the converter processes each subdirectory under `folder-from` as a skill and writes to the corresponding subdirectory under `folder-to`. Same for agents and commands.

**Rationale:** Preserves the organizational structure of the source tools. A skill at `folder-from/my-skill/SKILL.md` becomes `folder-to/my-skill/SKILL.md`.

## Risks / Trade-offs

| Risk | Mitigation |
|------|-----------|
| PyYAML security: `yaml.load()` with `UnsafeLoader` | Use `yaml.safe_load()` exclusively; never use `yaml.load()` with default loader |
| Frontmatter parsing edge cases (YAML with special chars) | Use `yaml.safe_load()` and catch `yaml.YAMLError`; fall back to metadata preservation |
| Unmapped field loss | All unmapped fields preserved in `metadata` key — lossless round-trip of source data |
| Direction not supported | CLI validates `from` and `to` are in `{claude, opencode}` and raises error for unsupported pairs |
| Destination directory doesn't exist | Auto-create destination directories with `os.makedirs(exist_ok=True)` |

## Open Questions

1. Should unsupported direction pairs produce a clear error message, or silently do nothing? → Clear error message with available options.
2. Should the converter handle `.md` files with no frontmatter (skip or error)? → Skip with a warning to stderr.
3. For OpenCode commands, the `template` field in frontmatter maps to body content in CC. Should we swap body↔frontmatter for commands? → Yes, for command conversion: CC body → OC `template` in frontmatter, and OC frontmatter body → CC body.
