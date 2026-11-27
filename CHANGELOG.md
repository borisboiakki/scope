# Changelog

## 0.1.0 — 2026-11-27

First release: method, templates, tool, six skills, reviewer agent, installer.
Pilot on opencode 1.18.29 passed (token use roughly 70 % lower than comparable BMAD runs).


- Method definition (`METHOD.md`), authoring guide, compatibility notes for Claude Code and opencode V2,
  design decision log.
- Compatibility with opencode 1.x (from 1.18.29) and 2.x; MIT license.
- Artifact templates (brief, spec, architecture, ADR, roadmap, epics, story, CR) and init templates
  (config, state, register, AGENTS section); artifact formats in `docs/artifacts.md`.
- Tool `scope.py` (setup, doctor, init, status, check, approvals with content hashes, CRs, story
  transitions with review-cycle and stop rules, release close with carry-over, register, trace,
  remaining, impact, extract, next-id, config, git policy) with pytest suite and CI.
- Skills `scope` (init, status, approvals, config), `scope-spec`, `scope-arch`, `scope-plan`; skill
  authoring checks in the test suite; example project `examples/todo-cli` up to the R1 plan approval.
- Tool: release ids allowed before the roadmap exists; coverage checked per acceptance criterion;
  `epics.md` versioned like the other planning documents.
- Skills `scope-build` (supervised and autonomous build, review cycles, stop rules B1–B7, git events)
  and `scope-change` (normal and quick change requests, apply and re-approve); reviewer agent source
  `agents/scope-reviewer.md` (read-only, fixed verdict format).
- Tool: reworked stories can restart in a done epic; quick stories relaunch a done epic; reopening a
  blocked story for a CR resolves the blocker; clearer messages.
- Installer `install.py` (install, upgrade keeping `.scope/.venv` and `docs/scope/`, uninstall, opencode
  v1/v2 agent formats, optional setup); getting started guide in the README.
- Verified with Claude Code 2.1.332: skills and reviewer agent discovered; reviewer subagent run read-only.
- Tool: ticking a story's task checkboxes is not a change of its approved definition.
- Installer: `--global` (skills in `~/.claude/skills`, agents in `~/.claude/agents` and
  `~/.config/opencode/agents`, tool in `~/.scope`) and custom folders (`--skills-dir`,
  `--claude-agents-dir`, `--opencode-agents-dir`, `--tool-dir`); the tool path is written into skills,
  agents and `AGENTS.md` when the tool is outside the project; `doctor` finds global and custom installs
  and notes a version mismatch.
- Python 3.9 supported (installer and tool); clearer installer usage message.
