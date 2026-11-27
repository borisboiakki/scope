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

## Getting started

Requirements: Python 3.10+, git, Claude Code or opencode (1.18.29+ or 2.x).

```bash
git clone https://github.com/borisboiakki/scope.git
cd my-project && git init            # if it is not a git repository yet
python3 ../scope/install.py . --setup
```

`install.py` copies the six skills to `.claude/skills/` (read by both tools), the reviewer agent to
`.claude/agents/` and `.opencode/agents/`, and the tool to `.scope/`; `--setup` creates `.scope/.venv`
with PyYAML. It never touches `docs/scope/`, so running it again upgrades SCOPE safely
(`--uninstall` removes it, `--opencode-format v2` writes the opencode 2.x native agent format).

**Global install** (once for all your projects):

```bash
python3 scope/install.py --global --setup
```

Skills go to `~/.claude/skills/` (Claude Code; opencode reads it too), the reviewer to `~/.claude/agents/`
and `~/.config/opencode/agents/`, the tool to `~/.scope/`; the skills call the tool by its full path.
Any folder can be chosen instead: `--skills-dir`, `--claude-agents-dir`, `--opencode-agents-dir`,
`--tool-dir` (the installer warns when a tool would not search the chosen skills folder). Each project
still gets its own `docs/scope/` when you say "set up SCOPE" in it. Upgrading a global install
changes SCOPE for every project; `doctor` notes when a project was set up with another version.

Then, in Claude Code or opencode, in the project:

| You say | Skill | What happens |
|---|---|---|
| "set up SCOPE" | `scope` | checks the environment, asks git policy, build mode, test command; creates `docs/scope/` |
| "write the brief" → "approve brief" | `scope-spec` | brief with goals and MVP; you approve it |
| "write the spec" → "approve spec" | `scope-spec` | requirements with release, criteria, sources |
| "design the architecture" → "approve architecture" | `scope-arch` | arc42/C4 + ADRs, project rules in `AGENTS.md` |
| "plan R1" → "approve plan R1" | `scope-plan` | roadmap, epics, self-contained stories |
| "launch EP-1 in autonomous mode" | `scope` | starts the epic (or supervised: you approve each story) |
| "build EP-1" | `scope-build` | implements, reviews (subagent), commits per policy; stops on blockers |
| "change FR-3 …", "there is a bug …" | `scope-change` | change request with impact; you approve; applied and re-approved |
| "status", "what's next" | `scope` | progress, blockers, open questions, next step |
| "close R1" | `scope` | release notes, carry-over, planning of R2 |

In Claude Code you can also call a skill directly (`/scope-plan`), in opencode with `@scope-plan`.

## Status

Work in progress (pre-release). Verified with Claude Code 2.1.332; opencode support is documented but
not yet tried on a real installation (see `docs/compatibility.md`).

| Milestone | Content | Status |
|---|---|---|
| M0 | Method (`METHOD.md`), compatibility research, authoring guide | done |
| M1 | Artifact templates, formats (`docs/artifacts.md`) | done |
| M2 | Tool `scope.py` + tests, CI | done |
| M3 | Skills `scope`, `scope-spec`, `scope-arch`, `scope-plan`; example project | done |
| M4 | `scope-build`, `scope-reviewer` agent, `scope-change` | done |
| M5 | Installer (`install.py`), getting started, real Claude Code check | done |
| M6 | Pilot on opencode ([docs/pilot.md](docs/pilot.md)), v0.1.0 | in progress |

## Example

[examples/todo-cli](examples/todo-cli) — a small project taken from brief to approved plan of its MVP.

## Documents

- [METHOD.md](METHOD.md) — the method (normative)
- [docs/authoring.md](docs/authoring.md) — how skills, agents and templates are written
- [docs/compatibility.md](docs/compatibility.md) — Claude Code / opencode installation details
- [docs/artifacts.md](docs/artifacts.md) — artifact formats parsed by the tool
- [docs/tool.md](docs/tool.md) — `scope.py` command reference
- [docs/decisions.md](docs/decisions.md) — design decisions
