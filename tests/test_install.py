import re
import subprocess
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

import install  # noqa: E402


def fm(path: Path) -> dict:
    m = re.match(r"---\n(.*?)\n---\n", path.read_text(encoding="utf-8"), re.S)
    return yaml.safe_load(m.group(1))


def make_project(tmp_path: Path) -> Path:
    proj = tmp_path / "proj"
    proj.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=proj, check=True)
    (proj / ".claude" / "skills" / "other").mkdir(parents=True)
    (proj / ".claude" / "skills" / "other" / "SKILL.md").write_text("---\nname: other\ndescription: x\n---\n")
    return proj


def test_install_layout(tmp_path, capsys):
    proj = make_project(tmp_path)
    assert install.main([str(proj)]) == 0
    skills = sorted(p.name for p in (proj / ".claude" / "skills").iterdir())
    assert skills == ["other", "scope", "scope-arch", "scope-build", "scope-change", "scope-plan", "scope-spec"]
    assert (proj / ".claude/skills/scope-plan/references/story.md").exists()
    claude = fm(proj / ".claude/agents/scope-reviewer.md")
    assert claude["name"] == "scope-reviewer" and "Edit" not in claude["tools"] and "Write" not in claude["tools"]
    oc = fm(proj / ".opencode/agents/scope-reviewer.md")
    assert oc["mode"] == "subagent" and oc["permission"]["edit"] == "deny" and oc["permission"]["task"] == "deny"
    assert "name" not in oc
    assert "VERDICT:" in (proj / ".opencode/agents/scope-reviewer.md").read_text()
    for rel in ("scope.py", "scope_lib/flow.py", "templates/config.yaml", "requirements.txt", "VERSION",
                ".gitignore"):
        assert (proj / ".scope" / rel).exists(), rel
    assert "Next:" in capsys.readouterr().out


def test_opencode_v2_format(tmp_path):
    proj = make_project(tmp_path)
    install.main([str(proj), "--opencode-format", "v2", "--no-claude"])
    oc = fm(proj / ".opencode/agents/scope-reviewer.md")
    assert {"action": "edit", "resource": "*", "effect": "deny"} in oc["permissions"]
    assert not (proj / ".claude/agents/scope-reviewer.md").exists()


def test_upgrade_keeps_project_data(tmp_path, capsys):
    proj = make_project(tmp_path)
    install.main([str(proj)])
    (proj / ".scope" / ".venv").mkdir()
    (proj / "docs" / "scope").mkdir(parents=True)
    (proj / "docs" / "scope" / "spec.md").write_text("keep")
    (proj / ".claude/skills/scope/SKILL.md").write_text("old")
    capsys.readouterr()
    install.main([str(proj)])
    assert "upgrading SCOPE" in capsys.readouterr().out
    assert (proj / ".scope" / ".venv").exists()
    assert (proj / "docs/scope/spec.md").read_text() == "keep"
    assert (proj / ".claude/skills/scope/SKILL.md").read_text() != "old"


def test_installed_tool_runs_and_doctor_sees_install(tmp_path):
    proj = make_project(tmp_path)
    install.main([str(proj)])
    run = lambda *a: subprocess.run([sys.executable, str(proj / ".scope/scope.py"), *a], cwd=proj,  # noqa: E731
                                    capture_output=True, text=True)
    assert run("init", "--name", "P").returncode == 0
    out = run("doctor").stdout
    assert "ok   skills installed: scope, scope-arch, scope-build, scope-change, scope-plan, scope-spec" in out
    assert "ok   reviewer agent for Claude Code" in out and "ok   reviewer agent for opencode" in out
    assert "scope_version:" in (proj / "docs/scope/config.yaml").read_text()
    assert "next: write the brief" in run("status").stdout


def test_uninstall_keeps_docs(tmp_path, capsys):
    proj = make_project(tmp_path)
    install.main([str(proj)])
    (proj / "docs" / "scope").mkdir(parents=True)
    install.main([str(proj), "--uninstall"])
    assert sorted(p.name for p in (proj / ".claude" / "skills").iterdir()) == ["other"]
    assert not (proj / ".scope").exists() and not (proj / ".opencode/agents/scope-reviewer.md").exists()
    assert (proj / "docs" / "scope").exists()


def test_refuses_source_repo(capsys):
    assert install.main([str(REPO)]) == 1
