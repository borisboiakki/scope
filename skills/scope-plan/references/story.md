---
id: ST-<n>
type: story
epic: EP-<n>
release: R<n>
status: draft
size: <S|M|L>
implements: [FR-1.1, FR-1.2]
adrs: [ADR-1]
depends_on: [ST-<n>]
---

# ST-<n> <title>

<!-- INVEST: independent, negotiable, valuable, estimable, small, testable.
     The story must be self-contained: the developer reads this file only, so copy here the few
     facts from spec and architecture it needs (short excerpts, with their IDs). -->

## Story
As a <user>, I want <capability>, so that <benefit>.

## Acceptance criteria
- **AC-1** (FR-1.1) Given <context>, when <action>, then <result>.
- **AC-2** (FR-1.2) Given <context>, when <action>, then <result>.

## Context for the developer
- **Architecture:** <module(s) to touch, patterns to follow> (ADR-1)
- **Constraints:** <NFR excerpts, limits>
- **Assumptions / open questions:** <ASM-n, OQ-n or none>

## Tasks
- [ ] <task>
- [ ] Tests for AC-1, AC-2

## Implementation record
<!-- Everything above this heading is frozen at plan approval. Filled during the build. -->
- **Branch / commits:** <branch, hashes>
- **Files changed:** <paths>
- **Tests:** <test names → AC>
- **Notes:** <decisions taken inside the story, new ASM/OQ IDs>

## Review record
| Cycle | Verdict | Findings (severity: summary, file:line) |
|---|---|---|
| 1 | <PASS/CHANGES/BLOCKED> | <findings> |

## Blocker record
<!-- Only if the build stopped: code B1–B7, what happened, what the human must decide. -->
