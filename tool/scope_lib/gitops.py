"""Apply the git policy of config.yaml at workflow events (METHOD.md section 10).

The tool creates branches and commits when the policy says the agent does it. It never merges or pushes:
for those it prints what the policy asks, and the agent asks the human when needed.
"""
from __future__ import annotations

import subprocess

from .model import Project
from .util import ScopeError, now, slugify

COMMIT_EVENTS = {"phase-artifact", "story-before-review", "story-after-review", "story-done", "epic-done"}
BRANCH_EVENTS = {"epic-start", "story-start"}


def _git(root, *args, check=True) -> str:
    res = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True)
    if check and res.returncode != 0:
        raise ScopeError(f"git {' '.join(args)} failed: {res.stderr.strip() or res.stdout.strip()}")
    return res.stdout.strip()


def _title(p: Project, ident: str) -> str:
    if ident in p.stories:
        return p.stories[ident].title()
    if ident in p.epics:
        return p.epics[ident]["title"]
    if ident in p.releases:
        return p.releases[ident]["title"]
    return ident


def _message(p: Project, event: str, ident: str, extra: str | None) -> str:
    if event == "phase-artifact":
        doc = p.docs.get(ident) or p.adrs.get(ident) or p.crs.get(ident)
        version = f" v{doc.version}" if doc is not None and doc.version else ""
        return f"docs(scope): {ident}{version}" + (f" {extra}" if extra else "")
    title = _title(p, ident)
    kind = {"story-before-review": "feat", "story-after-review": "fix", "story-done": "feat", "epic-done": "chore"}[event]
    suffix = {"story-before-review": " (ready for review)", "story-after-review": " (review fixes)",
              "story-done": "", "epic-done": " done"}[event]
    return f"{kind}({ident}): {title}{suffix}" + (f" - {extra}" if extra else "")


def event(p: Project, name: str, ident: str, extra: str | None = None) -> str:
    git = p.config.get("git", {})
    if not git.get("enabled", False):
        return "git policy: off (no git action)"
    if name in BRANCH_EVENTS:
        return _branch(p, git, name, ident)
    if name not in COMMIT_EVENTS:
        raise ScopeError(f"event must be one of {', '.join(sorted(BRANCH_EVENTS | COMMIT_EVENTS))}")
    out = []
    msg = _message(p, name, ident, extra)
    if name in git.get("commit_at", []) and "manual" not in git.get("commit_at", []):
        if git.get("commit_by") == "agent":
            _git(p.root, "add", "-A")
            if not _git(p.root, "status", "--porcelain"):
                out.append("nothing to commit")
            else:
                _git(p.root, "commit", "-q", "-m", msg)
                out.append(f"committed: {msg} ({_git(p.root, 'rev-parse', '--short', 'HEAD')})")
        else:
            out.append(f"HUMAN COMMIT CHECKPOINT: ask the human to commit now. Suggested message: {msg}")
    else:
        out.append(f"no commit at {name} (policy)")
    if name in ("epic-done", "story-done"):
        out += _merge_push_hint(p, git, name, ident)
    return "\n".join(out)


def _branch_for(p: Project, git: dict, name: str, ident: str) -> str | None:
    mode = git.get("branching", "none")
    if mode == "per-epic" and name == "epic-start":
        key = ident
    elif mode == "per-story" and name == "story-start":
        key = ident
    elif mode == "per-release" and name == "epic-start":
        key = p.epics.get(ident, {}).get("release") or ident
    else:
        return None
    return key


def _branch(p: Project, git: dict, name: str, ident: str) -> str:
    key = _branch_for(p, git, name, ident)
    if not key:
        return f"no branch at {name} (policy: {git.get('branching', 'none')})"
    branch = git.get("branch_pattern", "scope/{id}-{slug}").format(id=key, slug=slugify(_title(p, key)))
    current = _git(p.root, "rev-parse", "--abbrev-ref", "HEAD")
    if current == branch:
        return f"already on {branch}"
    exists = _git(p.root, "rev-parse", "--verify", "--quiet", f"refs/heads/{branch}", check=False)
    if exists:
        _git(p.root, "switch", branch)
        return f"switched to existing branch {branch}"
    _git(p.root, "switch", "-c", branch)
    p.state["branches"][key] = {"name": branch, "base": current, "date": now()}
    p.save_state()
    return f"created branch {branch} from {current}"


def _merge_push_hint(p: Project, git: dict, name: str, ident: str) -> list[str]:
    key = ident if name == "story-done" else ident
    info = p.state.get("branches", {}).get(key)
    out = []
    merge, push = git.get("merge", "never"), git.get("push", "never")
    if info and ((name == "epic-done" and git.get("branching") in ("per-epic", "per-release")) or
                 (name == "story-done" and git.get("branching") == "per-story")):
        if merge == "ask":
            out.append(f"ASK THE HUMAN: merge {info['name']} into {info['base']}?")
        elif merge == "on-epic-done" and name == "epic-done":
            out.append(f"policy: merge {info['name']} into {info['base']} now (git switch {info['base']} && "
                       f"git merge --no-ff {info['name']})")
        else:
            out.append(f"policy: no merge ({info['name']} stays open for the human)")
    if name == "epic-done":
        if push == "ask":
            out.append("ASK THE HUMAN: push the branch?")
        elif push == "on-epic-done":
            out.append("policy: push the branch now (git push -u origin HEAD)")
    return out
