# Artifact formats

Conventions shared by the templates (written by the skills) and `scope.py` (which parses them).
`METHOD.md` defines what the artifacts are; this file defines how they are written.

## Where the templates live

| Template | File | Written by |
|---|---|---|
| brief, spec | `skills/scope-spec/references/` | `scope-spec` |
| architecture, ADR | `skills/scope-arch/references/` | `scope-arch` |
| roadmap, epics, story | `skills/scope-plan/references/` | `scope-plan` |
| change request | `skills/scope-change/references/` | `scope-change` |
| config, state, register, AGENTS section | `tool/templates/` | `scope.py init` |

## General rules

- Markdown with YAML front matter. Common fields: `id`, `type`, `version` (`major.minor`, starting at
  `0.1` while draft, `1.0` at first approval), `status`.
- Approval data (who, when, hash) is stored in `docs/scope/state.yaml`, never in the artifact.
- The approval hash ignores status values (the front matter `status:` line and `- **Status:**` lines), which
  change during the lifecycle; any other change to approved content is detected by `scope.py check`.
- `<angle brackets>` are placeholders. `<!-- comments -->` are guidance for the agent: it follows them
  and **removes them** from the written artifact.
- IDs are written plainly (`FR-4.2`, `ASM-7`); the tool finds them with the patterns below.
- Lists of IDs in front matter are YAML lists: `implements: [FR-1.1, FR-1.2]`.
- Every versioned artifact (brief, spec, architecture, roadmap) ends with a `## Changelog` table:
  `| Version | Date | CR | Change |`.

## Parsed structures

| Item | Pattern the tool reads |
|---|---|
| Business goal | Heading `### BR-<n> <title>` in brief.md |
| Requirement | Heading `### FR-<n> <title>` or `### NFR-<n> <title>` in spec.md, followed by field lines `- **Release:** R1` and `- **Source:** BR-1` |
| Acceptance criterion | List item starting `- **FR-<n>.<m>**` under its requirement |
| Removed requirement | Heading keeps its ID, title suffixed ` (removed by CR-<n>)` |
| ADR | File `adr/ADR-<n>-<slug>.md`, front matter `id: ADR-<n>` |
| Release | Heading `## R<n> — <name>` in roadmap.md with field lines (`Status`, `Goal`, `In scope`, `Out of scope`, `Exit criteria`) |
| Epic | Heading `## EP-<n> <title>` in epics.md with field lines (`Release`, `Status`, `Goal`) and a stories table |
| Story | File `stories/ST-<n>-<slug>.md`, front matter (`id`, `epic`, `release`, `status`, `size`, `implements`, `adrs`, `depends_on`; `cr: CR-n` for a quick-track story, which is then not listed in epics.md) |
| Story definition | Everything above the heading `## Implementation record` (hashed at plan approval) |
| CR | File `changes/CR-<n>-<slug>.md`, front matter (`id`, `type: cr`, `change_type`, `class`, `quick`, `status`, `affects`, `date`) |
| Register item | Row of the table in register.md whose first cell is `ASM-<n>` or `OQ-<n>` |

## Statuses (values the tool accepts)

| Item | Values |
|---|---|
| brief, spec, architecture, roadmap, ADR | `draft`, `approved`, `superseded` |
| release | `planned`, `active`, `released` |
| epic | `planned`, `ready`, `launched`, `done`, `blocked` |
| story | `draft`, `ready`, `in-progress`, `in-review`, `done`, `blocked`, `needs-rework`, `removed` |
| CR | `proposed`, `approved`, `applied`, `rejected` |
| register item | `open`, `validated`, `invalidated`, `answered`, `closed` |
