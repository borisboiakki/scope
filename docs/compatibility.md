# Compatibility: Claude Code and opencode

How SCOPE is installed so that both tools load the same skills, rules and reviewer agent.

## Sources

- **opencode**: documentation in the opencode source repository (`services/site/src/docs/content/`
  `skills.mdx`, `agents.mdx`, `instructions.mdx`, `tools.mdx`, `migrate-v1.mdx`), read on 2026-11-26
  (commit `44344bd`). These pages describe opencode **V2**.
- **Claude Code**: skills in `.claude/skills/<name>/SKILL.md`, subagents in `.claude/agents/<name>.md`
  (front matter `name`, `description`, `tools`), `CLAUDE.md` with `@file` imports.

## Findings (opencode V2)

| Topic | Finding | Consequence for SCOPE |
|---|---|---|
| Skill discovery | Project sources: `.opencode/skills`, plus compatibility sources `.claude/skills` and `.agents/skills`, from the current directory up to the project root. | Install skills **once** in `.claude/skills/`; both tools find them. |
| Skill ID | Derived from the path (`<source>/<id>/SKILL.md`); `name` is only a display label. Portable IDs: lowercase kebab-case, 1–64 chars. | Folder name = `name` = ID, e.g. `scope-plan`. |
| Skill front matter | `name`, `description` (skills without description are not advertised), `disable-model-invocation`, `metadata.opencode/autoinvoke`. | Use only `name` and `description`. |
| Skill loading | The model calls the `skill` tool with the ID; the user can write `@skill-id`. Supporting files are not loaded automatically; the skill must say when to read them. | Progressive disclosure works as in Claude Code. |
| Instructions | `AGENTS.md` is read; `CLAUDE.md` only in a directory that has no `AGENTS.md`. | `AGENTS.md` holds the rules; `CLAUDE.md` contains `@AGENTS.md` for Claude Code. |
| Agents | Markdown files in `.opencode/agents/<name>.md` (V1 folders `agent/`, `mode/`… still read). Front matter `description`, `mode: subagent`, `model` (`provider/model#variant`), `permissions` (ordered list of `action` / `resource` / `effect`, last match wins). `.claude/agents/` is **not** listed as a source. | The installer writes the reviewer twice: Claude Code format and opencode V2 format. |
| V1 vs V2 agent files | A file using `permissions`, `request`, `system` or `disabled` is read as V2; V1 fields (`tools`, `permission`…) in it are ignored. V1 files are still translated. | Generate pure V2 front matter. If an older opencode must be supported, the installer can emit V1 instead (option, later). |
| Subagents | Run in a child session with fresh context, **always in the background**; the parent gets a report when the child goes idle. Default nesting depth 1. | The build skill launches the reviewer and waits for its report before continuing. The reviewer launches no subagents. |

## Reviewer front matter (planned)

Claude Code (`.claude/agents/scope-reviewer.md`):

```yaml
name: scope-reviewer
description: <when to use>
tools: Read, Grep, Glob, Bash
```

opencode V2 (`.opencode/agents/scope-reviewer.md`):

```yaml
description: <when to use>
mode: subagent
permissions:
  - { action: edit, resource: "*", effect: deny }
  - { action: subagent, resource: "*", effect: deny }
```

## Still to verify on a real installation

- Skills in `.claude/skills/` appear in opencode and load with `@scope-plan`.
- The reviewer subagent can be launched from a skill in both tools, and the opencode background report
  reaches the build skill.
- Running `.scope/.venv` Python from both tools' shell tool on Linux, macOS and Windows.
