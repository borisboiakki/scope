"""Load and parse the SCOPE artifacts of a project (formats: docs/artifacts.md)."""
from __future__ import annotations

import re
from pathlib import Path

from .util import (FIELD_RE, HEADING_RE, ScopeError, content_hash, ids_in, parse_front_matter, raw_fm_value,
                   read, strip_comments, yaml_module)

DOCS = ("brief", "spec", "architecture", "roadmap", "epics", "register")
VERSIONED = ("brief", "spec", "architecture", "roadmap", "epics")
REQ_H = re.compile(r"^###\s+(?P<id>(?:FR|NFR)-\d+)\b\s*(?P<title>.*)$")
BR_H = re.compile(r"^###\s+(?P<id>BR-\d+)\b\s*(?P<title>.*)$")
REL_H = re.compile(r"^##\s+(?P<id>R\d+)\b\s*[—–-]?\s*(?P<title>.*)$")
LATER_H = re.compile(r"^##\s+(?P<id>Later)\b(?P<title>.*)$", re.I)
EP_H = re.compile(r"^##\s+(?P<id>EP-\d+)\b\s*(?P<title>.*)$")
AC_RE = re.compile(r"^\s*-\s*\*\*(?P<id>(?:FR|NFR)-\d+\.\d+)\*\*\s*(?P<text>.*)$")
EP_ROW = re.compile(r"^\|\s*(?P<order>\d+)\s*\|\s*(?P<id>ST-\d+)\s*\|(?P<title>[^|]*)\|(?P<deps>[^|]*)\|(?P<size>[^|]*)\|")
REG_ROW = re.compile(r"^\|\s*(?P<id>(?:ASM|OQ)-\d+)\s*\|")
REVIEW_ROW = re.compile(r"^\|\s*(?P<cycle>\d+)\s*\|\s*(?P<verdict>PASS|CHANGES|BLOCKED)\b", re.I)
IMPL_HEADING = re.compile(r"^##\s+Implementation record\s*$", re.M)

STATUSES = {
    "artifact": {"draft", "approved", "superseded"},
    "release": {"planned", "active", "released"},
    "epic": {"planned", "ready", "launched", "done", "blocked"},
    "story": {"draft", "ready", "in-progress", "in-review", "done", "blocked", "needs-rework", "removed"},
    "cr": {"proposed", "approved", "applied", "rejected"},
    "register": {"open", "validated", "invalidated", "answered", "closed"},
}


def sections(text: str, pattern: re.Pattern) -> list[dict]:
    """Split text into sections whose heading matches pattern; a section ends at a heading of same or higher level."""
    result, cur = [], None
    for i, line in enumerate(text.split("\n")):
        h = HEADING_RE.match(line)
        if cur and h and len(h.group(1)) <= cur["level"]:
            result.append(cur)
            cur = None
        m = pattern.match(line)
        if m:
            cur = {"id": m.group("id"), "title": m.group("title").strip(), "level": len(h.group(1)),
                   "line": i + 1, "lines": [line]}
        elif cur:
            cur["lines"].append(line)
    if cur:
        result.append(cur)
    for sec in result:
        sec["text"] = "\n".join(sec.pop("lines"))
    return result


def fields(text: str) -> dict[str, str]:
    out = {}
    for line in strip_comments(text).split("\n"):
        m = FIELD_RE.match(line)
        if m:
            out.setdefault(m.group("key").strip().lower(), m.group("value").strip())
    return out


def id_list(value) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip() and str(v).strip().lower() not in ("none", "—", "-")]
    return ids_in(str(value))


class Doc:
    def __init__(self, path: Path):
        self.path = path
        self.text = read(path)
        self.error = None
        try:
            self.fm, self.body = parse_front_matter(self.text)
        except Exception as exc:  # YAML errors are reported by check
            self.fm, self.body, self.error = None, self.text, f"invalid front matter: {exc}"
        if self.fm is None and self.error is None:
            self.error = "missing front matter"
        self.fm = self.fm or {}

    @property
    def status(self) -> str:
        return str(self.fm.get("status", "")).strip()

    @property
    def version(self) -> str | None:
        return raw_fm_value(self.text, "version")

    def title(self) -> str:
        m = re.search(r"^#\s+(?:\S+\s+)?(.*)$", self.body, re.M)
        return m.group(1).strip() if m else ""

    def hash(self) -> str:
        return content_hash(self.text)


class Story(Doc):
    def definition(self) -> str:
        m = IMPL_HEADING.search(self.text)
        return self.text[: m.start()] if m else self.text

    def hash(self) -> str:
        return content_hash(self.definition())

    def reviews(self) -> list[tuple[int, str]]:
        m = re.search(r"^##\s+Review record\s*$(.*?)(?=^##\s|\Z)", self.text, re.M | re.S)
        rows = []
        for line in (m.group(1) if m else "").split("\n"):
            r = REVIEW_ROW.match(line)
            if r:
                rows.append((int(r.group("cycle")), r.group("verdict").upper()))
        return rows

    def title(self) -> str:
        m = re.search(r"^#\s+ST-\d+\s+(.*)$", self.body, re.M)
        return m.group(1).strip() if m else ""


class Project:
    def __init__(self, root: Path):
        self.root = Path(root).resolve()
        self.dir = self.root / "docs" / "scope"
        if not (self.dir / "state.yaml").exists():
            raise ScopeError(f"no SCOPE project at {self.root} (run `scope.py init`)")
        yaml = yaml_module()
        self.config = yaml.safe_load(read(self.dir / "config.yaml")) or {} if (self.dir / "config.yaml").exists() else {}
        self.state = yaml.safe_load(read(self.dir / "state.yaml")) or {}
        for key, default in (("approvals", []), ("blockers", []), ("waivers", []), ("history", []),
                             ("carryover", []), ("branches", {}), ("current", {})):
            if self.state.get(key) is None:
                self.state[key] = default
        self.docs: dict[str, Doc] = {}
        for name in DOCS:
            p = self.dir / f"{name}.md"
            if p.exists():
                self.docs[name] = Doc(p)
        self.adrs = self._load_dir("adr", "ADR", Doc)
        self.stories: dict[str, Story] = self._load_dir("stories", "ST", Story)
        self.crs = self._load_dir("changes", "CR", Doc)
        self.parse_errors: list[str] = []
        self._parse()

    # ---------- loading ----------
    def _load_dir(self, sub: str, prefix: str, cls):
        out = {}
        d = self.dir / sub
        for p in sorted(d.glob(f"{prefix}-*.md")) if d.exists() else []:
            doc = cls(p)
            m = re.match(rf"({prefix}-\d+)", p.name)
            doc.id = str(doc.fm.get("id") or (m.group(1) if m else p.stem))
            doc.file_id = m.group(1) if m else None
            out.setdefault(doc.id, doc)
            if out[doc.id] is not doc:
                doc.duplicate = True
                out.setdefault(f"{doc.id}#dup{len(out)}", doc)
        return out

    def _parse(self):
        self.brs, self.reqs, self.acs = {}, {}, {}
        self.releases, self.later, self.epics, self.register = {}, [], {}, {}
        if "brief" in self.docs:
            for s in sections(self.docs["brief"].body, BR_H):
                self._define(self.brs, s["id"], {"title": s["title"], "text": s["text"]}, "brief.md")
        if "spec" in self.docs:
            for s in sections(self.docs["spec"].body, REQ_H):
                f = fields(s["text"])
                acs = []
                for line in strip_comments(s["text"]).split("\n"):
                    m = AC_RE.match(line)
                    if m:
                        acs.append(m.group("id"))
                        self._define(self.acs, m.group("id"), {"req": s["id"], "text": line.strip()}, "spec.md")
                        if not m.group("id").startswith(s["id"] + "."):
                            self.parse_errors.append(f"spec.md: {m.group('id')} is listed under {s['id']}")
                self._define(self.reqs, s["id"], {
                    "title": s["title"], "text": s["text"], "release": f.get("release", "").strip(),
                    "sources": ids_in(f.get("source", "")), "acs": acs,
                    "removed": "removed by" in s["title"].lower(), "kind": s["id"].split("-")[0]}, "spec.md")
        if "roadmap" in self.docs:
            for s in sections(self.docs["roadmap"].body, REL_H):
                f = fields(s["text"])
                self._define(self.releases, s["id"], {
                    "title": s["title"], "text": s["text"], "status": f.get("status", "planned"),
                    "in_scope": ids_in(f.get("in scope", "")), "epics": ids_in(f.get("epics", "")),
                    "out_of_scope": ids_in(f.get("out of scope", ""))}, "roadmap.md")
            for s in sections(self.docs["roadmap"].body, LATER_H):
                self.later = [i for i in ids_in(s["text"]) if i.startswith(("FR", "NFR"))]
        if "epics" in self.docs:
            for s in sections(self.docs["epics"].body, EP_H):
                f = fields(s["text"])
                rows = []
                for line in s["text"].split("\n"):
                    m = EP_ROW.match(line)
                    if m:
                        rows.append({"order": int(m.group("order")), "id": m.group("id"), "title": m.group("title").strip(),
                                     "deps": ids_in(m.group("deps")), "size": m.group("size").strip()})
                self._define(self.epics, s["id"], {
                    "title": s["title"], "text": s["text"], "release": f.get("release", "").strip(),
                    "status": f.get("status", "planned"), "requirements": ids_in(f.get("requirements", "")),
                    "rows": sorted(rows, key=lambda r: r["order"])}, "epics.md")
        if "register" in self.docs:
            for line in self.docs["register"].body.split("\n"):
                if REG_ROW.match(line):
                    cells = [c.strip() for c in line.strip().strip("|").split("|")]
                    cells += [""] * (7 - len(cells))
                    self._define(self.register, cells[0], {
                        "statement": cells[1], "raised": cells[2], "blocking": cells[3].lower(),
                        "impacts": ids_in(cells[4]), "status": cells[5].lower(), "resolution": cells[6],
                        "line": line}, "register.md")

    def _define(self, table: dict, ident: str, data: dict, where: str):
        if ident in table:
            self.parse_errors.append(f"{where}: duplicate {ident}")
            return
        table[ident] = data

    # ---------- queries ----------
    def defined_ids(self) -> set[str]:
        ids = set(self.brs) | set(self.reqs) | set(self.acs) | set(self.releases) | set(self.epics) | set(self.register)
        ids |= {i for i in self.adrs if "#" not in i} | {i for i in self.stories if "#" not in i}
        ids |= {i for i in self.crs if "#" not in i}
        return ids

    def all_files(self):
        for doc in self.docs.values():
            yield doc
        for table in (self.adrs, self.stories, self.crs):
            yield from table.values()

    def req_of(self, ident: str) -> str:
        return self.acs[ident]["req"] if ident in self.acs else ident

    def effective_release(self, req_id: str) -> str:
        rel = self.reqs.get(req_id, {}).get("release", "")
        for c in self.state.get("carryover", []):
            if req_id in c.get("items", []):
                rel = c.get("to", rel)
        return rel

    def stories_implementing(self, req_id: str) -> list[str]:
        return [sid for sid, s in self.stories.items() if "#" not in sid
                and any(self.req_of(i) == req_id or i == req_id for i in id_list(s.fm.get("implements")))]

    def stories_of_epic(self, ep: str) -> list[str]:
        rows = [r["id"] for r in self.epics.get(ep, {}).get("rows", [])]
        extra = [sid for sid, s in self.stories.items() if str(s.fm.get("epic")) == ep and sid not in rows and "#" not in sid]
        return rows + extra

    def epics_of_release(self, rel: str) -> list[str]:
        return [e for e, d in self.epics.items() if d["release"] == rel]

    def req_done(self, req_id: str) -> bool:
        sts = self.stories_implementing(req_id)
        return bool(sts) and all(self.stories[s].status in ("done", "removed") for s in sts) \
            and any(self.stories[s].status == "done" for s in sts)

    def approvals_for(self, target: str) -> list[dict]:
        return [a for a in self.state["approvals"] if a.get("target") == target]

    def last_approval(self, target: str) -> dict | None:
        found = self.approvals_for(target)
        return found[-1] if found else None

    def is_approved(self, name: str) -> bool:
        doc = self.docs.get(name)
        return bool(doc and doc.status == "approved" and self.last_approval(name))

    def waived(self, gate: str) -> bool:
        return any(w.get("gate") == gate for w in self.state["waivers"])

    def plan_approved(self, rel: str) -> bool:
        return self.last_approval(f"plan {rel}") is not None

    def blocking_items(self) -> list[str]:
        return [i for i, r in self.register.items() if r["status"] == "open" and r["blocking"] in ("yes", "y", "true")]

    def story_hash_record(self, sid: str) -> str | None:
        """Latest approved hash of a story definition (plan approval or quick CR)."""
        for a in reversed(self.state["approvals"]):
            items = a.get("items") or {}
            if sid in items:
                return items[sid]
        return None

    # ---------- saving ----------
    def save_state(self):
        yaml = yaml_module()
        text = "# SCOPE state. Managed by scope.py only: do not edit by hand.\n"
        text += yaml.safe_dump(self.state, sort_keys=False, allow_unicode=True, width=120)
        (self.dir / "state.yaml").write_text(text, encoding="utf-8", newline="\n")

    def save_config(self):
        yaml = yaml_module()
        text = "# SCOPE configuration. Change it with `scope.py config` (see METHOD.md section 10).\n"
        text += yaml.safe_dump(self.config, sort_keys=False, allow_unicode=True, width=120)
        (self.dir / "config.yaml").write_text(text, encoding="utf-8", newline="\n")

    def log(self, message: str):
        from .util import now
        self.state["history"].append(f"{now()} {message}")

