#!/usr/bin/env python3
"""
build_review_widget.py  —  analysis.json  ->  review widget fragment (for the visualizer)

Emits an HTML *fragment* (no doctype/html/head/body) suitable to pass as `widget_code`
to the visualize:show_widget tool. Cards render statically (visible during streaming);
a trailing <script> wires accept/reject/edit toggles and the Apply button.

Apply calls the widget global sendPrompt(text) with a payload identical in shape to
decisions.json, so the same-chat Claude can write it to a file and run apply_decisions.py
with no manual JSON export. A "Copy decisions" button is the fallback where sendPrompt
is unavailable.

Usage:
  python build_review_widget.py analysis.json --source contract.docx -o widget.html
  python build_review_widget.py analysis.json --source contract.docx      # -> stdout
"""
import argparse, html, json, sys
from pathlib import Path

MAX_CURRENT = 320  # chars of original language shown in the collapsed "current" view


def esc(s):
    return html.escape("" if s is None else str(s), quote=True)


def clip(s, n=MAX_CURRENT):
    s = "" if s is None else str(s)
    return s if len(s) <= n else s[: n - 1].rstrip() + "\u2026"


def sev_rank(s):
    return {"critical": 0, "high": 1, "medium": 2, "low": 3}.get((s or "").lower(), 4)


def card_html(f):
    fid = esc(f.get("id", ""))
    kind = (f.get("kind") or "redline").lower()
    sev = (f.get("severity") or "medium").lower()
    cat = esc(f.get("category", ""))
    favors = f.get("favors")
    favors_tag = f'<span class="rv-fav">favours {esc(favors)}</span>' if favors else ""
    issue = esc(f.get("issue", ""))
    current = esc(clip(f.get("original_text", "")))
    suggested = esc(f.get("suggested_edit", ""))
    default_action = "comment" if kind == "comment" else "accept"

    # edit box only for redline-kind findings
    if kind == "comment":
        edit_block = ""
        also = ""
    else:
        edit_block = (
            f'<label class="rv-lbl">Suggested edit \u2014 edit before applying</label>'
            f'<textarea class="rv-edit" rows="3">{suggested}</textarea>'
        )
        also = (
            '<label class="rv-also"><input type="checkbox" class="rv-alsochk" checked> '
            "Also leave an explanatory comment</label>"
        )

    note_ph = (
        "Comment text sent to the counterparty"
        if kind == "comment"
        else "Optional note (kept with the comment)"
    )

    def btn(action, label):
        pressed = "true" if action == default_action else "false"
        return (
            f'<button type="button" class="rv-b rv-{action}" data-action="{action}" '
            f'aria-pressed="{pressed}">{label}</button>'
        )

    actions = btn("accept", "Accept") if kind != "comment" else ""
    actions += btn("comment", "Comment only" if kind != "comment" else "Comment")
    actions += btn("reject", "Reject")

    return f"""<div class="rv-card" data-id="{fid}" data-kind="{kind}" data-severity="{sev}" data-action="{default_action}">
  <div class="rv-top">
    <span class="rv-sev s-{sev}">{esc(sev)}</span>
    <span class="rv-cat">{cat}</span>
    {favors_tag}
    <span class="rv-id">{fid}</span>
  </div>
  <div class="rv-issue">{issue}</div>
  <details class="rv-cur"><summary>Current language</summary><div class="rv-curtext">{current}</div></details>
  {edit_block}
  <textarea class="rv-note" rows="2" placeholder="{note_ph}"></textarea>
  <div class="rv-acts">{actions}</div>
  {also}
</div>"""


def build(analysis, source):
    doc = analysis.get("document", {})
    title = esc(doc.get("title") or analysis.get("document_title") or "Contract review")
    party_raw = (doc.get("perspective") or doc.get("reviewed_for")
                 or doc.get("party") or analysis.get("perspective") or "")
    # perspective may already end in "party"/"Party" — don't double it downstream
    party = esc(party_raw.strip())
    score = analysis.get("score", {})
    overall = score.get("overall", "\u2013")
    try:
        overall_disp = f"{float(overall):.1f}"
    except (TypeError, ValueError):
        overall_disp = esc(overall)
    author_name = analysis.get("author_name") or doc.get("author_name") or ""
    author_initials = analysis.get("author_initials") or doc.get("author_initials") or ""
    source = source or doc.get("source_file") or doc.get("filename") or ""

    findings = sorted(
        analysis.get("findings", []),
        key=lambda f: (sev_rank(f.get("severity")), str(f.get("id"))),
    )
    cards = "\n".join(card_html(f) for f in findings)
    n = len(findings)

    perspective_line = f" \u00b7 reviewed for the {party}" if party else ""

    # config consumed by the script (source + author travel back with the decisions)
    cfg = json.dumps(
        {"source": source or "", "author_name": author_name,
         "author_initials": author_initials,
         "title": doc.get("title") or analysis.get("document_title") or ""},
        ensure_ascii=False,
    ).replace("</", "<\\/").replace("<!", "<\\!")

    style = """
.rv-wrap{padding:1rem 0;font-family:var(--font-sans);color:var(--text-primary)}
.rv-head{display:flex;align-items:center;gap:12px;margin:0 0 4px}
.rv-gauge{background:var(--surface-1);border-radius:var(--radius);padding:8px 12px;text-align:center;min-width:78px}
.rv-gauge b{display:block;font-size:22px;font-weight:500;line-height:1.1}
.rv-gauge span{font-size:12px;color:var(--text-muted)}
.rv-htext h2{font-size:18px;font-weight:500;margin:0}
.rv-htext p{font-size:13px;color:var(--text-secondary);margin:2px 0 0}
.rv-counts{display:flex;gap:14px;margin:12px 0 4px;font-size:13px;color:var(--text-secondary)}
.rv-counts b{font-weight:500;color:var(--text-primary)}
.rv-card{background:var(--surface-2);border:0.5px solid var(--border);border-radius:12px;padding:14px 16px;margin:12px 0}
.rv-card[data-action=reject]{opacity:.62}
.rv-top{display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin-bottom:6px}
.rv-sev{font-size:11px;font-weight:500;padding:2px 8px;border-radius:var(--radius)}
.s-critical{background:var(--bg-danger);color:var(--text-danger)}
.s-high{background:var(--bg-warning);color:var(--text-warning)}
.s-medium{background:var(--bg-accent);color:var(--text-accent)}
.s-low{background:var(--surface-1);color:var(--text-secondary)}
.rv-cat{font-size:12px;color:var(--text-secondary)}
.rv-fav{font-size:12px;color:var(--text-muted)}
.rv-id{margin-left:auto;font-size:12px;color:var(--text-muted);font-family:var(--font-mono)}
.rv-issue{font-size:14px;line-height:1.6;margin:2px 0 8px}
.rv-cur{margin:0 0 8px}
.rv-cur summary{font-size:12px;color:var(--text-secondary);cursor:pointer}
.rv-curtext{font-size:13px;color:var(--text-secondary);font-family:var(--font-voice);border-left:2px solid var(--border);padding:6px 0 6px 10px;margin-top:6px;border-radius:0}
.rv-lbl{display:block;font-size:12px;color:var(--text-secondary);margin:6px 0 4px}
.rv-edit,.rv-note{width:100%;font-family:var(--font-sans);font-size:13px;line-height:1.5;box-sizing:border-box}
.rv-note{margin-top:8px}
.rv-acts{display:flex;gap:8px;margin-top:10px}
.rv-b{font-size:13px;padding:6px 14px}
.rv-b[aria-pressed=true].rv-accept{background:var(--bg-success);color:var(--text-success);border-color:var(--border-success)}
.rv-b[aria-pressed=true].rv-comment{background:var(--bg-accent);color:var(--text-accent);border-color:var(--border-accent)}
.rv-b[aria-pressed=true].rv-reject{background:var(--bg-danger);color:var(--text-danger);border-color:var(--border-danger)}
.rv-also{display:flex;align-items:center;gap:6px;font-size:12px;color:var(--text-secondary);margin-top:8px}
.rv-bar{display:flex;align-items:center;gap:10px;margin-top:16px;padding-top:14px;border-top:0.5px solid var(--border)}
.rv-apply{font-size:14px;font-weight:500;padding:9px 18px}
.rv-note2{font-size:12px;color:var(--text-muted);margin-left:auto}
"""

    body = f"""<div class="rv-wrap">
<h2 class="sr-only" style="position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)">Interactive contract review: accept, edit, or reject each of {n} findings, then apply.</h2>
<div class="rv-head">
  <div class="rv-gauge"><b>{overall_disp}</b><span>/ 10</span></div>
  <div class="rv-htext"><h2>{title}</h2><p>{n} findings{perspective_line}</p></div>
</div>
<div class="rv-counts">
  <span><b id="rv-c-accept">0</b> accept</span>
  <span><b id="rv-c-comment">0</b> comment</span>
  <span><b id="rv-c-reject">0</b> reject</span>
</div>
{cards}
<div class="rv-bar">
  <button type="button" class="rv-apply" id="rv-apply">Apply review &amp; redline the document \u2197</button>
  <button type="button" id="rv-copy" style="font-size:13px;padding:9px 14px">Copy decisions</button>
  <span class="rv-note2">Apply sends your decisions straight back \u2014 no file needed</span>
</div>
</div>
<script>
(function(){{
  var CFG = {cfg};
  var cards = Array.prototype.slice.call(document.querySelectorAll('.rv-card'));
  function recount(){{
    var a=0,c=0,r=0;
    cards.forEach(function(card){{
      var x=card.getAttribute('data-action');
      if(x==='accept')a++;else if(x==='comment')c++;else if(x==='reject')r++;
    }});
    document.getElementById('rv-c-accept').textContent=a;
    document.getElementById('rv-c-comment').textContent=c;
    document.getElementById('rv-c-reject').textContent=r;
  }}
  cards.forEach(function(card){{
    card.querySelectorAll('.rv-b').forEach(function(btn){{
      btn.addEventListener('click',function(){{
        var act=btn.getAttribute('data-action');
        card.setAttribute('data-action',act);
        card.querySelectorAll('.rv-b').forEach(function(b){{
          b.setAttribute('aria-pressed', b===btn ? 'true':'false');
        }});
        recount();
      }});
    }});
  }});
  recount();
  function collect(){{
    var decisions=cards.map(function(card){{
      var action=card.getAttribute('data-action');
      var editEl=card.querySelector('.rv-edit');
      var noteEl=card.querySelector('.rv-note');
      var alsoEl=card.querySelector('.rv-alsochk');
      var d={{id:card.getAttribute('data-id'),action:action}};
      if(action==='accept'&&editEl) d.final_edit=editEl.value;
      var note=noteEl?noteEl.value.trim():'';
      if(note) d.note=note;
      if(action==='accept') d.as_comment = alsoEl ? !!alsoEl.checked : false;
      return d;
    }});
    return {{source_analysis:CFG.source,document_title:CFG.title,
             author_name:CFG.author_name,author_initials:CFG.author_initials,
             decisions:decisions}};
  }}
  document.getElementById('rv-apply').addEventListener('click',function(){{
    var payload=collect();
    var msg="Apply my contract-review decisions and regenerate the redlined document"
      +(CFG.source?(" for "+CFG.source):"")+"."
      +" Run phase 4 (apply_decisions.py) with these decisions, keep any existing"
      +" counterparty comments, and reply-and-resolve threads I've agreed with.\\n\\n"
      +"```json\\n"+JSON.stringify(payload,null,2)+"\\n```";
    if(typeof sendPrompt==='function'){{ sendPrompt(msg); }}
    else {{ try{{navigator.clipboard.writeText(JSON.stringify(payload,null,2));}}catch(e){{}}
            alert('Callback unavailable here. Decisions copied to clipboard \u2014 paste them into chat.'); }}
  }});
  document.getElementById('rv-copy').addEventListener('click',function(){{
    var payload=collect();
    try{{navigator.clipboard.writeText(JSON.stringify(payload,null,2));}}catch(e){{}}
  }});
}})();
</script>"""

    return "<style>" + style + "</style>\n" + body


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("analysis")
    ap.add_argument("--source", default="", help="original document filename (travels back with decisions)")
    ap.add_argument("-o", "--out", default="")
    a = ap.parse_args()
    analysis = json.loads(Path(a.analysis).read_text(encoding="utf-8"))
    frag = build(analysis, a.source)
    if a.out:
        Path(a.out).write_text(frag, encoding="utf-8")
        print(f"Wrote {a.out}  ({len(analysis.get('findings', []))} findings)", file=sys.stderr)
    else:
        sys.stdout.write(frag)


if __name__ == "__main__":
    main()
