# Example: todo-cli

A small SCOPE project taken through the first phases with the SCOPE skills, up to the approval of
the plan of release R1 (MVP). No code has been written yet: the next step is `approve launch EP-1`.

| Artifact | Content |
|---|---|
| `docs/scope/brief.md` | Problem, two business goals, MVP vs full idea |
| `docs/scope/spec.md` | FR-1..FR-5 and NFR-1..NFR-2, EARS statements, criteria, releases R1 / R2 / later |
| `docs/scope/architecture.md`, `adr/` | arc42/C4 essentials, ADR-1 storage, ADR-2 CLI |
| `docs/scope/roadmap.md` | R1 MVP, R2 housekeeping, Later |
| `docs/scope/epics.md`, `stories/` | EP-1 and EP-2, stories ST-1..ST-5 in build order |
| `docs/scope/register.md` | ASM-1 |
| `docs/scope/state.yaml` | approvals with hashes (written by the tool) |
| `docs/scope/reports/` | trace and remaining-work reports (generated) |

In this repository the tool is run as `python3 tool/scope.py --root examples/todo-cli <command>`
(in a real project: `python3 .scope/scope.py <command>`). Try `status`, `check`, `impact NFR-1`,
`extract ST-2`.
