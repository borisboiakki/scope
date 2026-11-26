---
name: scope-plan
description: Plans the releases of a SCOPE project (MVP first, then increments), then the epics and self-contained stories of the release being planned, with traceability to requirements and a clear record of what is out of scope and still remaining. Ends at the plan approval gate. Use when the user wants a roadmap, to split the work into epics and stories, to plan the MVP or the next release, or to see what remains to be done.
---

# SCOPE — release planning, epics and stories

`scope.py` means `python3 .scope/scope.py` (Windows: `python`). Work from the project root.
Templates: `references/roadmap.md`, `references/epics.md`, `references/story.md`.

## Rules

- Plan **one release at a time** in detail (epics with stories). Later releases keep their requirements
  and, at most, rough epics without stories.
- Every requirement of the spec sits in exactly one release's "In scope" or in "Later". Whatever a
  release does not do is written in its "Out of scope" with the target release and a one-line reason.
- Requirement releases come from the spec. If planning shows a requirement must move, propose it to
  the human: once the spec is approved, a move is a CR (skill `scope-change`, type `release-scope`).
- Assumptions and open questions: `scope.py register add …` with `--raised plan`; use the ID it prints, inline `[ASM-n]`.
- Question batch: at most 5, each with a proposed default.
- Remove all `<!-- … -->` guidance comments and placeholders from the written files.

## Workflow

1. `scope.py check --for plan`. If the gate is not passed, stop and report.
   `scope.py status` tells which release to plan: the first one not released and without an approved plan.
2. Inputs, read in this order and no more:
   - `scope.py remaining` (open requirements per release, carry-over from a closed release);
   - `docs/scope/spec.md` headings and release fields (read the full text only of the requirements of
     the release being planned, via `scope.py extract <ids>` when the spec is long);
   - `docs/scope/architecture.md` sections 4 and 7 (building blocks, cross-cutting concepts).
3. **Roadmap** (`docs/scope/roadmap.md` from `references/roadmap.md`; if it exists, update it — after a
   release close it is reopened as draft and needs a version bump; so does `epics.md`):
   - one `## R<n> — <name>` section per release with Status, Goal, In scope, Epics, Out of scope,
     Exit criteria; a `## Later` section;
   - confirm the MVP boundary with the human in the question batch.
4. **Epics** for the release (`docs/scope/epics.md` from `references/epics.md`, IDs `scope.py next-id EP`):
   - an epic = a user-visible capability, 2–8 stories, one release;
   - keep the Definition of Ready / Done sections (adapt them to the project if the human wants);
   - the stories table is the **build order**: a story comes after its dependencies.
5. **Stories** (`docs/scope/stories/ST-n-<slug>.md` from `references/story.md`, IDs `scope.py next-id ST`):
   - INVEST; size S or M (an L story must be split);
   - `implements:` the acceptance criteria (`FR-n.m`) it delivers; together the release's stories must
     cover **every** criterion of every requirement of the release;
   - acceptance criteria in Given/When/Then, each citing the spec criterion it derives from;
   - **Context for the developer**: the few facts the developer needs (module to touch, pattern, ADR,
     NFR limits), copied as short excerpts with their IDs, so the developer reads only this file;
   - `adrs:` and `depends_on:` filled; front matter `epic` and `release` match `epics.md`;
   - tasks: a short checklist ending with the tests for each AC.
6. Verify:
   - `scope.py check` → no errors; warning W06 lists requirements of the release still without story;
   - `scope.py trace` and read the release's table in `docs/scope/reports/trace.md`: every criterion of
     the release is covered by a story;
   - every story passes the Definition of Ready.
7. `scope.py remaining` to refresh the remaining-work report.
8. `scope.py git phase-artifact roadmap --extra "plan R<n>"`.
9. Summary: release goal, epics with their stories in order, what is out of scope and where it goes,
   open blocking items. Ask the human to review and say "approve plan R<n>"; after that, the next step is
   "launch EP-n" (skill `scope`), choosing supervised or autonomous mode.

## Revising before approval

Edit roadmap, epics and stories directly while they are draft. Keep IDs stable; a dropped story file is
deleted before approval, or set to `status: removed` after.

## Summary format

```
Done: plan of R<n>: <k> epics, <m> stories (sizes S <a>, M <b>); out of scope: <ids → release>
Register: <added/changed ids or none>
Next: review, then "approve plan R<n>", then "launch EP-n"
```
