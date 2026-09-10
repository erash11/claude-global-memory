# The post-practice coach report — what still needs deciding

The prototype asked a coach to react to three design directions on synthetic data. The
data is now real, and it answers some of those questions for us and sharpens the rest.
This is the shortlist of decisions left, with a recommendation on each so there is
something concrete to argue with.

The current dashboard (`python -m kinexon.build_dashboard`) already implements a
defensible default for every one of these. Nothing below is blocked — it is all
"is this the right default".

> **Status, 2026-08-03.** §1, §2, §3, §4, §6 and §7 are now **answered** and built.
> The design is in `docs/superpowers/specs/2026-08-02-post-practice-report-design.md`
> and it shipped as `python -m kinexon.build_report`. **§5 is still open** and is the
> only one that cannot be closed in code — it needs an answer from the volleyball
> staff about what drill-level export costs in-season.

---

## Settled by the data, not by preference

**Acute:chronic is out, for now.** It needs ~28 days; we have three. The prototype's
variant A was built around it. It comes back for free once four weeks are ingested.

**"Compared to what" has exactly one answer available today:** each athlete against her
own mean over these six practices. Not a squad average (a libero and a middle are not
comparable), not a population norm (we do not have one). With n=6, the honest framing is
*"unusual for her"*, not *"too much"*. The dashboard prints n everywhere it uses this.

**Jump load in joules cannot be the headline.** It only exists for Practice 1.
`Mechanical Load` is the load metric present for all six.

**Nothing heart-rate based is possible.** Those columns are empty in every row, and
there is no heart-rate collection capability in place to fill them. This is not a
"once we start pairing straps" item — everything here is external load, and internal
load is out of scope until that capability exists.

---

## 1. What is the report *for* — and when is it read? — **ANSWERED**

**The debrief, as its own artifact.** `build_report` emits one self-contained file per
practice; the dashboard keeps a browsable debrief tab. Both render the same precomputed
structure, so they cannot disagree.

The *timing* half of this question is still unanswered and still needs a coach: whether
a report landing 30 minutes after practice gets read, or whether the useful moment is
the next morning. Until that is settled, delivery stays manual — a file on the share
drive — because that is the one option that does not bet on the answer.

---

<details>
<summary>Original framing</summary>


The three plausible jobs pull the design in different directions:

| Job | Read when | Wants |
|---|---|---|
| **Debrief** — what happened today | that evening | one session, depth, drill detail |
| **Tomorrow's plan** — what do I change | night before | today vs the last few, exceptions only |
| **Weekly** — how is the block tracking | Monday | the grid, cumulative totals |

*Recommendation:* build the **debrief** first and make it the emailed artefact — it is
the one that has a natural trigger (practice ended) and the one the drill data makes
genuinely new. The block view already covers the weekly job well enough to defer it.

**Question for the coach: does a report that lands 30 minutes after practice actually
get read, or is the useful moment the next morning?** This changes whether we automate
on session-end or on a schedule.

</details>

## 2. What is the headline number? — **ANSWERED**

**Jumps and jumps per minute together, mechanical load second**, as recommended. The
report is fixed to them and has no metric picker: an artifact you hand someone should
not depend on which control they last touched. `--metric` overrides it.

Practice 6 is why. Second-lowest jump total in the block, second-highest density, and
the generated verdict for it reads:

> Second-shortest session of the block. 900 jumps at 9.39/min, against a block average
> of 1,015 and 6.78/min.

A report leading on totals alone would have called it the easy day.

<details>
<summary>Original framing</summary>


Right now the dashboard leads with squad jumps and lets you switch metric. Options:

- **Jumps** — most legible, most volleyball-specific, but blind to how hard they were
- **Mechanical load** — Kinexon's landing/impact measure; the better injury-adjacent number
- **Jumps per minute** — the one that survives a 1h36m session next to a 3h46m one

The block makes the case for density hard to ignore: Practice 6 has the *second-lowest*
jump total but the *second-highest* density, because it was half as long. A report
leading on totals would call Practice 6 an easy day. It was not.

> **Correction, 2026-08-03.** This paragraph originally said Practice 6 had the *lowest*
> jump total. It does not — Practice 2 does, at 529 against Practice 6's 900. Checked
> against the database: totals ascending are P2, P6, P5, P1, P4, P3. The argument is
> unaffected and the code never carried the error; the generated verdict for Practice 6
> reports only its duration, because its total sits 0.28 standard deviations from the
> block mean and never qualified as notable.

*Recommendation:* lead with **jumps and jumps/min together**, load second.

</details>

## 3. Does "above her own average" read as good or as risk? — **ANSWERED**

**Risk.** Settled 2026-08-02.

> "Above her average would mean more towards the risk side of the continuum than would
> mean that she's progressing. This is because we're looking at these loading parameters
> from a volume, intensity, and density standpoint to get a better gauge on the work
> demands the athletes have been exposed to."

The reasoning matters as much as the answer: these are **exposure** measures, not
performance measures. A higher number means more work absorbed, not better work done. So
the poles are now warm-above / cool-below everywhere the dashboard compares an athlete to
her own normal — the ranked session bars, the block grid in "vs own normal" mode, and the
pre-to-post readiness change (where a *decline* takes the warm pole, since a decline is
the adverse direction for an outcome measure).

The distinction between the two is worth holding onto as more metrics arrive: for an
**exposure**, up is the risk direction; for an **outcome** like Peak Power / BM, down is.
Getting that backwards on a single chart would quietly invert its meaning.

## 4. Everyone, or only the exceptions? — **ANSWERED**

**Both, in that order.** The named exceptions come first — a coach reading this after
practice wants the names, not to scan sixteen bars for them — and the full ranked list
follows, because it doubles as the attendance and sensor check that caught the issues
in §6.

The threshold is |z| ≥ 1.5 against the athlete's own block mean, the same one the
dashboard already flagged, so the two views can never disagree about who is unusual. An
athlete needs at least three sessions behind her average to be eligible at all, and the
n is printed wherever it is below the full block.

<details>
<summary>Original framing</summary>

Sixteen athletes fit on one screen, so the current design shows all of them ranked. At
a full roster of 18–20 with a scroll, "show me the four who are unusual" may beat "show
me everyone in order".

*Recommendation:* keep the full ranked list — it doubles as the attendance/sensor check
that caught the issues in §6 — but lead with a one-line exceptions summary above it.

</details>

## 5. Is drill-level export worth the extra work?

This is the highest-leverage question in the document.

Practice 1 was exported drill by drill. It shows Box Drill running at **26.8 jumps per
minute** and Whirlwind at **3.9** — a 7× spread inside one session that the session total
completely hides. The other five practices were exported as a single block, so for those
we can say a practice was heavy but never *which part of it* was.

If drill-level export becomes routine, the report stops describing the day and starts
describing the *plan* — which drills cost what, and what swapping one for another buys.
That is a different and much more useful product.

**Question: what does it actually take to cut sessions into drills in KINEXON OS, and is
that sustainable during the season?** If it is 10 minutes of tagging, it is worth it.

## 6. What do we do about the four data-quality items? — **ANSWERED (mechanism)**

The report now distinguishes two states, and the distinction is the point:

- **Confirmed** — a human entry in `config/data-quality.json` (gitignored;
  `config/data-quality.example.json` shows the format). Held out of the named
  exceptions and out of the usable count, kept in the ranked chart greyed, reason
  printed in the data notes.
- **Suspected** — one of `verify`'s heuristics. Never excluded on its own. Reported as
  unreviewed, and confirming it retires it so nobody appears as both.

With no config the report excludes nothing and prints *"no data-quality review on
file"* plus the unreviewed count. It can neither invent an exclusion nor present
unreviewed data as clean, and an entry naming someone off the roster is a hard error
rather than a silent no-op.

**The four items themselves still need a human answer.** The mechanism for recording
that answer exists; the answer does not. That is a conversation with the staff.

<details>
<summary>Original framing</summary>


`python -m kinexon.verify` flags these every run, with names (detail in
`data-inventory.md`; names are kept out of tracked files):

- jersey #9 assigned to two athletes
- one outside hitter at 23 block jumps against a 379 median for her group
- two zero-jump sessions, in a 2h 40m and a 3h 46m practice
- one middle blocker present from P4 only

A report that shows an athlete at "−74% vs her own normal" when the real story is a
sensor problem will burn trust faster than anything else on this list.

*Recommendation:* the report carries a short, visible **data-quality line** — "15 of 16
athletes with usable data, one excluded, see notes" — rather than silently printing a
number nobody believes. Decide with the staff which of the four are real.

</details>

## 7. How does it get delivered? — **ANSWERED**

**A file on the share drive, for now**, as recommended. `build_report --all` writes one
self-contained page per practice; it opens anywhere, needs no server or login, and
carries a print stylesheet so `html-to-pdf` produces a clean page rather than a
screenshot of a web app.

Email and scheduling stay unbuilt deliberately. Both depend on the timing half of §1,
which needs a coach's answer, and automating on the wrong trigger is harder to undo
than not automating at all.

<details>
<summary>Original framing</summary>

Currently one self-contained HTML file — opens anywhere, no server, no login, and it is
gitignored because it carries athlete names. Realistic options: leave it as a file on the
share drive, email it after each session, or print to PDF (`html-to-pdf`).

*Recommendation:* file on the share drive now; revisit once §1 settles whether the
useful moment is post-practice or next-morning.

</details>

---

## 8. Force plate readiness is now joined in — what is still missing

Volleyball CMJ is read live from the central force plate store
(`ForcePlate_DecisionSystem/data/forceplate.db`) and joined to practice load by athlete.
All 16 Kinexon athletes match, via an alias map for the three whose VALD spelling differs
from their preferred name.

What that gives today:

- **Who entered the block where** — last Peak Power / BM before 30 July, per athlete
- **Load absorbed against entry readiness** — the scatter that flags high-load /
  low-readiness athletes
- **Individual jump histories** — 24–29 CMJ tests per athlete going back to January

What it cannot give:

- **The block's effect on readiness.** There is no CMJ on or after 2 August. The pre/post
  comparison is written and returns "no post-block test yet"; it fills in automatically
  the day one is recorded. `docs/volleyball-jump-testing-ask.md` is the memo making that
  case to the volleyball staff.
- **Two athletes' baselines are 98 days old** (last tested 23 April). The dashboard fades
  their bars and says so rather than treating them as current.

Peak Power / BM is the default readiness metric, chosen on measured responsiveness from
687 paired football athlete-weeks rather than convention. RSI-modified — the field's usual
default — was the second *noisiest* measure in that analysis and is shown only with the
caveat attached.

## What would come next in the pipeline

None of this is blocked on the API. The CSV path works and is idempotent. When Kinexon
credentials arrive, `kinexon.ingest` gains a second source and nothing downstream changes.

The three things that would most improve the report are not code: **a post-block CMJ**
(§8), **drill-level exports** (§5), and **four weeks of practice history** (which unlocks
acute:chronic on its own).
