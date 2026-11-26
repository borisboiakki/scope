---
id: ST-2
type: story
epic: EP-1
release: R1
status: ready
size: S
implements: [FR-1.1, FR-1.2]
adrs: [ADR-2]
depends_on: [ST-1]
---

# ST-2 Add a task

## Story
As a developer, I want to add a task with one command, so that I capture it instantly.

## Acceptance criteria
- **AC-1** (FR-1.1) Given any list, when I run `todo add "Write docs"`, then an open task "Write docs" is stored and its number is printed.
- **AC-2** (FR-1.2) Given any list, when I run `todo add` with empty text, then nothing is stored and an error is printed (exit code 1).

## Context for the developer
- **Architecture:** `todo/cli.py` (argparse subcommand `add`, ADR-2), `todo/tasks.py` (numbering: max number + 1, never reused).
- **Constraints:** errors are one line on stderr, exit code 1.
- **Assumptions / open questions:** none

## Tasks
- [ ] `todo/tasks.py`: Task dataclass and `add`
- [ ] `todo/cli.py`: `main(argv)` with `add`
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
