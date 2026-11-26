<!-- scope:begin -->
## SCOPE workflow

This project is developed with SCOPE (spec-driven workflow). Artifacts are in `docs/scope/`,
configuration in `docs/scope/config.yaml`, state in `docs/scope/state.yaml` (managed by the tool).

- Start every session with the `scope` skill (`status`) to know the phase and the next step.
- Approved artifacts change only through a change request (`scope-change`).
- Approvals are recorded only when the human asks for them in this conversation.
- Log every assumption and open question in `docs/scope/register.md`.
- Run the tool with `<python> .scope/scope.py <command>`; run `check` before ending a step.

## Project rules
<!-- The project's constitution: rules every step and the reviewer apply. Keep it short. -->
- **Stack:** <languages, frameworks, versions>
- **Coding conventions:** <style, naming, structure>
- **Testing:** <what must be tested, how; command in config.yaml>
- **Security:** <secrets handling, input validation, dependencies policy>
- **Do not:** <forbidden practices>
<!-- scope:end -->
