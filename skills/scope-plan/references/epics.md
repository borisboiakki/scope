---
id: epics
type: epics
version: 0.1
status: draft
---

# Epics

<!-- One section per epic. An epic delivers a user-visible capability and belongs to one release.
     The stories table gives the build order: a story comes after the stories it depends on.
     Story status lives in the story file only (scope.py status shows it). -->

## Definition of Ready (all stories)
- Acceptance criteria are testable and trace to requirements.
- Dependencies are done or scheduled before it.
- No blocking open question in its `implements` or `adrs`.

## Definition of Done (all stories)
- Every acceptance criterion is implemented and covered by a test.
- Project tests and linters pass.
- Review verdict PASS (2 cycles in autonomous mode).
- Implementation and review records filled; register updated.

## EP-1 <title>
- **Release:** R1
- **Status:** planned
- **Goal:** <capability delivered>
- **Requirements:** FR-1, FR-2

| Order | Story | Title | Depends on | Size |
|---|---|---|---|---|
| 1 | ST-1 | <title> | — | S |
| 2 | ST-2 | <title> | ST-1 | M |

## EP-2 <title>
- **Release:** R1
- **Status:** planned
- **Goal:** <capability>
- **Requirements:** <IDs>

| Order | Story | Title | Depends on | Size |
|---|---|---|---|---|
| 1 | ST-3 | <title> | ST-2 | S |

## Changelog
| Version | Date | CR | Change |
|---|---|---|---|
| 0.1 | <date> | — | First draft |
