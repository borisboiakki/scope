# SCOPE

**S**imple, **C**ontrolled, **O**rchestrated **P**rocess for **E**ngineering — a light, spec-driven
development workflow for AI coding agents. Works with **Claude Code** and **opencode** (1.18.29+ and 2.x).
License: MIT.

```
brief ─G1─▶ spec ─G2─▶ architecture ─G3─▶ plan (releases, epics, stories) ─G4─▶ launch epic ─G5─▶ build + review ─▶ release
                         ▲                                                                             │
                         └──────────────────── change requests (CR) ◀──────────────────────────────────┘
```

- **Controlled**: human-approved gates, stable IDs, traceability, frozen approved artifacts, change requests.
- **Light**: six small skills, one reviewer agent, templates loaded on demand, mechanical checks in Python.
- **Incremental**: every requirement has a target release; remaining work is reported, never implicit.
- **Explicit**: assumptions and open questions are logged in one register through the whole process.
- **Safe autonomy**: build a whole epic autonomously with two mandatory review cycles per story, stopping on any blocker.

## Status

Work in progress — not usable yet.

| Milestone | Content | Status |
|---|---|---|
| M0 | Method (`METHOD.md`), compatibility research, authoring guide | done |
| M1 | Artifact templates, formats (`docs/artifacts.md`) | done |
| M2 | Tool `scope.py` + tests, CI | done |
| M3 | Skills `scope`, `scope-spec`, `scope-arch`, `scope-plan` | planned |
| M4 | `scope-build`, `scope-reviewer`, `scope-change` | planned |
| M5 | Installer, CI, example project | planned |
| M6 | Pilot, v0.1.0 | planned |

## Documents

- [METHOD.md](METHOD.md) — the method (normative)
- [docs/authoring.md](docs/authoring.md) — how skills, agents and templates are written
- [docs/compatibility.md](docs/compatibility.md) — Claude Code / opencode installation details
- [docs/artifacts.md](docs/artifacts.md) — artifact formats parsed by the tool
- [docs/tool.md](docs/tool.md) — `scope.py` command reference
- [docs/decisions.md](docs/decisions.md) — design decisions
