#!/usr/bin/env python3
"""SCOPE tool: deterministic checks and state changes for the SCOPE workflow (see METHOD.md).

Usage: python3 .scope/scope.py <command> [options]    (python3 .scope/scope.py -h for the list)
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from scope_lib.util import ScopeError  # noqa: E402

NEEDS_NO_YAML = {"setup", "doctor"}


def find_root(start: Path) -> Path:
    for d in [start, *start.parents]:
        if (d / "docs" / "scope" / "state.yaml").exists():
            return d
    return start


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="scope.py", description="SCOPE workflow tool")
    ap.add_argument("--root", help="project root (default: nearest folder with docs/scope/state.yaml)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("setup", help="create .scope/.venv and install requirements")
    s.add_argument("--system", action="store_true", help="use the current Python (PyYAML already installed)")
    sub.add_parser("doctor", help="check the environment and the installation")
    s = sub.add_parser("init", help="initialise SCOPE in the project")
    s.add_argument("--name", required=True)
    s.add_argument("--preset", default="story", help="git preset: story | fine | human | off")
    s.add_argument("--mode", default="supervised", help="default build mode: supervised | autonomous")
    s.add_argument("--language", default="en")
    s.add_argument("--test-cmd", default="")
    s.add_argument("--lint-cmd", default="")
    sub.add_parser("status", help="phase, progress, blockers and next step")
    s = sub.add_parser("check", help="validate the artifacts")
    s.add_argument("--for", dest="phase", help="also check the gate before a phase: spec | architecture | plan | build")
    s = sub.add_parser("approve", help="record a human approval")
    s.add_argument("target", nargs="+")
    s.add_argument("--by", default="human")
    s.add_argument("--mode", help="launch only: supervised | autonomous")
    s.add_argument("--carry", help="release-close only: release receiving unfinished work")
    s.add_argument("--reason")
    s = sub.add_parser("waive", help="waive a gate (only G3, architecture)")
    s.add_argument("gate")
    s.add_argument("--reason", required=True)
    s.add_argument("--by", default="human")
    s = sub.add_parser("reopen", help="reopen an approved artifact or story for an approved CR")
    s.add_argument("target")
    s.add_argument("--cr", required=True)
    s = sub.add_parser("cr", help="close (applied) or reject a change request")
    s.add_argument("action", choices=["close", "reject"])
    s.add_argument("id")
    s.add_argument("--by", default="human")
    s = sub.add_parser("story", help="story transitions: start | review | rework | done | block | unblock")
    s.add_argument("action")
    s.add_argument("id")
    s.add_argument("--code")
    s.add_argument("--summary")
    s = sub.add_parser("next-id", help="next free id for a prefix (FR, ST, ... or FR-3. for a criterion)")
    s.add_argument("prefix")
    s = sub.add_parser("extract", help="print the text of the given ids")
    s.add_argument("ids", nargs="+")
    sub.add_parser("trace", help="write reports/trace.md")
    s = sub.add_parser("impact", help="what depends on the given ids")
    s.add_argument("ids", nargs="+")
    sub.add_parser("remaining", help="write reports/remaining.md")
    s = sub.add_parser("register", help="list, add or update assumptions and open questions")
    s.add_argument("action", nargs="?", default="list", choices=["list", "add", "set"])
    s.add_argument("id", nargs="?")
    s.add_argument("--open", action="store_true")
    s.add_argument("--type", help="ASM | OQ")
    s.add_argument("--statement")
    s.add_argument("--raised", default="")
    s.add_argument("--blocking", default=None, help="yes | no")
    s.add_argument("--impacts", nargs="*", default=[])
    s.add_argument("--status")
    s.add_argument("--resolution")
    s = sub.add_parser("config", help="show or change config.yaml")
    s.add_argument("action", choices=["show", "preset", "set"])
    s.add_argument("key", nargs="?")
    s.add_argument("values", nargs="*")
    s = sub.add_parser("git", help="apply the git policy at an event")
    s.add_argument("event")
    s.add_argument("id")
    s.add_argument("--extra", help="text appended to the commit message")
    return ap


def run(args) -> str:
    from scope_lib import setup as st  # noqa: PLC0415

    root = Path(args.root).resolve() if args.root else find_root(Path.cwd())
    if args.cmd == "setup":
        return st.setup(args.system)
    if args.cmd == "doctor":
        return st.doctor(root)
    if args.cmd == "init":
        return st.init(Path(args.root).resolve() if args.root else Path.cwd(), args.name, args.preset, args.mode,
                       args.language, args.test_cmd, args.lint_cmd)

    from scope_lib import checks, flow, gitops, reports  # noqa: PLC0415
    from scope_lib.model import Project  # noqa: PLC0415

    p = Project(root)
    c = args.cmd
    if c == "status":
        return reports.status(p)
    if c == "check":
        report = checks.check_project(p)
        text = report.render()
        if args.phase:
            missing = checks.gate_report(p, args.phase)
            text += "\n" + (f"gate before {args.phase}: passed" if not missing else
                            f"gate before {args.phase}: NOT passed: " + "; ".join(missing))
            if missing:
                report.errors.append("gate")
        if report.errors:
            raise ScopeError(text)
        return text
    if c == "approve":
        return flow.approve(p, args.target, args.by, args.mode, args.carry, args.reason)
    if c == "waive":
        return flow.waive(p, args.gate, args.reason, args.by)
    if c == "reopen":
        return flow.reopen(p, args.target, args.cr)
    if c == "cr":
        return flow.cr_action(p, args.action, args.id, args.by)
    if c == "story":
        return flow.story(p, args.action, args.id, args.code, args.summary)
    if c == "next-id":
        return reports.next_id(p, args.prefix)
    if c == "extract":
        return reports.extract(p, args.ids)
    if c == "trace":
        return reports.trace(p)
    if c == "impact":
        return reports.impact(p, args.ids)
    if c == "remaining":
        return reports.remaining(p)
    if c == "register":
        if args.action == "list":
            return reports.register_list(p, args.open)
        if args.action == "add":
            if not args.type or not args.statement:
                raise ScopeError("register add needs --type ASM|OQ and --statement")
            blocking = (args.blocking or "no").lower() in ("yes", "y", "true")
            return reports.register_add(p, args.type, args.statement, args.raised, blocking, args.impacts)
        if not args.id:
            raise ScopeError("register set needs an id")
        return reports.register_set(p, args.id, args.status, args.resolution, args.blocking)
    if c == "config":
        return st.config(p, args.action, args.key, args.values)
    if c == "git":
        return gitops.event(p, args.event, args.id, args.extra)
    raise ScopeError(f"unknown command {c}")


def _reexec_in_venv(cmd: str):
    """Run again with .scope/.venv's Python when PyYAML is missing here."""
    if cmd in NEEDS_NO_YAML:
        return
    try:
        import yaml  # noqa: F401,PLC0415
        return
    except ImportError:
        pass
    from scope_lib.setup import venv_python  # noqa: PLC0415
    py = venv_python()
    if py.exists() and Path(sys.executable).resolve() != py.resolve():
        os.execv(str(py), [str(py), str(Path(__file__).resolve()), *sys.argv[1:]])


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    if argv is None:
        _reexec_in_venv(args.cmd)
    try:
        out = run(args)
    except ScopeError as exc:
        print(str(exc))
        return 1
    if out:
        print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
