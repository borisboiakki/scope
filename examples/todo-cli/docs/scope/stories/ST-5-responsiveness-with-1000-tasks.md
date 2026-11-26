---
id: ST-5
type: story
epic: EP-2
release: R1
status: ready
size: S
implements: [NFR-1.1]
adrs: [ADR-1]
depends_on: [ST-4]
---

# ST-5 Responsiveness with 1000 tasks

## Story
As a developer, I want every command to answer in less than 1 s with 1000 tasks, so that the tool never slows me down.

## Acceptance criteria
- **AC-1** (NFR-1.1) Given 1000 stored tasks, when I run `todo add x`, then the command ends in less than 1 s.

## Context for the developer
- **Architecture:** whole-file JSON load/save (ADR-1); measure, optimise only if needed.
- **Constraints:** NFR-1 limit 1 s on a developer laptop.
- **Assumptions / open questions:** none

## Tasks
- [ ] Timing test with 1000 generated tasks
- [ ] Fix hot spots if the test fails

## Implementation record
- **Branch / commits:** -
- **Files changed:** -
- **Tests:** -
- **Notes:** -

## Review record
| Cycle | Verdict | Findings (severity: summary, file:line) |
|---|---|---|

## Blocker record
