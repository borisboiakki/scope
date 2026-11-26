---
id: spec
type: spec
version: 1.0
status: approved
---

# Specification — todo-cli

## 1. Scope and context
A command-line program `todo` used by one developer in a terminal. It stores tasks in a local file
[ASM-1]. No network access, no other system.

## 2. Glossary
| Term | Meaning |
|---|---|
| Task | A short text with an identifier and a state (open or done) |

## 3. Functional requirements

### FR-1 Add a task
- **Release:** R1
- **Source:** BR-1
- **Statement:** When the user runs `todo add <text>`, the program shall store an open task with that text.
- **FR-1.1** Given any list, when I run `todo add "Write docs"`, then a new open task "Write docs" is stored and its number is printed.
- **FR-1.2** Given any list, when I run `todo add` with empty text, then nothing is stored and an error is printed.

### FR-2 List open tasks
- **Release:** R1
- **Source:** BR-2
- **Statement:** When the user runs `todo list`, the program shall print the open tasks in creation order.
- **FR-2.1** Given tasks "a" then "b" are open, when I run `todo list`, then it prints "1 a" and "2 b" in that order.
- **FR-2.2** Given no open task, when I run `todo list`, then it prints "No open task".

### FR-3 Complete a task
- **Release:** R1
- **Source:** BR-2
- **Statement:** When the user runs `todo done <number>`, the program shall mark that task as done.
- **FR-3.1** Given open task 1, when I run `todo done 1`, then task 1 is no longer listed by `todo list`.
- **FR-3.2** Given no task 7, when I run `todo done 7`, then an error is printed and nothing changes.

### FR-4 Delete a task
- **Release:** R2
- **Source:** BR-2
- **Statement:** When the user runs `todo rm <number>`, the program shall delete that task.
- **FR-4.1** Given task 1, when I run `todo rm 1`, then task 1 no longer exists.

### FR-5 Export to Markdown
- **Release:** later
- **Source:** BR-2
- **Statement:** When the user runs `todo export`, the program shall print the tasks as a Markdown checklist.
- **FR-5.1** Given tasks "a" (open) and "b" (done), when I run `todo export`, then it prints "- [ ] a" and "- [x] b".

## 4. Non-functional requirements

### NFR-1 Responsiveness
- **Release:** R1
- **Source:** BR-1
- **Statement:** The program shall complete any command on a list of 1000 tasks in less than 1 s.
- **NFR-1.1** Given 1000 stored tasks, when I run `todo add x`, then the command ends in less than 1 s.

### NFR-2 Data safety
- **Release:** R1
- **Source:** BR-1
- **Statement:** If writing the task file fails, then the program shall keep the previous file intact.
- **NFR-2.1** Given a write interrupted after the new content is half written, when I run `todo list`, then the previous tasks are listed.

## 5. Data and interfaces
Task: number (integer, never reused), text, state (open, done), creation time.

## 6. Release overview
| Release | Requirements |
|---|---|
| R1 | FR-1, FR-2, FR-3, NFR-1, NFR-2 |
| R2 | FR-4 |
| later | FR-5 |

## 7. Assumptions and open questions
ASM-1

## Changelog
| Version | Date | CR | Change |
|---|---|---|---|
| 0.1 | 2026-11-26 | — | First draft |
