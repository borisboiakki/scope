---
id: architecture
type: architecture
version: 0.1
status: draft
---

# Architecture — <product name>

<!-- arc42 essentials + C4 views (Mermaid or text). Only what guides implementation; cite IDs.
     Each significant choice gets an ADR (adr/ADR-n-<slug>.md) linked from here. -->

## 1. Goals and constraints
| Driver | Source |
|---|---|
| <quality goal or constraint> | NFR-1 / brief constraint |

## 2. Context (C4 level 1: users and external systems)
```mermaid
flowchart LR
  user[<User>] --> sys[<System>]
  sys --> ext[<External system>]
```

## 3. Solution strategy
<!-- Main technology choices and approach, each with its ADR. -->
- <choice> — ADR-1

## 4. Building blocks (C4 level 2)
| Container / module | Responsibility | Technology | Implements |
|---|---|---|---|
| <name> | <responsibility> | <tech> | FR-1, FR-2 |

## 5. Runtime scenarios
<!-- Only the 1–3 flows that matter most (sequence in bullets or Mermaid). -->
- **<scenario>** (FR-1): <steps>

## 6. Deployment and environments
<where it runs, how it is built and delivered>

## 7. Cross-cutting concepts
- **Data:** <storage, model, migrations>
- **Errors and logging:** <approach>
- **Security:** <authentication, secrets, input validation>
- **Testing strategy:** <unit / integration / end-to-end, test command>
- **Coding conventions:** <pointer to AGENTS.md rules>

## 8. Decisions
| ADR | Title | Status |
|---|---|---|
| ADR-1 | <title> | draft |

## 9. Risks, technical debt, assumptions
- <risk / debt, mitigation>
- Register items: <ASM-n, OQ-n (details in register.md)>

## Changelog
| Version | Date | CR | Change |
|---|---|---|---|
| 0.1 | <date> | — | First draft |
