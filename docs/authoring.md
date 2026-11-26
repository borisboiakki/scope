# Authoring guide for SCOPE skills, agents and templates

The rules every skill, agent profile and template of SCOPE follows. They come from established practices,
adapted to SCOPE's goal: low token cost with high rigor.

## 1. Skills

Based on the Agent Skills format (`SKILL.md` + optional `references/`, `scripts/`), shared by Claude Code
and opencode, and on Anthropic's published skill-authoring best practices.

| Rule | Why |
|---|---|
| Folder name = skill ID: lowercase kebab-case, ≤ 64 chars (`^[a-z0-9]+(-[a-z0-9]+)*$`); `name` in front matter equals it. | Same ID in both tools (opencode derives the ID from the path). |
| `description` in third person, ≤ 1024 chars, says **what** the skill does **and when** to use it, with the trigger words a user would say. | The description is the only text always in context; it decides when the skill loads. |
| `SKILL.md` body ≤ 150 lines (SCOPE limit; general guidance is < 500). | Token cost on every load. |
| **Progressive disclosure**: templates, checklists and long rules go to `references/`, one level deep, and the body says exactly when to read each. | Only what the current step needs is loaded. |
| Assume the model is capable: no explanations of general knowledge, only project-specific rules. | Conciseness. |
| Write steps as a numbered **workflow with a checklist**; end with a validation loop (run `scope.py check`, fix, re-run). | Rigor through feedback loops, not long prose. |
| Deterministic operations go to `scope.py`, never re-implemented in prose. | Reliable and token-free. |
| Set the degree of freedom on purpose: strict steps for gates, approvals, git and the build loop; free text for writing content. | Fragile operations need exact instructions. |
| One term per concept (use the glossary in METHOD.md: *story*, *gate*, *register*…). | Consistency. |
| No time-sensitive statements, no tool-specific syntax in bodies (no `$ARGUMENTS`, no Claude-only or opencode-only tool names); refer to "the reviewer subagent", "ask the human". | Portability across tools and versions. |
| Paths inside a skill are relative to the skill folder; paths to project files start at the project root. | Both tools resolve them the same way. |
| Every skill ends its step with the standard summary: files written, register changes, next command. | Cheap hand-over between steps and sessions. |

## 2. Agent profile (`scope-reviewer`)

Based on common subagent practices (Claude Code subagents, opencode agents):

- **Single responsibility**: review one story; never fix code.
- **Least privilege**: read, search and run tests only; no edit/write tools.
- **Fresh context, explicit input**: the caller passes the story path, the diff range and the extract
  file; the agent reads nothing else unless a finding needs it.
- **Fixed output format** (verdict, findings table) so the caller can parse it and write it into the story.
- **Description says when to use it**, so the main agent delegates correctly.
- One neutral source (`agents/scope-reviewer.md`), rendered by the installer into Claude Code and
  opencode front matter. No model is pinned: the agent inherits the session model.

## 3. Templates and the frameworks behind them

| Artifact | Framework used (light form) |
|---|---|
| Brief | Lean product brief: problem, users, goals (`BR`), success metrics, constraints, out of scope |
| Spec | Requirement quality criteria of ISO/IEC/IEEE 29148 (necessary, unambiguous, verifiable, singular); **EARS** patterns for functional requirements; measurable NFRs (ISO 25010 quality characteristics as a checklist) |
| Architecture | **arc42** sections reduced to the essentials, **C4** context and container views (text or Mermaid) |
| ADR | **MADR** (Markdown Any Decision Records), short form |
| Stories | **INVEST**; acceptance criteria in **Given / When / Then**; Definition of Ready and Definition of Done |
| Review | Severity-ranked findings (blocker / major / minor / nit), checklist derived from the story's acceptance criteria |
| Commits | **Conventional Commits**, with the SCOPE ID as the scope |
| Versions | **Semantic Versioning** for SCOPE itself; `major.minor` for artifacts |

## 4. Checks before committing a skill, agent or template

- Length limits respected (CI checks them).
- Front matter valid; skill name equals folder name.
- No tool-specific syntax in the body.
- The workflow runs end-to-end on `examples/` (`scope.py check` passes).
