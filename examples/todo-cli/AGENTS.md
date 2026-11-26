# Project rules

<!-- scope:begin -->
## SCOPE workflow

This project is developed with SCOPE (spec-driven workflow). Artifacts are in `docs/scope/`,
configuration in `docs/scope/config.yaml`, state in `docs/scope/state.yaml` (managed by the tool).

- Start every session with the `scope` skill (`status`) to know the phase and the next step.
- Approved artifacts change only through a change request (`scope-change`).
- Approvals are recorded only when the human asks for them in this conversation.
- Log every assumption and open question in `docs/scope/register.md`.
- Run the tool with `python3 .scope/scope.py <command>`; run `check` before ending a step.

## Project rules
- **Stack:** Python 3.10+, standard library only (ADR-1, ADR-2); package `todo/`.
- **Coding conventions:** PEP 8, type hints on public functions, `ruff check .` clean.
- **Testing:** pytest; every acceptance criterion has a test named after it (`test_fr_1_1_…`).
- **Security:** never execute user input; the task file path comes only from `TODO_FILE` or the default.
- **Do not:** add dependencies without an ADR; print stack traces to the user.
<!-- scope:end -->
