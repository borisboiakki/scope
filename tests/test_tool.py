import subprocess

from conftest import scope


def test_init_creates_project(run):
    for rel in ("config.yaml", "state.yaml", "register.md"):
        assert run.path(rel).exists()
    agents = (run.root / "AGENTS.md").read_text()
    assert "<!-- scope:begin -->" in agents
    assert f"python3 {(scope.Path(scope.__file__).resolve()).as_posix()}" in agents  # tool outside the project
    assert (run.root / "CLAUDE.md").read_text().strip() == "@AGENTS.md"
    run("init", "--name", "Todo")  # idempotent
    assert agents == (run.root / "AGENTS.md").read_text()


def test_check_sample_is_clean(sample):
    out = sample("check")
    assert "0 error(s)" in out
    out = sample("check", "--for", "plan", ok=False)
    assert "brief is not approved" in out or "spec is not approved" in out


def test_dangling_reference(sample):
    sample.edit("spec.md", "- **Source:** BR-1\n- **Statement:** When the user deletes",
                "- **Source:** BR-9\n- **Statement:** When the user deletes")
    out = sample("check", ok=False)
    assert "E06" in out and "BR-9" in out


def test_releases_before_roadmap(sample):
    sample.path("roadmap.md").unlink()
    sample.path("epics.md").unlink()
    for st in sample.path("stories").glob("*.md"):
        st.unlink()
    assert "0 error(s)" in sample("check")


def test_requirement_without_criterion(sample):
    sample.edit("spec.md", '- **FR-2.1** Given a list with "a", when I delete "a", then the list is empty.\n', "")
    assert "E09" in sample("check", ok=False)


def test_approval_chain(sample):
    out = sample("approve", "spec", ok=False)
    assert "brief must be approved" in out
    assert "approved brief v1.0" in sample("approve", "brief")
    assert "version: 1.0" in sample.path("brief.md").read_text()
    sample("approve", "spec")
    out = sample("approve", "architecture")
    assert "ADR-1" in out
    assert "status: approved" in sample.path("adr/ADR-1-use-sqlite.md").read_text()
    out = sample("approve", "plan", "R1")
    assert "2 story(ies), 2 made ready" in out
    assert "status: ready" in sample.path("stories/ST-1-add-a-task.md").read_text()
    assert "- **Status:** ready" in sample.path("epics.md").read_text()
    assert "0 error(s)" in sample("check")
    assert "gate before build: NOT passed" in sample("check", "--for", "build", ok=False)


def test_drift_and_change_request(planned):
    planned.edit("spec.md", "store the task", "store the task and its date")
    out = planned("check", ok=False)
    assert "E15" in out and "spec.md" in out
    assert "must exist and be approved" in planned("reopen", "spec", "--cr", "CR-1", ok=False)
    planned.write("changes/CR-1-add-date.md", """---
id: CR-1
type: cr
status: proposed
change_type: requirement
class: minor
quick: false
affects: [FR-1]
date: 2026-11-26
---

# CR-1 Store the date

## Reason
Users need the date.
""")
    assert "approval refused" in planned("approve", "spec", ok=False)  # check fails (drift)
    planned("approve", "CR-1")
    planned("reopen", "spec", "--cr", "CR-1")
    assert "bump the version" in planned("approve", "spec", ok=False)
    planned.edit("spec.md", "version: 1.0", "version: 1.1")
    assert "approved spec v1.1" in planned("approve", "spec")
    assert "CR-1 applied" in planned("cr", "close", "CR-1")
    assert "0 error(s)" in planned("check")


def test_manual_status_change_is_detected(planned):
    planned.edit("spec.md", "status: approved", "status: draft")
    assert "E16" in planned("check", ok=False)


def test_story_definition_drift(planned):
    planned.edit("stories/ST-1-add-a-task.md", "then it works", "then it really works")
    assert "E15" in planned("check", ok=False)


def test_story_records_do_not_drift(planned):
    planned.edit("stories/ST-1-add-a-task.md", "- **Files changed:** -", "- **Files changed:** app.py")
    assert "0 error(s)" in planned("check")


def test_plan_needs_coverage(sample):
    for t in ("brief", "spec", "architecture"):
        sample("approve", t)
    sample.edit("stories/ST-2-fast-listing.md", "implements: [NFR-1.1]", "implements: [FR-1.1]")
    sample.edit("stories/ST-2-fast-listing.md", "(NFR-1.1)", "(FR-1.1)")
    out = sample("approve", "plan", "R1", ok=False)
    assert "E13" in out and "NFR-1.1" in out


def test_blocking_question_blocks_approval(sample):
    out = sample("register", "add", "--type", "OQ", "--statement", "Which database?", "--raised", "brief",
                 "--blocking", "yes", "--impacts", "NFR-1")
    assert out.strip() == "OQ-1"
    assert "blocking register item open: OQ-1" in sample("approve", "brief", ok=False)
    sample("register", "set", "OQ-1", "--status", "answered", "--resolution", "SQLite")
    sample("approve", "brief")
    assert "OQ-1 [answered" in sample("register")


def test_invalidated_assumption_hints_cr(sample):
    sample("register", "add", "--type", "ASM", "--statement", "Single user", "--impacts", "FR-1")
    assert "propose a CR" in sample("register", "set", "ASM-1", "--status", "invalidated")
    assert "ASM-1: impacts FR-1" in sample("impact", "ASM-1")


def _build_story(run, sid, cycles=2):
    run("story", "start", sid)
    for cycle in range(1, cycles + 1):
        run("story", "review", sid)
        verdict = "PASS" if cycle == cycles else "CHANGES"
        run.add_review(sid, cycle, verdict)
        if verdict == "CHANGES":
            run("story", "rework", sid)


def test_autonomous_epic_and_release_close(planned):
    assert "launched EP-1 (autonomous)" in planned("approve", "launch", "EP-1", "--mode", "autonomous")
    assert "- **Status:** active" in planned.path("roadmap.md").read_text()
    assert "depends on unfinished ST-1" in planned("story", "start", "ST-2", ok=False)
    planned("story", "start", "ST-1")
    planned("story", "review", "ST-1")
    planned.add_review("ST-1", 1, "PASS")
    assert "2 review cycles" in planned("story", "done", "ST-1", ok=False)
    planned("story", "rework", "ST-1")
    planned("story", "review", "ST-1")
    planned.add_review("ST-1", 2, "PASS")
    planned("story", "done", "ST-1")
    _build_story(planned, "ST-2")
    assert "EP-1 done" in planned("story", "done", "ST-2")
    assert "0 error(s)" in planned("check")
    assert "approve release-close R1" in planned("status")
    out = planned("approve", "release-close", "R1")
    assert "released R1" in out
    notes = planned.path("reports/release-R1.md").read_text()
    assert "FR-1 Add task" in notes and "ST-2" in notes
    assert "status: draft" in planned.path("roadmap.md").read_text()
    assert "0 error(s)" in planned("check")


def test_supervised_story_needs_human(planned):
    planned("approve", "launch", "EP-1")
    planned("story", "start", "ST-1")
    planned("story", "review", "ST-1")
    planned.add_review("ST-1", 1, "PASS")
    assert "the human approves the story" in planned("story", "done", "ST-1", ok=False)
    assert "approved ST-1: done" in planned("approve", "ST-1", "--by", "human via opencode")


def test_block_and_unblock(planned):
    planned("approve", "launch", "EP-1", "--mode", "autonomous")
    planned("story", "start", "ST-1")
    assert "needs --code" in planned("story", "block", "ST-1", ok=False)
    assert "BLOCKED (B5)" in planned("story", "block", "ST-1", "--code", "B5", "--summary", "AC-1 ambiguous")
    assert "- **Status:** blocked" in planned.path("epics.md").read_text()
    assert "BLOCKER ST-1 B5" in planned("status")
    assert "unblocked -> in-progress" in planned("story", "unblock", "ST-1")
    assert "- **Status:** launched" in planned.path("epics.md").read_text()


def test_release_close_with_carry(planned):
    planned("approve", "launch", "EP-1", "--mode", "autonomous")
    _build_story(planned, "ST-1")
    planned("story", "done", "ST-1")
    assert "unfinished work" in planned("approve", "release-close", "R1", ok=False)
    out = planned("approve", "release-close", "R1", "--carry", "R2", "--reason", "time box")
    assert "released R1" in out
    rem = planned("remaining")
    assert "R2: 2 requirement(s)" in rem
    text = planned.path("reports/remaining.md").read_text()
    assert "carried R1 -> R2" in text and "NFR-1" in text


def test_quick_change_request(planned):
    planned.write("stories/ST-3-fix-title.md", """---
id: ST-3
type: story
epic: EP-1
release: R1
status: draft
size: S
implements: [FR-1.1]
adrs: []
depends_on: []
cr: CR-1
---

# ST-3 Trim titles

## Acceptance criteria
- **AC-1** (FR-1.1) Given " a ", when I add it, then the list shows "a".

## Implementation record
""")
    planned.write("changes/CR-1-trim.md", """---
id: CR-1
type: cr
status: proposed
change_type: defect
class: minor
quick: true
affects: [ST-3, FR-1]
date: 2026-11-26
---

# CR-1 Trim titles
""")
    assert "1 quick story(ies) ready" in planned("approve", "CR-1")
    assert "status: ready" in planned.path("stories/ST-3-fix-title.md").read_text()


def test_reports_and_queries(planned):
    assert planned("next-id", "ST").strip() == "ST-3"
    assert planned("next-id", "FR-1.").strip() == "FR-1.2"
    assert planned("next-id", "R").strip() == "R3"
    out = planned("extract", "FR-1.1", "ADR-1")
    assert "FR-1 Add task" in out and "SQLite" in out and "<!--" not in out
    out = planned("impact", "NFR-1")
    assert "ST-2" in out and "ADR-1" in out and "R1" in out
    planned("trace")
    assert "| FR-1 Add task |" in planned.path("reports/trace.md").read_text()
    assert "next:" in planned("status")


def test_config(run):
    assert "git.branching = per-story" in run("config", "set", "git.branching", "per-story")
    assert "preset: custom" in run("config", "show")
    assert "accepts" in run("config", "set", "build.mode", "fast", ok=False)
    run("config", "preset", "human")
    assert "commit_by: human" in run("config", "show")


def test_git_policy(planned):
    root = planned.root
    for cmd in (["init", "-q", "-b", "main"], ["config", "user.email", "t@example.com"], ["config", "user.name", "t"]):
        subprocess.run(["git", *cmd], cwd=root, check=True)
    out = planned("git", "phase-artifact", "spec")
    assert "committed: docs(scope): spec v1.0" in out
    out = planned("git", "epic-start", "EP-1")
    assert "created branch scope/EP-1-task-list from main" in out
    assert "no commit at story-before-review" in planned("git", "story-before-review", "ST-1")
    (root / "app.py").write_text("print('hi')\n")
    out = planned("git", "story-done", "ST-1")
    assert "committed: feat(ST-1): Add a task" in out
    out = planned("git", "epic-done", "EP-1")
    assert "no merge" in out
    planned("config", "preset", "human")
    assert "HUMAN COMMIT CHECKPOINT" in planned("git", "phase-artifact", "spec")


def test_doctor_runs(run):
    out = run("doctor", ok=None)
    assert "doctor:" in out and "project initialised" in out


def test_example_project_is_consistent(tmp_path, capsys):
    import shutil
    from pathlib import Path
    src = Path(__file__).resolve().parent.parent / "examples" / "todo-cli"
    shutil.copytree(src, tmp_path / "todo-cli")
    code = scope.main(["--root", str(tmp_path / "todo-cli"), "check"])
    out = capsys.readouterr().out
    assert code == 0 and "0 error(s), 0 warning(s)" in out, out


def test_rework_after_epic_done(planned):
    planned("approve", "launch", "EP-1", "--mode", "autonomous")
    for sid in ("ST-1", "ST-2"):
        _build_story(planned, sid)
        planned("story", "done", sid)
    planned.write("changes/CR-1-change.md", """---
id: CR-1
type: cr
status: proposed
change_type: requirement
class: minor
quick: false
affects: [FR-1, ST-1]
date: 2026-11-26
---

# CR-1 Change ST-1
""")
    planned("approve", "CR-1")
    planned("reopen", "ST-1", "--cr", "CR-1")
    planned.edit("stories/ST-1-add-a-task.md", "then it works", "then it works and shows the date")
    assert "approval refused" not in planned("check", ok=None)
    planned("reopen", "epics", "--cr", "CR-1")
    planned.edit("epics.md", "version: 1.0", "version: 1.1")
    planned("approve", "plan", "R1")
    assert "- **Status:** ready" in planned.path("epics.md").read_text()
    planned("cr", "close", "CR-1")
    planned("approve", "launch", "EP-1", "--mode", "autonomous")
    _build_story(planned, "ST-1")
    assert "EP-1 done" in planned("story", "done", "ST-1")


def test_quick_story_in_done_epic(planned):
    planned("approve", "launch", "EP-1", "--mode", "autonomous")
    for sid in ("ST-1", "ST-2"):
        _build_story(planned, sid)
        planned("story", "done", sid)
    planned.write("stories/ST-3-fix.md", """---
id: ST-3
type: story
epic: EP-1
release: R1
status: draft
size: S
implements: [FR-1.1]
adrs: []
depends_on: []
cr: CR-1
---

# ST-3 Fix trailing spaces

## Implementation record

## Review record
| Cycle | Verdict | Findings (severity: summary, file:line) |
|---|---|---|

## Blocker record
""")
    planned.write("changes/CR-1-fix.md", """---
id: CR-1
type: cr
status: proposed
change_type: defect
class: minor
quick: true
affects: [ST-3, FR-1]
date: 2026-11-26
---

# CR-1 Fix trailing spaces
""")
    planned("approve", "CR-1")
    planned("cr", "close", "CR-1")
    assert "- **Status:** launched" in planned.path("epics.md").read_text()
    _build_story(planned, "ST-3")
    assert "EP-1 done" in planned("story", "done", "ST-3")
    assert "0 error(s)" in planned("check")


def test_ticking_tasks_is_not_drift(planned):
    planned.edit("stories/ST-1-add-a-task.md", "## Implementation record", "## Tasks\n- [x] done\n\n## Implementation record")
    assert "E15" in planned("check", ok=False)  # a new task is a real change
    planned.edit("stories/ST-1-add-a-task.md", "- [x] done", "- [ ] done")
    assert "E15" in planned("check", ok=False)


def test_checkbox_state_ignored_by_hash():
    from scope_lib.util import content_hash
    assert content_hash("a\n- [ ] task\n") == content_hash("a\n- [x] task\n")
    assert content_hash("a\n- [ ] task\n") != content_hash("a\n- [ ] other\n")
