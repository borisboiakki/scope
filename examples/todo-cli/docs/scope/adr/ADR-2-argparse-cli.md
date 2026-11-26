---
id: ADR-2
type: adr
version: 1.0
status: approved
date: 2026-11-26
supersedes: none
relates_to: [FR-1, FR-2, FR-3]
---

# ADR-2 Command-line interface with argparse

## Context and problem
The program exposes subcommands (`add`, `list`, `done`); it must run wherever Python 3.10+ runs.

## Decision drivers
- Brief constraint: Python 3.10+, offline, three operating systems.

## Options considered
1. **argparse (standard library)** — no dependency, subcommands supported.
2. **click / typer** — nicer API, one more dependency to install.

## Decision
Chosen: **argparse**, because it has no dependency and covers the needed subcommands.

## Consequences
- **Good:** install is a single file or package without dependencies.
- **Bad / accepted trade-off:** more boilerplate for help texts.
- **Follow-up:** none.
