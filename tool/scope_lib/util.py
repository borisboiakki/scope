"""Small helpers shared by all commands. Standard library only (PyYAML is imported lazily)."""
from __future__ import annotations

import hashlib
import re
from datetime import datetime, timezone
from pathlib import Path

ID_RE = re.compile(r"\b(?:BR|FR|NFR|ADR|EP|ST|CR|ASM|OQ)-\d+(?:\.\d+)?\b|\bR\d+\b")
FM_RE = re.compile(r"\A---\r?\n(.*?)\r?\n---[ \t]*(?:\r?\n|\Z)", re.S)
COMMENT_RE = re.compile(r"<!--.*?-->", re.S)
FIELD_RE = re.compile(r"^-\s*\*\*(?P<key>[A-Za-z][A-Za-z ]*):\*\*\s*(?P<value>.*)$")
HEADING_RE = re.compile(r"^(#{1,6})\s")
STATUS_LINE_RE = re.compile(r"^\s*-\s*\*\*Status:\*\*")
CHECKBOX_RE = re.compile(r"^(\s*[-*]\s+)\[[xX ]\]")


class ScopeError(Exception):
    """An error reported to the user without a traceback."""


def yaml_module():
    try:
        import yaml  # noqa: PLC0415
    except ImportError as exc:  # pragma: no cover - depends on the environment
        raise ScopeError("PyYAML is missing: run `python3 .scope/scope.py setup`") from exc
    return yaml


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def today() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def split_front_matter(text: str) -> tuple[str | None, str]:
    m = FM_RE.match(text)
    if not m:
        return None, text
    return m.group(1), text[m.end():]


def parse_front_matter(text: str) -> tuple[dict | None, str]:
    raw, body = split_front_matter(text)
    if raw is None:
        return None, body
    data = yaml_module().safe_load(raw) or {}
    if not isinstance(data, dict):
        raise ValueError("front matter is not a mapping")
    return data, body


def raw_fm_value(text: str, key: str) -> str | None:
    """Value of a front matter key as written (keeps '1.10' as text)."""
    raw, _ = split_front_matter(text)
    if raw is None:
        return None
    m = re.search(rf"^{re.escape(key)}\s*:\s*(.*?)\s*$", raw, re.M)
    if not m:
        return None
    return m.group(1).strip().strip("'\"")


def set_fm_field(text: str, key: str, value: str) -> str:
    m = FM_RE.match(text)
    if not m:
        raise ScopeError("file has no front matter")
    lines = m.group(1).split("\n")
    pat = re.compile(rf"^{re.escape(key)}\s*:")
    for i, line in enumerate(lines):
        if pat.match(line):
            lines[i] = f"{key}: {value}"
            break
    else:
        lines.append(f"{key}: {value}")
    return "---\n" + "\n".join(lines) + "\n---\n" + text[m.end():]


def set_section_field(text: str, heading_id: str, key: str, value: str) -> str:
    """Set the `- **Key:** value` line inside the section whose heading starts with heading_id."""
    lines = text.split("\n")
    level = None
    for i, line in enumerate(lines):
        h = HEADING_RE.match(line)
        if level is None:
            if h and re.match(rf"^#+\s+{re.escape(heading_id)}\b", line):
                level = len(h.group(1))
            continue
        if h and len(h.group(1)) <= level:
            break
        m = FIELD_RE.match(line)
        if m and m.group("key").strip().lower() == key.lower():
            lines[i] = f"- **{m.group('key')}:** {value}"
            return "\n".join(lines)
    raise ScopeError(f"field '{key}' not found under {heading_id}")


def strip_comments(text: str) -> str:
    return COMMENT_RE.sub("", text)


def ids_in(text: str) -> list[str]:
    return ID_RE.findall(strip_comments(text))


def content_hash(text: str) -> str:
    """sha256 of the content, ignoring status values and checkbox ticks (they change during the lifecycle)."""
    raw, body = split_front_matter(text)
    if raw is not None:
        kept = [ln for ln in raw.split("\n") if not re.match(r"^status\s*:", ln)]
        text = "---\n" + "\n".join(kept) + "\n---\n" + body
    lines = [CHECKBOX_RE.sub(r"\1[ ]", ln.rstrip()) for ln in text.replace("\r\n", "\n").split("\n")
             if not STATUS_LINE_RE.match(ln)]
    return hashlib.sha256("\n".join(lines).strip().encode("utf-8")).hexdigest()


def version_tuple(version: str | None) -> tuple[int, int]:
    m = re.fullmatch(r"(\d+)\.(\d+)", str(version or "").strip())
    if not m:
        raise ScopeError(f"invalid version '{version}' (expected major.minor, e.g. 1.2)")
    return int(m.group(1)), int(m.group(2))


def slugify(title: str, limit: int = 40) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return slug[:limit].rstrip("-") or "item"


def id_number(identifier: str) -> int:
    return int(re.search(r"(\d+)(?:\.\d+)?$", identifier).group(1))


def sort_ids(ids):
    def key(i):
        nums = [int(n) for n in re.findall(r"\d+", i)]
        return (re.match(r"[A-Z]+", i).group(0), nums)
    return sorted(set(ids), key=key)
