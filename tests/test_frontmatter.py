"""Tests for frontmatter parsing and writing."""

import pytest
from agent_tools_converter.utils.frontmatter import parse_frontmatter, write_frontmatter


class TestParseFrontmatter:
    def test_parse_valid_frontmatter(self):
        text = "---\nname: test\ndescription: A test\n---\nBody content\n"
        fm, body = parse_frontmatter(text)
        assert fm["name"] == "test"
        assert fm["description"] == "A test"
        assert body == "Body content\n"

    def test_parse_frontmatter_with_list(self):
        text = "---\nname: test\ntools:\n  - read\n  - write\n---\nBody\n"
        fm, body = parse_frontmatter(text)
        assert fm["name"] == "test"
        assert fm["tools"] == ["read", "write"]
        assert body == "Body\n"

    def test_parse_no_frontmatter(self):
        text = "No frontmatter here\n"
        with pytest.raises(ValueError, match="No frontmatter block found"):
            parse_frontmatter(text)

    def test_parse_no_closing_dashes(self):
        text = "---\nname: test\nBody\n"
        with pytest.raises(ValueError, match="No closing"):
            parse_frontmatter(text)

    def test_parse_invalid_yaml(self):
        text = "---\nname: [invalid\n---\nBody\n"
        with pytest.raises(ValueError, match="Invalid YAML"):
            parse_frontmatter(text)

    def test_parse_empty_frontmatter(self):
        text = "---\n---\nBody\n"
        fm, body = parse_frontmatter(text)
        assert fm == {}
        assert body == "Body\n"

    def test_parse_nested_dict(self):
        text = "---\npermission:\n  tools:\n    - read\n  disallowedTools:\n    - write\n---\nBody\n"
        fm, body = parse_frontmatter(text)
        assert fm["permission"]["tools"] == ["read"]
        assert fm["permission"]["disallowedTools"] == ["write"]


class TestWriteFrontmatter:
    def test_write_simple(self):
        fm = {"name": "test", "description": "A test"}
        result = write_frontmatter(fm, "Body content\n")
        assert result.startswith("---\n")
        assert "name: test" in result
        assert "description: A test" in result
        assert "---\nBody content\n" in result

    def test_write_with_list(self):
        fm = {"name": "test", "tools": ["read", "write"]}
        result = write_frontmatter(fm, "")
        assert "tools:" in result
        assert "- read" in result
        assert "- write" in result

    def test_write_empty_body(self):
        fm = {"name": "test"}
        result = write_frontmatter(fm, "")
        assert result.startswith("---\n")
        assert "name: test" in result
        assert result.endswith("\n")

    def test_roundtrip(self):
        original_fm = {"name": "test", "description": "A test", "metadata": {"key": "value"}}
        body = "Body content\n"
        written = write_frontmatter(original_fm, body)
        parsed_fm, parsed_body = parse_frontmatter(written)
        assert parsed_fm["name"] == "test"
        assert parsed_fm["description"] == "A test"
        assert parsed_fm["metadata"]["key"] == "value"
        assert parsed_body == body
