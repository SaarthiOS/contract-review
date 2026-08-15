# analysis.json schema

The single structured artifact that drives both the HTML review and the final
document markup. Write it in Phase 1e. Keep `original_text` VERBATIM from the
document — Phase 4 uses it to locate the clause for redlining/commenting, so any
paraphrase there breaks the anchor.

```json
{
  "document": {
    "title": "Mutual Non-Disclosure Agreement",
    "type": "NDA",
    "parties": ["Acme Corp", "AI Gurukul Pvt Ltd"],
    "reviewed_for": "AI Gurukul Pvt Ltd",
    "perspective": "Receiving party",
    "author_name": "Full Name",
    "author_initials": "FN",
    "source_file": "acme_nda.docx",
    "source_format": "docx"
  },
  "score": {
    "overall": 5.5,
    "favors": "Disclosing party",
    "summary": "Off-market against the Receiving party: perpetual confidentiality on ordinary info, no carve-outs, hostile forum.",
    "categories": [
      { "name": "confidentiality", "score": 4, "note": "No standard carve-outs; perpetual term." },
      { "name": "governing_law", "score": 3, "note": "Exclusive foreign forum." }
    ]
  },
  "findings": [
    {
      "id": "F1",
      "category": "confidentiality",
      "clause_ref": "Section 3",
      "severity": "critical",
      "favors": "Disclosing party",
      "kind": "redline",
      "original_text": "The obligations of confidentiality shall survive in perpetuity.",
      "issue": "Perpetual confidentiality on all information is off-market; 2–5 years is standard for commercial info, with perpetual reserved for trade secrets.",
      "suggested_edit": "The obligations of confidentiality shall survive for three (3) years following termination, except for trade secrets, which remain protected for as long as they qualify as trade secrets under applicable law.",
      "fallback": "Five (5) years for commercial information; perpetual only for information expressly marked as a trade secret.",
      "rationale": "Caps the recipient's indefinite exposure while still protecting genuine trade secrets."
    }
  ],
  "generated_at": "2026-08-06T00:00:00Z",
  "disclaimer": "Analysis to support your review. Have a qualified lawyer review before signing."
}
```

## Field notes

- **`kind`**: `"redline"` (a text change to apply as a tracked change) or
  `"comment"` (a judgement/ask flagged for discussion, no text change). Comment-
  only is right when the fix is a business decision, the clause is missing (no
  text to replace), or you're raising a question rather than proposing wording.
- **`severity`**: `critical` | `high` | `medium` | `low` (see scoring-rubric.md).
- **`favors`**: which side the current clause benefits.
- **`original_text`**: verbatim span from the document. For a **missing** clause,
  set this to `""` and set `kind` to `"comment"` — it will attach at the most
  relevant nearby location chosen in Phase 4, or as a document-level note.
- **`clause_ref`**: human-readable location ("Section 3", "Clause 7.2") for the
  user; not used for machine matching.
- **`suggested_edit`**: real replacement language, ready to drop in.
- **`fallback`**: the position to retreat to if the counterparty rejects the
  primary edit. Shown to the user; optional.
- **`id`**: stable, unique. The decisions file references these ids.

## decisions.json (produced by the HTML in Phase 3)

The review HTML exports this. Phase 4 consumes it.

```json
{
  "source_analysis": "analysis.json",
  "document_title": "Mutual Non-Disclosure Agreement",
  "author_name": "Full Name",
  "author_initials": "FN",
  "decisions": [
    {
      "id": "F1",
      "action": "accept",
      "final_edit": "The obligations of confidentiality shall survive for three (3) years ...",
      "note": "Non-negotiable for us.",
      "as_comment": true
    },
    { "id": "F2", "action": "reject", "note": "" },
    { "id": "F3", "action": "comment", "note": "Ask them to confirm the measurement window.", "final_edit": "" }
  ]
}
```

- **`action`**: `accept` (apply per `kind`), `reject` (do nothing), `comment`
  (attach a comment only, regardless of original `kind`).
- **`final_edit`**: the user's possibly-edited version of `suggested_edit`. If
  empty on an accepted redline, fall back to the analysis `suggested_edit`.
- **`as_comment`**: on an accepted redline, whether to ALSO attach an explanatory
  comment alongside the tracked change (default true).
- **`note`**: the user's free-text instruction; include it in the comment body.
