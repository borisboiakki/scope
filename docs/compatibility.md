# Compatibility: Claude Code and opencode

How SCOPE is installed so that both tools load the same skills, rules and reviewer agent.

**Supported targets:** Claude Code (current) and opencode **1.x from 1.18.29** (the owner's version) and **2.x**.

## Sources

- **opencode 1.18.29**: documentation at tag `v1.18.29` of the opencode source repository
  (`packages/web/src/content/docs/skills.mdx`, `agents.mdx`, `rules.mdx`), read on 2026-11-26.
- **opencode 2.x**: documentation in the same repository at commit `44344bd`
  (`services/site/src/docs/content/skills.mdx`, `agents.mdx`, `instructions.mdx`, `tools.mdx`,
  `migrate-v1.mdx`), read on 2026-11-26.
- **Claude Code**: skills in `.claude/skills/<name>/SKILL.md`, subagents in `.claude/agents/<name>.md`
  (front matter `name`, `description`, `tools`), `CLAUDE.md` with `@file` imports.

## Findings

| Topic | opencode 1.18.29 | opencode 2.x | Consequence for SCOPE |
|---|---|---|---|
| Skill locations | `.opencode/skills/`, `.claude/skills/`, `.agents/skills/` (project, walking up to the git worktree) and the global equivalents | Same sources | Install skills **once** in `.claude/skills/`. The target project should be a git repository. |
| Skill front matter | `name` (required, = folder name, `^[a-z0-9]+(-[a-z0-9]+)*$`, 1–64 chars), `description` (required, 1–1024 chars); `license`, `compatibility`, `metadata` optional; other fields ignored | `name` is a display label, ID from the path; `description` needed to be advertised | Use `name` = folder name and a `description` ≤ 1024 chars: valid in both, and in Claude Code. |
| Skill loading | `skill` tool (`skill({ name: "scope-plan" })`) | `skill` tool with the ID; user can write `@scope-plan` | Progressive disclosure works as in Claude Code. |
| Disabling switch | `OPENCODE_DISABLE_CLAUDE_CODE=1` or `OPENCODE_DISABLE_CLAUDE_CODE_SKILLS=1` turn off `.claude/skills` | `OPENCODE_DISABLE_CLAUDE_CODE=1` | `scope doctor` warns when these are set. |
| Project rules | `AGENTS.md`; `CLAUDE.md` only if no `AGENTS.md` | Same | `AGENTS.md` holds the rules; `CLAUDE.md` contains `@AGENTS.md` for Claude Code. |
| Agent files | `.opencode/agents/<name>.md`; front matter `description`, `mode: subagent`, `model`, `permission:` map (`edit`, `bash`, `task`, `webfetch`… → `allow` / `ask` / `deny`) | `.opencode/agents/`; native front matter uses a `permissions` list, but **V1 files are still read and translated** | Write the opencode reviewer in the **1.x format**: it works in both. A 2.x-native format can be an installer option later. |
| `.claude/agents/` | Not read | Not read | The reviewer is written twice: Claude Code and opencode format. |
| Subagent call | The primary agent calls it with the task tool, or the user `@`-mentions it; it runs in a child session | Child session, always in the background; the parent gets a report when the child is idle | The build skill asks for the reviewer by name and waits for its report before continuing. The reviewer launches no subagent. |

## Reviewer front matter (planned)

Claude Code (`.claude/agents/scope-reviewer.md`):

```yaml
name: scope-reviewer
description: <what it does and when to use it>
tools: Read, Grep, Glob, Bash
```

opencode 1.x format, also read by 2.x (`.opencode/agents/scope-reviewer.md`):

```yaml
description: <what it does and when to use it>
mode: subagent
permission:
  edit: deny
  task: deny
  webfetch: deny
```

No model is pinned: the reviewer uses the session's model.

## Still to verify on a real installation (opencode 1.18.29 and Claude Code)

- Skills in `.claude/skills/` appear in opencode and load on request.
- The build skill can launch `scope-reviewer` in both tools and receives its report.
- The reviewer cannot edit files in either tool.
- The tool's Python environment (`.scope/.venv`) runs from both tools' shell on Linux, macOS and Windows.
