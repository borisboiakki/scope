---
id: CR-<n>
type: cr
status: proposed
change_type: <requirement|architecture|defect|scope|release-scope>
class: <minor|major>
quick: <true|false>
affects: [<FR-n>, <ADR-n>, <ST-n>, <R-n>]
date: <YYYY-MM-DD>
---

# CR-<n> <title>

## Reason
<why the change is needed; source: human request, review finding, invalidated ASM-n, defect…>

## Change
<!-- Write the change as deltas on the approved artifacts. Quote IDs; give the new text in full. -->

### ADDED
- <artifact>: <new ID and full text>

### MODIFIED
- <artifact> <ID>: <old text> → <new text>

### REMOVED
- <artifact> <ID>: <reason>

## Impact
<!-- Paste the short output of scope.py impact; then judge it. -->
- **Artifacts to reopen:** <spec v1.2 → v1.3, …>
- **Stories:** <ST-n → needs-rework; new stories to create>
- **Releases:** <moves between releases, if any>
- **Classification:** <minor: wording, no story impact | major: behaviour, architecture or plan change>

## Decision
- **Human decision:** <approved / rejected>, <date>, <comment>

## Applied
| Artifact | From version | To version |
|---|---|---|
| <spec> | <1.2> | <1.3> |
