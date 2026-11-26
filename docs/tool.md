# scope.py — command reference

`python3 .scope/scope.py <command>` (on Windows `python`). The tool re-runs itself with `.scope/.venv`
when PyYAML is missing. Output is short plain text; exit code 1 means refused or failed, with the reason.
`--root <path>` selects the project (default: nearest folder with `docs/scope/state.yaml`).

## Environment and setup

| Command | Does |
|---|---|
| `setup [--system]` | Creates `.scope/.venv` and installs `requirements.txt` (`--system`: use the current Python). |
| `doctor` | Checks Python, PyYAML, venv, git, installed skills and agents, opencode switches, initialisation. |
| `init --name N [--preset story\|fine\|human\|off] [--mode supervised\|autonomous] [--language en] [--test-cmd C] [--lint-cmd C]` | Creates `docs/scope/` (config, state, register, folders), the SCOPE section of `AGENTS.md` and `CLAUDE.md`. Never overwrites. |
| `config show` · `config preset <name>` · `config set <key> <value…>` | Shows or changes `config.yaml` (keys: `build.mode`, `git.*`, `project.*`…). Logged in the state history. |

## Reading

| Command | Does |
|---|---|
| `status` | Phase, artifacts, releases, active epics, blockers, open register items and CRs, **next step**. |
| `check [--for spec\|architecture\|plan\|build]` | All validation rules (codes below); `--for` also checks the gate before that phase. |
| `extract <ids…>` | Prints the text of requirements, criteria, BRs, ADRs, story definitions, epics, releases, register rows, CRs. |
| `impact <ids…>` | Requirements, stories, epics, releases, ADRs, CRs and register items affected by the ids. |
| `next-id <prefix>` | Next free id: `FR`, `NFR`, `BR`, `ADR`, `EP`, `ST`, `CR`, `ASM`, `OQ`, `R`, or `FR-3.` for a criterion. |
| `trace` | Writes `reports/trace.md` (requirement → criteria → stories → done, per release). |
| `remaining` | Writes `reports/remaining.md` (open requirements and stories per release, carry-over, CRs, register). |
| `register [list] [--open]` | Lists assumptions and open questions. |

## Changing state

| Command | Does |
|---|---|
| `approve brief\|spec\|architecture\|ADR-n [--by WHO]` | Records a human approval (status, version 1.0 or bump check, hash). Architecture also approves its draft ADRs. |
| `approve plan R<n>` | Approves roadmap and epics, sets the release's epics `ready` and stories `ready`, hashes every story definition. Needs full coverage of the release. |
| `approve launch EP-n [--mode supervised\|autonomous]` | Launches the epic (release becomes `active`). |
| `approve ST-n` | Supervised mode: story in review with a final PASS becomes `done`. |
| `approve CR-n` | Approves a change request; a quick CR also makes its draft stories `ready`. |
| `approve release-close R<n> [--carry R<m> --reason TEXT]` | Closes the release, writes release notes, reopens roadmap and epics for the next plan. |
| `waive G3 --reason TEXT` | Skips the architecture gate (small projects). |
| `reopen <brief\|spec\|architecture\|roadmap\|epics\|ADR-n\|ST-n> --cr CR-n` | Reopens approved content for an approved CR (documents → `draft`, story → `needs-rework`; a blocked story's blocker is resolved). Re-approving the plan makes reworked stories `ready` and relaunches a done epic only after `approve launch`. |
| `cr close\|reject CR-n` | `close`: all reopened artifacts re-approved → `applied`. `reject`: proposed → `rejected`. |
| `story start\|review\|rework\|done\|block\|unblock ST-n [--code B1..B7 --summary TEXT]` | Story transitions with their rules (dependencies, launch, review cycles, blockers). `done` is for autonomous mode. |
| `register add --type ASM\|OQ --statement TEXT [--raised WHERE] [--blocking yes\|no] [--impacts IDS…]` | Adds a row, prints its id. |
| `register set ID [--status S] [--resolution TEXT] [--blocking yes\|no]` | Updates a row. |
| `git <event> <id> [--extra TEXT]` | Applies the git policy. Events: `epic-start`, `story-start` (branches); `phase-artifact`, `story-before-review`, `story-after-review`, `story-done`, `epic-done` (commits). Never merges or pushes. |

## Check codes

| Code | Meaning |
|---|---|
| E01 | Parse problem (duplicate id, criterion under the wrong requirement) |
| E02 | Missing or invalid front matter |
| E03 | Invalid status or blocking value |
| E04 | Invalid version |
| E05 | Duplicate id or id not matching the file name |
| E06 | Undefined reference (warning W03 in a proposed/approved CR) |
| E07 | Requirement release invalid or not in the roadmap |
| E08 | Requirement without source BR |
| E09 | Requirement without acceptance criterion |
| E10 | Epic release not in the roadmap |
| E11 | Epics table and story files disagree |
| E12 | Story implements no requirement |
| E13 | Acceptance criterion of a planned release not implemented by any story (a story implementing `FR-n` covers all its criteria) |
| E14 | Status approved/active without a recorded approval |
| E15 | Approved content changed (needs a CR) |
| E16 | Approved artifact set back to another status without a CR |
| W01–W06 | Open blocker, blocking register item, CR forward references, roadmap/spec scope mismatch, epic without stories, release not fully covered yet |
