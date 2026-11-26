"""Authoring rules of docs/authoring.md, checked on every skill and template."""
import re
from pathlib import Path

import pytest
import yaml

from conftest import scope

REPO = Path(__file__).resolve().parent.parent
SKILLS = sorted((REPO / "skills").glob("*/SKILL.md"))
FORBIDDEN = ["$ARGUMENTS", "AskUserQuestion", "TodoWrite", "Task tool", "subagent_type", "opencode/autoinvoke",
             "mcp__"]
COMMANDS = set(scope.build_parser()._subparsers._group_actions[0].choices)


def front_matter(path):
    text = path.read_text(encoding="utf-8")
    m = re.match(r"---\n(.*?)\n---\n", text, re.S)
    assert m, f"{path}: no front matter"
    return yaml.safe_load(m.group(1)), text


def test_skills_exist():
    names = {p.parent.name for p in SKILLS}
    assert {"scope", "scope-spec", "scope-arch", "scope-plan"} <= names


@pytest.mark.parametrize("path", SKILLS, ids=lambda p: p.parent.name)
def test_skill_rules(path):
    fm, text = front_matter(path)
    assert set(fm) == {"name", "description"}, "only name and description are portable"
    assert fm["name"] == path.parent.name
    assert re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", fm["name"]) and len(fm["name"]) <= 64
    assert 1 <= len(fm["description"]) <= 1024
    assert re.search(r"\bUse (when|at|for)\b", fm["description"]), "description must say when to use it"
    assert len(text.splitlines()) <= 150
    for token in FORBIDDEN:
        assert token not in text, f"tool-specific syntax: {token}"
    for ref in re.findall(r"`(references/[\w.-]+)`", text):
        assert (path.parent / ref).exists(), f"missing {ref}"
    for cmd in re.findall(r"scope\.py ([a-z-]+)", text):
        assert cmd in COMMANDS, f"unknown scope.py command: {cmd}"


@pytest.mark.parametrize("path", sorted((REPO / "skills").glob("*/references/*")) +
                         sorted((REPO / "tool" / "templates").glob("*")), ids=lambda p: p.name)
def test_template_size(path):
    assert len(path.read_text(encoding="utf-8").splitlines()) <= 60
