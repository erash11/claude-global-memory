# Athletics Technology Inventory — Form Build Spec

## Built — live Google Form (scaffold)

A working Google Form has been created from this spec, to be transformed into
Microsoft Forms.

- **Edit / view:** https://docs.google.com/forms/d/1qVAdjmDs0uNGz1pV-1Nzdb6sEHx7RxL6MQmZd1pHsks/edit
- **Preview as respondent:** https://docs.google.com/forms/d/e/1FAIpQLSfP3vLBN6RrdXPHit1NFAEEug7MnnQZhco3W6vVZO2Y2c2EJw/viewform
- **Form ID:** `1qVAdjmDs0uNGz1pV-1Nzdb6sEHx7RxL6MQmZd1pHsks`
- Built via `gws forms` on the **personal** Google account (eric.rash11@gmail.com),
  not Baylor. 17 questions across 4 sections, verified against this spec.

> **Loose end:** the form is currently published and accepting responses. Nothing is
> shared, so exposure is minimal, but it should not collect real responses on a
> personal account. Turn off "Accepting responses" in the Forms UI, or delete the form
> once it has been transformed to Microsoft Forms.

---

**Platform for actual collection: Microsoft Forms**, not Google Forms. Baylor is a Microsoft tenant (Teams,
OneDrive, SharePoint), responses stay inside Baylor, and results drop straight to
Excel on OneDrive. Collecting an inventory of athlete-data systems through a personal
Google account would work against the point of the exercise.

**Audience:** Directors of Operations, one response per sport program or unit.
Also usable as an in-person conversation script — same questions, someone else types.

**Design rule:** every question that asks for certainty offers **"Not sure."** Jon
Allen's estimate is that 80–90% of platforms are known and the rest surface as
surprises. Forcing certainty produces confident wrong answers instead of a usable
map of what nobody knows.

**Target completion time: under 10 minutes.**

---

## Section 1 — About you

1. **Your name** — short answer
2. **Sport or unit** — dropdown, 26 options
   *Sports:* Baseball · Basketball (M) · Basketball (W) · Football · Golf (M) ·
   Golf (W) · Soccer · Softball · Tennis (M) · Tennis (W) ·
   Track & Field / Cross Country · Volleyball · Acrobatics & Tumbling · Equestrian
   *Units:* Applied Performance · Athletics Performance · Athletic Medicine ·
   Athletic Mental Health Services · Performance Nutrition ·
   Student-Athlete Services · Business Office · Communications · Marketing ·
   Compliance · Operations · Other

---

## Section 2 — Technology currently in use

*Repeat this block for each item. In Microsoft Forms, either use a repeating section
or instruct "submit the form once per technology" — a single submission per item is
easier to analyze and easier to fill.*

3. **Name of the technology, software, app, or platform** — short answer
4. **What do you use it for?** — one or two sentences
5. **Who uses it?** — checkboxes, select all
   Coaches · Athletics Performance · Athletic Medicine · Operations ·
   Analytics / Video · Student-athletes themselves · Other
   *Renamed to match the unit names in Q2. Performance Nutrition, Applied
   Performance, and Athletic Mental Health Services are deliberately not listed here
   — this question captures broad user groups rather than the full org chart. Say the
   word if they should be added.*
6. **Does it involve any student-athlete information?** — choice
   Yes · No · Not sure
7. **If yes, what kind?** — checkboxes, select all
   Names or roster only · Video of athletes · Performance or training data ·
   Health, injury, or medical · Wellness or survey responses · Academic ·
   Not sure
8. **Roughly when did you start using it?** — choice
   Within the last year · 1–3 years ago · More than 3 years ago · Not sure
9. **How is it paid for?** — choice
   Sport program budget · Department budget · Free / no cost ·
   Provided by a vendor or partner · Not sure
10. **Do you know when the contract or subscription ends?** — short answer,
    "Not sure" allowed
11. **How was it originally set up — did it go through the ITS IDEA form?** — choice
    Yes, through the IDEA form · No, we set it up directly with the vendor ·
    It came with something else we already had · Not sure

> Question 11 is the one that turns an anecdote into a number. The meeting put the
> bypass rate at roughly 20% by estimate. This measures it.

---

## Section 3 — Technology you have stopped using

12. **Have you stopped using any technology or software in the last year or so?**
    — Yes / No. If No, skip to Section 4.
13. **What was it?** — short answer
14. **Why did you stop?** — choice
    Cost · Didn't get used · Replaced by something better · Staff change ·
    Vendor issue · Other
15. **Do you know whether the vendor still has our data?** — choice
    They deleted it · They still have it · We exported it first · Not sure

> Question 15 matters more than it looks. If a product was discontinued and the
> vendor still holds student-athlete data, that is an open exposure with no owner.
> Nothing in the current process closes that loop.

---

## Section 4 — Coming up

16. **Is there anything you are currently evaluating, or planning to request?**
    — long answer, optional
17. **Anything you use that you are not sure counts as "technology"?**
    — long answer, optional

> Question 17 catches the long tail — shared spreadsheets, a free scheduling app, a
> vendor portal, a phone app a coach installed. That tail is exactly the 10–20%
> nobody currently has visibility into.

---

## After collection

- Export to Excel on OneDrive; one row per technology.
- Flag every row where Q6 = Yes or Not sure — that is the athlete-data population and
  the priority for review.
- Flag every row where Q11 ≠ "Yes, through the IDEA form" — that sizes the bypass.
- Flag every row where Q15 = "They still have it" or "Not sure" — open data exposure.
- Cross-check against Business Office contract records for anything with a cost, and
  against the ITS IDEA form history, to find items that appear in one and not the other.
