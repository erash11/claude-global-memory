# Handoff — RTP Constraints Course, lesson 0001 shipped

**Date:** 2026-09-03 (evening) · **Workspace:** `/Users/kristinarash/DEV/RTP_Constraints_Course/`
**Reads on, does not repeat:** `docs/handoffs/2026-09-03-gray-book-and-joe-prep.md` and
`docs/handoffs/2026-09-02-research-phase-complete.md`. This file records only what changed after
the Joe interview.

**Not a git repository.** Nothing is committed anywhere. Files on disk are the only state.

---

## What this session did

Eric typed `/teach` with the instruction: *lesson 0001 is the opposed/unopposed hook, point at
MISSION.md and the interview digest.* The lesson was built, checked, and opened.

### Decisions

- **Lesson 0001 hook = opposed vs unopposed.** Chosen by Eric, not by the agent. The other three
  candidates in `NOTES.md` stay live for lessons 0002–0004. Reasoning is in the learning record.
- **The lesson starts from Joe's own case** (the returning offensive lineman whose non-reactive
  drills hid a deficit), phrased exactly as `MISSION.md` phrases it. **No athlete names appear in
  any lesson, reference or learning-record file.** The lesson links to the interview digest; it
  does not quote it.
- **Primary source is Parry, Myszka, Yearby, O Sullivan & Otte (2025), *Quest*,** Zotero
  `CA2CRR6Z`, page-cited (argument pp. 3–7, football case pp. 11–16, who-plays-the-opponent
  p. 15). Full text was pulled from Zotero for the session only; **the PDF was not copied into
  the workspace.**
- **The rehab application of Parry is labelled as this course's extension**, in a visible
  callout. Every later lesson that leans on it must keep that label.
- **Caldeira et al. (2023) is a pointer only.** Not found on Crossref under obvious terms. The
  lesson names it as study 17 in Gray's comparative table and says so.
- **Quiz rule enforced:** every option is eight words; the correct answer sits in a different
  slot in each of the three quizzes (D, A, C) and is never the shortest or longest.
- **`GLOSSARY.md` still not created.** Two candidates flagged: *opposed / unopposed*,
  *decompose vs simplify*. Promote when Joe uses them correctly.

### Files created

| Path | What |
|---|---|
| `lessons/0001-opposed-vs-unopposed.html` | The lesson. ~40 min the way Joe works. Three quizzes, one field task. |
| `reference/0001-opposed-vs-unopposed.html` | One-page cheat sheet: two words, decompose vs simplify, the ladder, who plays the opponent, three questions, the sentence template. |
| `assets/quiz.js` | Quiz widget. Wrong = marked + coached + retry; right = marked + locked. Markup contract in file header. |
| `learning-records/0001-lesson-0001-hook-opposed-vs-unopposed.md` | Hook decision, Joe's starting floor from the interview, implications. |
| `docs/handoffs/2026-09-03-lesson-0001-shipped.md` | This file. |

### Files modified

| Path | Change |
|---|---|
| `assets/course.css` | Appended one rule: `.quiz__opt:disabled` keeps full ink. |
| `assets/README.md` | Added `quiz.js` row; removed it from "Still to build". |
| `CLAUDE.md` | `lessons/` and `learning-records/` rows now say 0001 exists. |
| `NOTES.md` | Lesson-0001 candidates block now opens with the decision and points at the learning record. |

### Changed today by a parallel session (not this one)

`MISSION.md` (rewritten in Joe's words, DRAFT banner gone), `email-shawn-myszka.md`,
`reference/gray-infographics/` (Gray's free infographics saved locally, plus a `README.md` that
already names two rows for lesson 0001). This session read them and built on them. **Do not
overwrite them; they are current.**

---

## Next actions, most important first

1. **Eric reads the lesson once.** It is open in the browser, or:
   `open ~/DEV/RTP_Constraints_Course/lessons/0001-opposed-vs-unopposed.html`
2. **Send Joe two things:** the lesson path (or a copy of the `lessons/`, `reference/` and
   `assets/` folders, since the HTML uses relative links) **and the Parry PDF.** The journal is
   paywalled; Joe cannot follow the DOI. Zotero key `CA2CRR6Z`, attachment `4TCHWHC2`.
   Yearby 2024 is free and linked in the lesson as the fallback.
3. **Wait for Joe's field task** (one unopposed drill, one opposed replacement at reduced
   pressure, five or six reps, two written lines). Lesson 0002 should open from those two lines.
4. **Then `/teach` for lesson 0002.** A human must type it. Natural next: the attentional-focus
   chain (Gray 2015 → Singh/Gokeler/Benjaminse `EYKZD68B`), because it explains the same
   athlete from the inside. Alternative: agility vs change-of-direction (verify the Young
   citation first, per `NOTES.md`).
5. Still open from earlier handoffs: Gray's $1,995 certification waitlist decision; ingest the
   Gray book (`/ingest-book`) or read first; Zotero duplicate item cleanup (UI job for Eric).

## Mid-flight

- **Who sits at the keyboard for `/teach`** is still not settled in `NOTES.md`. Lesson 0001
  is written to Joe in the second person and assumes he runs it at his laptop, per the interview.
  If Eric delivers instead, the voice still works; the quizzes do not need a facilitator.
- **The Caldeira row** should be verified before any lesson cites it as a study.
- `~/.claude/jobs/7680b1c9/tmp/parry.txt` holds the extracted Parry text for this job only. It
  is auto-cleaned. Re-pull with `zotero-research-library-pp-cli items fulltext 4TCHWHC2 --agent`.

## Gotchas found this session

- **`dcg` blocks shell redirects to a `$VAR/path`** ("redirect-truncate-dynamic-path"). Use a
  literal absolute path for the redirect target.
- The Zotero CLI works for full text: `items fulltext <attachmentKey> --agent`. The MCP is still
  gated. Page numbers survive in the extracted text as running headers (`QUEST 7`,
  `6 T. E. PARRY ET AL.`), which is how the lesson was page-cited.
