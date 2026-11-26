---
id: ST-4
type: story
epic: EP-2
release: R1
status: ready
size: S
implements: [FR-3.1, FR-3.2]
adrs: [ADR-2]
depends_on: [ST-3]
---

# ST-4 Complete a task

## Story
As a developer, I want to mark a task as done, so that it leaves my open list.

## Acceptance criteria
- **AC-1** (FR-3.1) Given open task 1, when I run `todo done 1`, then task 1 is no longer listed by `todo list`.
- **AC-2** (FR-3.2) Given no task 7, when I run `todo done 7`, then an error is printed and nothing changes.

## Context for the developer
- **Architecture:** subcommand `done` in `todo/cli.py`; state change in `todo/tasks.py`; saved with `store.save` (ADR-1).
- **Constraints:** a done task keeps its number.
- **Assumptions / open questions:** none

## Tasks
- [ ] Subcommand `done`
- [ ] Tests for AC-1 and AC-2

## Implementation record
- **Branch / commits:** -
- **Files changed:** -
- **Tests:** -
- **Notes:** -

## Review record
| Cycle | Verdict | Findings (severity: summary, file:line) |
|---|---|---|

## Blocker record
