---
name: scope-arch
description: Writes the architecture of a SCOPE project from its approved specification, as a short arc42/C4 document plus MADR decision records (ADRs), and completes the project rules in AGENTS.md (stack, conventions, test command). Ends at the architecture approval gate. Use when the user wants to design the architecture, choose the technology, record an architecture decision, or skip the architecture phase for a small project.
---

# SCOPE — architecture

`scope.py` means `python3 .scope/scope.py` (Windows: `python`). Work from the project root.
Templates: `references/architecture.md` and `references/adr.md`.

## Rules

- Never edit an approved architecture or ADR: changes go through skill `scope-change`.
- Write only what guides implementation; every section cites the requirement IDs it serves.
- One ADR per significant decision: hard to change later, or trading off quality goals
  (language, framework, storage, deployment, integration style, security model).
- Assumptions and open questions: `scope.py register add --type ASM|OQ --statement "…" --raised architecture
  --blocking yes|no --impacts <ids>`; use the ID it prints and reference it inline `[ASM-n]`.
- Question batch: at most 5, each with a proposed default.
- Remove all `<!-- … -->` guidance comments and placeholders from the written files.

## Small projects

If the product is small and has no real architectural choice (a script, a single-module tool), say so
and ask the human whether to skip this phase. Only on their decision: `scope.py waive G3 --reason "…"`,
then still fill the **Project rules** of `AGENTS.md` (step 6) and stop. Next: skill `scope-plan`.

## Workflow

1. `scope.py check --for architecture`. If the gate is not passed, stop and report.
2. Inputs:
   - `docs/scope/spec.md` (requirements and NFRs);
   - `AGENTS.md` (project rules) and `scope.py register --open`;
   - existing code, if any: list the top-level structure and read only the build files (package
     manifests, CI config) to learn the stack. Do not read source files in bulk.
3. Identify the drivers: NFRs with their targets, constraints from the brief, existing systems.
4. Decide the significant choices. For each, write `docs/scope/adr/ADR-n-<slug>.md` from
   `references/adr.md` (ID from `scope.py next-id ADR`), with `relates_to:` listing the NFR/FR it serves,
   2–3 real options and the reason tied to the drivers. Ask the human about choices with strong
   preferences (language, cloud, database) in the question batch.
5. Copy `references/architecture.md` to `docs/scope/architecture.md` and fill it:
   - context diagram (C4 level 1) and building blocks table (C4 level 2) with the FRs each implements;
   - 1–3 runtime scenarios for the riskiest requirements;
   - cross-cutting concepts, including the **testing strategy** (levels, tools, test command);
   - decisions table listing every ADR; risks and technical debt.
6. Complete the project's constitution:
   - fill or update the **Project rules** section of `AGENTS.md` (stack, coding conventions, testing,
     security, forbidden practices) to match the decisions;
   - set the commands: `scope.py config set project.test_command <cmd>` and `project.lint_command`.
   Show the human these changes in the summary.
7. Check coverage: every FR appears in at least one building block; every NFR is addressed by a
   building block, a concept or an ADR. Fix gaps or log an `OQ`.
8. `scope.py check`; fix every error.
9. `scope.py git phase-artifact architecture`.
10. Summary; ask the human to review and say "approve architecture" (it approves the draft ADRs too).

## ADR added later

An ADR can be added after the architecture is approved when a new significant decision appears
(e.g. during planning): write it as draft, reference it from the stories that need it, and ask the human
to "approve ADR-n". If it changes an approved decision or the architecture text, use `scope-change`.

## Summary format

```
Done: architecture v<version>, ADRs <ids>; AGENTS.md project rules updated; test command <cmd>
Register: <added/changed ids or none>
Next: review, then "approve architecture"
```
