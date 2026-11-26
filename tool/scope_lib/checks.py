"""Validation rules run by `scope.py check` and before every approval."""
from __future__ import annotations

import re

from .model import STATUSES, VERSIONED, Project, id_list
from .util import ids_in, version_tuple

REL_VALUE = re.compile(r"^(R\d+|later)$", re.I)


class Report:
    def __init__(self):
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, code: str, msg: str):
        self.errors.append(f"{code} {msg}")

    def warn(self, code: str, msg: str):
        self.warnings.append(f"{code} {msg}")

    def render(self, quiet_ok: bool = False) -> str:
        lines = [f"ERROR {e}" for e in self.errors] + [f"WARN  {w}" for w in self.warnings]
        if not lines and quiet_ok:
            return ""
        lines.append(f"check: {len(self.errors)} error(s), {len(self.warnings)} warning(s)")
        return "\n".join(lines)


def rel_name(p: Project, doc) -> str:
    return str(doc.path.relative_to(p.dir))


def check_project(p: Project, extra_covered_release: str | None = None) -> Report:
    r = Report()
    for msg in p.parse_errors:
        r.error("E01", msg)
    _check_files(p, r)
    _check_refs(p, r)
    _check_spec(p, r)
    _check_plan(p, r, extra_covered_release)
    _check_approvals(p, r)
    for b in p.state["blockers"]:
        if not b.get("resolved"):
            r.warn("W01", f"open blocker on {b.get('story')}: {b.get('code')} {b.get('summary')}")
    for i in p.blocking_items():
        r.warn("W02", f"blocking register item open: {i} (prevents approvals)")
    return r


def _check_files(p: Project, r: Report):
    kinds = {"brief": "artifact", "spec": "artifact", "architecture": "artifact", "roadmap": "artifact",
             "epics": "artifact"}
    for name, doc in p.docs.items():
        if doc.error:
            r.error("E02", f"{name}.md: {doc.error}")
        if name in kinds and doc.status not in STATUSES["artifact"]:
            r.error("E03", f"{name}.md: invalid status '{doc.status}'")
        if name in VERSIONED:
            try:
                version_tuple(doc.version)
            except Exception as exc:
                r.error("E04", f"{name}.md: {exc}")
    for table, kind, prefix in ((p.adrs, "artifact", "ADR"), (p.stories, "story", "ST"), (p.crs, "cr", "CR")):
        for ident, doc in table.items():
            where = rel_name(p, doc)
            if doc.error:
                r.error("E02", f"{where}: {doc.error}")
            if getattr(doc, "duplicate", False) or "#" in ident:
                r.error("E05", f"{where}: duplicate id {doc.id}")
            if doc.file_id and doc.fm.get("id") and str(doc.fm.get("id")) != doc.file_id:
                r.error("E05", f"{where}: front matter id {doc.fm.get('id')} does not match the file name")
            if doc.status not in STATUSES[kind]:
                r.error("E03", f"{where}: invalid status '{doc.status}'")
    for rel, d in p.releases.items():
        if d["status"] not in STATUSES["release"]:
            r.error("E03", f"roadmap.md {rel}: invalid status '{d['status']}'")
    for ep, d in p.epics.items():
        if d["status"] not in STATUSES["epic"]:
            r.error("E03", f"epics.md {ep}: invalid status '{d['status']}'")
    for i, row in p.register.items():
        if row["status"] not in STATUSES["register"]:
            r.error("E03", f"register.md {i}: invalid status '{row['status']}'")
        if row["blocking"] not in ("yes", "no", "y", "n", "true", "false"):
            r.error("E03", f"register.md {i}: blocking must be yes or no")


def _check_refs(p: Project, r: Report):
    defined = p.defined_ids()
    no_roadmap = "roadmap" not in p.docs  # releases are named in the spec before the roadmap defines them
    for doc in p.all_files():
        where = rel_name(p, doc)
        missing = sorted({i for i in ids_in(doc.text) if i not in defined
                          and not (no_roadmap and re.fullmatch(r"R\d+", i))})
        if not missing:
            continue
        if doc.fm.get("type") == "cr" and doc.status in ("proposed", "approved"):
            r.warn("W03", f"{where}: references not defined yet: {', '.join(missing)}")
        else:
            r.error("E06", f"{where}: undefined reference(s): {', '.join(missing)}")


def _check_spec(p: Project, r: Report):
    if "spec" not in p.docs:
        return
    for rid, req in p.reqs.items():
        if req["removed"]:
            continue
        if not REL_VALUE.match(req["release"]):
            r.error("E07", f"spec.md {rid}: release must be R<n> or later (got '{req['release']}')")
        elif p.releases and req["release"].lower() != "later" and req["release"] not in p.releases:
            r.error("E07", f"spec.md {rid}: release {req['release']} is not in roadmap.md")
        if not req["sources"]:
            r.error("E08", f"spec.md {rid}: no source (BR)")
        if not req["acs"]:
            r.error("E09", f"spec.md {rid}: no acceptance criterion")
        if p.releases:
            rel = req["release"]
            listed = [x for x, d in p.releases.items() if rid in d["in_scope"]]
            if rel.lower() == "later":
                if listed:
                    r.warn("W04", f"{rid} has release later but is in scope of {', '.join(listed)}")
            elif rel in p.releases and rid not in p.releases[rel]["in_scope"]:
                r.warn("W04", f"{rid} (release {rel}) is not listed in roadmap {rel} 'In scope'")


def _check_plan(p: Project, r: Report, extra_release: str | None):
    for ep, d in p.epics.items():
        if p.releases and d["release"] not in p.releases:
            r.error("E10", f"epics.md {ep}: release '{d['release']}' is not in roadmap.md")
        if not d["rows"]:
            r.warn("W05", f"epics.md {ep}: no stories")
        for row in d["rows"]:
            st = p.stories.get(row["id"])
            if not st:
                r.error("E11", f"epics.md {ep}: story file for {row['id']} not found")
                continue
            if str(st.fm.get("epic")) != ep:
                r.error("E11", f"{rel_name(p, st)}: epic is {st.fm.get('epic')}, but epics.md lists it under {ep}")
            if st.fm.get("release") and str(st.fm.get("release")) != d["release"]:
                r.error("E11", f"{rel_name(p, st)}: release {st.fm.get('release')} differs from {ep} ({d['release']})")
    listed = {row["id"] for d in p.epics.values() for row in d["rows"]}
    for sid, st in p.stories.items():
        if "#" in sid or st.status == "removed":
            continue
        if p.epics and sid not in listed and not st.fm.get("cr"):
            r.error("E11", f"{rel_name(p, st)}: not listed in epics.md")
        if not id_list(st.fm.get("implements")):
            r.error("E12", f"{rel_name(p, st)}: implements no requirement")
    releases = {rel for rel in p.releases if p.plan_approved(rel)}
    if extra_release:
        releases.add(extra_release)
    implemented = {i for sid, st in p.stories.items() if "#" not in sid and st.status != "removed"
                   for i in id_list(st.fm.get("implements"))}
    for rel in p.releases:
        uncovered = []
        for rid, q in p.reqs.items():
            if q["removed"] or p.effective_release(rid) != rel or rid in implemented:
                continue
            uncovered += [ac for ac in q["acs"] if ac not in implemented] if q["acs"] else [rid]
        if not uncovered:
            continue
        if rel in releases:
            r.error("E13", f"{rel}: acceptance criteria without story: {', '.join(uncovered)}")
        elif p.epics_of_release(rel):
            r.warn("W06", f"{rel}: acceptance criteria without story yet: {', '.join(uncovered)}")


def _check_approvals(p: Project, r: Report):
    reopened = {x.get("target") for x in p.state.get("reopens", []) if not x.get("closed")}
    targets = [(name, doc) for name, doc in p.docs.items() if name != "register"]
    targets += [(i, d) for i, d in p.adrs.items() if "#" not in i]
    for target, doc in targets:
        last = p.last_approval(target)
        if doc.status == "approved":
            if not last:
                r.error("E14", f"{rel_name(p, doc)}: status approved but no approval recorded (use scope.py approve)")
            elif last.get("sha256") != doc.hash():
                r.error("E15", f"{rel_name(p, doc)}: changed after approval; reopen it with a CR "
                               f"(scope.py reopen {target} --cr CR-n)")
        elif last and target not in reopened and doc.status != "superseded":
            r.error("E16", f"{rel_name(p, doc)}: was approved, now '{doc.status}' without a reopen through a CR")
    for sid, st in p.stories.items():
        if "#" in sid or st.status in ("draft", "removed", "needs-rework"):
            continue
        recorded = p.story_hash_record(sid)
        if not recorded:
            r.error("E14", f"{rel_name(p, st)}: status {st.status} but its definition was never approved")
        elif recorded != st.hash():
            r.error("E15", f"{rel_name(p, st)}: definition changed after approval; reopen it with a CR")


def gate_report(p: Project, phase: str) -> list[str]:
    """Reasons why a phase cannot start (empty list = gate passed)."""
    missing = []
    need = {"spec": ["brief"], "architecture": ["spec"], "plan": ["spec", "architecture"], "build": ["spec"]}
    if phase not in need:
        raise ValueError(f"unknown phase '{phase}' (brief has no gate; use spec, architecture, plan or build)")
    for name in need[phase]:
        if name == "architecture" and p.waived("G3"):
            continue
        if not p.is_approved(name):
            missing.append(f"{name} is not approved")
    if phase == "build":
        if not any(d["status"] in ("launched",) for d in p.epics.values()):
            missing.append("no launched epic (approve launch EP-n)")
    return missing

