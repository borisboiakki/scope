"""State-changing workflow commands: approve, waive, reopen, story, cr."""
from __future__ import annotations

import re

from .checks import check_project
from .model import VERSIONED, Project, id_list
from .util import ScopeError, now, read, set_fm_field, set_section_field, sort_ids, today, version_tuple, write

BLOCK_CODES = {f"B{i}" for i in range(1, 8)}


def _set_doc_status(doc, status: str):
    write(doc.path, set_fm_field(read(doc.path), "status", status))


def _set_epic_status(p: Project, ep: str, status: str):
    doc = p.docs["epics"]
    write(doc.path, set_section_field(read(doc.path), ep, "Status", status))


def _set_release_status(p: Project, rel: str, status: str):
    doc = p.docs["roadmap"]
    write(doc.path, set_section_field(read(doc.path), rel, "Status", status))


def _record(p: Project, target: str, by: str, version=None, sha=None, items=None, **extra):
    rec = {"target": target, "date": now(), "by": by}
    if version is not None:
        rec["version"] = str(version)
    if sha:
        rec["sha256"] = sha
    if items:
        rec["items"] = items
    rec.update({k: v for k, v in extra.items() if v is not None})
    p.state["approvals"].append(rec)
    p.log(f"approved {target} by {by}")


def _require_clean(p: Project, allow_blocking: bool = False, extra_release: str | None = None,
                   ignore: tuple = ()):
    report = check_project(p, extra_release)
    problems = [e for e in report.errors if not e.startswith(ignore)] if ignore else list(report.errors)
    if not allow_blocking:
        problems += [f"blocking register item open: {i}" for i in p.blocking_items()]
    if problems:
        raise ScopeError("approval refused:\n  " + "\n  ".join(problems))
    return report


def _close_reopen(p: Project, target: str):
    for x in p.state.get("reopens", []):
        if x.get("target") == target and not x.get("closed"):
            x["closed"] = now()


def _approve_doc(p: Project, target: str, doc, by: str) -> str:
    """Approve a versioned document (brief, spec, architecture, roadmap, ADR). Returns a message."""
    last = p.last_approval(target)
    text = read(doc.path)
    version = doc.version or "0.1"
    if target in VERSIONED or target.startswith("ADR-"):
        vt = version_tuple(version)
        if last is None and vt < (1, 0):
            version = "1.0"
            text = set_fm_field(text, "version", version)
        elif last is not None:
            changed = doc.hash() != last.get("sha256") or doc.status != "approved"
            if doc.status == "approved" and not changed:
                return f"{target} already approved (v{last.get('version')})"
            if version_tuple(version) <= version_tuple(last.get("version", "0.0")):
                raise ScopeError(f"{target}: bump the version above {last.get('version')} before re-approval "
                                 "(minor for wording, major for behaviour changes)")
    text = set_fm_field(text, "status", "approved")
    write(doc.path, text)
    doc.text = text
    from .util import content_hash
    _record(p, target, by, version=version, sha=content_hash(text))
    _close_reopen(p, target)
    return f"approved {target} v{version}"


def approve(p: Project, target: list[str], by: str, mode: str | None = None, carry: str | None = None,
            reason: str | None = None) -> str:
    if not target:
        raise ScopeError("approve what? brief | spec | architecture | ADR-n | plan R<n> | launch EP-n | ST-n | CR-n | "
                         "release-close R<n>")
    head = target[0]
    if re.fullmatch(r"CR-\d+", head):
        return _approve_cr(p, head, by)
    if head in ("brief", "spec", "architecture") or re.fullmatch(r"ADR-\d+", head):
        _require_clean(p)
        return _approve_artifact(p, head, by)
    if head == "plan":
        return _approve_plan(p, _arg(target, "plan R<n>"), by)
    if head == "launch":
        return _launch(p, _arg(target, "launch EP-n"), by, mode)
    if re.fullmatch(r"ST-\d+", head):
        return _approve_story(p, head, by)
    if head == "release-close":
        return _close_release(p, _arg(target, "release-close R<n>"), by, carry, reason)
    raise ScopeError(f"unknown approval target '{head}'")


def _arg(target, usage):
    if len(target) < 2:
        raise ScopeError(f"usage: approve {usage}")
    return target[1]


def _approve_artifact(p: Project, name: str, by: str) -> str:
    prereq = {"spec": "brief", "architecture": "spec"}
    if name.startswith("ADR-"):
        doc = p.adrs.get(name)
        if not doc:
            raise ScopeError(f"{name} not found in docs/scope/adr/")
        if not p.is_approved("architecture"):
            raise ScopeError("approve the architecture first (it approves its ADRs together)")
        msg = _approve_doc(p, name, doc, by)
        p.save_state()
        return msg
    doc = p.docs.get(name)
    if not doc:
        raise ScopeError(f"docs/scope/{name}.md not found")
    if name in prereq and not p.is_approved(prereq[name]):
        raise ScopeError(f"{prereq[name]} must be approved before {name}")
    msgs = [_approve_doc(p, name, doc, by)]
    if name == "architecture":
        for aid, adr in p.adrs.items():
            if "#" not in aid and adr.status == "draft":
                msgs.append(_approve_doc(p, aid, adr, by))
        p.state["phase"] = "plan"
    else:
        p.state["phase"] = {"brief": "spec", "spec": "architecture"}[name]
    p.save_state()
    return "\n".join(msgs)


def _approve_plan(p: Project, rel: str, by: str) -> str:
    if rel not in p.releases:
        raise ScopeError(f"{rel} is not in roadmap.md")
    if not p.is_approved("spec"):
        raise ScopeError("spec must be approved before the plan")
    if not (p.is_approved("architecture") or p.waived("G3")):
        raise ScopeError("architecture must be approved (or gate G3 waived) before the plan")
    if "epics" not in p.docs:
        raise ScopeError("docs/scope/epics.md not found")
    epics = p.epics_of_release(rel)
    if not epics:
        raise ScopeError(f"no epic for {rel} in epics.md")
    _require_clean(p, extra_release=rel)
    msgs = [_approve_doc(p, "roadmap", p.docs["roadmap"], by), _approve_plan_epics(p, by)]
    items = {}
    for ep in epics:
        if p.epics[ep]["status"] == "planned":
            _set_epic_status(p, ep, "ready")
        for sid in p.stories_of_epic(ep):
            st = p.stories[sid]
            if st.status in ("draft", "needs-rework"):
                _set_doc_status(st, "ready")
            items[sid] = st.hash()
    _record(p, f"plan {rel}", by, items=items)
    for sid in items:
        _close_reopen(p, sid)
    p.state["phase"] = "build"
    p.state["current"]["release"] = p.state["current"].get("release") or rel
    p.save_state()
    msgs.append(f"approved plan {rel}: {len(epics)} epic(s), {len(items)} story(ies) ready")
    return "\n".join(m for m in msgs if m)


def _approve_plan_epics(p: Project, by: str) -> str:
    doc = p.docs["epics"]
    last = p.last_approval("epics")
    if doc.status == "approved" and last and last.get("sha256") == doc.hash():
        return ""
    text = set_fm_field(read(doc.path), "status", "approved")
    write(doc.path, text)
    from .util import content_hash
    _record(p, "epics", by, sha=content_hash(text))
    _close_reopen(p, "epics")
    return "approved epics.md"


def _launch(p: Project, ep: str, by: str, mode: str | None) -> str:
    d = p.epics.get(ep)
    if not d:
        raise ScopeError(f"{ep} not in epics.md")
    if not p.plan_approved(d["release"]):
        raise ScopeError(f"plan {d['release']} is not approved")
    if d["status"] != "ready":
        raise ScopeError(f"{ep} is '{d['status']}', it must be 'ready' to launch")
    _require_clean(p)
    mode = mode or p.config.get("build", {}).get("mode", "supervised")
    if mode not in ("supervised", "autonomous"):
        raise ScopeError("mode must be supervised or autonomous")
    _set_epic_status(p, ep, "launched")
    rel = d["release"]
    if p.releases.get(rel, {}).get("status") == "planned":
        _set_release_status(p, rel, "active")
    _record(p, f"launch {ep}", by, mode=mode)
    p.state["current"].update({"release": rel, "epic": ep, "build_mode": mode})
    p.state.setdefault("epic_modes", {})[ep] = mode
    p.save_state()
    return f"launched {ep} ({mode})"


def _approve_story(p: Project, sid: str, by: str) -> str:
    st = p.stories.get(sid)
    if not st:
        raise ScopeError(f"{sid} not found")
    if st.status != "in-review":
        raise ScopeError(f"{sid} is '{st.status}'; it must be 'in-review' with a PASS review")
    reviews = st.reviews()
    if not reviews or reviews[-1][1] != "PASS":
        raise ScopeError(f"{sid}: the last review verdict is not PASS")
    _require_clean(p)
    _set_doc_status(st, "done")
    _record(p, sid, by)
    msg = f"approved {sid}: done"
    p.state["current"]["story"] = None
    msg += _maybe_epic_done(p, str(st.fm.get("epic")))
    p.save_state()
    return msg


def _maybe_epic_done(p: Project, ep: str) -> str:
    fresh = Project(p.root)
    sts = fresh.stories_of_epic(ep)
    if sts and all(fresh.stories[s].status in ("done", "removed") for s in sts if s in fresh.stories):
        _set_epic_status(p, ep, "done")
        p.log(f"{ep} done")
        if p.state["current"].get("epic") == ep:
            p.state["current"]["epic"] = None
        return f"\n{ep} done: all its stories are done"
    return ""


def _approve_cr(p: Project, cid: str, by: str) -> str:
    cr = p.crs.get(cid)
    if not cr:
        raise ScopeError(f"{cid} not found")
    if cr.status != "proposed":
        raise ScopeError(f"{cid} is '{cr.status}', only a proposed CR can be approved")
    # a CR is how drift is fixed, so drift errors (E15, E16) do not prevent its approval
    _require_clean(p, allow_blocking=True, ignore=("E15", "E16"))
    _set_doc_status(cr, "approved")
    items = {}
    if str(cr.fm.get("quick")).lower() == "true":
        for sid in id_list(cr.fm.get("affects")):
            st = p.stories.get(sid)
            if st and st.status == "draft":
                _set_doc_status(st, "ready")
                items[sid] = st.hash()
    _record(p, cid, by, items=items or None)
    p.save_state()
    extra = f" ({len(items)} quick story(ies) ready)" if items else ""
    return f"approved {cid}{extra}; apply it with scope.py reopen <artifact> --cr {cid}"


def _close_release(p: Project, rel: str, by: str, carry: str | None, reason: str | None) -> str:
    d = p.releases.get(rel)
    if not d:
        raise ScopeError(f"{rel} not in roadmap.md")
    if d["status"] == "released":
        raise ScopeError(f"{rel} is already released")
    open_stories = [s for ep in p.epics_of_release(rel) for s in p.stories_of_epic(ep)
                    if s in p.stories and p.stories[s].status not in ("done", "removed")]
    open_reqs = [rid for rid, q in p.reqs.items() if not q["removed"] and p.effective_release(rid) == rel
                 and not p.req_done(rid)]
    if (open_stories or open_reqs) and not carry:
        raise ScopeError(f"{rel} has unfinished work: stories {', '.join(open_stories) or '-'}; requirements "
                         f"{', '.join(open_reqs) or '-'}. Finish it or close with --carry R<n> --reason \"…\"")
    if carry and (carry not in p.releases or not reason):
        raise ScopeError("--carry needs a release defined in roadmap.md and a --reason")
    _require_clean(p)
    from .reports import release_notes
    notes = release_notes(p, rel, open_stories, open_reqs, carry, reason)
    write(p.dir / "reports" / f"release-{rel}.md", notes)
    _set_release_status(p, rel, "released")
    if open_stories or open_reqs:
        p.state["carryover"].append({"from": rel, "to": carry, "items": sort_ids(open_reqs + open_stories),
                                     "reason": reason, "date": today()})
    _record(p, f"release-close {rel}", by)
    for name in ("roadmap", "epics"):
        if name in p.docs and p.docs[name].status == "approved":
            _set_doc_status(p.docs[name], "draft")
            p.state.setdefault("reopens", []).append({"target": name, "cr": f"release-close {rel}", "date": now()})
    p.state["phase"] = "plan"
    p.state["current"] = {"release": carry or None, "epic": None, "story": None, "build_mode": None}
    p.save_state()
    return f"released {rel}; notes in docs/scope/reports/release-{rel}.md; roadmap and epics reopened for planning"


def waive(p: Project, gate: str, reason: str, by: str) -> str:
    if gate != "G3":
        raise ScopeError("only G3 (architecture) can be waived")
    if not reason:
        raise ScopeError("--reason is required")
    p.state["waivers"].append({"gate": gate, "reason": reason, "by": by, "date": now()})
    p.log(f"waived {gate}: {reason}")
    if p.state.get("phase") == "architecture":
        p.state["phase"] = "plan"
    p.save_state()
    return f"waived {gate}"


def reopen(p: Project, target: str, cr_id: str) -> str:
    cr = p.crs.get(cr_id)
    if not cr or cr.status != "approved":
        raise ScopeError(f"{cr_id} must exist and be approved to reopen anything")
    if target in p.docs and target != "register":
        doc, new = p.docs[target], "draft"
    elif target in p.adrs:
        doc, new = p.adrs[target], "draft"
    elif target in p.stories:
        doc, new = p.stories[target], "needs-rework"
    else:
        raise ScopeError(f"cannot reopen '{target}'")
    _set_doc_status(doc, new)
    p.state.setdefault("reopens", []).append({"target": target, "cr": cr_id, "date": now()})
    p.log(f"reopened {target} for {cr_id}")
    p.save_state()
    hint = "re-approve the plan of its release" if new == "needs-rework" else f"bump its version and approve {target}"
    return f"{target} -> {new} for {cr_id}; apply the change, then {hint}"


def cr_action(p: Project, action: str, cid: str, by: str) -> str:
    cr = p.crs.get(cid)
    if not cr:
        raise ScopeError(f"{cid} not found")
    if action == "reject":
        if cr.status != "proposed":
            raise ScopeError(f"{cid} is '{cr.status}'")
        _set_doc_status(cr, "rejected")
        p.log(f"{cid} rejected by {by}")
        p.save_state()
        return f"{cid} rejected"
    if action == "close":
        if cr.status != "approved":
            raise ScopeError(f"{cid} is '{cr.status}', it must be approved")
        pending = [x["target"] for x in p.state.get("reopens", []) if x.get("cr") == cid and not x.get("closed")]
        if pending:
            raise ScopeError(f"{cid}: still reopened, approve again: {', '.join(pending)}")
        _set_doc_status(cr, "applied")
        p.log(f"{cid} applied")
        p.save_state()
        return f"{cid} applied"
    raise ScopeError("cr action must be close or reject")


def story(p: Project, action: str, sid: str, code: str | None = None, summary: str | None = None) -> str:
    st = p.stories.get(sid)
    if not st:
        raise ScopeError(f"{sid} not found")
    ep = str(st.fm.get("epic"))
    epic = p.epics.get(ep, {})
    status = st.status
    if action == "start":
        if status != "ready":
            raise ScopeError(f"{sid} is '{status}'; only a ready story can start")
        if epic.get("status") != "launched":
            raise ScopeError(f"{ep} is not launched (approve launch {ep})")
        deps = [d for d in id_list(st.fm.get("depends_on")) if d in p.stories and p.stories[d].status != "done"]
        if deps:
            raise ScopeError(f"{sid} depends on unfinished {', '.join(deps)}")
        if p.blocking_items():
            raise ScopeError("blocking register items are open: " + ", ".join(p.blocking_items()))
        _set_doc_status(st, "in-progress")
        p.state["current"].update({"story": sid, "epic": ep})
        msg = f"{sid} in progress"
    elif action == "review":
        if status != "in-progress":
            raise ScopeError(f"{sid} is '{status}', it must be in progress")
        _set_doc_status(st, "in-review")
        msg = f"{sid} in review (cycle {len(st.reviews()) + 1})"
    elif action == "rework":
        if status != "in-review":
            raise ScopeError(f"{sid} is '{status}', it must be in review")
        _set_doc_status(st, "in-progress")
        msg = f"{sid} back in progress"
    elif action == "done":
        mode = p.state.get("epic_modes", {}).get(ep, p.state["current"].get("build_mode"))
        if mode != "autonomous":
            raise ScopeError(f"{sid}: supervised mode, the human approves the story (approve {sid})")
        reviews = st.reviews()
        if status != "in-review" or len(reviews) < 2 or reviews[-1][1] != "PASS":
            raise ScopeError(f"{sid}: autonomous mode needs 2 review cycles and a final PASS "
                             f"(found {len(reviews)}, last {reviews[-1][1] if reviews else '-'})")
        _set_doc_status(st, "done")
        p.state["current"]["story"] = None
        msg = f"{sid} done" + _maybe_epic_done(p, ep)
    elif action == "block":
        if code not in BLOCK_CODES or not summary:
            raise ScopeError("block needs --code B1..B7 and --summary")
        _set_doc_status(st, "blocked")
        if epic:
            _set_epic_status(p, ep, "blocked")
        p.state["blockers"].append({"story": sid, "code": code, "summary": summary, "date": now(), "resolved": False,
                                    "previous": status})
        msg = f"{sid} BLOCKED ({code}): {summary}. The human must decide."
    elif action == "unblock":
        if status != "blocked":
            raise ScopeError(f"{sid} is not blocked")
        prev = "in-progress"
        for b in p.state["blockers"]:
            if b.get("story") == sid and not b.get("resolved"):
                b["resolved"] = now()
                prev = b.get("previous") if b.get("previous") in ("ready", "in-progress", "in-review") else prev
        _set_doc_status(st, prev)
        if epic.get("status") == "blocked":
            _set_epic_status(p, ep, "launched")
        msg = f"{sid} unblocked -> {prev}"
    else:
        raise ScopeError("story action must be start, review, rework, done, block or unblock")
    p.log(f"story {action} {sid}")
    p.save_state()
    return msg
