---
id: epics
type: epics
version: 1.0
status: approved
---

# Epics

## Definition of Ready (all stories)
- Acceptance criteria are testable and trace to requirements.
- Dependencies are done or scheduled before it.
- No blocking open question in its `implements` or `adrs`.

## Definition of Done (all stories)
- Every acceptance criterion is implemented and covered by a test.
- Project tests and linters pass.
- Review verdict PASS (2 cycles in autonomous mode).
- Implementation and review records filled; register updated.

## EP-1 Capture and list tasks
- **Release:** R1
- **Status:** ready
- **Goal:** tasks are stored safely and can be added and listed
- **Requirements:** FR-1, FR-2, NFR-2

| Order | Story | Title | Depends on | Size |
|---|---|---|---|---|
| 1 | ST-1 | Atomic task storage | — | S |
| 2 | ST-2 | Add a task | ST-1 | S |
| 3 | ST-3 | List open tasks | ST-2 | S |

## EP-2 Complete tasks
- **Release:** R1
- **Status:** ready
- **Goal:** tasks can be closed, and every command stays fast
- **Requirements:** FR-3, NFR-1

| Order | Story | Title | Depends on | Size |
|---|---|---|---|---|
| 1 | ST-4 | Complete a task | ST-3 | S |
| 2 | ST-5 | Responsiveness with 1000 tasks | ST-4 | S |

## Changelog
| Version | Date | CR | Change |
|---|---|---|---|
| 0.1 | 2026-11-26 | — | First draft |
