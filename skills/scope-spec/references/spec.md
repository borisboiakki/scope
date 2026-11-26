---
id: spec
type: spec
version: 0.1
status: draft
---

# Specification — <product name>

<!-- ISO/IEC/IEEE 29148: each requirement necessary, singular, unambiguous, feasible, verifiable.
     EARS: "The <system> shall …" | "When <trigger>, …" | "While <state>, …" |
           "If <condition>, then the <system> shall …" | "Where <feature>, …"
     Each requirement has a target release (R1, R2… or later) and a BR source.
     Acceptance criteria: Given / When / Then, numbered under their requirement. -->

## 1. Scope and context
<one paragraph: system boundary, external actors and systems>

## 2. Glossary
| Term | Meaning |
|---|---|
| <term> | <meaning> |

## 3. Functional requirements

### FR-1 <short title>
- **Release:** R1
- **Source:** BR-1
- **Statement:** When <trigger>, the <system> shall <response>.
- **FR-1.1** Given <context>, when <action>, then <observable result>.
- **FR-1.2** Given <context>, when <action>, then <observable result>.

## 4. Non-functional requirements
<!-- Check the ISO 25010 characteristics: performance, compatibility, usability, reliability,
     security, maintainability, portability. Every NFR has a measurable target. -->

### NFR-1 <short title>
- **Release:** R1
- **Source:** BR-1
- **Statement:** The <system> shall <quality> <measurable target>.
- **NFR-1.1** Given <conditions>, when <measurement>, then <threshold>.

## 5. Data and interfaces
<!-- Main data entities and external interfaces, only what requirements depend on. -->
<entities, interfaces>

## 6. Release overview
| Release | Requirements |
|---|---|
| R1 | FR-1, NFR-1 |
| later | <IDs> |

## 7. Assumptions and open questions
<ASM-n, OQ-n (details in register.md)>

## Changelog
| Version | Date | CR | Change |
|---|---|---|---|
| 0.1 | <date> | — | First draft |
