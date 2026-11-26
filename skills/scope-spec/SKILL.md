---
name: scope-spec
description: Writes the product brief and then the specification of a SCOPE project, each ending at a human approval gate. The spec has traceable requirements (FR/NFR with EARS statements, Given/When/Then acceptance criteria) and a target release for each requirement (MVP vs later). Use when the user wants to describe a new product or feature, write or revise the brief, or write the requirements/specification.
---

# SCOPE — brief and specification

`scope.py` means `python3 .scope/scope.py` (Windows: `python`). Work from the project root.
Templates: `references/brief.md` and `references/spec.md` (read the one you need, when you need it).

## Rules

- Never edit an approved brief or spec: if it needs a change, use skill `scope-change`.
- Every assumption and open question goes to the register at once:
  `scope.py register add --type ASM|OQ --statement "…" --raised "<brief|spec>" --blocking yes|no --impacts <ids>`.
  Use the ID the tool prints (never invent one) and reference it inline where it is used: `[ASM-3]`. Mark it blocking only if approval must wait for it.
- Ask questions in one batch (at most 5), each with a proposed default. Do not ask what the input
  already answers.
- Remove all `<!-- … -->` guidance comments and placeholders from the written files.

Pick the mode: no approved brief → **Brief**; brief approved → **Spec**.

## Brief

1. `scope.py status`. If the brief is approved, stop and tell the human (changes go through a CR).
2. Read the human's input (message, attached notes, existing README). Identify gaps in: problem,
   users, business goals with measurable indicators, full idea vs first release (MVP), constraints,
   out of scope.
3. Ask the question batch. If the human prefers, proceed on proposed defaults and log each as `ASM`.
4. Copy `references/brief.md` to `docs/scope/brief.md` and fill it:
   - goals as `### BR-n <goal>` headings, each with a measurable **Success indicator**;
   - "Product idea" separates the **full idea** from the **MVP candidate**;
   - "Assumptions and open questions" lists only register IDs.
5. `scope.py check`; fix every error in the brief.
6. `scope.py git phase-artifact brief` (follow its output).
7. Summary, then ask the human to review and say "approve brief" (skill `scope` records it).

## Spec

1. `scope.py check --for spec`. If the gate is not passed, stop and report.
2. Inputs: `docs/scope/brief.md` and `scope.py register --open`. Read nothing else unless the human
   points to existing material.
3. Copy `references/spec.md` to `docs/scope/spec.md` and write the requirements:
   - one `### FR-n <title>` per capability; IDs from `scope.py next-id FR` (NFR, criteria: `next-id FR-3.`);
   - field lines exactly as in the template: `- **Release:**`, `- **Source:**`, `- **Statement:**`;
   - statement in an **EARS** pattern; one requirement = one behaviour (split "and");
   - 1–4 acceptance criteria per requirement, `- **FR-n.m** Given …, when …, then …` with an
     observable, testable result;
   - **Release**: `R1` for the MVP, `R2`… for later increments, `later` for kept-but-unplanned ideas.
     Propose the split from the brief's MVP candidate; include it in the question batch;
   - **Source**: the BR(s) the requirement serves; a requirement with no BR is either out of scope or
     reveals a missing goal (ask);
   - NFRs: walk the checklist performance, compatibility, usability, reliability, security,
     maintainability, portability; keep only those that matter, each with a measurable target.
4. Quality pass on every requirement (ISO/IEC/IEEE 29148): necessary, singular, unambiguous (no "fast",
   "easy", "etc."), feasible, verifiable, free of design decisions. Every "TBD" becomes an `OQ`.
5. Fill "Release overview" (requirements per release) and "Assumptions and open questions" (IDs).
6. `scope.py check`; fix every error (E06–E09 are the usual ones).
7. `scope.py git phase-artifact spec`.
8. Summary with the count of requirements per release and the open blocking items; ask the human to
   review and say "approve spec".

## Revising before approval

While the brief or spec is still `draft`, edit it directly on the human's feedback, keep IDs stable
(never renumber; a dropped requirement keeps its heading with "(removed by …)" only after approval —
before approval simply delete it), and run `scope.py check` again.

## Summary format

```
Done: <file> v<version> (<n> requirements: R1 <a>, R2 <b>, later <c>)
Register: <added/changed ids or none>
Next: review, then "approve <brief|spec>"
```
