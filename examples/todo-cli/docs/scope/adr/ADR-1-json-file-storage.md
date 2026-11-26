---
id: ADR-1
type: adr
version: 1.0
status: approved
date: 2026-11-26
supersedes: none
relates_to: [NFR-1, NFR-2, FR-1]
---

# ADR-1 Store tasks in one JSON file with atomic replace

## Context and problem
Tasks must survive between runs, be fast for 1000 tasks (NFR-1) and not be lost on a failed write (NFR-2).

## Decision drivers
- NFR-1 response time, NFR-2 data safety, no external service.

## Options considered
1. **JSON file, write to a temporary file then rename** — simple, atomic on all platforms; whole file rewritten.
2. **SQLite** — robust and fast; heavier for a tiny data set, binary file.

## Decision
Chosen: **JSON file with atomic replace**, because 1000 tasks are a few kB and `os.replace` keeps the old file intact on failure.

## Consequences
- **Good:** human-readable file, standard library only.
- **Bad / accepted trade-off:** concurrent runs may lose an update (single user, accepted).
- **Follow-up:** none.
