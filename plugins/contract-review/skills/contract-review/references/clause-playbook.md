# Clause Playbook

Standard market positions, common traps, and balanced fallback language for
each clause family. Use this in Phase 1c: for every clause in the document,
find its family here, judge how far the drafted version sits from the balanced
position, and draft the specific edit.

"Balanced" means neither side can weaponize it — mutual where mutual is fair,
capped where uncapped is reckless, reciprocal where one-sided is extractive.
Directional notes ("favours X") tell you who benefits from the *aggressive*
version so you know which way to push for the user's side.

## Contents
1. Confidentiality (NDA core)
2. IP & copyright ownership
3. Licence grant & feedback
4. Indemnification
5. Limitation of liability
6. Penalties & liquidated damages
7. Service levels (SLAs)
8. Term & termination
9. Non-compete / non-solicit / no-hire
10. Governing law & jurisdiction / dispute resolution
11. Assignment & change of control
12. Warranties & disclaimers
13. Data protection & security
14. Payment terms
15. Boilerplate that bites (force majeure, notices, entire agreement, severability, survival)
16. Commonly missing clauses checklist

---

## 1. Confidentiality (NDA core)

**Balanced position:** Mutual obligations; a clear definition of Confidential
Information; standard carve-outs; a defined term for the obligation; return/
destruction on termination; disclosure compelled by law permitted with notice.

**Traps to flag:**
- **One-way when it should be mutual.** If both sides will actually exchange
  info, a one-way NDA favouring the discloser is off-market. (Favours discloser.)
- **No standard carve-outs.** Confidentiality must NOT cover info that is (a)
  already public, (b) already known to the recipient, (c) independently
  developed without use of the disclosure, or (d) rightfully received from a
  third party. Absence of these is a serious trap. (Favours discloser.)
- **Perpetual confidentiality on ordinary business info.** 2–5 years post-term
  is standard for commercial info; perpetual is reasonable ONLY for trade
  secrets and should be scoped to them. (Favours discloser.)
- **Definition captures everything, including unmarked oral disclosures**, with
  no requirement to mark or confirm in writing. (Favours discloser.)
- **Residuals clause** letting the recipient freely use anything retained in
  memory — quietly guts the NDA. (Favours recipient.)
- **No compelled-disclosure exception**, or one with no notice-to-discloser
  requirement. (Favours whichever side omitted it.)
- **Injunctive relief / no-bond language** stacked only for one side.

**Fair fallback language (carve-outs):**
> Confidential Information does not include information that: (a) is or becomes
> publicly available through no breach of this Agreement by the Receiving Party;
> (b) was rightfully known to the Receiving Party without confidentiality
> obligation before disclosure; (c) is independently developed by the Receiving
> Party without use of or reference to the Confidential Information; or (d) is
> rightfully obtained from a third party without breach of any obligation.

> If the Receiving Party is compelled by law or court order to disclose
> Confidential Information, it may do so provided it gives the Disclosing Party
> prompt written notice (where legally permitted) and reasonable cooperation to
> seek protective treatment, and discloses only the portion legally required.

---

## 2. IP & copyright ownership

**Balanced position:** Each party keeps its background/pre-existing IP.
Ownership of work product/deliverables is stated explicitly. Any assignment is
accompanied by the consideration and scope it needs; licences back are granted
where a party needs continued use.

**Traps to flag:**
- **"All IP conceived during the engagement" assigned to one party** with no
  carve-out for the other's pre-existing/background IP or independently created
  works. Broadest version sweeps in things it shouldn't. (Favours the assignee —
  often the customer/employer.)
- **Assignment with no license-back**, leaving the creator unable to reuse its
  own tools, libraries, or know-how. (Favours assignee.)
- **Copyright assignment implied but not clearly granted** — for a work-for-hire
  deliverable the customer expects to own, silence is a dispute waiting to
  happen. Under many laws copyright stays with the author absent an express
  written assignment. (Ambiguity favours the author/vendor by default, which
  surprises customers.)
- **Moral rights** not addressed where the jurisdiction recognizes them.
- **Feedback/derivatives of the vendor's product** assigned away by the vendor. (Favours customer.)
- **Joint ownership** — usually a trap for BOTH sides (each needs consent to
  exploit in many jurisdictions); prefer sole ownership + licence.

**Fair fallback language (background IP + license-back):**
> Each party retains all right, title, and interest in its Background IP.
> [Assignee] owns the Deliverables created specifically for it under this
> Agreement, excluding [Creator]'s Background IP embedded therein, which
> [Creator] hereby licenses to [Assignee] on a non-exclusive, perpetual,
> royalty-free basis solely to use the Deliverables. [Creator] retains the
> right to use its general skills, know-how, and residual techniques.

---

## 3. Licence grant & feedback

**Balanced position:** Grant scope (exclusive/non-exclusive, territory, term,
sublicensable?) matches what was paid for. Feedback licence is non-exclusive
and limited to improving the product.

**Traps:**
- **Grant broader than the fee** (perpetual/irrevocable/worldwide for a term
  subscription). (Favours licensee.)
- **Feedback clause assigning ownership** of user feedback/ideas rather than a
  licence. (Favours licensor.)
- **Sublicensing / affiliate use unbounded**, expanding usage without extra fee. (Favours licensee.)
- **No survival of the licence** for deliverables the customer paid for, so it
  evaporates on termination. (Favours licensor.)

---

## 4. Indemnification

**Balanced position:** Each party indemnifies the other for the risks it
controls — typically the vendor for third-party IP infringement by its product
and for its own gross negligence/willful misconduct; the customer for its data
and its misuse of the product. Indemnity is subject to prompt notice, control
of defense, and cooperation, and is usually the exception carved OUT of the
liability cap (or subject to a higher super-cap).

**Traps:**
- **One-way indemnity** where mutual is fair, or the user's side indemnifying
  the counterparty for things outside the user's control. (Favours indemnitee.)
- **Uncapped indemnity that swallows the liability cap** — if the indemnity is
  broad AND excluded from the cap, the cap is meaningless. Scope the indemnity
  narrowly OR subject it to a super-cap. (Favours indemnitee.)
- **Indemnity for "any claim arising from the Agreement"** — far too broad;
  should be tied to specific, controllable triggers (IP infringement, breach of
  confidentiality, data breach, personal injury). (Favours indemnitee.)
- **No procedure**: without prompt-notice + control-of-defense + cooperation,
  the indemnifier is exposed to sandbagging. (Favours indemnitee.)
- **No IP-infringement remedy/mitigation** (procure a licence / modify /
  refund) capping the vendor's exposure. (Favours customer if missing.)

**Fair fallback language (mutual, procedural):**
> The indemnifying party's obligations are conditioned on the indemnified party:
> (a) promptly notifying it in writing of the claim; (b) granting it sole
> control of the defense and settlement (provided no settlement admits fault or
> imposes non-monetary obligations on the indemnified party without consent);
> and (c) providing reasonable cooperation at the indemnifying party's expense.

---

## 5. Limitation of liability

**Balanced position:** Mutual cap (commonly 12 months' fees, or 1–2× fees);
mutual exclusion of indirect/consequential/special damages; carve-outs from the
cap for confidentiality breach, IP indemnity, data breach, and gross
negligence/willful misconduct — applied to BOTH sides.

**Traps:**
- **One-sided cap** (vendor capped, customer unlimited, or vice versa). (Favours
  the capped party.)
- **Cap so low it is illusory** (e.g. fees paid in the last month) — check it
  against realistic exposure. (Favours the party at risk of causing damage.)
- **Consequential-damages waiver that is one-way.** (Favours whoever it protects.)
- **Carve-outs asymmetric** — e.g. customer's payment obligation carved out but
  vendor's data-breach liability capped. (Favours the party with fewer carve-outs against it.)
- **No cap at all** on a high-exposure agreement. (Favours the low-risk party.)
- **Gross negligence / willful misconduct / fraud capped** — usually
  unenforceable and always aggressive. (Favours the wrongdoer.)

**Fair fallback language (mutual cap + symmetric carve-outs):**
> Except for the Excluded Claims, each party's total aggregate liability arising
> out of or related to this Agreement will not exceed the fees paid or payable
> in the twelve (12) months preceding the claim. Neither party is liable for
> indirect, incidental, special, consequential, or punitive damages, or lost
> profits or revenue. "Excluded Claims" means each party's indemnification
> obligations, breaches of confidentiality, a party's gross negligence or
> willful misconduct, and amounts owed for the services.

---

## 6. Penalties & liquidated damages

**Balanced position:** Liquidated damages must be a genuine pre-estimate of
loss, not a penalty (penalties are unenforceable in many common-law
jurisdictions). Amounts are reciprocal or at least proportionate. Service
credits are the customer's sole-and-exclusive remedy only if they are meaningful.

**Traps:**
- **Penalty dressed as liquidated damages** — disproportionate to any real loss;
  flag enforceability risk. (Favours the beneficiary.)
- **One-directional penalties** (vendor pays for delay; customer's late payment
  merely accrues modest interest, or vice versa). (Favours the protected side.)
- **Late-payment interest above the statutory/enforceable ceiling.** (Favours creditor.)
- **Service credits as sole remedy but trivial in size**, capping the vendor's
  real exposure for chronic failure. (Favours vendor.)
- **Termination-for-convenience fees** that are punitive. (Favours the locked-in beneficiary.)

---

## 7. Service levels (SLAs)

**Balanced position:** Clear, measurable metrics (uptime %, response/resolution
times by severity), a defined measurement method and reporting, remedies
(service credits) that scale with the miss, and a chronic-failure termination
right for the customer.

**Traps:**
- **Vague or unmeasurable targets** ("commercially reasonable efforts",
  "industry-standard uptime") with no number. (Favours vendor.)
- **Uptime with generous exclusions** (maintenance windows, "force majeure",
  third-party failures) that hollow out the number. (Favours vendor.)
- **Credits capped low / hard to claim** (short claim window, customer must
  request in writing within days). (Favours vendor.)
- **No chronic-failure / termination right** for repeated misses. (Favours vendor.)
- **No definition of severity levels** driving response times. (Favours vendor.)

---

## 8. Term & termination

**Balanced position:** Clear initial term; renewal terms transparent (auto-
renewal with adequate notice to cancel); termination for cause with a cure
period; effects of termination (return of data, wind-down, refund of prepaid
unused fees) spelled out and mutual where fair.

**Traps:**
- **Auto-renewal with a long lock and a short/again-buried cancellation
  window.** (Favours vendor.)
- **Termination for convenience for one side only.** (Favours the side with the right.)
- **No cure period for breach**, allowing termination on any technical slip. (Favours the terminating side.)
- **No data-return / transition assistance** on exit. (Favours vendor.)
- **No refund of prepaid unused fees** on termination for the vendor's breach. (Favours vendor.)
- **Survival clause missing key obligations** (confidentiality, IP, liability,
  payment) — or over-broad, surviving things that should end.

---

## 9. Non-compete / non-solicit / no-hire

**Balanced position:** Restrictions reasonable in scope, geography, and
duration, and enforceable in the governing jurisdiction (many jurisdictions,
incl. several US states and parts of India, limit or void non-competes). Non-
solicit of employees/customers is more defensible than a broad non-compete.

**Traps:**
- **Overbroad non-compete** (unlimited geography/duration, whole industry) —
  likely unenforceable and chilling. (Favours the imposer.)
- **No-hire clauses** restraining the user's ability to hire generally. (Favours the imposer.)
- **Non-solicit sweeping in general advertising / inbound applicants.** (Favours the imposer.)
- **Restrictions on the wrong party** given who actually needs protection.

---

## 10. Governing law & jurisdiction / dispute resolution

**Balanced position:** A neutral or home-favourable governing law and forum;
consistent choice of law + forum; a sensible escalation path (negotiation →
mediation → arbitration/litigation); arbitration seat/rules named if used.

**Traps:**
- **Foreign/hostile forum** forcing the user to litigate far away at high cost —
  a major practical deterrent to enforcing rights. (Favours the drafting party's home side.)
- **Mismatched law and forum** (e.g. Delaware law, courts of England) creating
  cost and uncertainty.
- **Mandatory arbitration** with an inconvenient seat, expensive rules, or a
  class-action waiver — evaluate whether it helps or hurts the user. (Usually
  favours the repeat-player drafter.)
- **One-sided fee-shifting** (loser pays, but only when the user loses). (Favours drafter.)
- **Waiver of jury trial** buried in boilerplate.

**Note:** For India-based users, flag if the seat/venue is offshore or the
governing law is foreign without commercial reason; prefer a named Indian seat
(e.g. courts at the user's principal place of business) or a neutral,
enforceable seat, and confirm the arbitration clause satisfies the Arbitration
& Conciliation Act if Indian-seated.

---

## 11. Assignment & change of control

**Balanced position:** Neither party assigns without consent, EXCEPT to an
affiliate or in connection with a merger/sale of substantially all assets,
usually with notice. Consent "not to be unreasonably withheld".

**Traps:**
- **One party may freely assign, the other may not.** (Favours the free-assigner.)
- **No change-of-control provision** where the user cares who ends up on the
  other side (e.g. a competitor acquiring the vendor). (Favours the acquired party.)
- **Consent withholdable at absolute discretion**, freezing legitimate M&A. (Favours the consenting party.)

---

## 12. Warranties & disclaimers

**Balanced position:** Vendor warrants the services will materially conform to
docs and be performed in a professional manner, plus authority/non-infringement
warranties; a fair "AS IS" disclaimer of implied warranties beyond those; mutual
authority warranties.

**Traps:**
- **Total disclaimer of all warranties incl. the express ones** — leaves the
  customer with no performance promise. (Favours vendor.)
- **No non-infringement or authority warranty.** (Favours vendor.)
- **Warranty remedy illusory** (sole remedy = re-perform, but no timeline). (Favours vendor.)
- **Customer warranties overbroad** (warranting things it cannot control). (Favours vendor.)

---

## 13. Data protection & security

**Balanced position:** A DPA or data clause defining roles (controller/
processor), permitted processing, security measures, breach notification with a
defined timeline, sub-processor controls, data-return/deletion on exit, and
audit rights proportionate to sensitivity. Cross-border transfer mechanism named.

**Traps:**
- **No breach-notification timeline**, or an unreasonably long one. (Favours processor/vendor.)
- **Vendor may use customer data for its own purposes / model training** without
  clear consent. (Favours vendor.)
- **No sub-processor controls or notice.** (Favours vendor.)
- **No data-return/deletion on termination.** (Favours vendor.)
- **Security described as "reasonable" with no specifics** for sensitive data. (Favours vendor.)
- **Missing DPA entirely** where personal data is processed (GDPR/DPDP Act
  exposure). (Favours neither — a compliance gap for both, usually worse for the controller.)

**Note:** For Indian personal data, check alignment with the DPDP Act 2023
(consent, purpose limitation, breach reporting); for EU data, check GDPR
Art. 28 processor terms and a valid transfer mechanism.

---

## 14. Payment terms

**Balanced position:** Clear amounts, currency, invoicing cadence, net-payment
period, taxes handled, disputed-invoice mechanism, and fair late-payment
interest. Price increases capped and noticed.

**Traps:**
- **Unbounded price increases on renewal.** (Favours vendor.)
- **No disputed-invoice carve-out** — customer must pay even contested amounts. (Favours vendor.)
- **Fees non-refundable in all cases**, including vendor breach. (Favours vendor.)
- **Aggressive late fees / suspension rights** on any delay. (Favours vendor.)
- **Taxes gross-up** shifting the counterparty's tax onto the user.

---

## 15. Boilerplate that bites

- **Force majeure**: should be mutual and NOT excuse payment obligations; watch
  for one-sided or overbroad triggers (e.g. "market conditions").
- **Notices**: method and address must be workable (email permitted?); a
  notice clause requiring courier-only can trap a party into missed deadlines.
- **Entire agreement / no reliance**: fine, but check it doesn't disclaim
  representations the user is relying on.
- **Severability**: standard; ensure a void restrictive covenant is blue-
  pencilled, not fatal to the whole.
- **Survival**: confidentiality, IP, liability limits, indemnity, payment, and
  dispute resolution should survive termination.
- **Amendment / waiver**: written-only amendment protects both; a one-sided
  right to change terms unilaterally (common in SaaS ToS) favours the vendor —
  flag it.
- **Counterparts / e-signature**: usually benign.

---

## 16. Commonly missing clauses checklist

Flag as a finding if ABSENT and relevant:

- Confidentiality carve-outs and compelled-disclosure exception
- Limitation of liability cap (either direction)
- Mutual indemnity with procedure
- IP background-IP carve-out and licence-back
- Data-return/deletion on termination
- Breach-notification timeline (data)
- Cure period before termination for cause
- Refund of prepaid unused fees on termination for cause
- Survival clause
- Assignment / change-of-control provision
- SLA remedies + chronic-failure termination right
- Dispute-resolution escalation and named seat/forum
- Cap carve-outs applied symmetrically
