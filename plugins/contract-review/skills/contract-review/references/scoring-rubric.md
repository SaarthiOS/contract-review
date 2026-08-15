# Favorability Scoring

Produce a defensible score, not a vibe. The score is always **from the user's
chosen side** and states the bias direction explicitly.

## Overall score (0–10, from the user's side)

- **9–10** — Balanced-to-favourable. Mutual protections, fair caps, no
  landmines. Ready to sign with minor tidy-ups.
- **7–8** — Broadly fair. A few clauses lean against the user; all addressable
  with standard edits.
- **5–6** — Meaningfully one-sided. Several material clauses favour the
  counterparty; negotiation needed before signing.
- **3–4** — Heavily one-sided. Core protections (liability, indemnity, IP,
  termination) stacked against the user; significant redline required.
- **0–2** — Predatory / unsignable as-is. Uncapped liability, one-way
  everything, unenforceable penalties, hostile forum. Walk or rewrite.

State it as, e.g.: *"5.5/10 from the Vendor's side — the document currently
favours the Customer, driven by an uncapped indemnity and a one-way liability
cap."*

## Per-category sub-scores

Score each applicable category 0–10 on the same scale, with a one-line
rationale. Categories (skip any the document doesn't touch):

confidentiality · ip_ownership · licence · indemnification ·
limitation_of_liability · penalties · sla · term_termination ·
restrictive_covenants · governing_law · assignment · warranties ·
data_protection · payment · boilerplate

## How to weight

Weight by real-world exposure, not clause count. A single uncapped-liability
clause can pull the overall score down more than five minor boilerplate nits.
Rough weighting for a commercial agreement:

- **High impact:** limitation_of_liability, indemnification, ip_ownership,
  data_protection, term_termination.
- **Medium:** confidentiality, sla, penalties, governing_law, payment, licence.
- **Lower (unless egregious):** assignment, warranties, restrictive_covenants,
  boilerplate.

A **missing** high-impact clause (e.g. no liability cap) scores as badly as a
bad one — treat absence as a finding.

## Severity per finding

Tag every finding so the review can be triaged:

- **critical** — could cause uncapped or existential loss; unenforceable term
  the user is relying on; one-way indemnity/liability. Must-fix before signing.
- **high** — materially one-sided; real money or rights at stake. Should-fix.
- **medium** — off-market but survivable; worth pushing on.
- **low** — tidy-up, clarity, or nice-to-have symmetry.

The overall score should move roughly with the count and weight of critical/high
findings. If there are any criticals, the overall score cannot be ≥ 8.

## Bias direction

Always name which side the document currently favours overall, and note any
categories where the bias runs the *other* way (sometimes a document is
lopsided in the user's favour on one axis — flag it so the user knows their
leverage, even though you push for their side).
