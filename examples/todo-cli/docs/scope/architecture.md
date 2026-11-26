---
id: architecture
type: architecture
version: 1.0
status: approved
---

# Architecture — todo-cli

## 1. Goals and constraints
| Driver | Source |
|---|---|
| Any command under 1 s with 1000 tasks | NFR-1 |
| No data loss on a failed write | NFR-2 |
| Python 3.10+, offline, Linux/macOS/Windows | brief constraint |

## 2. Context (C4 level 1: users and external systems)
```mermaid
flowchart LR
  dev[Developer] -->|todo add/list/done| cli[todo-cli]
  cli --> file[(tasks.json)]
```

## 3. Solution strategy
- Single Python package, standard library only — ADR-2
- Storage in one JSON file replaced atomically — ADR-1 [ASM-1]

## 4. Building blocks (C4 level 2)
| Container / module | Responsibility | Technology | Implements |
|---|---|---|---|
| `todo/cli.py` | Parse arguments, print results and errors | argparse | FR-1, FR-2, FR-3 |
| `todo/store.py` | Load and save tasks atomically | json, os.replace | FR-1, FR-3, NFR-1, NFR-2 |
| `todo/tasks.py` | Task model and rules (numbering, states) | dataclasses | FR-1, FR-2, FR-3 |

## 5. Runtime scenarios
- **Add a task** (FR-1): cli parses → store loads → tasks adds with next number → store writes temp file and renames → cli prints the number.

## 6. Deployment and environments
Installed with `pip install .`; entry point `todo`. File in `~/.todo/tasks.json` (override with `TODO_FILE`).

## 7. Cross-cutting concepts
- **Data:** JSON list of tasks; numbers never reused.
- **Errors and logging:** user errors print one line on stderr and exit code 1; no logging.
- **Security:** no input is executed; the file path comes only from the environment.
- **Testing strategy:** pytest unit tests per module, CLI tests through `main(argv)`, a timing test for NFR-1; `pytest -q`.
- **Coding conventions:** see AGENTS.md project rules.

## 8. Decisions
| ADR | Title | Status |
|---|---|---|
| ADR-1 | Store tasks in one JSON file with atomic replace | draft |
| ADR-2 | Command-line interface with argparse | draft |

## 9. Risks, technical debt, assumptions
- Concurrent runs may lose an update (accepted in ADR-1).
- Register items: ASM-1

## Changelog
| Version | Date | CR | Change |
|---|---|---|---|
| 0.1 | 2026-11-26 | — | First draft |
