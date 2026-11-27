#!/usr/bin/env python3
"""Install, upgrade or remove SCOPE for Claude Code and opencode. Standard library only.

Per project (default):
    python3 install.py <project> [--setup]
        .claude/skills/scope*/, .claude/agents/scope-reviewer.md, .opencode/agents/scope-reviewer.md, .scope/

Global (all projects of this user):
    python3 install.py --global [--setup]
        ~/.claude/skills/scope*/       (Claude Code; opencode reads it too)
        ~/.claude/agents/scope-reviewer.md
        ~/.config/opencode/agents/scope-reviewer.md
        ~/.scope/                      (the tool, shared by all projects)

Custom folders (override any default, with a project or with --global):
    --skills-dir PATH  --claude-agents-dir PATH  --opencode-agents-dir PATH  --tool-dir PATH

Other options:
    --opencode-format v1|v2   opencode agent format (default v1: read by opencode 1.x and 2.x)
    --no-claude / --no-opencode   skip that tool's reviewer agent
    --setup                   create <tool-dir>/.venv and install PyYAML
    --uninstall               remove what the same options would install (never docs/scope/)

The installer never touches docs/scope/, AGENTS.md or CLAUDE.md: `scope.py init` (skill `scope`) creates them.
When the tool is not in <project>/.scope, the installed skills and agents call it by its full path.
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
DEFAULT_TOOL_REF = ".scope/scope.py"


def home() -> Path:
    return Path.home()


def known_skill_dirs(project: Path | None) -> dict[str, list[Path]]:
    """Folders each tool searches for skills (docs/compatibility.md)."""
    h = home()
    claude = [h / ".claude" / "skills"]
    opencode = [h / ".config" / "opencode" / "skills", h / ".claude" / "skills", h / ".agents" / "skills"]
    if project:
        claude.append(project / ".claude" / "skills")
        opencode += [project / ".opencode" / "skills", project / ".claude" / "skills", project / ".agents" / "skills"]
    return {"Claude Code": claude, "opencode": opencode}


class Layout:
    def __init__(self, args):
        self.project = Path(args.project).expanduser().resolve() if args.project else None
        h = home()
        if args.global_:
            base = {"skills": h / ".claude" / "skills", "claude_agents": h / ".claude" / "agents",
                    "opencode_agents": h / ".config" / "opencode" / "agents", "tool": h / ".scope"}
        elif self.project:
            p = self.project
            base = {"skills": p / ".claude" / "skills", "claude_agents": p / ".claude" / "agents",
                    "opencode_agents": p / ".opencode" / "agents", "tool": p / ".scope"}
        else:
            base = {}
        given = {"skills": args.skills_dir, "claude_agents": args.claude_agents_dir,
                 "opencode_agents": args.opencode_agents_dir, "tool": args.tool_dir}
        self.dirs = {}
        for key in ("skills", "claude_agents", "opencode_agents", "tool"):
            value = Path(given[key]).expanduser().resolve() if given[key] else base.get(key)
            if value is None:
                raise SystemExit("usage: python3 install.py <project folder> [--setup]   (per project)\n"
                                 "       python3 install.py --global [--setup]           (all projects)\n"
                                 "       python3 install.py -h                           (all options)")
            self.dirs[key] = value

    def tool_ref(self) -> str:
        """How skills and agents call the tool: relative to the project when inside it, else the full path."""
        script = self.dirs["tool"] / "scope.py"
        if self.project and script.is_relative_to(self.project):
            return script.relative_to(self.project).as_posix()
        ref = script.as_posix()
        return f'"{ref}"' if " " in ref else ref


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
    with open(path, "w", encoding="utf-8", newline="\n") as fh:  # Path.write_text(newline=) needs 3.10
        fh.write(text)


def install(lay: Layout, claude: bool, opencode: bool, fmt: str) -> list[str]:
    out = []
    version = (SRC / "VERSION").read_text().strip()
    tool_dir = lay.dirs["tool"]
    old = tool_dir / "VERSION"
    out.append(f"upgrading SCOPE {old.read_text().strip()} -> {version}" if old.exists()
               else f"installing SCOPE {version}")
    ref = lay.tool_ref()
    # skills: replace only SCOPE's own folders
    skills_dir = lay.dirs["skills"]
    for src in sorted((SRC / "skills").iterdir()):
        if (src / "SKILL.md").exists():
            dst = skills_dir / src.name
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst, ignore=shutil.ignore_patterns("__pycache__"))
            if ref != DEFAULT_TOOL_REF:
                skill = dst / "SKILL.md"
                skill.write_text(skill.read_text(encoding="utf-8").replace(DEFAULT_TOOL_REF, ref), encoding="utf-8")
    out.append(f"skills -> {skills_dir}")
    meta, body = read_agent_source()
    body = body.replace(DEFAULT_TOOL_REF, ref)
    if claude:
        write(lay.dirs["claude_agents"] / "scope-reviewer.md", render_claude(meta, body))
        out.append(f"reviewer agent (Claude Code) -> {lay.dirs['claude_agents'] / 'scope-reviewer.md'}")
    if opencode:
        write(lay.dirs["opencode_agents"] / "scope-reviewer.md", render_opencode(meta, body, fmt))
        out.append(f"reviewer agent (opencode {fmt}) -> {lay.dirs['opencode_agents'] / 'scope-reviewer.md'}")
    # tool, keeping its .venv
    tool_dir.mkdir(parents=True, exist_ok=True)
    for name in TOOL_FILES:
        src, dst = SRC / "tool" / name, tool_dir / name
        if dst.is_dir():
            shutil.rmtree(dst)
        if src.is_dir():
            shutil.copytree(src, dst, ignore=shutil.ignore_patterns("__pycache__"))
        else:
            shutil.copyfile(src, dst)
    shutil.copyfile(SRC / "VERSION", tool_dir / "VERSION")
    write(tool_dir / ".gitignore", ".venv/\n__pycache__/\n")
    manifest = {"version": version, "tool_ref": ref, "skills_dir": str(skills_dir),
                "claude_agents_dir": str(lay.dirs["claude_agents"]) if claude else None,
                "opencode_agents_dir": str(lay.dirs["opencode_agents"]) if opencode else None}
    write(tool_dir / "install.json", json.dumps(manifest, indent=2) + "\n")
    out.append(f"tool -> {tool_dir} (skills call it as `python3 {ref}`)")
    out += _visibility_warnings(lay, claude, opencode)
    return out


def _visibility_warnings(lay: Layout, claude: bool, opencode: bool) -> list[str]:
    warnings = []
    skills = lay.dirs["skills"]
    for tool, dirs in known_skill_dirs(lay.project).items():
        if (tool == "Claude Code" and not claude) or (tool == "opencode" and not opencode):
            continue
        if skills not in dirs:
            hint = ('add it to opencode.json: "skills": ["' + skills.as_posix() + '"]' if tool == "opencode"
                    else "Claude Code reads skills only from ~/.claude/skills and <project>/.claude/skills")
            warnings.append(f"WARNING: {tool} does not search {skills} for skills; {hint}")
    return warnings


def uninstall(lay: Layout) -> list[str]:
    removed = []
    for p in sorted(lay.dirs["skills"].glob("scope*")) if lay.dirs["skills"].exists() else []:
        if (p / "SKILL.md").exists():
            shutil.rmtree(p)
            removed.append(str(p))
    for p in (lay.dirs["claude_agents"] / "scope-reviewer.md", lay.dirs["opencode_agents"] / "scope-reviewer.md"):
        if p.exists():
            p.unlink()
            removed.append(str(p))
    if (lay.dirs["tool"] / "scope.py").exists():
        shutil.rmtree(lay.dirs["tool"])
        removed.append(str(lay.dirs["tool"]))
    return [f"removed {r}" for r in removed] + ["kept every docs/scope/, AGENTS.md and CLAUDE.md"]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Install SCOPE for Claude Code and opencode",
                                 formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    ap.add_argument("project", nargs="?", help="project root (omit with --global)")
    ap.add_argument("--global", dest="global_", action="store_true", help="install for all projects of this user")
    ap.add_argument("--skills-dir", help="folder receiving the skills")
    ap.add_argument("--claude-agents-dir", help="folder receiving the Claude Code reviewer agent")
    ap.add_argument("--opencode-agents-dir", help="folder receiving the opencode reviewer agent")
    ap.add_argument("--tool-dir", help="folder receiving scope.py (default <project>/.scope or ~/.scope)")
    ap.add_argument("--opencode-format", choices=["v1", "v2"], default="v1")
    ap.add_argument("--no-claude", action="store_true", help="do not write the Claude Code reviewer agent")
    ap.add_argument("--no-opencode", action="store_true", help="do not write the opencode reviewer agent")
    ap.add_argument("--setup", action="store_true", help="also run `scope.py setup` (virtual environment)")
    ap.add_argument("--uninstall", action="store_true")
    args = ap.parse_args(argv)
    if args.global_ and args.project:
        print("give either a project or --global, not both")
        return 1
    if args.project and not Path(args.project).expanduser().is_dir():
        print(f"not a folder: {args.project}")
        return 1
    lay = Layout(args)
    if lay.project == SRC or any(d == SRC or SRC in d.parents for d in lay.dirs.values()):
        print("refusing to install into the SCOPE source repository itself")
        return 1
    if args.uninstall:
        print("\n".join(uninstall(lay)))
        return 0
    lines = install(lay, not args.no_claude, not args.no_opencode, args.opencode_format)
    if lay.project and not (lay.project / ".git").exists():
        lines.append("WARNING: the project is not a git repository; opencode finds project skills only inside one")
    if args.setup:
        res = subprocess.run([sys.executable, str(lay.dirs["tool"] / "scope.py"), "setup"],
                             capture_output=True, text=True)
        lines.append((res.stdout + res.stderr).strip())
        if res.returncode:
            print("\n".join(lines))
            return 1
    where = "the project" if lay.project else "any project (a git repository)"
    lines += ["", "Next:",
              f"  1. open {where} in Claude Code or opencode",
              "  2. ask: \"set up SCOPE\" (skill scope: environment, git policy, build mode, init)",
              "  3. then: \"write the brief\" (skill scope-spec)"]
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
