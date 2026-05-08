## ADDED Requirements

### Requirement: Parse YAML frontmatter from markdown
The system SHALL extract YAML frontmatter from the beginning of a markdown file, delimited by `---` markers.

#### Scenario: Parse valid frontmatter
- **WHEN** a markdown file starts with `---`, contains valid YAML, and ends with `---`
- **THEN** the system returns a dictionary of parsed frontmatter fields and the remaining markdown body

#### Scenario: Handle empty frontmatter
- **WHEN** a markdown file has `---` markers with no content between them
- **THEN** the system returns an empty dictionary for frontmatter and the remaining content as body

#### Scenario: Reject invalid YAML
- **WHEN** a markdown file contains malformed YAML between `---` markers
- **THEN** the system raises a `YAMLError` and reports the parsing failure

### Requirement: Write YAML frontmatter to markdown
The system SHALL serialize a dictionary to YAML frontmatter and prepend it to a markdown body.

#### Scenario: Write frontmatter with simple values
- **WHEN** a dictionary with string and integer values is serialized
- **THEN** the output is valid YAML between `---` markers followed by the markdown body

#### Scenario: Write frontmatter with nested metadata
- **WHEN** a dictionary contains a `metadata` key with nested string values
- **THEN** the output preserves the nested YAML structure correctly

#### Scenario: Write frontmatter preserving body
- **WHEN** a markdown body with special characters (code blocks, backticks) is written
- **THEN** the body content is preserved unchanged after the frontmatter closing `---`

### Requirement: Preserve unmapped fields in metadata
The system SHALL collect frontmatter fields that have no equivalent in the destination format into a `metadata` key.

#### Scenario: Collect unmapped CLAUDE Code fields
- **WHEN** converting a Claude Code skill frontmatter where `when_to_use`, `allowed-tools`, `disable-model-invocation` have no OpenCode equivalents
- **THEN** these fields are collected under `metadata` in the output

#### Scenario: Collect unmapped OpenCode fields
- **WHEN** converting an OpenCode skill frontmatter where `license`, `compatibility`, `metadata` keys have no Claude Code equivalents
- **THEN** these fields are collected under `metadata` in the output

#### Scenario: Preserve metadata on reverse conversion
- **WHEN** a converted file with `metadata` is converted back to the original format
- **THEN** the original unmapped fields are restored from `metadata`

### Requirement: Handle metadata serialization format
The system SHALL serialize metadata values as strings in the YAML output.

#### Scenario: Serialize string metadata values
- **WHEN** metadata contains string key-value pairs
- **THEN** each pair is written as a YAML scalar under the `metadata` key

#### Scenario: Serialize non-string metadata values
- **WHEN** metadata contains non-string values (integers, booleans, lists)
- **THEN** values are serialized as their YAML representation without string conversion
