## ADDED Requirements

### Requirement: Convert skill from Claude Code to OpenCode
The system SHALL convert a Claude Code skill (`.claude/skills/<name>/SKILL.md`) to OpenCode format (`.opencode/skills/<name>/SKILL.md`), mapping frontmatter fields and preserving the markdown body.

#### Scenario: Convert skill with standard fields
- **WHEN** the user runs `python -m agent_tools_converter skill claude opencode /path/to/claude/skills /path/to/opencode/skills`
- **THEN** each subdirectory in the source folder is read as a skill, its `SKILL.md` is converted, and written to the corresponding destination subdirectory

#### Scenario: Map CLAUDE Code skill frontmatter to OpenCode
- **WHEN** converting a Claude Code skill with `name`, `description`, `when_to_use`, `allowed-tools`, `disable-model-invocation`, `context`, `hooks`
- **THEN** the output OpenCode skill frontmatter contains `name`, `description`, `license` (empty), `compatibility` (empty), and `metadata` with unmapped fields (`when_to_use`, `allowed-tools`, `disable-model-invocation`, `context`, `hooks`)
- **AND** the markdown body is preserved unchanged

#### Scenario: Preserve markdown body unchanged
- **WHEN** converting a Claude Code skill
- **THEN** the markdown content after the frontmatter closing `---` is written verbatim to the destination `SKILL.md`

### Requirement: Convert skill from OpenCode to Claude Code
The system SHALL convert an OpenCode skill (`.opencode/skills/<name>/SKILL.md`) to Claude Code format (`.claude/skills/<name>/SKILL.md`), mapping frontmatter fields and preserving the markdown body.

#### Scenario: Convert skill with standard fields
- **WHEN** the user runs `python -m agent_tools_converter skill opencode claude /path/to/opencode/skills /path/to/claude/skills`
- **THEN** each subdirectory in the source folder is read as a skill, its `SKILL.md` is converted, and written to the corresponding destination subdirectory

#### Scenario: Map OpenCode frontmatter to Claude Code
- **WHEN** converting an OpenCode skill with `name`, `description`, `license`, `compatibility`, `metadata`
- **THEN** the output Claude Code skill frontmatter contains `name`, `description`, and `metadata` fields are expanded to top-level fields where possible (`when_to_use` from `metadata`, `allowed-tools` from `metadata`)
- **AND** unmapped metadata fields are preserved in the `metadata` block

#### Scenario: Preserve markdown body unchanged
- **WHEN** converting an OpenCode skill
- **THEN** the markdown content after the frontmatter closing `---` is written verbatim to the destination `SKILL.md`

### Requirement: Convert agent from Claude Code to OpenCode
The system SHALL convert a Claude Code agent (`.claude/agents/<name>.md`) to OpenCode format (`.opencode/agents/<name>.md`), mapping frontmatter fields and preserving the system prompt body.

#### Scenario: Convert agent with standard fields
- **WHEN** the user runs `python -m agent_tools_converter agent claude opencode /path/to/claude/agents /path/to/opencode/agents`
- **THEN** each `.md` file in the source folder is read as an agent, its frontmatter is converted, and written to the corresponding destination path

#### Scenario: Map CLAUDE Code agent frontmatter to OpenCode
- **WHEN** converting a Claude Code agent with `name`, `description`, `tools`, `disallowedTools`, `model`, `permissionMode`, `maxTurns`, `skills`, `mcpServers`, `memory`, `hooks`, `background`, `effort`, `isolation`, `color`, `initialPrompt`
- **THEN** the output OpenCode agent frontmatter maps `tools`/`disallowedTools` to `permission`, `maxTurns` to `steps`, `model` to `model`, and preserves unmapped fields (`hooks`, `background`, `effort`, `isolation`, `color`, `initialPrompt`, `mcpServers`) in `metadata`
- **AND** the markdown body (system prompt) is preserved unchanged

#### Scenario: Preserve system prompt body unchanged
- **WHEN** converting a Claude Code agent
- **THEN** the markdown content after the frontmatter closing `---` is written verbatim to the destination `.md` file

### Requirement: Convert agent from OpenCode to Claude Code
The system SHALL convert an OpenCode agent (`.opencode/agents/<name>.md`) to Claude Code format (`.claude/agents/<name>.md`), mapping frontmatter fields and preserving the system prompt body.

#### Scenario: Convert agent with standard fields
- **WHEN** the user runs `python -m agent_tools_converter agent opencode claude /path/to/opencode/agents /path/to/claude/agents`
- **THEN** each `.md` file in the source folder is read as an agent, its frontmatter is converted, and written to the corresponding destination path

#### Scenario: Map OpenCode frontmatter to Claude Code
- **WHEN** converting an OpenCode agent with `description`, `mode`, `model`, `temperature`, `steps`, `prompt`, `permission`, `hidden`, `top_p`
- **THEN** the output Claude Code agent frontmatter maps `description` to `name`+`description`, `steps` to `maxTurns`, `permission` to `tools`/`disallowedTools`, and preserves unmapped fields (`temperature`, `hidden`, `top_p`) in `metadata`

#### Scenario: Preserve system prompt body unchanged
- **WHEN** converting an OpenCode agent
- **THEN** the markdown content after the frontmatter closing `---` is written verbatim to the destination `.md` file

### Requirement: Convert command from Claude Code to OpenCode
The system SHALL convert a Claude Code command (`.claude/commands/<name>.md`) to OpenCode format (`.opencode/commands/<name>.md`), mapping frontmatter fields and preserving the command template body.

#### Scenario: Convert command with standard fields
- **WHEN** the user runs `python -m agent_tools_converter command claude opencode /path/to/claude/commands /path/to/opencode/commands`
- **THEN** each `.md` file in the source folder is read as a command, its frontmatter is converted, and written to the corresponding destination path

#### Scenario: Map CLAUDE Code command frontmatter to OpenCode
- **WHEN** converting a Claude Code command with `description`, `agent`, `model`
- **THEN** the output OpenCode command frontmatter contains `description`, `agent`, `model`, and the markdown body is written as the `template` field in OpenCode frontmatter

#### Scenario: Preserve command template body unchanged
- **WHEN** converting a Claude Code command
- **THEN** the markdown content after the frontmatter closing `---` is written verbatim to the destination `.md` file as the template

### Requirement: Convert command from OpenCode to Claude Code
The system SHALL convert an OpenCode command (`.opencode/commands/<name>.md`) to Claude Code format (`.claude/commands/<name>.md`), mapping frontmatter fields and preserving the command template body.

#### Scenario: Convert command with standard fields
- **WHEN** the user runs `python -m agent_tools_converter command opencode claude /path/to/opencode/commands /path/to/claude/commands`
- **THEN** each `.md` file in the source folder is read as a command, its frontmatter is converted, and written to the corresponding destination path

#### Scenario: Map OpenCode frontmatter to Claude Code
- **WHEN** converting an OpenCode command with `description`, `agent`, `model`, `template`
- **THEN** the output Claude Code command frontmatter contains `description`, `agent`, `model`, and the `template` content is merged into the markdown body

#### Scenario: Preserve command template body unchanged
- **WHEN** converting an OpenCode command
- **THEN** the markdown content after the frontmatter closing `---` is written verbatim to the destination `.md` file

### Requirement: Validate input arguments
The system SHALL validate that the user provides valid type, from, to, and folder arguments.

#### Scenario: Reject unsupported type
- **WHEN** the user provides a type other than `skill`, `agent`, or `command`
- **THEN** the system exits with a non-zero code and an error message listing the valid types

#### Scenario: Reject unsupported direction
- **WHEN** the user provides a `from` or `to` value other than `claude` or `opencode`
- **THEN** the system exits with a non-zero code and an error message listing the valid values

#### Scenario: Reject unsupported direction pair
- **WHEN** the user provides a direction pair that is not `claude→opencode` or `opencode→claude` (e.g., `claude→claude`)
- **THEN** the system exits with a non-zero code and an error message indicating the direction is not supported

#### Scenario: Reject missing source folder
- **WHEN** the source folder does not exist
- **THEN** the system exits with a non-zero code and an error message indicating the folder was not found

### Requirement: Handle files without frontmatter
The system SHALL gracefully handle markdown files that lack YAML frontmatter.

#### Scenario: Skip file with no frontmatter
- **WHEN** a source `.md` file has no `---` delimited frontmatter block
- **THEN** the system skips the file and logs a warning to stderr

#### Scenario: Skip file with invalid YAML frontmatter
- **WHEN** a source `.md` file has a malformed YAML frontmatter block
- **THEN** the system skips the file and logs an error to stderr

### Requirement: Auto-create destination directories
The system SHALL create destination directories if they do not exist.

#### Scenario: Create nested destination directories
- **WHEN** the destination folder path does not exist
- **THEN** the system creates all necessary parent directories automatically

### Requirement: Process only top-level files
The system SHALL process only files at the top level of the source folder, not recursively.

#### Scenario: Process top-level skill directories only
- **WHEN** the source folder contains subdirectories (for skills) or `.md` files (for agents/commands)
- **THEN** only the immediate children are processed, not nested subdirectories

#### Scenario: Skip non-target files
- **WHEN** the source folder contains files that are not `SKILL.md` (for skills) or not `.md` files (for agents/commands)
- **THEN** those files are skipped
