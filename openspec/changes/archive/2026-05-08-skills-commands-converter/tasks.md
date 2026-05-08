## 1. Project Setup

- [x] 1.1 Create pyproject.toml with package metadata, dependencies (pyyaml), and console script entry point
- [x] 1.2 Create package directory structure: agent_tools_converter/__init__.py, converters/, utils/
- [x] 1.3 Create tests/ directory with __init__.py and conftest.py

## 2. Frontmatter Parsing Utilities

- [x] 2.1 Implement `utils/frontmatter.py` with `parse_frontmatter(text)` that extracts YAML between `---` markers and returns (dict, body_string)
- [x] 2.2 Implement `write_frontmatter(frontmatter_dict, body)` that serializes YAML and prepends `---` markers followed by body
- [x] 2.3 Implement `utils/file_walker.py` with `list_skill_dirs(path)`, `list_md_files(path)` that return top-level entries only (no recursion)
- [x] 2.4 Ensure `yaml.safe_load()` is used exclusively; no `yaml.load()` with unsafe loader

## 3. Data Models

- [x] 3.1 Create `models.py` with `Artifact` dataclass containing `name`, `description`, `frontmatter` (dict), `body` (str)
- [x] 3.2 Create `Skill` dataclass extending `Artifact` with `license` and `compatibility` fields
- [x] 3.3 Create `Agent` dataclass extending `Artifact` with `mode`, `model`, `temperature`, `steps`, `prompt`, `permission`, `hidden`, `top_p` fields
- [x] 3.4 Create `Command` dataclass extending `Artifact` with `agent`, `model`, `template` fields
- [x] 3.5 Add factory functions `from_file(type, path)` that parse a markdown file and return the appropriate model instance

## 4. Base Converter Abstraction

- [x] 4.1 Create `converters/base.py` with abstract `BaseConverter` class defining `convert_file(source_path, dest_path)` and `convert_folder(source_dir, dest_dir)`
- [x] 4.2 Define direction mapping attributes in base: `source_fields` (set of fields to map) and `destination_fields` (set of fields to map)
- [x] 4.3 Implement shared helper `_extract_mapped(source_fm, source_fields, dest_fm)` that copies known fields and collects unknowns into `metadata`
- [x] 4.4 Implement shared helper `_restore_metadata(source_fm, metadata_key)` that expands `metadata` back to top-level fields

## 5. Skill Converter

- [x] 5.1 Create `converters/skill_converter.py` with `SkillConverter(BaseConverter)`
- [x] 5.2 Implement `claude_to_opencode()` mapping: `name`→`name`, `description`→`description`, unmapped→`metadata`
- [x] 5.3 Implement `opencode_to_claude()` mapping: `name`→`name`, `description`→`description`, `metadata` expanded back, unmapped→`metadata`
- [x] 5.4 Ensure `license` and `compatibility` are set to empty strings in OpenCode output
- [x] 5.5 Implement `convert_file()` that reads source, maps frontmatter, writes destination preserving body

## 6. Agent Converter

- [x] 6.1 Create `converters/agent_converter.py` with `AgentConverter(BaseConverter)`
- [x] 6.2 Implement `claude_to_opencode()` mapping: `name`→`description`, `description`→`description`, `tools`/`disallowedTools`→`permission`, `maxTurns`→`steps`, `model`→`model`, unmapped→`metadata`
- [x] 6.3 Implement `opencode_to_claude()` mapping: `description`→`name`+`description`, `steps`→`maxTurns`, `permission`→`tools`/`disallowedTools`, `model`→`model`, unmapped→`metadata`
- [x] 6.4 Map `permissionMode` to OpenCode `permission` rules
- [x] 6.5 Implement `convert_file()` that reads source, maps frontmatter, writes destination preserving body

## 7. Command Converter

- [x] 7.1 Create `converters/command_converter.py` with `CommandConverter(BaseConverter)`
- [x] 7.2 Implement `claude_to_opencode()` mapping: `description`→`description`, `agent`→`agent`, `model`→`model`, body→`template` in frontmatter
- [x] 7.3 Implement `opencode_to_claude()` mapping: `description`→`description`, `agent`→`agent`, `model`→`model`, `template`→body
- [x] 7.4 Handle the special case where OpenCode `template` becomes CC body and CC body becomes OC `template`
- [x] 7.5 Implement `convert_file()` that reads source, maps frontmatter, writes destination

## 8. Converter Factory

- [x] 8.1 Create `converters/factory.py` with `create_converter(type, direction)` function
- [x] 8.2 Register skill, agent, and command converters in factory
- [x] 8.3 Return None for unsupported type
- [x] 8.4 Direction is validated by CLI before factory call

## 9. CLI Entry Point

- [x] 9.1 Create `cli.py` with argparse defining 5 positional arguments: type, from, to, folder-from, folder-to
- [x] 9.2 Validate type is one of: skill, agent, command
- [x] 9.3 Validate from/to is one of: claude, opencode
- [x] 9.4 Validate direction pair is bidirectional (not same source and destination)
- [x] 9.5 Validate source folder exists, raise error if not
- [x] 9.6 Auto-create destination directories with `Path.mkdir(parents=True, exist_ok=True)`
- [x] 9.7 Dispatch to factory to get the correct converter, then call `convert_folder()`
- [x] 9.8 Print conversion summary to stdout: number of files converted and skipped
- [x] 9.9 Log warnings to stderr for files skipped due to missing frontmatter
- [x] 9.10 Add `__main__.py` to enable `python -m agent_tools_converter` invocation
- [x] 9.11 Configure console script entry point in `pyproject.toml`

## 10. Tests

- [x] 10.1 Write tests for `frontmatter.py`: valid parse, empty frontmatter, invalid YAML handling
- [x] 10.2 Write tests for `file_walker.py`: top-level listing, no recursion, skip non-target files
- [x] 10.3 Write tests for `SkillConverter`: claude→opencode mapping, opencode→claude mapping, body preservation
- [x] 10.4 Write tests for `AgentConverter`: claude→opencode mapping, opencode→claude mapping, body preservation
- [x] 10.5 Write tests for `CommandConverter`: claude→opencode mapping (body→template), opencode→claude mapping (template→body)
- [x] 10.6 Write tests for `ConverterFactory`: correct dispatch, unsupported type error, unsupported direction error
- [x] 10.7 Write tests for CLI argument validation: valid args, invalid type, invalid direction, missing source folder
- [x] 10.8 Write integration test: full end-to-end conversion of a sample skill file

## 11. Package Distribution

- [x] 11.1 Add `README.md` with installation and usage instructions
- [x] 11.2 Verify `pip install -e .` works from project root
- [x] 11.3 Verify `python -m agent_tools_converter --help` shows argument help
- [x] 11.4 Run a manual conversion test with sample Claude Code skill files
