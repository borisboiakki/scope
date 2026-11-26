# Changelog

## 0.0.1 — unreleased

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
