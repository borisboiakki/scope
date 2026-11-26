# Design decisions

Decision log of the SCOPE method itself. Newest last. Each entry: decision, reason, source.

| ID | Date | Decision | Reason / source |
|---|---|---|---|
| D-001 | 2026-11-26 | Name **SCOPE** (Simple, Controlled, Orchestrated Process for Engineering). | Chosen by the owner. |
| D-002 | 2026-11-26 | Six skills (`scope`, `scope-spec`, `scope-arch`, `scope-plan`, `scope-build`, `scope-change`), one agent (`scope-reviewer`), one Python tool. No personas. | Lighter than persona-based methods; one skill per phase keeps the loaded context small. |
| D-003 | 2026-11-26 | Approvals are **triggered by the human** and **recorded by the agent** through the tool (with content hash). | Owner. |
| D-004 | 2026-11-26 | Human gates: brief, spec, architecture, plan (epics + stories), epic launch; story approval in supervised mode; CRs; release close. | Owner (brief→plan and epic launch); CR and release close added for consistency. |
| D-005 | 2026-11-26 | Two build modes: supervised (story by story) and autonomous (whole epic). In autonomous mode two review cycles are mandatory; any blocking problem stops the run. | Owner. |
| D-006 | 2026-11-26 | Supervised mode: 1 to 2 review cycles, then hand-over to the human. | Proposed default, to be confirmed in the pilot. |
| D-007 | 2026-11-26 | Git policy asked at init (presets Story / Fine / Human / Off), changeable at any time. | Owner. |
| D-008 | 2026-11-26 | Tool in Python ≥ 3.10 with PyYAML only, in a project venv; setup guided by the agent. | Owner (Python, few libraries). |
| D-009 | 2026-11-26 | Requirements carry a target release; roadmap states in/out of scope per release; `remaining` report; release close moves leftovers explicitly. | Owner: incremental releases must be clear, remaining work tracked. |
| D-010 | 2026-11-26 | One register for assumptions (`ASM`) and open questions (`OQ`), maintained by every skill, shown at every gate. | Owner: hypotheses and open points must be logged throughout. |
| D-011 | 2026-11-26 | Skills installed once in `.claude/skills/` (read by both tools); reviewer rendered for both tools; `AGENTS.md` + `CLAUDE.md` importing it. | opencode V2 docs, see `compatibility.md`. |
| D-012 | 2026-11-26 | Templates use established light frameworks: EARS, ISO 29148 quality criteria, arc42 + C4, MADR, INVEST, Given/When/Then, Conventional Commits. | Owner: use common best practices; see `authoring.md`. |
| D-013 | 2026-11-26 | No comparison run against BMAD. | Owner. |
| D-014 | 2026-11-26 | Support opencode 1.x from **1.18.29** (owner's version) and 2.x: skills in `.claude/skills/` (read by both); opencode reviewer written in the 1.x agent format, which 2.x still reads. | opencode docs at tag v1.18.29 and 2.x, see `compatibility.md`. |
| D-015 | 2026-11-26 | License: **MIT**. | Owner. |
| D-016 | 2026-11-26 | Each template lives in the `references/` folder of the skill that writes it; the files `scope.py init` creates (config, state, register, AGENTS section) live in `tool/templates/`. Formats the tool parses are fixed in `docs/artifacts.md`. | Progressive disclosure: a skill loads only its own templates. |
| D-017 | 2026-11-26 | Test and lint commands are stored in `config.yaml` (`project.test_command`, `project.lint_command`) so build and review run them without guessing. | Needed by the build loop and the reviewer. |
| D-018 | 2026-11-26 | The approval hash ignores status values; story status lives only in the story file (no status column in the epics table). | Statuses change during the build; everything else is frozen. |
| D-019 | 2026-11-26 | A CR can be approved while the check reports drift (E15/E16): the CR is how drift is resolved. Other errors still block it. | Otherwise an unapproved edit could never be regularised. |
| D-020 | 2026-11-26 | The tool creates branches and commits per policy; it never merges or pushes, it prints what the policy asks. | Merges and pushes are outward-facing; the agent asks the human. |
| D-021 | 2026-11-26 | Closing a release reopens roadmap and epics (logged) so the next release can be planned without a CR; unfinished work moves only with `--carry` and a reason. | Incremental releases without paperwork for normal planning. |
| D-022 | 2026-11-26 | Quick-track stories carry `cr: CR-n` and are not listed in epics.md. | Avoids reopening the approved plan for a small fix. |
| D-023 | 2026-11-26 | `scope.py` re-runs itself with `.scope/.venv` when PyYAML is missing, so skills always call `python3 .scope/scope.py`. | One command line in all skills and tools. |
| D-024 | 2026-11-26 | Release ids (R1, R2…) are not reported as undefined until the roadmap exists. | The spec assigns releases before the plan defines them (found in the M3 dry run). |
| D-025 | 2026-11-26 | Plan coverage is checked per acceptance criterion; a story implementing `FR-n` covers all its criteria. | The plan skill promises every criterion is covered; the tool now enforces it. |
| D-026 | 2026-11-26 | `epics.md` is versioned (1.0 at first approval, bump after a release close) like the roadmap. | Consistent versioning of approved planning documents. |
| D-027 | 2026-11-26 | Skills reference the tool as `scope.py` defined once at their top, and must use the IDs the tool prints. | Short skills; the dry run showed invented IDs break references. |
| D-028 | 2026-11-26 | The reviewer is one neutral source file (`agents/scope-reviewer.md`, front matter `name` + `description`); the installer renders it per tool. It never edits; it may run tests, lint and read-only git and `scope.py` commands. | Single source, least privilege. |
| D-029 | 2026-11-26 | Autonomous mode: cycle 1 findings are always fixed before the mandatory cycle 2, even after a PASS. | Two real review passes, not a repeated verdict. |
| D-030 | 2026-11-26 | A blocker whose answer changes an approved document is resolved through a CR; reopening the blocked story for that CR closes the blocker. | Found in the M4 dry run: the blocked story could not otherwise be reworked. |
| D-031 | 2026-11-26 | Quick track = one new story on existing criteria, no approved document changes; the CR is closed right after its approval; a done epic is relaunched in its previous mode. | Keeps the quick track quick and consistent with the reopen rule. |
| D-032 | 2026-11-26 | The story's implementation record starts with the base commit, which the reviewer diffs against. | The reviewer sees exactly the story's changes, committed or not. |
| D-033 | 2026-11-26 | `install.py` (standard library) copies skills, renders the reviewer for each tool and copies the tool to `.scope/`; it never touches `docs/scope/`, `AGENTS.md` or `CLAUDE.md` (created by `scope.py init` through skill `scope`). opencode agent in 1.x format by default, `--opencode-format v2` optional. | One command to install or upgrade; project data stays under the project's control. |
| D-034 | 2026-11-26 | The approval hash ignores checkbox ticks; the build skill ticks the story's tasks. | Found by the real reviewer run: unticked tasks on a done story, and ticking them would have counted as drift. |
