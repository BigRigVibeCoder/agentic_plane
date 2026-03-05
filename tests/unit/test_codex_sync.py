import pytest
from pathlib import Path
from codex_to_plane_sync import parse_markdown_file

@pytest.fixture
def sample_markdown_file(tmp_path):
    content = """---
id: TEST-001
title: "The Agentic Architecture"
author: architect
---

# Introduction
This is a test document.
"""
    file_path = tmp_path / "test_doc.md"
    file_path.write_text(content, encoding="utf-8")
    return file_path

@pytest.fixture
def markdown_file_no_frontmatter(tmp_path):
    content = """# Just a title
No frontmatter here.
"""
    file_path = tmp_path / "no_frontmatter.md"
    file_path.write_text(content, encoding="utf-8")
    return file_path

@pytest.mark.unit
def test_parse_markdown_with_frontmatter(sample_markdown_file):
    title, content = parse_markdown_file(sample_markdown_file)
    assert title == "The Agentic Architecture"
    assert "# Introduction" in content
    assert "---" not in content

@pytest.mark.unit
def test_parse_markdown_no_frontmatter(markdown_file_no_frontmatter):
    title, content = parse_markdown_file(markdown_file_no_frontmatter)
    assert title == "no_frontmatter"
    assert "# Just a title" in content
