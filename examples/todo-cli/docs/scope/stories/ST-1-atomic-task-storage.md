---
id: ST-1
type: story
epic: EP-1
release: R1
status: ready
size: S
implements: [NFR-2.1]
adrs: [ADR-1]
depends_on: []
---

# ST-1 Atomic task storage

## Story
As a developer, I want my tasks to survive a failed write, so that I never lose my list.

## Acceptance criteria
- **AC-1** (NFR-2.1) Given a saved list, when a save is interrupted before the rename, then loading returns the previous list.

## Context for the developer
- **Architecture:** `todo/store.py` with `load(path)` and `save(path, tasks)`; write to `<file>.tmp` then `os.replace` (ADR-1).
- **Constraints:** NFR-2: the previous file stays intact on failure. File from `TODO_FILE` or `~/.todo/tasks.json`.
- **Assumptions / open questions:** ASM-1

## Tasks
- [ ] `todo/store.py`: load (missing file = empty list) and atomic save
- [ ] Test for AC-1 (simulate failure before rename)

## Implementation record
- **Branch / commits:** -
- **Files changed:** -
- **Tests:** -
- **Notes:** -

## Review record
| Cycle | Verdict | Findings (severity: summary, file:line) |
|---|---|---|

## Blocker record
