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
