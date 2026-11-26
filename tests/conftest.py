import sys
from pathlib import Path

import pytest

TOOL = Path(__file__).resolve().parent.parent / "tool"
sys.path.insert(0, str(TOOL))

import scope  # noqa: E402

BRIEF = """---
id: brief
type: brief
version: 0.1
status: draft
---

# Brief — Todo

## Business goals

### BR-1 Track tasks
- **Success indicator:** a task is added in less than 5 s
"""

SPEC = """---
id: spec
type: spec
version: 0.1
status: draft
---

# Specification — Todo

## 3. Functional requirements

### FR-1 Add task
- **Release:** R1
- **Source:** BR-1
- **Statement:** When the user enters a title, the system shall store the task.
- **FR-1.1** Given an empty list, when I add "a", then the list shows "a".

### FR-2 Delete task
- **Release:** R2
- **Source:** BR-1
- **Statement:** When the user deletes a task, the system shall remove it.
- **FR-2.1** Given a list with "a", when I delete "a", then the list is empty.

## 4. Non-functional requirements

### NFR-1 Speed
- **Release:** R1
- **Source:** BR-1
- **Statement:** The system shall list 1000 tasks in less than 100 ms.
- **NFR-1.1** Given 1000 tasks, when I list them, then it takes less than 100 ms.
"""

ARCH = """---
id: architecture
type: architecture
version: 0.1
status: draft
---

# Architecture — Todo

## 3. Solution strategy
- SQLite storage — ADR-1 (NFR-1)
"""

ADR = """---
id: ADR-1
type: adr
version: 0.1
status: draft
date: 2026-11-26
supersedes: none
relates_to: [NFR-1]
---

# ADR-1 Use SQLite

## Decision
Chosen: **SQLite**, because it is fast enough for NFR-1.
"""

ROADMAP = """---
id: roadmap
type: roadmap
version: 0.1
status: draft
---

# Roadmap — Todo

## R1 — MVP
- **Status:** planned
- **Goal:** add and list tasks
- **In scope:** FR-1, NFR-1
- **Epics:** EP-1
- **Out of scope:** FR-2 (R2)
- **Exit criteria:** all R1 stories done

## R2 — Editing
- **Status:** planned
- **Goal:** delete tasks
- **In scope:** FR-2
- **Epics:** to plan
- **Out of scope:** none
- **Exit criteria:** all R2 stories done
"""

EPICS = """---
id: epics
type: epics
version: 0.1
status: draft
---

# Epics

## EP-1 Task list
- **Release:** R1
- **Status:** planned
- **Goal:** users manage a task list
- **Requirements:** FR-1, NFR-1

| Order | Story | Title | Depends on | Size |
|---|---|---|---|---|
| 1 | ST-1 | Add a task | — | S |
| 2 | ST-2 | Fast listing | ST-1 | M |
"""

STORY = """---
id: {id}
type: story
epic: EP-1
release: R1
status: draft
size: S
implements: [{impl}]
adrs: [{adrs}]
depends_on: [{deps}]
---

# {id} {title}

## Story
As a user, I want {title}, so that I track my work.

## Acceptance criteria
- **AC-1** ({impl}) Given a list, when I act, then it works.

## Implementation record
- **Files changed:** -

## Review record
| Cycle | Verdict | Findings (severity: summary, file:line) |
|---|---|---|

## Blocker record
"""


class Runner:
    def __init__(self, root: Path, capsys):
        self.root = root
        self.capsys = capsys

    def __call__(self, *args, ok=True):
        self.capsys.readouterr()
        code = scope.main(["--root", str(self.root), *args])
        out = self.capsys.readouterr().out
        if ok is not None:
            assert (code == 0) == ok, f"scope {' '.join(args)} -> {code}\n{out}"
        return out

    def path(self, rel: str) -> Path:
        return self.root / "docs" / "scope" / rel

    def write(self, rel: str, text: str):
        p = self.path(rel)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")

    def edit(self, rel: str, old: str, new: str):
        p = self.path(rel)
        text = p.read_text(encoding="utf-8")
        assert old in text, f"{old!r} not in {rel}"
        p.write_text(text.replace(old, new, 1), encoding="utf-8")

    def add_review(self, sid: str, cycle: int, verdict: str):
        p = next(self.path("stories").glob(f"{sid}-*.md"))
        text = p.read_text(encoding="utf-8")
        marker = "|---|---|---|\n"
        idx = text.index(marker) + len(marker)
        rows = text[idx:].split("\n## Blocker record")[0]
        new_rows = rows + f"| {cycle} | {verdict} | none |\n"
        p.write_text(text[:idx] + new_rows + text[idx + len(rows):], encoding="utf-8")


@pytest.fixture
def run(tmp_path, capsys):
    r = Runner(tmp_path, capsys)
    r("init", "--name", "Todo", "--test-cmd", "pytest -q")
    return r


@pytest.fixture
def sample(run):
    run.write("brief.md", BRIEF)
    run.write("spec.md", SPEC)
    run.write("architecture.md", ARCH)
    run.write("adr/ADR-1-use-sqlite.md", ADR)
    run.write("roadmap.md", ROADMAP)
    run.write("epics.md", EPICS)
    run.write("stories/ST-1-add-a-task.md", STORY.format(id="ST-1", title="Add a task", impl="FR-1.1", adrs="",
                                                        deps=""))
    run.write("stories/ST-2-fast-listing.md", STORY.format(id="ST-2", title="Fast listing", impl="NFR-1.1",
                                                           adrs="ADR-1", deps="ST-1"))
    return run


@pytest.fixture
def planned(sample):
    for target in ("brief", "spec", "architecture"):
        sample("approve", target)
    sample("approve", "plan", "R1")
    return sample
