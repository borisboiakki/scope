---
id: brief
type: brief
version: 1.0
status: approved
---

# Brief — todo-cli

## Problem
Developers keep short task lists in scattered text files. They lose tasks and cannot see quickly what
is still open. They want a task list that lives in the terminal, next to their code.

## Users and stakeholders
| Who | Need | Today's workaround |
|---|---|---|
| Developer working in a terminal | Capture and close tasks without leaving the shell | TODO.txt edited by hand |

## Business goals

### BR-1 Capture tasks instantly
- **Success indicator:** adding a task takes one command and less than 1 s

### BR-2 Know what is open
- **Success indicator:** listing open tasks shows them in creation order in one command

## Product idea
- **Full idea:** add, list, complete and delete tasks; due dates; export to Markdown.
- **First release (MVP) candidate:** add, list and complete tasks, stored in a local file.

## Constraints
- Python 3.10+, no external service, works offline on Linux, macOS and Windows.

## Out of scope
- Synchronisation between machines, multiple users.

## Risks
- Data loss if the storage file is corrupted.

## Assumptions and open questions
ASM-1

## Changelog
| Version | Date | CR | Change |
|---|---|---|---|
| 0.1 | 2026-11-26 | — | First draft |
