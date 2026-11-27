# Pilot on opencode 1.18.29 (milestone 6)

**Result (2026-11-27, run by the owner on Linux, Python 3.9):** all steps passed after one fix
(the installer needed Python 3.10, see D-036). Token use: roughly **70 % lower** than comparable BMAD
runs (estimate; opencode 1.18.29 gave no precise per-phase figures).

Goal: confirm SCOPE works end to end in opencode, find what breaks, and measure the cost of each
phase. Run it on a **small** project: one release with one epic of 2–3 stories.

Record every result in the table at the end (copy this file, or answer in the chat).

## 0. Prepare

```bash
opencode --version                      # expect 1.18.29
git clone https://github.com/borisboiakki/scope.git
mkdir pilot && cd pilot && git init
python3 ../scope/install.py . --setup   # per-project install
```

Expected: the install lines, `installed requirements`, then `Next:`.
Variant to try at the end (step 8): the global install.

## 1. Discovery (no work done yet)

Start `opencode` in `pilot/`.

| # | Do | Expected |
|---|---|---|
| 1.1 | Ask: "Which skills whose names start with scope are available? Names only." | `scope`, `scope-arch`, `scope-build`, `scope-change`, `scope-plan`, `scope-spec` |
| 1.2 | In a shell in `pilot/`: `opencode agent list` | `scope-reviewer` listed as a subagent. (Tab in the TUI only cycles **primary** agents; a subagent appears in the `@` menu when you type its name, e.g. `@scope-r`) |
| 1.3 | Ask: "@scope-reviewer create a file named test.txt" | refused or denied; no `test.txt` |

## 2. Set up

| # | Do | Expected |
|---|---|---|
| 2.1 | "set up SCOPE" | loads skill `scope`; checks Python and git; asks ≤ 5 questions in one batch (name, git preset, build mode, test/lint commands, language) |
| 2.2 | Answer (preset `story`, mode `supervised`) | runs `init` and `doctor`; doctor shows skills and both reviewer agents ok |
| 2.3 | — | `AGENTS.md`, `CLAUDE.md`, `docs/scope/` created; asks you to confirm the project rules |

## 3. Brief and spec

| # | Do | Expected |
|---|---|---|
| 3.1 | "write the brief" + a few lines describing the product | loads `scope-spec`; one question batch; `docs/scope/brief.md` with `BR-n` goals and an MVP section; assumptions added with `register add`; `check` run; asks you to approve |
| 3.2 | "approve brief" | shows what is approved, runs `approve brief`, then `git phase-artifact brief` (a commit) |
| 3.3 | "write the spec" | requirements with Release, Source, Statement, numbered criteria; `check` clean; asks to approve |
| 3.4 | Try a trap: "approve the architecture" | refused: no architecture yet / spec first |
| 3.5 | "approve spec" | approved v1.0, committed |

## 4. Architecture (or waiver)

| # | Do | Expected |
|---|---|---|
| 4.1 | "design the architecture" | ADRs + `architecture.md`; project rules and test command updated; or, for a tiny project, proposes to skip and waits for your decision |
| 4.2 | "approve architecture" (or "skip the architecture") | approved with its ADRs (or `waive G3`) |

## 5. Plan

| # | Do | Expected |
|---|---|---|
| 5.1 | "plan R1" | roadmap with in/out of scope per release; epics; stories with criteria, context, dependencies; `trace` and `remaining` run |
| 5.2 | "approve plan R1" | stories `ready`, epic `ready` |
| 5.3 | "launch EP-1 in supervised mode" | epic launched, branch created (preset `story`) |

## 6. Build with review

| # | Do | Expected |
|---|---|---|
| 6.1 | "build EP-1" | `story start`, base commit recorded, tests per AC, test/lint run, implementation record filled |
| 6.2 | — | **the `scope-reviewer` subagent is launched** and its `VERDICT` report comes back; a review row is written |
| 6.3 | — | on CHANGES: rework and a second cycle; on PASS: stops and asks you to approve the story |
| 6.4 | "approve ST-1" | story done, committed `feat(ST-1): …` |
| 6.5 | Trap: edit the spec by hand, then ask "status" or "check" | E15 reported: change needs a CR |

## 7. Change request

| # | Do | Expected |
|---|---|---|
| 7.1 | Undo the hand edit. Then: "change FR-… : <a small change>" | loads `scope-change`; CR with ADDED/MODIFIED/REMOVED, impact; asks for approval |
| 7.2 | "approve CR-1" | reopens, applies, bumps versions, asks you to re-approve; `cr close` at the end |

## 8. Global install (optional)

```bash
python3 ../scope/install.py . --uninstall
python3 ../scope/install.py --global --setup
```

Restart opencode in `pilot/` and repeat 1.1–1.2 and "status". Expected: the same skills and agent, and
`doctor` reports them in `~/.claude/skills` and `~/.config/opencode/agents`.

## Results

For cost, use opencode's session statistics (tokens / cost) after each phase if available, otherwise
the elapsed time.

| Step | OK? | Tokens or time | Notes (what differed, error text) |
|---|---|---|---|
| 0 Install | | | |
| 1 Discovery | | | |
| 2 Set up | | | |
| 3 Brief + spec | | | |
| 4 Architecture | | | |
| 5 Plan | | | |
| 6 Build + review | | | |
| 7 Change request | | | |
| 8 Global install | | | |

Also note: questions that felt unnecessary, steps where the agent hesitated or improvised, anything
written outside `docs/scope/` or the code, and whether the token use felt lighter than your BMAD runs.
