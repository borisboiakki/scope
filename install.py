#!/usr/bin/env python3
"""Install, upgrade or remove SCOPE in a project (Claude Code and opencode). Standard library only.

    python3 install.py <project>                     install or upgrade
    python3 install.py <project> --opencode-format v2  opencode 2.x native agent format (default: v1, read by 1.x and 2.x)
    python3 install.py <project> --no-opencode       Claude Code only (or --no-claude)
    python3 install.py <project> --setup             also create .scope/.venv and install PyYAML
    python3 install.py <project> --uninstall         remove skills, agents and .scope/ (keeps docs/scope/)

What it writes in the project:
    .claude/skills/scope*/          the six skills (read by Claude Code and by opencode)
    .claude/agents/scope-reviewer.md
    .opencode/agents/scope-reviewer.md
    .scope/                         scope.py, scope_lib/, templates/, requirements.txt, VERSION, .gitignore
It never touches docs/scope/, AGENTS.md or CLAUDE.md: `scope.py init` (skill `scope`) creates those.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parent
TOOL_FILES = ("scope.py", "scope_lib", "templates", "requirements.txt")
CLAUDE_TOOLS = "Read, Grep, Glob, Bash"


def read_agent_source() -> tuple[dict, str]:
    text = (SRC / "agents" / "scope-reviewer.md").read_text(encoding="utf-8")
    _, fm, body = text.split("---\n", 2)
    meta = {}
    for line in fm.strip().splitlines():
        key, _, value = line.partition(":")
        meta[key.strip()] = value.strip()
    return meta, body.lstrip("\n")


def render_claude(meta: dict, body: str) -> str:
    return (f"---\nname: {meta['name']}\ndescription: {json.dumps(meta['description'])}\n"
            f"tools: {CLAUDE_TOOLS}\n---\n\n{body}")


def render_opencode(meta: dict, body: str, fmt: str) -> str:
    desc = json.dumps(meta["description"])
    if fmt == "v2":
        perms = ("permissions:\n"
                 "  - { action: edit, resource: \"*\", effect: deny }\n"
                 "  - { action: subagent, resource: \"*\", effect: deny }\n"
                 "  - { action: webfetch, resource: \"*\", effect: deny }\n"
                 "  - { action: websearch, resource: \"*\", effect: deny }\n")
    else:
        perms = "permission:\n  edit: deny\n  task: deny\n  webfetch: deny\n  websearch: deny\n"
    return f"---\ndescription: {desc}\nmode: subagent\n{perms}---\n\n{body}"


def write(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def install(target: Path, claude: bool, opencode: bool, fmt: str) -> list[str]:
    out = []
    version = (SRC / "VERSION").read_text().strip()
    old = target / ".scope" / "VERSION"
    if old.exists():
        out.append(f"upgrading SCOPE {old.read_text().strip()} -> {version}")
    else:
        out.append(f"installing SCOPE {version}")
    # skills: replace only SCOPE's own folders
    skills_dir = target / ".claude" / "skills"
    for src in sorted((SRC / "skills").iterdir()):
        if (src / "SKILL.md").exists():
            dst = skills_dir / src.name
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst, ignore=shutil.ignore_patterns("__pycache__"))
    out.append(f"skills -> {skills_dir.relative_to(target)}/ "
               f"({', '.join(p.name for p in sorted(skills_dir.glob('scope*')))})")
    meta, body = read_agent_source()
    if claude:
        write(target / ".claude" / "agents" / "scope-reviewer.md", render_claude(meta, body))
        out.append("reviewer agent -> .claude/agents/scope-reviewer.md")
    if opencode:
        write(target / ".opencode" / "agents" / "scope-reviewer.md", render_opencode(meta, body, fmt))
        out.append(f"reviewer agent -> .opencode/agents/scope-reviewer.md (opencode {fmt} format)")
    # tool, keeping .scope/.venv
    tool_dst = target / ".scope"
    tool_dst.mkdir(parents=True, exist_ok=True)
    for name in TOOL_FILES:
        src, dst = SRC / "tool" / name, tool_dst / name
        if dst.is_dir():
            shutil.rmtree(dst)
        if src.is_dir():
            shutil.copytree(src, dst, ignore=shutil.ignore_patterns("__pycache__"))
        else:
            shutil.copyfile(src, dst)
    shutil.copyfile(SRC / "VERSION", tool_dst / "VERSION")
    write(tool_dst / ".gitignore", ".venv/\n__pycache__/\n")
    out.append("tool -> .scope/ (scope.py, scope_lib/, templates/)")
    return out


def uninstall(target: Path) -> list[str]:
    removed = []
    for p in sorted((target / ".claude" / "skills").glob("scope*")):
        if (p / "SKILL.md").exists():
            shutil.rmtree(p)
            removed.append(str(p.relative_to(target)))
    for p in (target / ".claude/agents/scope-reviewer.md", target / ".opencode/agents/scope-reviewer.md"):
        if p.exists():
            p.unlink()
            removed.append(str(p.relative_to(target)))
    if (target / ".scope").exists():
        shutil.rmtree(target / ".scope")
        removed.append(".scope")
    return [f"removed {r}" for r in removed] + ["kept docs/scope/, AGENTS.md and CLAUDE.md"]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Install SCOPE into a project")
    ap.add_argument("project", help="path of the project (its root folder)")
    ap.add_argument("--opencode-format", choices=["v1", "v2"], default="v1")
    ap.add_argument("--no-claude", action="store_true", help="do not write the Claude Code reviewer agent")
    ap.add_argument("--no-opencode", action="store_true", help="do not write the opencode reviewer agent")
    ap.add_argument("--setup", action="store_true", help="also run `scope.py setup` (virtual environment)")
    ap.add_argument("--uninstall", action="store_true")
    args = ap.parse_args(argv)
    target = Path(args.project).resolve()
    if not target.is_dir():
        print(f"not a folder: {target}")
        return 1
    if target == SRC:
        print("refusing to install into the SCOPE source repository itself")
        return 1
    if args.uninstall:
        print("\n".join(uninstall(target)))
        return 0
    lines = install(target, not args.no_claude, not args.no_opencode, args.opencode_format)
    if not (target / ".git").exists():
        lines.append("WARNING: the project is not a git repository; opencode finds skills only inside one (git init)")
    if args.setup:
        res = subprocess.run([sys.executable, str(target / ".scope" / "scope.py"), "setup"], cwd=target,
                             capture_output=True, text=True)
        lines.append((res.stdout + res.stderr).strip())
        if res.returncode:
            print("\n".join(lines))
            return 1
    lines += ["", "Next:",
              "  1. open the project in Claude Code or opencode",
              "  2. ask: \"set up SCOPE\" (skill scope: environment, git policy, build mode, init)",
              "  3. then: \"write the brief\" (skill scope-spec)"]
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
