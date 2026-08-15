# Changelog

## 1.0.0
- Initial release.
- Four-phase workflow: analyse (perspective + favorability score + clause findings),
  interactive review, one-click apply, and a regenerated `.docx` with tracked
  changes and native comments authored as the reviewer.
- Self-contained WordprocessingML engine (`scripts/ooxml.py`): comments, reply
  threading, thread resolution, and run-merging. No external skill dependency.
- Interactive review as a `sendPrompt`-wired widget (default) with a standalone
  HTML + JSON-export fallback.
- Clause playbook covering confidentiality, IP & copyright, indemnification,
  limitation of liability, penalties, SLAs, termination, non-compete, governing
  law & jurisdiction, assignment, warranties, and data protection.
