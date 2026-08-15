#!/usr/bin/env python3
"""
ooxml.py — self-contained WordprocessingML helpers for the contract-review skill.

Original implementation (no third-party skill code) covering exactly what the
redliner needs against an unpacked .docx directory:

  add_comment(doc_dir, text, author, initials, parent_id=None, comment_id=None)
      -> (comment_id:int, para_id:str, "ok")
      Creates/extends the five comment parts (comments, commentsExtended,
      commentsIds, commentsExtensible, people), registering content-types and
      document relationships as needed. Threads replies via parent_id. Does NOT
      touch document.xml — the caller places the range markers.

  merge_runs(doc_dir)
      Coalesces adjacent identical-formatted <w:r><w:t> runs within each
      paragraph so a clause reads as one contiguous run (best-effort; skipped
      quietly if lxml is unavailable or parsing fails).

The comment-part XML skeletons are the standard OOXML / Microsoft-extension
namespace declarations defined by ECMA-376 and the [MS-DOCX] extensions.
"""
from __future__ import annotations
import random
import re
from datetime import datetime, timezone
from pathlib import Path
from xml.sax.saxutils import escape as _xml_escape

# ---- namespaces / content-types / relationship types -----------------------

_NS = (
    'xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006" '
    'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
    'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
    'xmlns:w14="http://schemas.microsoft.com/office/word/2010/wordml" '
    'xmlns:w15="http://schemas.microsoft.com/office/word/2012/wordml" '
    'xmlns:w16cex="http://schemas.microsoft.com/office/word/2018/wordml/cex" '
    'xmlns:w16cid="http://schemas.microsoft.com/office/word/2016/wordml/cid"'
)

_SKELETONS = {
    "comments.xml": f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
                    f'<w:comments {_NS} mc:Ignorable="w14 w15 w16cid w16cex">\n</w:comments>',
    "commentsExtended.xml": f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
                    f'<w15:commentsEx {_NS} mc:Ignorable="w14 w15 w16cid w16cex">\n</w15:commentsEx>',
    "commentsIds.xml": f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
                    f'<w16cid:commentsIds {_NS} mc:Ignorable="w14 w15 w16cid w16cex">\n</w16cid:commentsIds>',
    "commentsExtensible.xml": f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
                    f'<w16cex:commentsExtensible {_NS} '
                    f'xmlns:cr="http://schemas.microsoft.com/office/comments/2020/reactions" '
                    f'mc:Ignorable="w14 w15 w16cid w16cex cr">\n</w16cex:commentsExtensible>',
    "people.xml": '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
                    '<w15:people xmlns:w15="http://schemas.microsoft.com/office/word/2012/wordml">\n</w15:people>',
}

_CT = {
    "comments.xml": "application/vnd.openxmlformats-officedocument.wordprocessingml.comments+xml",
    "commentsExtended.xml": "application/vnd.openxmlformats-officedocument.wordprocessingml.commentsExtended+xml",
    "commentsIds.xml": "application/vnd.openxmlformats-officedocument.wordprocessingml.commentsIds+xml",
    "commentsExtensible.xml": "application/vnd.openxmlformats-officedocument.wordprocessingml.commentsExtensible+xml",
    "people.xml": "application/vnd.openxmlformats-officedocument.wordprocessingml.people+xml",
}

_REL = {
    "comments.xml": "http://schemas.openxmlformats.org/officeDocument/2006/relationships/comments",
    "commentsExtended.xml": "http://schemas.microsoft.com/office/2011/relationships/commentsExtended",
    "commentsIds.xml": "http://schemas.microsoft.com/office/2016/09/relationships/commentsIds",
    "commentsExtensible.xml": "http://schemas.microsoft.com/office/2018/08/relationships/commentsExtensible",
    "people.xml": "http://schemas.microsoft.com/office/2011/relationships/people",
}


def _rand_hex8(seen: set) -> str:
    # paraId / durableId are signed 32-bit in OOXML: keep the value < 0x80000000
    # by constraining the high nibble to 0-7. Also avoid 00000000.
    while True:
        v = (random.choice("1234567")
             + "".join(random.choice("0123456789ABCDEF") for _ in range(7)))
        if v not in seen:
            seen.add(v)
            return v


def _ensure_parts(word: Path):
    """Create any missing comment parts, and register content-types + rels."""
    for fname, skel in _SKELETONS.items():
        p = word / fname
        if not p.exists():
            p.write_text(skel, encoding="utf-8")

    # [Content_Types].xml overrides
    ct = word.parent / "[Content_Types].xml"
    if ct.exists():
        s = ct.read_text(encoding="utf-8")
        adds = ""
        for fname, ctype in _CT.items():
            if f'/word/{fname}"' not in s:
                adds += f'<Override PartName="/word/{fname}" ContentType="{ctype}"/>'
        if adds:
            s = s.replace("</Types>", adds + "</Types>")
            ct.write_text(s, encoding="utf-8")

    # word/_rels/document.xml.rels relationships
    rels = word / "_rels" / "document.xml.rels"
    if rels.exists():
        s = rels.read_text(encoding="utf-8")
        existing = set(re.findall(r'Id="([^"]+)"', s))
        base = 9100
        adds = ""
        for fname, rtype in _REL.items():
            if f'Target="{fname}"' not in s:
                while f"rId{base}" in existing:
                    base += 1
                rid = f"rId{base}"; existing.add(rid); base += 1
                adds += f'<Relationship Id="{rid}" Type="{rtype}" Target="{fname}"/>'
        if adds:
            s = s.replace("</Relationships>", adds + "</Relationships>")
            rels.write_text(s, encoding="utf-8")


def _para_id_for_comment(comments_xml: str, cid: int):
    m = re.search(rf'<w:comment[^>]*\bw:id="{cid}"[^>]*>\s*<w:p[^>]*w14:paraId="([0-9A-Fa-f]+)"',
                  comments_xml)
    return m.group(1) if m else None


def add_comment(doc_dir, text, author="Reviewer", initials="R",
                parent_id=None, comment_id=None):
    """Append a comment (or reply) to the unpacked docx at doc_dir. Returns
    (comment_id, para_id, "ok"). Caller places range markers in document.xml."""
    word = Path(doc_dir) / "word"
    _ensure_parts(word)

    comments = word / "comments.xml"
    ext = word / "commentsExtended.xml"
    ids = word / "commentsIds.xml"
    cex = word / "commentsExtensible.xml"
    people = word / "people.xml"

    c_txt = comments.read_text(encoding="utf-8")
    e_txt = ext.read_text(encoding="utf-8")
    i_txt = ids.read_text(encoding="utf-8")
    x_txt = cex.read_text(encoding="utf-8")
    p_txt = people.read_text(encoding="utf-8")

    # ids
    used_cids = [int(n) for n in re.findall(r'<w:comment[^>]*\bw:id="(\d+)"', c_txt)]
    cid = comment_id if comment_id is not None else (max(used_cids) + 1 if used_cids else 0)
    seen_hex = set(re.findall(r'w14:paraId="([0-9A-Fa-f]+)"', c_txt)) \
        | set(re.findall(r'w16cid:durableId="([0-9A-Fa-f]+)"', i_txt))
    para_id = _rand_hex8(seen_hex)
    durable = _rand_hex8(seen_hex)
    date = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    body = _xml_escape(text)
    auth = _xml_escape(author)
    inits = _xml_escape(initials or (author[:2] if author else "R"))

    comment = (
        f'<w:comment w:id="{cid}" w:author="{auth}" w:date="{date}" w:initials="{inits}">'
        f'<w:p w14:paraId="{para_id}" w14:textId="77777777">'
        f'<w:pPr><w:pStyle w:val="CommentText"/></w:pPr>'
        f'<w:r><w:rPr><w:rStyle w:val="CommentReference"/></w:rPr><w:annotationRef/></w:r>'
        f'<w:r><w:t xml:space="preserve">{body}</w:t></w:r>'
        f'</w:p></w:comment>'
    )
    comments.write_text(c_txt.replace("</w:comments>", comment + "\n</w:comments>"), encoding="utf-8")

    # commentsExtended: link the thread (reply carries paraIdParent)
    parent_attr = ""
    if parent_id is not None:
        ppid = _para_id_for_comment(c_txt, parent_id)
        if ppid:
            parent_attr = f' w15:paraIdParent="{ppid}"'
    ex = f'<w15:commentEx w15:paraId="{para_id}"{parent_attr} w15:done="0"/>'
    ext.write_text(e_txt.replace("</w15:commentsEx>", ex + "\n</w15:commentsEx>"), encoding="utf-8")

    # commentsIds
    cidx = f'<w16cid:commentId w16cid:paraId="{para_id}" w16cid:durableId="{durable}"/>'
    ids.write_text(i_txt.replace("</w16cid:commentsIds>", cidx + "\n</w16cid:commentsIds>"),
                   encoding="utf-8")

    # commentsExtensible
    cexx = f'<w16cex:commentExtensible w16cex:durableId="{durable}" w16cex:dateUtc="{date}"/>'
    cex.write_text(x_txt.replace("</w16cex:commentsExtensible>", cexx + "\n</w16cex:commentsExtensible>"),
                   encoding="utf-8")

    # people (dedupe by author)
    if f'w15:author="{auth}"' not in p_txt:
        person = (f'<w15:person w15:author="{auth}">'
                  f'<w15:presenceInfo w15:providerId="None" w15:userId="{auth}"/></w15:person>')
        people.write_text(p_txt.replace("</w15:people>", person + "\n</w15:people>"), encoding="utf-8")

    return cid, para_id, "ok"


# ---- run merging ------------------------------------------------------------

def merge_runs(doc_dir):
    """Best-effort: merge adjacent runs with identical rPr and plain <w:t> text
    within each paragraph, so clause text is one contiguous run. Quietly no-ops
    if lxml is missing or the document can't be parsed."""
    try:
        from lxml import etree
    except Exception:
        return False
    W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
    doc = Path(doc_dir) / "word" / "document.xml"
    try:
        tree = etree.parse(str(doc))
    except Exception:
        return False
    root = tree.getroot()

    def rpr_key(r):
        rpr = r.find(f"{{{W}}}rPr")
        return etree.tostring(rpr) if rpr is not None else b""

    def is_plain_text_run(r):
        # exactly one child that is <w:t> (plus optional rPr); no breaks/drawings
        kids = [c for c in r if not c.tag.endswith("}rPr")]
        return len(kids) == 1 and kids[0].tag == f"{{{W}}}t"

    changed = False
    for para in root.iter(f"{{{W}}}p"):
        run = para.find(f"{{{W}}}r")
        prev = None
        for r in list(para.findall(f"{{{W}}}r")):
            if prev is not None and is_plain_text_run(prev) and is_plain_text_run(r) \
                    and rpr_key(prev) == rpr_key(r):
                tp = prev.find(f"{{{W}}}t")
                tc = r.find(f"{{{W}}}t")
                tp.text = (tp.text or "") + (tc.text or "")
                tp.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
                para.remove(r)
                changed = True
            else:
                prev = r
    if changed:
        tree.write(str(doc), xml_declaration=True, encoding="UTF-8", standalone=True)
    return changed
