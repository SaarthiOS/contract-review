# Review widget — the no-export path

The default Phase 2 review renders through the visualizer `show_widget` tool
instead of a downloadable HTML file. The point is the callback: the widget's
**Apply** button posts the user's decisions straight back into the chat, so
Phase 4 runs with no file export, upload, or copy-paste.

## Why a widget and not a plain artifact

A normal HTML artifact is sandboxed and cannot start a new chat turn, so a
standalone review can only *export* a decisions file the user then hands back.
The visualizer runtime exposes a global `sendPrompt(text)` that sends a message
as if the user typed it. Rendering the review as a widget is what makes the
one-click round-trip possible. The trade: the widget renders inline (≈680px,
not downloadable). If the user wants an offline/shareable artifact, use the
standalone HTML fallback (`build_review_html.py`) instead.

## How to render it

1. Build the fragment, passing the original filename so it returns with the
   decisions:

   ```bash
   python scripts/build_review_widget.py analysis.json --source <original_file> -o review_widget.html
   ```

2. Read `review_widget.html` and pass its **entire contents** as the
   `widget_code` argument of `show_widget`. It is already a bare fragment
   (leading `<style>`, then the cards, then a trailing `<script>`) with no
   doctype/html/head/body — exactly what the visualizer wants.

3. The generator reads `document.author_name` / `document.author_initials` /
   `document.source_file` from `analysis.json` if present, so the returning
   payload is authored correctly. If those are missing, pass `--source` at least;
   ask the user for their name/initials before Phase 4 if still unknown.

Do not narrate the visualizer setup to the user. Just present the review and
tell them how to use it (edit, set accept/comment/reject, hit Apply).

## The Apply payload contract

When the user clicks **Apply**, the widget calls `sendPrompt()` with a short
instruction plus a fenced ```json block. That JSON is identical in shape to
`decisions.json` (see `analysis-schema.md`):

```json
{
  "source_analysis": "<original_file>",
  "document_title": "…",
  "author_name": "…",
  "author_initials": "…",
  "decisions": [
    { "id": "F1", "action": "accept", "final_edit": "…", "note": "…", "as_comment": true },
    { "id": "F7", "action": "comment", "note": "…" },
    { "id": "F3", "action": "reject" }
  ]
}
```

Field rules the widget follows:

- `action` is one of `accept` | `comment` | `reject`.
- `final_edit` is present only on **accepted redline** findings and reflects any
  in-box edits the user made to the suggested language.
- `note` is included only when non-empty. For a `comment` action it is the
  comment text; for an `accept` it is an optional extra note.
- `as_comment` (accepted redlines only) is whether to also attach an explanatory
  comment alongside the tracked change.
- Comment-only findings never carry `final_edit`.

## Consuming it in Phase 4

Save the fenced JSON to `decisions.json` verbatim, then run `apply_decisions.py`
with `--analysis analysis.json` (for the verbatim anchors) and `--resolve-agreed`
(to reply-and-close agreed pre-existing threads). Author under
`author_name`/`author_initials` from the payload. Everything else is the normal
Phase 4 recipe in `docx-comments.md`.

## Fallback behaviour

If `sendPrompt` is not defined in the runtime, the Apply button copies the same
JSON to the clipboard and tells the user to paste it into chat. The **Copy
decisions** button does this unconditionally. So the widget degrades to the same
manual round-trip as the standalone HTML rather than failing.
