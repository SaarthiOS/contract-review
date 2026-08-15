# Producing the marked-up document (Phase 4 recipe)

The goal: hand back the ORIGINAL document with the user's accepted edits as
tracked changes and native Word comments, authored as the user, threaded onto
any existing comments and closing the ones now resolved.

`scripts/apply_decisions.py` orchestrates all of this and is **self-contained** —
it uses the bundled `scripts/ooxml.py` for the comment plumbing and run-merging,
with no external skill dependency. This file is the map of what the script does
and the traps to check, so you can drive it (and fix edge cases) by hand when a
document is unusual.

## Order of operations (what apply_decisions.py does)

1. **Unpack once.** Unzip `original.docx` to a temp dir and delete any symlinks
   (external docs are untrusted).
2. **Coalesce runs** so clause text is findable as a contiguous string
   (`ooxml.merge_runs`). Word fragments text across `<w:r>` runs; without this,
   `original_text` from the analysis often won't match. Best-effort; skips
   quietly if `lxml` is unavailable.
3. **Inventory existing comments** from `word/comments.xml` and
   `commentsExtended.xml`: each comment's anchored text, its `w14:paraId`, and
   whether it is already `w15:done="1"`. Needed to thread/resolve correctly.
4. **Apply each accepted decision** (below).
5. **Rezip** to the output `.docx`.
6. **Validate / eyeball** (below).

## Applying a redline (text change) as a tracked change

Locate `original_text` in `word/document.xml` (after run-merge) and replace it
with tracked-change markup, authored as the user:

```xml
<w:del w:id="{id}" w:author="{Full Name}" w:date="{ISO8601}">
  <w:r><w:rPr>...</w:rPr><w:delText xml:space="preserve">{old text}</w:delText></w:r>
</w:del>
<w:ins w:id="{id+1}" w:author="{Full Name}" w:date="{ISO8601}">
  <w:r><w:rPr>...</w:rPr><w:t xml:space="preserve">{new text}</w:t></w:r>
</w:ins>
```

Traps to heed:
- Inside `<w:del>` the text element is `<w:delText>`, not `<w:t>`.
- Deleting a whole paragraph = `<w:del>` around every run **plus** a deleted
  paragraph mark: `<w:pPr><w:rPr><w:del .../></w:rPr></w:pPr>`, and the `<w:del/>`
  must come **before** the rPr's other children (schema-enforced order).
- Preserve the original run properties (`<w:rPr>`) so formatting survives.
- Use a unique, increasing `w:id` per `<w:ins>`/`<w:del>` (the script starts at
  90000 to avoid colliding with existing IDs).
- Keep `xml:space="preserve"` to protect leading/trailing spaces.
- Do NOT pretty-print or reformat `document.xml` — surgical edits only.

If `original_text` can't be found even after run-merge (heavy formatting,
tables), fall back to a **comment-only** on the nearest matching run and tell the
user that clause needs a manual edit, rather than editing the wrong span. The
script reports these under `degraded` / `not_found`.

## Attaching a comment

The bundled helper manages the comment parts and returns the new comment id and
its paragraph id:

```python
from ooxml import add_comment
cid, para_id, _ = add_comment(unpacked_dir, "{comment body}",
                              author="{Full Name}", initials="{FN}")
```

`add_comment` creates/extends the five comment parts (`comments.xml`,
`commentsExtended.xml`, `commentsIds.xml`, `commentsExtensible.xml`,
`people.xml`) and registers the content-types and document relationships. It does
**not** touch `document.xml` — you must wrap the target text with the range
markers so the comment is visible:

```xml
<w:commentRangeStart w:id="{cid}"/> ... commented text ... <w:commentRangeEnd w:id="{cid}"/>
<w:r><w:rPr><w:rStyle w:val="CommentReference"/></w:rPr><w:commentReference w:id="{cid}"/></w:r>
```

Anchor it to the same span as the redline (or to the clause the comment is
about). Generated `w14:paraId` / `w16cid:durableId` values must stay below
`0x80000000` (they are signed 32-bit) — `ooxml._rand_hex8` already enforces this.

**Comment body** should carry the reasoning and the user's note, e.g.:
> [CRITICAL · confidentiality] Perpetual confidentiality is off-market; proposing
> a 3-year term with a trade-secret carve-out. — {note from the user}

For an accepted redline with `as_comment: true`, attach BOTH the tracked change
and a comment anchored to the same range.

## Threading onto and resolving EXISTING comments

This is the part users care about — don't clobber the counterparty's comments.

- **Agreeing with an existing thread** on this clause: add a **reply**, don't
  open a new top-level comment. Pass the existing comment's id as the parent:
  ```python
  add_comment(unpacked_dir, "Agreed - updating to a 3-year term.",
              author="{Full Name}", initials="{FN}", parent_id={existing_id})
  ```
  `add_comment` sets `w15:paraIdParent` on the reply so it nests under the
  original. Then **close the thread**: in `word/commentsExtended.xml`, find the
  `<w15:commentEx>` for that thread's root `w14:paraId` and set `w15:done="1"`
  (new threads are written `done="0"`; resolving is a one-attribute flip).
- **New point** (no existing thread on that clause): add a fresh top-level
  comment as above.
- **Never** delete or rewrite an existing `<w:comment>` — only append replies and
  flip `done`. The existing comments are the other side's record.

`apply_decisions.py --resolve-agreed` does the reply + close automatically when an
accepted finding overlaps an existing thread; verify the flips in
`commentsExtended.xml` afterward.

## Validate and eyeball

After writing the output, render it and read it back:

```bash
soffice --headless --convert-to pdf out.docx   # LibreOffice, if available
pdftoppm -jpeg -r 100 out.pdf page && ls page-*.jpg   # then Read the images
```

Confirm: every intended text change is inside `<w:ins>`/`<w:del>` (an untracked
edit is a silent, invisible change and a liability), each change is authored
under the user's name, comments anchor to the right spans, and rejected clauses
are untouched. Quick self-check: `grep -c '<w:ins ' word/document.xml` and
`grep -o 'w:author="[^"]*"' word/document.xml` should show only the user's name
on changes.

## PDF originals — be honest

Word-grade tracked changes and threaded comments do not exist natively in PDF.
Two real options, offered to the user (never silently pretend a PDF got Word
redlines):

1. **Deliver as .docx (recommended).** Convert the PDF to docx
   (`soffice --headless --convert-to docx file.pdf`), run the full recipe, deliver
   the .docx redline. Most counterparties expect Word redlines anyway.
2. **PDF annotations + change summary (lower fidelity).** Add text / `FreeText`
   annotations with `pypdf` at approximate clause locations for each accepted
   item, plus a generated summary page listing every change and comment. This is
   a review aid, not a true redline; say so.

Ask which the user prefers before generating a PDF deliverable.
