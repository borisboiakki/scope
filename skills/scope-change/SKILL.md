---
name: scope-change
description: Manages change requests (CRs) in a SCOPE project. Writes the CR as ADDED/MODIFIED/REMOVED deltas with an impact analysis, gets the human's decision, applies it to the approved documents with version bumps, and sends the affected stories back to rework. Also handles the quick track for defects and small changes, moves of requirements between releases, and invalidated assumptions. Use when an approved brief, spec, architecture, ADR, roadmap, epic or story must change, when a defect is reported, when scope moves between releases, or when a build stopped with B3 or B4.
---

# SCOPE — change requests

`scope.py` means `python3 .scope/scope.py` (Windows: `python`). Work from the project root.
Template: `references/cr.md`.

## Rules

- Approved content changes **only** through an approved CR, then `scope.py reopen`.
- Approvals (`approve CR-n`, re-approvals) are recorded only when the human asks for them in this
  conversation: `scope.py approve <target> --by "human via <tool>"`.
- Keep IDs stable: never renumber. A removed requirement keeps its heading with the suffix
  `(removed by CR-n)` and no criteria are deleted from a story that was already built: the story is
  reworked instead.
- Assumptions and open questions: `scope.py register add …` with `--raised CR-n`.

## 1. Propose

1. `scope.py status`. Identify the trigger: human request, defect, review finding, blocker B3/B4,
   invalidated assumption (`scope.py register` shows it), release-scope move.
2. `scope.py impact <ids>` for every id concerned; read only the affected requirement or ADR texts
   (`scope.py extract <ids>`).
3. Choose the track:
   - **Quick**: a defect or small change that keeps every approved document as it is (it only adds
     one story implementing existing criteria). Otherwise **normal**.
4. Write `docs/scope/changes/CR-n-<slug>.md` from `references/cr.md` (id: `scope.py next-id CR`):
   - reason with its source; `change_type`; `affects:` all impacted ids;
   - the change as **ADDED / MODIFIED / REMOVED** items with the full new text (new ids from
     `scope.py next-id`, criteria in Given/When/Then);
   - impact: paste the short `scope.py impact` output and list the artifacts to reopen with their new
     version (`minor` → x.y+1 for wording or small behaviour, `major` → x+1.0 for behaviour,
     architecture or plan changes) and the stories going to rework;
   - `class: minor|major`, `quick: true|false`.
5. Quick track only: also write the story `docs/scope/stories/ST-n-<slug>.md` (from the plan skill's
   story template, or by copying an existing story's structure) with `cr: CR-n`, the epic it belongs to,
   `implements:` the existing criteria it restores, `status: draft`.
6. `scope.py check` (references to ids the CR adds are only warnings), then
   `scope.py git phase-artifact CR-n`.
7. Present the CR in a few lines (what, why, impact, class) and ask the human to approve or reject it.
   Rejected: `scope.py cr reject CR-n`, done.

## 2. Apply (after "approve CR-n")

1. `scope.py approve CR-n --by "human via <tool>"`. A quick CR also makes its story `ready`: build it with
   skill `scope-build`; the CR has nothing to reopen, so close it at once with `scope.py cr close CR-n`.
2. For each artifact to change: `scope.py reopen <brief|spec|architecture|roadmap|epics|ADR-n|ST-n> --cr CR-n`.
3. Apply exactly the deltas of the CR, nothing more:
   - documents: edit the text, bump `version:` as planned, add a changelog row
     `| <version> | <date> | CR-n | <change> |`;
   - release moves: update the requirement's `Release` field in the spec and the roadmap's In scope /
     Out of scope lists;
   - stories: update their definition (criteria, context); new stories go into `epics.md` (reopened)
     in build order.
4. `scope.py check`. Fix errors. The remaining errors must only be "approval needed" ones.
5. Ask the human to re-approve each reopened item, in gate order: brief, spec, architecture (and ADRs),
   then `plan R<n>` for roadmap, epics and stories. Record each with `scope.py approve …`.
6. `scope.py cr close CR-n` (refused while something is still reopened).
7. If the CR came from a blocker, tell the human the story can be resumed (skill `scope-build`,
   after `scope.py story unblock ST-n` when it is still blocked).

## Summary format

```
CR-n <title>: <proposed | approved | applied | rejected> (<minor|major>, <quick|normal>)
Impact: <artifacts and versions; stories to rework; release moves>
Next: <"approve CR-n" | re-approve <targets> | build ST-n>
```
