## ADDED Requirements

### Requirement: Accept CLI arguments
The system SHALL accept five positional arguments: `type`, `from`, `to`, `folder-from`, `folder-to`.

#### Scenario: Run with all arguments
- **WHEN** the user runs `python -m agent_tools_converter skill claude opencode /src /dst`
- **THEN** the system parses `type=skill`, `from=claude`, `to=opencode`, `folder_from=/src`, `folder_to=/dst`

#### Scenario: Run with agent type
- **WHEN** the user runs `python -m agent_tools_converter agent opencode claude /src/agents /dst/agents`
- **THEN** the system parses `type=agent`, `from=opencode`, `to=claude`, `folder_from=/src/agents`, `folder_to=/dst/agents`

#### Scenario: Run with command type
- **WHEN** the user runs `python -m agent_tools_converter command claude opencode /src/commands /dst/commands`
- **THEN** the system parses `type=command`, `from=claude`, `to=opencode`, `folder_from=/src/commands`, `folder_to=/dst/commands`

### Requirement: Validate type argument
The system SHALL validate that `type` is one of `skill`, `agent`, or `command`.

#### Scenario: Accept valid type
- **WHEN** the user provides `skill`, `agent`, or `command` as the type argument
- **THEN** the system accepts the argument and proceeds

#### Scenario: Reject invalid type
- **WHEN** the user provides `plugin` or any other value as the type argument
- **THEN** the system exits with code 1 and prints an error message: "Invalid type. Must be one of: skill, agent, command"

### Requirement: Validate direction arguments
The system SHALL validate that `from` and `to` are one of `claude` or `opencode`.

#### Scenario: Accept valid direction
- **WHEN** the user provides `claude` and `opencode` as from/to values
- **THEN** the system accepts the arguments and proceeds

#### Scenario: Reject invalid direction
- **WHEN** the user provides `cursor` or any other value as a direction argument
- **THEN** the system exits with code 1 and prints an error message listing valid values

### Requirement: Validate direction pair
The system SHALL validate that the direction pair is either `claude→opencode` or `opencode→claude`.

#### Scenario: Accept valid direction pair
- **WHEN** the user provides `claude→opencode` or `opencode→claude`
- **THEN** the system accepts the direction pair and proceeds

#### Scenario: Reject same-direction pair
- **WHEN** the user provides `claude→claude` or `opencode→opencode`
- **THEN** the system exits with code 1 and prints an error message indicating bidirectional conversion is required

### Requirement: Validate source folder
The system SHALL validate that the source folder exists and is accessible.

#### Scenario: Accept valid source folder
- **WHEN** the source folder exists and is readable
- **THEN** the system proceeds with conversion

#### Scenario: Reject missing source folder
- **WHEN** the source folder does not exist
- **THEN** the system exits with code 1 and prints an error message: "Source folder not found: <path>"

### Requirement: Dispatch to correct converter
The system SHALL select the appropriate converter based on the `type` argument.

#### Scenario: Dispatch skill conversion
- **WHEN** the type is `skill`
- **THEN** the system instantiates and uses the `SkillConverter`

#### Scenario: Dispatch agent conversion
- **WHEN** the type is `agent`
- **THEN** the system instantiates and uses the `AgentConverter`

#### Scenario: Dispatch command conversion
- **WHEN** the type is `command`
- **THEN** the system instantiates and uses the `CommandConverter`

### Requirement: Report conversion summary
The system SHALL print a summary of converted files to stdout after processing.

#### Scenario: Report successful conversion
- **WHEN** files are successfully converted
- **THEN** the system prints a summary showing the number of files converted and their paths

#### Scenario: Report skipped files
- **WHEN** some files are skipped due to missing frontmatter
- **THEN** the system prints warnings for skipped files and includes them in the summary
