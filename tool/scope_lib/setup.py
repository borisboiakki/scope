"""Environment setup, diagnostics, project initialisation and configuration."""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

from .util import ScopeError, now, read, write

TOOL_DIR = Path(__file__).resolve().parent.parent          # folder holding scope.py (.scope/ when installed)
TEMPLATES = TOOL_DIR / "templates"
MIN_PY = (3, 9)

PRESETS = {
    "story": {"enabled": True, "commit_by": "agent", "commit_at": ["phase-artifact", "story-done"],
              "branching": "per-epic", "merge": "never", "push": "never"},
    "fine": {"enabled": True, "commit_by": "agent",
             "commit_at": ["phase-artifact", "story-before-review", "story-after-review", "story-done"],
             "branching": "per-story", "merge": "ask", "push": "never"},
    "human": {"enabled": True, "commit_by": "human", "commit_at": ["phase-artifact", "story-done"],
              "branching": "none", "merge": "never", "push": "never"},
    "off": {"enabled": False, "commit_by": "human", "commit_at": ["manual"], "branching": "none",
            "merge": "never", "push": "never"},
}
ALLOWED = {
    "language": None, "project.name": None, "project.test_command": None, "project.lint_command": None,
    "python": None,
    "build.mode": {"supervised", "autonomous"},
    "build.supervised_max_cycles": {"1", "2"},
    "git.enabled": {"true", "false"},
    "git.commit_by": {"agent", "human"},
    "git.commit_at": {"phase-artifact", "story-before-review", "story-after-review", "story-done", "epic-done",
                      "manual"},
    "git.branching": {"none", "per-release", "per-epic", "per-story"},
    "git.branch_pattern": None,
    "git.merge": {"never", "ask", "on-epic-done"},
    "git.push": {"never", "ask", "on-epic-done"},
}


def tool_ref(root: Path | None = None) -> str:
    """How to call this scope.py: relative to the project when it is inside it, else its full path."""
    script = TOOL_DIR / "scope.py"
    root = (root or Path.cwd()).resolve()
    if script.is_relative_to(root):
        return script.relative_to(root).as_posix()
    ref = script.as_posix()
    return f'"{ref}"' if " " in ref else ref


def install_manifest() -> dict:
    import json  # noqa: PLC0415
    path = TOOL_DIR / "install.json"
    try:
        return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    except ValueError:
        return {}


def venv_python(tool_dir: Path = TOOL_DIR) -> Path:
    sub = "Scripts/python.exe" if os.name == "nt" else "bin/python"
    return tool_dir / ".venv" / sub


def setup(system: bool = False) -> str:
    """Create .scope/.venv and install requirements (standard library only)."""
    if sys.version_info < MIN_PY:
        raise ScopeError(f"Python {MIN_PY[0]}.{MIN_PY[1]}+ required, found {sys.version.split()[0]}")
    req = TOOL_DIR / "requirements.txt"
    if system:
        try:
            import yaml  # noqa: F401,PLC0415
            return "using the system Python: PyYAML available"
        except ImportError as exc:
            raise ScopeError(f"PyYAML is not installed for {sys.executable}") from exc
    py = venv_python()
    out = []
    if not py.exists():
        import venv  # noqa: PLC0415
        venv.EnvBuilder(with_pip=True).create(TOOL_DIR / ".venv")
        out.append(f"created {TOOL_DIR / '.venv'}")
    res = subprocess.run([str(py), "-m", "pip", "install", "-q", "-r", str(req)], capture_output=True, text=True)
    if res.returncode != 0:
        raise ScopeError("pip install failed (network or proxy?):\n" + (res.stderr or res.stdout)[-1500:])
    out.append("installed requirements")
    return "\n".join(out)


def doctor(root: Path) -> str:
    lines, problems = [], 0

    def item(ok: bool, text: str, hint: str = ""):
        nonlocal problems
        problems += 0 if ok else 1
        lines.append(f"{'ok  ' if ok else 'FAIL'} {text}" + ("" if ok or not hint else f" -> {hint}"))

    item(sys.version_info >= MIN_PY, f"python {sys.version.split()[0]} ({sys.executable})", "install Python 3.9+")
    try:
        import yaml  # noqa: PLC0415
        item(True, f"PyYAML {yaml.__version__}")
    except ImportError:
        venv_ok = venv_python().exists() and subprocess.run(
            [str(venv_python()), "-c", "import yaml"], capture_output=True).returncode == 0
        item(venv_ok, "PyYAML" + (" (in .scope/.venv, used automatically)" if venv_ok else ""),
             f"run: python3 {tool_ref(root)} setup")
    item(venv_python().exists(), f"virtual environment {venv_python()}", f"run: python3 {tool_ref(root)} setup")
    git = shutil.which("git")
    item(bool(git), "git installed", "install git (needed by opencode skill discovery and the git policy)")
    if git:
        res = subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], cwd=root, capture_output=True, text=True)
        item(res.stdout.strip() == "true", "project is a git repository", "run: git init")
    man, home = install_manifest(), Path.home()
    skill_dirs = [Path(man["skills_dir"])] if man.get("skills_dir") else []
    skill_dirs += [root / ".claude" / "skills", home / ".claude" / "skills", home / ".config" / "opencode" / "skills"]
    found_in = next((d for d in skill_dirs if len(list(d.glob("scope*/SKILL.md"))) >= 6), None)
    names = sorted(p.parent.name for p in found_in.glob("scope*/SKILL.md")) if found_in else []
    item(bool(found_in), f"skills installed: {', '.join(names) or 'none'}" + (f" ({found_in})" if found_in else ""),
         "run the SCOPE installer")
    for label, key, dirs in (("Claude Code", "claude_agents_dir", [root / ".claude/agents", home / ".claude/agents"]),
                             ("opencode", "opencode_agents_dir",
                              [root / ".opencode/agents", home / ".config/opencode/agents"])):
        dirs = ([Path(man[key])] if man.get(key) else []) + dirs
        where = next((d for d in dirs if (d / "scope-reviewer.md").exists()), None)
        item(bool(where), f"reviewer agent for {label}" + (f" ({where})" if where else ""), "run the installer")
    for var in ("OPENCODE_DISABLE_CLAUDE_CODE", "OPENCODE_DISABLE_CLAUDE_CODE_SKILLS"):
        item(not os.environ.get(var), f"{var} not set", "unset it, or opencode will not load .claude/skills")
    item((root / "docs/scope/state.yaml").exists(), "project initialised (docs/scope/)", "run: scope.py init")
    cfg = root / "docs/scope/config.yaml"
    installed = read(TOOL_DIR / "VERSION").strip() if (TOOL_DIR / "VERSION").exists() else "dev"
    if cfg.exists():
        import re  # noqa: PLC0415
        m = re.search(r"^scope_version:\s*['\"]?([^'\"\n]+)", read(cfg), re.M)
        if m and m.group(1).strip() != installed:
            lines.append(f"note project set up with SCOPE {m.group(1).strip()}, installed tool is {installed}")
    lines.append(f"doctor: {problems} problem(s)")
    return "\n".join(lines)


def init(root: Path, name: str, preset: str, mode: str, language: str, test_cmd: str, lint_cmd: str) -> str:
    from .util import yaml_module  # noqa: PLC0415
    yaml = yaml_module()
    if preset not in PRESETS:
        raise ScopeError(f"preset must be one of {', '.join(PRESETS)}")
    if mode not in ("supervised", "autonomous"):
        raise ScopeError("mode must be supervised or autonomous")
    d = root / "docs" / "scope"
    out = []
    for sub in ("adr", "stories", "changes", "reports"):
        (d / sub).mkdir(parents=True, exist_ok=True)
    version = read(TOOL_DIR / "VERSION").strip() if (TOOL_DIR / "VERSION").exists() else "dev"
    if not (d / "config.yaml").exists():
        cfg = {
            "scope_version": version, "language": language,
            "project": {"name": name, "test_command": test_cmd, "lint_command": lint_cmd},
            "python": "python" if os.name == "nt" else "python3",
            "build": {"mode": mode, "supervised_max_cycles": 2, "autonomous_cycles": 2},
            "git": {"preset": preset, **PRESETS[preset], "branch_pattern": "scope/{id}-{slug}"},
        }
        write(d / "config.yaml", "# SCOPE configuration. Change it with `scope.py config` (METHOD.md section 10).\n"
              + yaml.safe_dump(cfg, sort_keys=False, allow_unicode=True))
        out.append("created docs/scope/config.yaml")
    if not (d / "state.yaml").exists():
        state = yaml.safe_load(read(TEMPLATES / "state.yaml"))
        state["history"] = [f"{now()} init (preset {preset}, mode {mode})"]
        state.update({"reopens": [], "carryover": [], "branches": {}, "epic_modes": {}})
        write(d / "state.yaml", "# SCOPE state. Managed by scope.py only: do not edit by hand.\n"
              + yaml.safe_dump(state, sort_keys=False, allow_unicode=True))
        out.append("created docs/scope/state.yaml")
    if not (d / "register.md").exists():
        shutil.copyfile(TEMPLATES / "register.md", d / "register.md")
        out.append("created docs/scope/register.md")
    out.append(_install_agents_md(root, "python" if os.name == "nt" else "python3", tool_ref(root)))
    claude = root / "CLAUDE.md"
    if not claude.exists():
        write(claude, "@AGENTS.md\n")
        out.append("created CLAUDE.md (imports AGENTS.md)")
    elif "@AGENTS.md" not in read(claude):
        write(claude, read(claude).rstrip("\n") + "\n\n@AGENTS.md\n")
        out.append("CLAUDE.md now imports AGENTS.md")
    return "\n".join(x for x in out if x)


def _install_agents_md(root: Path, python: str, ref: str) -> str:
    section = read(TEMPLATES / "agents-section.md").replace("<python>", python).replace(".scope/scope.py", ref)
    path = root / "AGENTS.md"
    if not path.exists():
        write(path, "# Project rules\n\n" + section)
        return "created AGENTS.md"
    text = read(path)
    if "<!-- scope:begin -->" in text and "<!-- scope:end -->" in text:
        return "AGENTS.md already has the SCOPE section"
    write(path, text.rstrip("\n") + "\n\n" + section)
    return "added the SCOPE section to AGENTS.md"


def config(project, action: str, key: str | None, values: list[str]) -> str:
    cfg = project.config
    if action == "show":
        from .util import yaml_module  # noqa: PLC0415
        return yaml_module().safe_dump(cfg, sort_keys=False).rstrip()
    if action == "preset":
        if key not in PRESETS:
            raise ScopeError(f"preset must be one of {', '.join(PRESETS)}")
        cfg.setdefault("git", {}).update({"preset": key, **PRESETS[key]})
        msg = f"git preset {key}"
    elif action == "set":
        if key not in ALLOWED:
            raise ScopeError(f"unknown key '{key}'; keys: {', '.join(ALLOWED)}")
        allowed = ALLOWED[key]
        if not values:
            raise ScopeError("give a value")
        if allowed and any(v not in allowed for v in values):
            raise ScopeError(f"{key} accepts: {', '.join(sorted(allowed))}")
        if key == "git.commit_at":
            value = values
        elif key == "git.enabled":
            value = values[0] == "true"
        elif key == "build.supervised_max_cycles":
            value = int(values[0])
        else:
            value = " ".join(values)
        section, _, leaf = key.rpartition(".")
        target = cfg.setdefault(section, {}) if section else cfg
        target[leaf] = value
        if section == "git":
            cfg["git"]["preset"] = "custom"
        msg = f"{key} = {value}"
    else:
        raise ScopeError("config action must be show, preset or set")
    project.save_config()
    project.log(f"config: {msg}")
    project.save_state()
    return msg
