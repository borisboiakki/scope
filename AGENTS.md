# Working on the SCOPE repository

This repository defines SCOPE, a spec-driven workflow for AI coding agents (see `README.md`).

## Read first

- `METHOD.md` is normative. Skills, templates and the tool implement it; if they disagree, fix them or
  propose a change to `METHOD.md` (and log it in `docs/decisions.md`).
- `docs/authoring.md` before writing or editing a skill, agent profile or template.
- `docs/compatibility.md` before touching installation paths or front matter.
- Supported targets: Claude Code and opencode 1.x (from 1.18.29) and 2.x.

## Rules

- Everything must work in **Claude Code and opencode**: no tool-specific syntax in skill bodies.
- Respect the size limits: `SKILL.md` ≤ 150 lines, templates/checklists ≤ 60 lines.
- Mechanical checks belong in `tool/scope.py`, with pytest tests, not in skill prose.
- Python ≥ 3.9 (tested in CI), standard library + PyYAML only for the tool (pytest for development).
- Record every design decision in `docs/decisions.md`; never present an unverified tool behaviour as
  fact (mark it "to verify" in `docs/compatibility.md`).
- Commits: Conventional Commits (`feat(tool): …`, `docs(method): …`). Bump `VERSION` (semver) and
  `CHANGELOG.md` for every change meant for a release.
