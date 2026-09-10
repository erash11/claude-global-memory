# Handoff — RTP Constraints Course, research phase complete

**Date:** 2026-09-02 · **Workspace:** `/Users/kristinarash/DEV/RTP_Constraints_Course/`
**Supersedes:** `/tmp/handoff-rtp-constraints-course-20260901.md` (not durable — /tmp)

## What happened

Session 1 scaffolded the workspace. **This session did the research and closed it.**
`RESOURCES.md` grew from 200 to 517 lines. **No lessons written — still deliberate.**

**The headline: the research phase is over.** Theory and method are saturated; lessons 1–3
could be written now. What blocks the course is not more reading — it is **talking to Joe.**

## Read these first

| File | What it holds |
|---|---|
| `CLAUDE.md` | How to work here. Start here. |
| `INTERVIEW.md` | **NEW.** 25-question mission interview. **Run this before lesson 0001.** |
| `MISSION.md` | Still **DRAFT** — every line is inferred, never confirmed with Joe. |
| `NOTES.md` | 253 lines. Open questions, lesson candidates, tool spec, gotchas. |
| `RESOURCES.md` | 517 lines. ~60 sources, annotated. |
| `email-rob-gray.md` | **NEW.** Ready-to-send outreach draft. |

## Decisions made, with reasoning that would otherwise be lost

1. **The course spine is DRILL DESIGN, not injury.** Eric said this twice. Earlier research
   over-screened sources for "does it mention rehab" — that was the wrong test. Return to
   performance is the *context* Joe applies it in, not the search filter. `RESOURCES.md` was
   rewritten to drop that test.
2. **Sarama = design layer; Taberner = dosage layer.** Sarama answers *what does the task look
   like and which constraint do I turn*. Taberner answers *how much can this athlete take today*.
   Joe arrives holding dosage and short on design.
3. **The success band is a PARAMETER, not a constant.** Gray says 70–75%; Sarama independently
   says ~60%. They agree on mechanism (success rate is the trigger) and ceiling (~80% = harder),
   and differ on target by 10–15 points. **Ship it as a labelled, user-settable range.**
4. **Teach Bobrownicki (2022), not Fransen, as the rebuttal.** It is peer-reviewed, attacks this
   course's own anchor paper, and is about American football specifically.
5. **Declined to strip Kindle DRM** (asked twice, second time as "convert to EPUB"). Legitimate
   routes given: email Gray, or highlights export → `/ingest-book`.
6. **No memory file written for course content** — the workspace files hold it. Only a working-
   memory thread line was added.

## Files created or modified this session

**Created:**
- `/Users/kristinarash/DEV/RTP_Constraints_Course/INTERVIEW.md`
- `/Users/kristinarash/DEV/RTP_Constraints_Course/email-rob-gray.md`
- `/Users/kristinarash/DEV/RTP_Constraints_Course/scans/` (empty, for book scans)
- `/Users/kristinarash/DEV/RTP_Constraints_Course/docs/handoffs/2026-09-02-research-phase-complete.md`

**Modified:**
- `/Users/kristinarash/DEV/RTP_Constraints_Course/RESOURCES.md` (200 → 517 lines)
- `/Users/kristinarash/DEV/RTP_Constraints_Course/NOTES.md` (129 → 253 lines)
- `/Users/kristinarash/DEV/RTP_Constraints_Course/CLAUDE.md` (router row for `INTERVIEW.md`)
- `/Users/kristinarash/.claude/global-memory/MEMORY.md` (new active thread; consolidated two)

**Machine change:** `brew install ocrmypdf` — `ocrmypdf` 17.11.0 + `tesseract` 5.5.3 now at
`/opt/homebrew/bin/`. **May prove unnecessary — see next actions.**

**Backups:** `/Users/kristinarash/.claude/jobs/3ba15b10/tmp/RESOURCES.md.bak2` … `.bak11`
(job-scoped; they disappear with the job).

## Major finds

- **[Football Beyond The Stats](https://footballbeyondthestats.wordpress.com/)** — Myszka's free,
  active-since-2013 blog breaking down a weekly NFL play as a movement problem. **Fills the file's
  biggest gap: football-specific worked examples.** Every other source needed translating.
- **Four Rob Gray videos transcribed in full**, including his 70–75% rule, four-step coaching
  cycle, transition feedback, and the connection-ball example (now the leading lesson-0001
  candidate — an injury-driven movement fix via one task constraint, no body-part cue).
- **Gray's eight free infographics** at perceptionaction.com — best free teaching material found.
- **Bobrownicki et al. (2022)** — football-specific peer-reviewed critique of the anchor paper.
- **Zotero sweep**: 71 matches, ~25 genuine CLA holdings, all now listed.

## Next actions, most important first

1. **Run `INTERVIEW.md` with Joe.** 45 min. Part 1 tests whether he actually wants this niche —
   nobody has asked. **Everything else is blocked behind this.**
2. **Rewrite `MISSION.md` in Joe's words; delete the DRAFT banner.**
3. **Pick lesson 0001** from the four candidates in `NOTES.md`, using interview Q7 and Q10.
4. **`/model` → Fable 5.1**, then `cd` here and **`/teach`**. A human must type it —
   `disable-model-invocation: true`.
5. **Send `email-rob-gray.md`** to robgray@asu.edu (address verified).
6. **Check ASIN `B0FMQWN1NK` for a Kindle edition of the football textbook BEFORE scanning.**
   Unverified; if it exists it deletes the whole scanning/OCR job.

## Mid-flight / open

- **`MISSION.md` unconfirmed.** The single biggest risk in the project.
- **Who drives `/teach`** — Joe or Eric. Changes lesson voice. Now interview Q23.
- **Tool: record or design aid?** Now interview Q15. Assumed design aid.
- **Gap 3 still open** — no American-football positional demand profile. Likely has to be built
  from Baylor GPS/film as a course output, not found by reading.
- **Gray's certification** — $1,995, 2027 sessions full, waitlist only. Decision for Eric.
- **`RESOURCES.md` is 517 lines and reads as a research log** — ⭐ markers, four "lesson 0001
  candidates", same-day correction notes. **A consolidation pass before `/teach` is worth
  considering.**

## Trust note for the next session

Review caught roughly **seven** attribution or overclaim errors before they shipped this session —
wrong bylines (the Transforming Basketball posts are by George Vaz, not Sarama), hedged evidence
firmed up, two "discoveries" that were already listed. All corrected, with correction notes left
in place. **Treat "verified <date>" markers as solid; treat everything else as citable only after
a check.** Video quotes come from YouTube auto-captions and are flagged as such.
