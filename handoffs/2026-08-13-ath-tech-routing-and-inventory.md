# Handoff — ATH Technology Framework: post-meeting routing sheet + inventory

**Date:** 2026-08-13
**Owner:** Eric Rash (Applied Performance, Baylor Athletics)
**Predecessor:** `2026-08-12-ath-tech-software-framework.md` (the merge/build session)
**Superseded in part by:** `2026-08-14-ncaa-crosswalk-appendix.md` and
`2026-08-14-ath-tech-scripts` — a newer document set shipped 8/14 (framework with
Appendix A NCAA crosswalk, workflow, exec summary; older versions moved to `_Archive/`).
**Read those first for current document state.** This file remains the reference for
the routing sheet, the two inventory forms, and the 8/13 meeting record.
**Status:** Meeting held 8/13 4:16 PM. Direction changed. Four new deliverables built,
two Google Forms live, one Gmail draft staged.

---

## What happened

The 8/13 "INITIAL DISCUSSION: ATH Technology/Software Review" meeting took place
(39.5 min, 7 speakers). Full transcript reviewed via
`fireflies-pp-cli transcripts get 01KZYFQ9F92NHG57AHSQJ2DFR4 --live`.

**The direction changed.** Micah Lamb (ITS) is writing a **counter-proposal**. He
likes the content but does not want a process running parallel to the university's
existing workflow:

> "I really don't think we need to go that far… if we instead had a more standardized
> intake and a more standardized framework around the requests coming from athletics,
> that would really streamline and speed up the path through the existing process.
> That's where I think we will see most of our gain for less effort."

Kenny Boyd then gave follow-up direction: build a **simple internal athletics routing
document** — yes/no logic, keyed on data type, Business Office as first layer, simple
enough to show ITS that review happens inside Athletics before requests reach them.
Separately: get a real **technology inventory**, and set a **standing meeting with
Micah**.

## Key decisions and the reasoning that would otherwise be lost

1. **The routing sheet outputs the settled Levels rather than competing with §6.**
   Three yes/no questions produce Level 1/2/3 as already defined. This answers Kenny
   (simple) and Micah (no parallel process) simultaneously, and keeps one definition of
   the levels instead of two. Truth table verified: all 8 combinations map to exactly
   one level, zero mismatches vs §6.

2. **Data type sets the floor; cost can only raise the level.** Pre-meeting analysis
   found zero-cost tools are the highest-risk, lowest-friction entry point — the
   Business Office filters on budget/contract/duplication and a free app has none of
   the three. This rule stops a free trial from downgrading an athlete-data request.

3. **The sheet says "before an IDEA form *or* a TCM request."** Erin Boyette raised
   that a request can complete the entire IT review before the Business Office sees it,
   because the Business Office only appears at the contract stage where TCM requires an
   IT project ID (added by Procurement without ITS's knowledge). Naming both entry
   points closes that gap.

4. **Plain language over §2.4 definitions.** "Physiologic" was replaced with "anything
   about an athlete's body, health, injury, or recovery." Micah's central complaint was
   that different people call the same data different things; formal definitions would
   reproduce the problem.

5. **Two inventory forms, not one.** A 5-question Quick Inventory for breadth, and the
   17-question Detailed Inventory as a targeted second pass. Asking 17 questions per
   product up front would suppress response rate.

6. **Microsoft Forms is the collection platform**; the Google Forms are scaffolds only.
   Collecting an inventory of athlete-data systems via a personal Google account would
   work against the project's own premise.

7. **Humanizer applied as pattern-removal only.** The skill's "add soul / first person
   / let some mess in" half is blog advice and would damage a staff email CC'ing Kenny
   and Jovon. Same call as the 8/12 session made on the framework doc.

8. **Entry point settled 2026-08-13:** every request starts with the Business Office
   as the first control point, regardless of level or data type. No Level 1 bypass.

## Files created this session

All under `/Users/kristinarash/DEV/SoftwareTech_Mgmt_Framework/docs/`:

- `TALKING_POINTS_ER_2026-08-13_internal.md` — pre-meeting; shareable block + prep notes
- `MEETING_RECORD_2026-08-13_tech-software-review.md` — full transcript synthesis
- `ROUTING_ONEPAGER_ATH_2026-08-13.md` — **the core deliverable**
- `INVENTORY_FORM_SPEC_2026-08-13.md` — 17-question Microsoft Forms build spec
- `INVENTORY_EMAIL_DRAFT_2026-08-13.md` — distribution email (humanized)
- `INVENTORY_FORMS_LINKS.md` — both form URLs + shared 26-option department list
- `MICAH_MEETING_REQUEST_2026-08-13.md` — meeting request + standing-meeting agenda

Memory files written:
- `~/.claude/projects/-Users-kristinarash-DEV/memory/project_gws-forms-api.md` (new)
- `.../project_fireflies-cli-broken-on-mac.md` (appended: `--live` requirement)

**Nothing was changed in `deliverables/`.** The merged framework docx is untouched —
Micah's counter-proposal is coming and editing now means editing twice.

## Live external state

- **Google Form — Quick Inventory** (5 q):
  `16gu5e962Iuyun-cyVTg4vxXlW2tLw5MngjcXMALRIxA`
- **Google Form — Detailed Inventory** (17 q):
  `1qVAdjmDs0uNGz1pV-1Nzdb6sEHx7RxL6MQmZd1pHsks`
- Both on the **personal** Google account, both **published and accepting responses**.
  Unpublish or delete once transferred to Microsoft Forms.
- **Gmail draft** `r-1535866246841293577` — inventory request email, To/Cc empty,
  personal account. Copy to Baylor mail before sending.
- **Gmail draft** `r-1467170420815929116` — Micah follow-up. **Superseded: the email
  was sent from Baylor mail on 8/14.** Safe to delete this stale personal-account copy.

## Next actions, most important first

1. **Micah follow-up email SENT Fri 2026-08-14.** Asked for 30 minutes next week
   before he finalizes his markups, plus a standing weekly cadence. **Awaiting his
   reply.** When the meeting lands, use the 30-minute agenda further down this file,
   and raise that framework §1.7 already specified the weekly ITS standing meeting
   Kenny independently asked for.
2. **Rebuild the Quick Inventory in Microsoft Forms**, add recipients, send from Baylor
   mail with Kenny + Jovon on CC. Suggested deadline Fri Aug 29 (adjust for fall camp).
3. **Then** report out to Cody Hall and Jovon Overshown per Kenny's instruction.
4. Unpublish/delete the two Google Forms after transfer.

## Still open from pre-meeting analysis — not discussed on 8/13

These were found in the framework and remain unaddressed:
- **Trials/pilots:** Form 1 offers "Provisional / trial" and the Scorecard offers
  "Approve as trial with hard end date," but the framework body has zero occurrences of
  trial/pilot/demo (§8.2 was cut on Aug 11; the forms are dated Aug 4 and were never
  revised). Decide: restore a short section, or strip the option from the forms.
- **Student-Athlete Notice:** defined in §2.4, required nowhere. §3 claims the framework
  is Baylor's NCAA SSI implementation, where athlete transparency is central.
  (Note: Form 2's "notice" is *contract cancellation* notice — a different concept.)
- **Discontinuation:** Phase 3.4 can conclude "discontinue"; Procurement's role requires
  contracts to address retention/deletion/portability; no phase step executes either.
- **No effective date, transition plan, or bypass-detection mechanism.**

## Context worth carrying

- Kenny closed the meeting frustrated — nine years of hearing athletics systems can't
  connect with campus health and counseling, and he said the campus EMR investment
  doesn't solve athletics' problem. Temperature matters for follow-ups.
- Micah committed to adding the Athletics Business Office to IDEA form
  auto-notifications (can start immediately for athletics), a business-officer dropdown
  campus-wide by mid-fall, and optionally auto-looping Kenny's team on athlete-data
  requests. Confirm Athletics is in the first wave.
- Roughly 1,000 IDEA form requests came through last year (~3/day, clumped). Jon Allen
  warned against two serial processes turning a 2-week turnaround into 8–10 weeks —
  any defense of the framework must answer this.
- Bypass rate estimated at ~20% by Cody and Kenny. Quick-form question 11 ("did it go
  through the IDEA form?") is designed to measure it rather than estimate it.
