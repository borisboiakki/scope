---
name: scope-build
description: Implements the stories of a launched SCOPE epic with tests, then has each one reviewed by the read-only scope-reviewer subagent. Supervised mode builds one story and waits for the human's approval; autonomous mode builds the whole epic with two mandatory review cycles per story and stops at the first blocking problem. Applies the git policy. Use when the user says "build ST-n", "build EP-n", "continue the epic", "resume after the blocker", or after an epic is launched.
---

# SCOPE — build and review

`scope.py` means `python3 .scope/scope.py` (Windows: `python`). Work from the project root.

## Rules

- Work on **one story at a time**, in the order of `epics.md`. Read the story file; for anything else
  use `scope.py extract <ids>`. Read only the code the story touches.
- Stay inside the story: no unrelated refactoring, no work of other stories, no change to approved
  documents (spec, architecture, ADRs, roadmap, epics, story definitions).
- Every acceptance criterion gets a test whose name or comment cites it (`AC-2`, `FR-1.2`).
- New assumptions or open questions: `scope.py register add … --raised ST-n`.
- **Stop rules**: on any situation below, block and stop. Never guess, never work around.

| Code | Stop when |
|---|---|
| B1 | review not PASS after the allowed cycles |
| B2 | tests or build fail and cannot be fixed within the story |
| B3 | the story needs a change to an approved document (draft the CR with skill `scope-change`, do not apply it) |
| B4 | a new blocking open question appears, or an assumption proves wrong |
| B5 | an acceptance criterion is ambiguous or contradictory |
| B6 | environment, tool or dependency failure you cannot solve safely |
| B7 | the reviewer returns BLOCKED |

To block: `scope.py story block ST-n --code Bx --summary "<one line>"`, write the *Blocker record* of the
story (what happened, what you tried, the decision the human must take), then stop with the summary.

## Start

1. `scope.py status` and `scope.py check --for build`. The epic must be launched; its mode
   (supervised or autonomous) was chosen at launch and is shown by `status`.
2. If a story is `blocked`, the human must have decided: apply the decision, then
   `scope.py story unblock ST-n` and continue where it stopped.
3. On the first story of the epic: `scope.py git epic-start EP-n` (branch per policy).
4. `scope.py config show` → note `project.test_command` and `project.lint_command`.

## Story loop

1. **Start**: `scope.py story start ST-n` (refused if dependencies are not done or blocking items are
   open). `scope.py git story-start ST-n`. Record the base commit (`git rev-parse HEAD`) in the
   *Implementation record*.
2. **Ready check**: every AC is testable and clear; otherwise B5.
3. **Implement**: tests first when practical, then the code, following the story context, the ADRs and
   the project rules of `AGENTS.md`.
4. **Verify**: run the test and lint commands until they pass (otherwise B2).
5. **Record**: fill the *Implementation record* (files changed, tests → AC, notes, new register ids).
6. **Review cycle**:
   - `scope.py story review ST-n`, then `scope.py git story-before-review ST-n`;
   - launch the **scope-reviewer** subagent with: the story path, the base commit, the cycle number,
     the test and lint commands. Wait for its report (in some tools it runs in the background: wait
     for its result before doing anything else);
   - add a row to the story's *Review record*: `| <cycle> | <VERDICT> | <findings, severity: text, location> |`.
7. **Decide** (`N` = 2 in autonomous mode; `build.supervised_max_cycles` in supervised mode):
   - `BLOCKED` → block with B7 and stop;
   - cycle < N (autonomous: always after cycle 1, even on PASS):
     `scope.py story rework ST-n`, fix every blocker/major finding (and minor ones when cheap), answer
     the others in the notes, re-run tests and lint, `scope.py git story-after-review ST-n`, go to step 6;
   - cycle = N and verdict not PASS → block with B1 and stop;
   - `PASS` and supervised → stop and ask the human to approve the story (summary below). The human
     says "approve ST-n"; record it with `scope.py approve ST-n --by "human via <tool>"`;
   - `PASS` at cycle 2 and autonomous → `scope.py story done ST-n`.
8. **Close**: `scope.py git story-done ST-n` (follow its output).
9. **Next**: supervised → stop after one story unless the human asked for more. Autonomous → next
   story of the epic. When the tool reports the epic done: `scope.py git epic-done EP-n`; if it prints
   "ASK THE HUMAN" (merge, push), ask and do only what the human answers.

## Summaries

After a story (supervised):

```
ST-n <title>: ready for approval (review cycle <c>: PASS)
Files: <list>  Tests: <n> (all pass)  Findings left: <minor/nit or none>
Register: <ids or none>
Next: "approve ST-n", then build ST-m
```

After an autonomous run, or when stopped:

```
EP-n: <k>/<m> stories done (<ids>)
Stopped: <none | ST-n Bx: summary + the decision needed>
Register: <ids or none>
Next: <launch next epic | answer the blocker, then "resume EP-n">
```
