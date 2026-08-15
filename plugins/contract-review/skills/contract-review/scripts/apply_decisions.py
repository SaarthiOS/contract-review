#!/usr/bin/env python3
"""Apply reviewed decisions to the ORIGINAL document as tracked changes + comments.

    python apply_decisions.py --original contract.docx --decisions decisions.json \
        --analysis analysis.json --author "Full Name" --initials "FN" \
        -o contract_reviewed.docx [--resolve-agreed]

For each ACCEPTED decision:
  - kind "redline": wraps the original span in <w:del>/<w:ins> authored as the
    user, and (if as_comment) anchors an explanatory comment to the same span.
  - kind "comment" / action "comment": anchors a native comment, no text change.
Rejected decisions do nothing.

Self-contained: uses the bundled ooxml.py for comment plumbing and run-merging
(no external skill dependency). Runs merge_runs first so clause text is findable
as a contiguous run. When a span
isn't a clean single run, it degrades to a comment on that run rather than
risk corrupting the XML, and reports it so the user can edit by hand.

Existing comments are never deleted. With --resolve-agreed, an accepted finding
that overlaps an existing comment thread is added as a REPLY to that thread and
the thread is closed (w15:done="1").
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from datetime import datetime, timezone
from html import unescape
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from ooxml import add_comment, merge_runs as _merge_runs  # bundled, self-contained


def _find_soffice():
    """Locate a LibreOffice binary for legacy .doc conversion, if present."""
    for name in ("soffice", "libreoffice"):
        p = shutil.which(name)
        if p:
            return p
    return None

WNS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


def log(msg):
    print(msg, file=sys.stderr)


# ---------- packaging ----------

def unpack(original: Path, work: Path) -> Path:
    if original.is_dir():
        shutil.copytree(original, work / "unpacked")
        d = work / "unpacked"
    else:
        src = original
        if original.suffix.lower() == ".doc":
            so = _find_soffice()
            if not so:
                sys.exit("Legacy .doc input needs LibreOffice (soffice) on PATH, "
                         "or convert to .docx first.")
            log("Converting legacy .doc → .docx …")
            subprocess.run([so, "--headless", "--convert-to", "docx",
                            "--outdir", str(work), str(original)], check=True)
            src = next(work.glob("*.docx"))
        d = work / "unpacked"
        d.mkdir()
        with zipfile.ZipFile(src) as z:
            z.extractall(d)
    # strip symlinks — external docs are untrusted
    for p in d.rglob("*"):
        if p.is_symlink():
            p.unlink()
    return d


def merge_runs(d: Path):
    try:
        _merge_runs(d)
    except Exception as e:
        log(f"warning: run-merge skipped ({e}); clause matching may be less reliable")


def rezip(d: Path, out: Path):
    if out.exists():
        out.unlink()
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(d.rglob("*")):
            if p.is_file():
                z.write(p, p.relative_to(d).as_posix())


# ---------- text matching in raw document.xml ----------

RUN_SIMPLE = re.compile(
    r"<w:r\b[^>]*>(?P<rpr>(?:<w:rPr\b.*?</w:rPr>)?)"
    r"<w:t(?P<tattr>[^>]*)>(?P<inner>.*?)</w:t></w:r>",
    re.DOTALL)


def norm(s: str) -> str:
    """Normalize for fuzzy comparison: unescape, straighten quotes, collapse ws."""
    s = unescape(s)
    s = (s.replace("\u201c", '"').replace("\u201d", '"')
           .replace("\u2018", "'").replace("\u2019", "'")
           .replace("\u2013", "-").replace("\u2014", "-"))
    return re.sub(r"\s+", " ", s).strip()


def esc_text(s: str) -> str:
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def find_clean_run(xml: str, needle: str):
    """Return the first simple <w:r><w:t>…needle…</w:t></w:r> match object whose
    text contains `needle` (fuzzy). None if no clean single-run match."""
    nn = norm(needle)
    if not nn:
        return None
    for m in RUN_SIMPLE.finditer(xml):
        if nn and nn in norm(m.group("inner")):
            return m
    return None


def locate_needle_in_inner(inner: str, needle: str):
    """Find needle within a run's raw inner text. Returns (start, end, matched_raw)
    or None. Tries raw, escaped, and quote-variant forms."""
    for cand in (needle, esc_text(needle),
                 esc_text(needle).replace("'", "&#x2019;").replace('"', "&#x201C;")):
        i = inner.find(cand)
        if i != -1:
            return i, i + len(cand), cand
    # fuzzy fallback: match on normalized, then map back approximately to full inner
    if norm(needle) and norm(needle) in norm(inner):
        return 0, len(inner), inner
    return None


# ---------- edit builders ----------

def run(rpr: str, tattr: str, text: str) -> str:
    attr = tattr or ' xml:space="preserve"'
    return f"<w:r>{rpr}<w:t{attr}>{text}</w:t></w:r>"


def del_run(rpr: str, text: str, wid: int, author: str, date: str) -> str:
    return (f'<w:del w:id="{wid}" w:author="{author}" w:date="{date}">'
            f'<w:r>{rpr}<w:delText xml:space="preserve">{text}</w:delText></w:r></w:del>')


def ins_run(rpr: str, text: str, wid: int, author: str, date: str) -> str:
    return (f'<w:ins w:id="{wid}" w:author="{author}" w:date="{date}">'
            f'<w:r>{rpr}<w:t xml:space="preserve">{text}</w:t></w:r></w:ins>')


def range_start(cid: int) -> str:
    return f'<w:commentRangeStart w:id="{cid}"/>'


def range_end(cid: int) -> str:
    return (f'<w:commentRangeEnd w:id="{cid}"/>'
            f'<w:r><w:rPr><w:rStyle w:val="CommentReference"/></w:rPr>'
            f'<w:commentReference w:id="{cid}"/></w:r>')


# ---------- existing comments ----------

def existing_ranges(xml: str):
    """Map existing comment id -> anchored plain text (normalized)."""
    out = {}
    for m in re.finditer(r'<w:commentRangeStart w:id="(\d+)"/>(.*?)<w:commentRangeEnd w:id="\1"/>',
                         xml, re.DOTALL):
        cid = int(m.group(1))
        text = "".join(re.findall(r"<w:t[^>]*>(.*?)</w:t>", m.group(2), re.DOTALL))
        out[cid] = norm(text)
    return out


def comment_para_id(word: Path, cid: int):
    cx = word / "comments.xml"
    if not cx.exists():
        return None
    txt = cx.read_text(encoding="utf-8")
    m = re.search(rf'<w:comment[^>]*w:id="{cid}"[^>]*>\s*<w:p[^>]*w14:paraId="([0-9A-Fa-f]+)"',
                  txt)
    return m.group(1) if m else None


def resolve_thread(word: Path, para_id: str):
    ext = word / "commentsExtended.xml"
    if not ext.exists() or not para_id:
        return False
    s = ext.read_text(encoding="utf-8")
    pat = re.compile(rf'(<w15:commentEx w15:paraId="{para_id}"[^>]*w15:done=")0(")')
    s2, n = pat.subn(r"\g<1>1\g<2>", s)
    if n:
        ext.write_text(s2, encoding="utf-8")
    return bool(n)


# ---------- main apply ----------

def comment_body(f: dict, note: str) -> str:
    sev = (f.get("severity") or "").upper()
    cat = (f.get("category") or "").replace("_", " ")
    head = f"[{sev}" + (f" · {cat}" if cat else "") + "] " if sev or cat else ""
    body = head + (f.get("issue") or "")
    if note:
        body += f" — {note}"
    return body.strip()


def main():
    ap = argparse.ArgumentParser(description="Apply reviewed decisions to the original document.")
    ap.add_argument("--original", required=True)
    ap.add_argument("--decisions", required=True)
    ap.add_argument("--analysis", required=True)
    ap.add_argument("--author", default="Reviewer")
    ap.add_argument("--initials", default="R")
    ap.add_argument("-o", "--output", default="reviewed.docx")
    ap.add_argument("--resolve-agreed", action="store_true",
                    help="Reply to & close existing comment threads that overlap an accepted finding")
    args = ap.parse_args()

    analysis = json.loads(Path(args.analysis).read_text(encoding="utf-8"))
    findings = {f["id"]: f for f in analysis.get("findings", [])}
    decisions = json.loads(Path(args.decisions).read_text(encoding="utf-8")).get("decisions", [])

    work = Path(tempfile.mkdtemp(prefix="redline_"))
    d = unpack(Path(args.original), work)
    merge_runs(d)
    doc = d / "word" / "document.xml"
    xml = doc.read_text(encoding="utf-8")
    word = d / "word"

    ex_ranges = existing_ranges(xml)
    date = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    wid = 90000
    report = {"redlined": [], "commented": [], "replied_resolved": [], "degraded": [], "not_found": []}

    for dec in decisions:
        fid = dec.get("id")
        action = dec.get("action")
        f = findings.get(fid)
        if not f or action == "reject":
            continue
        note = dec.get("note", "")
        final_edit = dec.get("final_edit") or f.get("suggested_edit") or ""
        needle = f.get("original_text") or ""
        is_redline = (f.get("kind") != "comment") and action == "accept"
        also_comment = dec.get("as_comment", True)

        # Missing-clause / no anchor text → document-level comment at first paragraph
        anchor_run = find_clean_run(xml, needle) if needle else None

        # Existing-thread reply/resolve
        replied = False
        if args.resolve_agreed and needle:
            nn = norm(needle)
            for cid, atext in ex_ranges.items():
                if atext and (nn in atext or atext in nn):
                    rid, _, _ = add_comment(d, comment_body(f, note or "Agreed; addressing this."),
                                            author=args.author, initials=args.initials, parent_id=cid)
                    pj = comment_para_id(word, cid)
                    resolve_thread(word, pj)
                    report["replied_resolved"].append({"finding": fid, "thread": cid})
                    replied = True
                    break

        if anchor_run is None:
            # No clean run: comment at top of body (document-level note)
            cid, _, _ = add_comment(d, comment_body(f, note), author=args.author, initials=args.initials)
            # place on first run in first paragraph
            first = RUN_SIMPLE.search(xml)
            if first:
                s, e = first.span()
                xml = xml[:s] + range_start(cid) + xml[s:e] + range_end(cid) + xml[e:]
                report["not_found"].append({"finding": fid, "note": "anchored document-level"})
            else:
                report["not_found"].append({"finding": fid, "note": "no anchor placed"})
            continue

        rpr = anchor_run.group("rpr")
        tattr = anchor_run.group("tattr")
        inner = anchor_run.group("inner")
        run_start, run_end = anchor_run.span()
        run_xml = xml[run_start:run_end]

        loc = locate_needle_in_inner(inner, needle)

        if is_redline and loc:
            i, j, matched = loc
            pre, post = inner[:i], inner[j:]
            wid += 1
            block = del_run(rpr, matched, wid, args.author, date)
            wid += 1
            block += ins_run(rpr, esc_text(final_edit), wid, args.author, date)
            parts = []
            if pre:
                parts.append(run(rpr, tattr, pre))
            comment_cid = None
            if also_comment and not replied:
                comment_cid, _, _ = add_comment(d, comment_body(f, note),
                                                author=args.author, initials=args.initials)
                block = range_start(comment_cid) + block + range_end(comment_cid)
            parts.append(block)
            if post:
                parts.append(run(rpr, tattr, post))
            xml = xml[:run_start] + "".join(parts) + xml[run_end:]
            report["redlined"].append({"finding": fid, "comment": comment_cid})

        else:
            # comment-only (accepted comment, or redline we couldn't cleanly split)
            if is_redline and not loc:
                report["degraded"].append({"finding": fid,
                                           "note": "span not cleanly locatable; commented instead of redlined"})
            if not replied:
                cid, _, _ = add_comment(d, comment_body(f, note),
                                        author=args.author, initials=args.initials)
                xml = xml[:run_start] + range_start(cid) + run_xml + range_end(cid) + xml[run_end:]
                report["commented"].append({"finding": fid, "comment": cid})

        # refresh existing-range map is not needed; markers we add use fresh ids

    doc.write_text(xml, encoding="utf-8")
    out = Path(args.output)
    rezip(d, out)

    print(json.dumps(report, indent=2))
    log(f"\nWrote {out}")
    log("Open it in Word (or LibreOffice) with Track Changes shown to review the "
        "redlines and comment threads before sending.")


if __name__ == "__main__":
    main()
