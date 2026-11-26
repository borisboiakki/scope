---
id: ST-3
type: story
epic: EP-1
release: R1
status: ready
size: S
implements: [FR-2.1, FR-2.2]
adrs: [ADR-2]
depends_on: [ST-2]
---

# ST-3 List open tasks

## Story
As a developer, I want to list my open tasks, so that I know what is left.

## Acceptance criteria
- **AC-1** (FR-2.1) Given tasks "a" then "b" are open, when I run `todo list`, then it prints "1 a" and "2 b" in that order.
- **AC-2** (FR-2.2) Given no open task, when I run `todo list`, then it prints "No open task".

## Context for the developer
- **Architecture:** subcommand `list` in `todo/cli.py`; order by creation (task number).
- **Constraints:** output format exactly `<number> <text>`.
- **Assumptions / open questions:** none

## Tasks
- [ ] Subcommand `list`
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
