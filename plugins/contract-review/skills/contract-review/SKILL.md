---
name: contract-review
description: "Review an NDA, contract, MSA, DPA, employment, or licensing agreement from ONE party's perspective, rate how favorable/balanced it is, and produce a clause-by-clause redline. Use whenever the user uploads or pastes a legal agreement and wants it reviewed, redlined, marked up, checked for fairness, or negotiated — even without the word 'redline'. Also trigger on 'is this contract fair', 'review this NDA', 'what should I push back on', 'check the indemnification/IP/jurisdiction clauses'. Covers confidentiality, IP & copyright, indemnification, limitation of liability, penalties, SLAs, termination, non-compete, governing law & jurisdiction, assignment, warranties, and data protection. Produces an interactive HTML review where the user accepts/rejects/edits each suggestion, then generates the next version in the ORIGINAL FORMAT (.docx/.pdf) with tracked-change redlines and native comments authored as the user, threading onto and resolving pre-existing comments. Analysis to support review, not legal advice."
license: Proprietary
---

# Contract & NDA Review

Review a legal agreement the way a diligent in-house counsel would: from one
party's side, scoring how balanced it is, flagging every clause that is
one-sided or missing, and proposing the specific edit that makes it fair —
then packaging all of that back into the original document with real
tracked changes and comments the user can send straight to the counterparty.

This skill is analysis to support the user's own judgment. It is not a
substitute for a licensed attorney, and the final output always says so.

## The four phases

The work runs in four phases. Phases 1–2 happen in one turn. In Phase 3 the
user works through the review. Phase 4 happens when their decisions come back —
by default automatically, the moment they hit **Apply**. Never skip Phase 2's
interactive review and jump straight to marking up the document — the whole
point is that the user decides, per clause, what goes in.

```
Phase 1  INTAKE + ANALYSE   read the doc, fix the perspective, score it, build the redline table
Phase 2  REVIEW WIDGET      render an interactive review the user edits + accept/rejects in
Phase 3  USER DECIDES        user works in the widget, hits Apply → decisions return to chat
Phase 4  APPLY               regenerate the original doc with tracked changes + threaded comments
```

---

## Phase 1 — Intake and analysis

### 1a. Fix the perspective first — it changes every judgment

Favorability is directional. The same indemnification clause that is dangerous
for a vendor is a gift for a customer. Before analysing anything, establish
**which side the user is on**. If it is not obvious from the conversation or
the document, ask once, compactly:

- NDA → Disclosing party, Receiving party, or Mutual?
- Services/SaaS → Customer/Buyer or Vendor/Supplier?
- Licensing → Licensor or Licensee?
- Employment/consulting → Employer/Company or Employee/Contractor?

Also capture any hard constraints the user already knows (e.g. "liability must
be capped at fees paid", "governing law must be India / Karnataka", "we cannot
accept assignment on change of control"). These become non-negotiables in the
scoring. Ask for the user's name/initials to author comments under — default to
the name in memory/profile if present, otherwise ask.

### 1b. Read the document properly

- **.docx**: `pandoc -t markdown file.docx` for clean text. Then `unzip` it and
  inspect `word/comments.xml` — **pre-existing comments must be preserved and
  addressed in Phase 4**, so capture them now (who said what, on which text).
- **.pdf**: extract with `pdftotext -layout file.pdf out.txt` (or `pdfplumber`).
  Note whether it is a real text PDF or a scan needing OCR.
- **.doc (legacy)**: convert first with
  `soffice --headless --convert-to docx file.doc` (LibreOffice), then read the .docx.

Read the WHOLE document. Do not sample. Missing clauses matter as much as bad
ones — a mutual NDA with no carve-outs for compelled disclosure, or an MSA with
no liability cap, is a finding even though there is no text to quote.

### 1c. Analyse every clause against the playbook

Read `references/clause-playbook.md` — it holds the standard/market position,
the common traps, and the balanced fallback language for each clause family
(confidentiality, IP & copyright, licence grant, indemnification, limitation of
liability, penalties/liquidated damages, SLAs, term & termination,
non-compete/non-solicit, governing law & jurisdiction, assignment, warranties,
data protection). Walk the document clause by clause and, for each, decide:

- Which family it belongs to.
- Who it currently favours, and how far off balance it is.
- The concrete risk to the user's side if left as-is.
- The specific edit that makes it fair — real replacement language, not "consider revising".
- A fallback position if the counterparty won't accept the primary edit.

Also scan for **missing** clauses the playbook says should be present.

### 1d. Score favorability

Follow `references/scoring-rubric.md` to produce an overall favorability score
(0–10 from the user's side, with the bias direction named) plus per-category
sub-scores and a one-line rationale each. The score must be defensible from the
findings — never a vibe.

### 1e. Write the analysis to a structured file

Save the full analysis as `analysis.json` in the working directory using the
schema in `references/analysis-schema.md`. This file drives both the HTML
review and the final markup, so every finding needs: a stable `id`, the clause
family, severity, the original text span (verbatim, so it can be located in the
document later), the issue, the suggested edit, the fallback, and whether it is
a redline (text change) or comment-only (judgement call flagged for discussion).

Show the user a tight summary in chat: the headline score, the 3–5 things that
matter most, and a note that the full interactive review is ready.

---

## Phase 2 — The interactive review

Give the user a per-finding review they can edit, accept, reject, and comment on.
There are two delivery paths. **Default to the widget** — it closes the loop with
no file hand-off.

### Default: the wired review widget (no export step)

Build the widget fragment, then render it with the visualizer `show_widget`
tool. Pass the original filename as `--source` so it travels back with the
decisions:

```bash
python scripts/build_review_widget.py analysis.json --source <original_file> -o review_widget.html
```

Read `review_widget.html` and pass its contents as `show_widget`'s `widget_code`
(it is already a bare fragment — no doctype/html/body). See
`references/review-widget.md` for the payload contract and rendering notes.

Per finding the widget gives the user: the severity chip and which side the
clause favours; the issue in plain language; the original language (collapsible);
for redline findings an **editable suggested-edit box**; a free-text note; and
**Accept / Comment-only / Reject** controls, plus an "also leave a comment"
toggle. A live score gauge and running accept/comment/reject counts sit on top.

The key difference from a plain artifact: the **Apply** button calls the widget
runtime's `sendPrompt()`, which posts the user's decisions back into the chat as
a JSON payload (same shape as `decisions.json`). No download, no copy-paste — the
user reviews, hits Apply, and Phase 4 runs. A **Copy decisions** button is the
fallback if the callback is unavailable.

Tell the user plainly: work through the cards, adjust any wording, set each to
accept/comment/reject, then hit **Apply** to redline the document.

### Fallback: standalone HTML + exported decisions file

Use this when the visualizer isn't available, or the user wants a downloadable /
offline / shareable review artifact:

```bash
python scripts/build_review_html.py analysis.json -o contract-review.html
```

Present `contract-review.html` (template: `assets/review-template.html`). Same
per-finding controls, but decisions leave via an **Export decisions** button
(copy + download) and the user brings that JSON back for Phase 4. State is
in-memory only (no browser storage), so the template warns them to export before
closing.

---

## Phase 3 — User decides

With the widget, this phase is one click: the user hits **Apply** and their
decisions arrive as the next chat message — a short instruction followed by a
```json fenced block. Take that block as the `decisions.json` payload and go
straight to Phase 4. With the HTML fallback, they return with an exported file
or pasted JSON instead.

Either way, if they come back in a **fresh session**, the original document and
`analysis.json` won't be in context — ask for both before applying.

---

## Phase 4 — Apply decisions to the original document

Read `references/docx-comments.md` in full before doing this — it is the exact
recipe for tracked changes, native comments, threading onto existing comments,
and closing resolved threads. The mechanics are unforgiving and that file
covers the traps.

If the decisions arrived inline from the widget's **Apply** button, first save
the JSON from the fenced block to `decisions.json` (its `author_name` /
`author_initials` carry the name to author under). Then:

```bash
python scripts/apply_decisions.py \
    --original path/to/original.docx \
    --decisions decisions.json \
    --analysis analysis.json \
    --author "Full Name" --initials "FN" \
    --resolve-agreed \
    -o original_reviewed.docx
```

`--analysis` supplies the verbatim clause anchors; `--resolve-agreed` turns on
replying-to-and-closing pre-existing comment threads the user agreed with.

For each decision the user **accepted**:

- **Redline findings** → apply the edit as a tracked change (`<w:ins>`/`<w:del>`
  authored as the user, dated) AND attach a native comment explaining why, so
  the counterparty sees both the change and the reasoning.
- **Comment-only findings** → attach a native comment stating the ask, no text change.

For findings the user **rejected**: do nothing (no change, no comment).

**Pre-existing comments (do this carefully):**

- If the user's decision agrees with an existing comment thread on that clause,
  **reply to that thread** (apply_decisions.py does this with `--resolve-agreed`) rather than opening a new one,
  and **close it** by setting `w15:done="1"` on that thread in
  `commentsExtended.xml`.
- If it is a new point, add a fresh comment.
- Never delete or overwrite existing comments — they are the counterparty's
  record. Only add and resolve.

Always author under the user's real name/initials so the markup reads as if the
user made it. After writing, verify: every intended text change must be wrapped
in `<w:ins>`/`<w:del>` (an untracked edit is invisible in the accepted view and a
silent liability), and only the user's name should appear as the change author.
Render to images (`soffice --headless --convert-to pdf`, then `pdftoppm`) and
eyeball that comments anchor to the right spans and redlines read correctly. See
`references/docx-comments.md`.

**.pdf originals:** true native comments/redlines are not cleanly supported in
PDF. Be honest with the user and offer the two real options: (a) deliver the
redline as a .docx (best — most counterparties expect Word redlines anyway),
or (b) add PDF text annotations + a separate change-summary page via `pypdf`,
which is lower-fidelity. Do not silently pretend a PDF got Word-quality
tracked changes. `references/docx-comments.md` has the PDF fallback notes.

Deliver the final file plus a short changelog: what was redlined, what was
commented, what existing threads were closed, and the residual risks the user
accepted by rejecting suggestions.

---

## Guardrails

- This is decision support, not legal representation. Every deliverable (HTML
  footer and final changelog) states that a qualified lawyer should review
  before signing. Do not claim attorney privilege or certainty.
- Quote the user's own uploaded document freely — it is theirs. Do not paste
  large passages of third-party model contracts or paywalled clause libraries
  from the web; work from the playbook and the user's document.
- Keep the perspective the user chose. Do not quietly "balance" a clause in the
  counterparty's favour when the user is the disclosing party and the market
  norm actually favours them — flag it, but the user's side is the client.
- If the document is not actually a contract (e.g. a term sheet, a policy, a
  letter), say so and adapt rather than forcing the clause playbook onto it.

## Files in this skill

- `references/clause-playbook.md` — per-clause standard positions, traps, fair language. Read in Phase 1c.
- `references/scoring-rubric.md` — how to score favorability. Read in Phase 1d.
- `references/analysis-schema.md` — the `analysis.json` structure. Read in Phase 1e.
- `references/docx-comments.md` — tracked-changes + comments + existing-thread handling recipe. Read in Phase 4.
- `references/review-widget.md` — the wired widget path: rendering via `show_widget`, the `sendPrompt` payload contract, fallback. Read in Phase 2.
- `scripts/build_review_widget.py` — `analysis.json` → review widget fragment for `show_widget` (default Phase 2 path).
- `assets/review-template.html` — the standalone HTML review UI (fallback; data injected by the build script).
- `scripts/build_review_html.py` — `analysis.json` → `contract-review.html` (fallback path).
- `scripts/apply_decisions.py` — `decisions.json` + original doc → marked-up document. Self-contained.
- `scripts/ooxml.py` — bundled WordprocessingML helpers (comments, threading, run-merge). No external skill dependency.
