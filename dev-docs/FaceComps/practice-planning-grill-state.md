# Practice Planning & Prescription — Grill Session State

**Status:** ACTIVE — macro camp model design approved; building candidate models next.
**Last updated:** 2026-06-16
**Goal:** Build a plan to add a **planning & prescription layer** (MorphoCycle + color/rep
model) on top of the existing load simulator.

## 2026-06-16 — Mock-week refinement (AJ feedback, applied)

AJ reviewed the mock-week sequencing; four adjustments applied to the v2 source (`render_camp_models_v2.py`
→ regenerated v2 + v3 decks) and the brief (`2026-06-15-mock-week-brief.{md,html}`):
1. **Tuesday (red) → full pads** (was shells/thud) to mimic the regular-season hardest day.
2. **Tue/Wed situational emphases flipped** so the physical and volume stimuli split, not stack:
   **Tue = red zone / short yardage** (condensed field, collision work); **Wed = 3rd down** with
   tempo + vertical plays downfield (a red-zone emphasis on the volume day would cap reps in
   condensed space — AJ's point).
3. **"Coming out" installed early** (Mon), the way it's used in-season — was missing.
4. **Walk-through relabeled MD-2** (was "game-day minus 1"). Mock is Saturday (MD-0) → Fri = MD-1,
   Thu walk-through = MD-2.
All four mirror the in-season week, consistent with the locked "mock = run as a real game week" frame.
PDFs not regenerated in this pass (no headless-Chrome step run); HTML is current.

## 2026-06-15 — LOCKED: plan of record = 14-day (3/3/4/4) + Moderate

Staff selected the **14-day install structure (3 / 3 / 4 / 4)** run at the **Moderate** ramp as the
plan of record for 2026 fall camp — the recommended flavor of the two-structure / three-intensity
v2 comparison. Consequences:
- The other five candidates (15-day; Conservative/Aggressive) are no longer live; keep them in the
  v2 deck as the decision record, but the **coach-facing artifact is now the pruned v3 deck**
  (`2026-fall-camp-models-v3` + `-internal-v3`, md→ n/a, html+pdf) showing only this build + the
  mock week. Built by `scripts/render_camp_models_v3.py` (imports v2's machinery; lifts v2's CSS).
- The mock week (Sun/Mon green → Tue red grind → Wed yellow → Thu walk-through → Fri fast Friday →
  Sat controlled mock) is unchanged and rides on the v3 deck too.
- Next deliverable (per-day color/quality templates) targets THIS build's days, not the full matrix.

## 2026-06-15 — LOCKED: mock game = controlled rehearsal (Aranda staff confirmed)

The **Mock Game (Aug 29)** is a **controlled rehearsal of operations and timing** — it runs the
in-season game-week cadence at game-week *operations*, NOT game-week *collision*. Confirmed by
Aranda-side staff (Eric, 2026-06-15), upgrading the prior one-sided Fireflies note
("AJ & Coach Red: mock game = green day", `01KS5YFDZ0KESCNSWP1C8B4K3M`) to a staff-wide decision.

Consequences:
- **Anchors the taper.** A live/competitive mock would re-spike load during the bleed-off and break
  the freshness math every candidate model is built to deliver. Hold this line if anyone pushes to
  "make the mock competitive."
- **Resolves B6** (MorphoCycle vs camp), finalized 2026-06-15. The mock/game week is the
  morphocycle-shaped layer (run as a real game week, day-of-week aligned, drawn day-by-day on the v3
  deck); camp stays block-shaped — the 5 MC qualities do NOT tile across camp blocks. The mock-week
  day-quality is a *controlled* rehearsal, not a peak. The day-by-day color templates for
  that week are the next build (Aranda's late-June blue/green/yellow/red deliverable lives here).

## 2026-06-15 — LOCKED: NCAA five-day acclimatization is a hard front-of-camp constraint

Aug 5 = **practice day 1** (Eric confirmed Baylor runs NO pre-camp acclimatization), so the NCAA
mandatory acclimatization period governs Days 1–5 of every model and is **not a design lever**:
- **Days 1–2 (Aug 5–6):** helmets & spider pads only → GREEN ceiling.
- **Days 3–5 (Aug 7, 9, 10):** shoulder pads max, **no full pads** → never RED.
- **Full pads + live contact only from Day 6 (Aug 11 / P6).** One required day off in the first 7
  (Aug 8 film day, ≤2 hrs film). ≤2 consecutive full-contact days thereafter (already covered by
  the no-stacked-red rule). Source: NCAA preseason regs photo (prior-year dates; rule is current).

Impact on the v2 candidate models (fixed 2026-06-15, commit on this branch):
- **Conservative** (both structures) was already compliant — unchanged.
- **Moderate** (the recommendation) had full pads on P5 (Aug 10) — **one day illegal**. Fixed by
  reordering Block 2 `Y R G → Y G R` (first red moves P5→P6). Zero change to block ramp or red count.
- **Aggressive** had shoulder pads P2, full pads P3, and a live mock on P5 — **multiple violations**.
  Front rebuilt to `G G Y / Y Y R …`; B2–B4 hot plateau preserved, B1 now a mandated easy-in.
  Counts 1G/7Y/6R → 2G/7Y/5R (14-day) and 1G/7Y/7R → 2G/7Y/6R (15-day); 3rd scrimmage moved P5→P7.
- Added `check_acclimatization()` gate to `scripts/render_camp_models_v2.py`; all six machine-checked.
- **Pitch upgrade:** the rule forbids any red before Aug 11, so the easy-in start + back-loaded peak
  are partly *mandated* — the strongest form of the anti-front-loading argument.
- **Phase B (late-June per-day templates):** fold in the within-day operational caps (3-hr practice
  limit, +1 hr walk-through, 3-hr recovery between sessions during acclimatization, ≤3 scrimmages).

## 2026-06-04 session — macro camp model (BIG progress; design spec written)

Design spec: **`docs/superpowers/specs/2026-06-04-fall-camp-2026-load-model-design.md`** (read first).
Commits 4f5fab0 / 2d0df9a on main (pushed). What got locked:

- **Provenance corrected:** the FC24/FC25 GPS calibration is **Baylor's own** 2024/2025 camps.
  Kansas State 24/25 (`SourceFaces/Camp_Models.pdf` p2–3) is **structure only, no GPS** — a borrowed
  template. **Page 1 = the real Baylor 2026 projected camp = the calendar of record** (Aranda confirmed).
- **Day-type spine (3 dims):** active duration (primary), period count, Ones reps (secondary, paused).
  Historical envelopes overlap badly (green 105 / yellow 115 / red 133 — 10-min gaps) = the monotony.
- **Secondary-modifier composite RESOLVED** (earlier in session): reps gate the GREEN↔YELLOW boundary,
  74%→80% overall / 75%→88% FC25. See `docs/fall-camp/2026-06-03-secondary-modifier-test.md`.
- **In-season game-week reference built:** `simulator/scripts/build-inseason-duration.ts` →
  `docs/fall-camp/inseason_duration_2025.csv`. **100% game week = ~370 active min Mon-Thu; game day = 92 min.**
  Stable cycle Mon69/Tue105/Wed88/Thu98. GPS pulled via `catapult-openfield-connect-pp-cli` (token in
  `simulator/.env.local`); in-season activities named `{OPP} - P{N} - MM.DD.YY`. FULL 2025 season available.
- **Two findings drive the model (Baylor's own data):** (1) camps front-loaded (W2-3 ~180% cum / 147%/day);
  (2) colors not separable = training monotony (Foster). Current 2026 projected faces repeat both (2G/10Y/6R).
- **Decisions locked:** anchor on **active minutes** (PL is an outcome); **textbook 70/100/120 ramp**
  (a change from history, peak lighter); **per-day anchored, both units**; **polarize** the day-types →
  **prescribed targets green 85 / yellow 112 / red 132** (non-overlapping, 47-min green→red contrast);
  color follows dress/tempo; **peak moves to Block 4**; greens are genuinely short days.
- **MACRO UNIT = work-blocks** (consecutive days between off/film), not calendar weeks. 2026 install:
  Block1 Aug5-7 (3, 70%), Block2 Aug9-11 (3, ~90%), Block3 Aug13-16 (4, ~105%, scrim1),
  Block4 Aug18-21 (4, 120% PEAK, scrim2), Taper Aug23-29 (Mock 29), Game wk Aug30-Sep5 (Auburn).
- **DELIVERABLE = multiple candidate models** for Aranda to pick (conservative / moderate / aggressive),
  not one prescription. Dress/scrimmage sequencing is flexible.
- **NEXT SESSION:** build the 2–3 candidate block-based models. **RECONCILE** my GPS-historical targets
  (green 85 / yellow 112 / red 132) with the staff's stated meeting bands (green 80-90 / yellow 90-105 /
  red 105-120, line ~22 below) — the meeting bands are lighter and could anchor the "conservative" model.
  Deferred: output medium (HTML/Excel/Word); in-season Ones reps (manual); planned-vs-realized color validation.

## Sources reviewed (don't re-read unless needed)
- **MorphoCycle doc:** `SourceFaces/Baylor Football Fast Friday.xlsx` — 4 sheets
  (Morphocycle, Guide, Standard, Standard Football). Game-week day-quality template:
  P1 Activation 30-35% → P2 Collision 40-55% → P3 Volume/Density 55-70% → P4 Recovery 20-25%
  → P5 Speed/Decisions 35-40%. Each day has dress, field size, plays/series, density, group emphasis.
- **PreSummer_Planning** (Fireflies `01KS8B4X2AEDVNZ290YXR5PTKV`, 2026-05-22) — Aranda, Viloria,
  Klanderman, Orloff. The "large meeting." Color system (blue/green/yellow/red), rep ramp 88→180,
  5-min periods, recovery mandates, speed maintenance (90% top speed q10min). **Aranda assigned Eric
  late-June deliverables:** blue/green/yellow/red day templates, rep-progression schedule, Baylor
  history mapped into colors.
- **KSU_Planning_Brief_LYancy** (Fireflies `01KSJ7NPPAQ0X26NEMVT2M039P`, 2026-05-26) — the K-State
  methodology Rosetta Stone (see decisions below).
- **2026-05-14_Applied_Planning** (`01KRKRXFNG0AHVHFW6CCGYY24T`) — Viloria; "plan vs actual"
  accountability, practice builder tool, Aranda decided to adopt the planning tool.
- **AJ & Coach Red — Camp Load & Recovery** (`01KS5YFDZ0KESCNSWP1C8B4K3M`, 2026-05-21) — green
  80-90min / yellow 90-105 / red 105-120; "4 on, 1 off" cycles; mock game = green day.

## Current data model (simulator/lib/types.ts)
- `Practice`: season, practice_num, date, day_of_week, dress, tempo, emphasis, total_duration_min, synced_at.
- `Period`: name, order_index, minutes, pl_team_projected, pl_team_actual, pl_per_min_actual.
- Classify by PL/player → GREEN/YELLOW/RED. Domains: `'2026 Spring'`, `'2026 Fall Camp'` (18 DEF
  faces seeded to prod). **No rep, day-color, day-quality, or prescription concept exists yet.**
- Baylor constraint: indoor, no clear-sky → no yardage/max-velocity; S7 hardware (no auto-participation);
  reps must be counted manually (like K-State). Existing currency = PL/player.

## Decisions locked so far
1. **Deliverable = 3 phases, macro first:** (A) macro camp plan/ramp → (B) per-day templates
   (the late-June coach deliverable) → (C) fold into simulator as a planning layer. Macro is the
   spine; templates hang off it; software automates it. *(User leaned option 4-then-1.)*
2. **Color = day type = a single COARSE composite axis**, not two axes, no shades ("red is red").
   Composite of: duration, scripted reps, %double-rep/two-spot + good-on-good team periods, field
   condensation, dress. *(User chose "one axis"; Yancy confirmed coarse + composite.)*
3. **Rep ramp lives at the BLOCK level** (separate camp-progression layer). Block totals ramp
   88→124→152→180→taper (built backward from in-season ~180 reps/wk, the QB's season avg). Days
   undulate by color WITHIN a block to distribute that volume (e.g. 40/48/32/56). *(Option 1.)*
4. **Planning currency: reps to plan, PL/player to validate.** Reps scripted on Accountable Periods
   (TEAM / 7-on-7 / 9-on-7). Adds a rep field per accountable period (main new plumbing). PL engine
   unchanged, becomes the post-practice actual check. *(Option A.)*
5. **Color is a triad: Intended / Scripted / Realized.** Tool's core job = two comparisons:
   Intended↔Scripted (planning-time guardrail catch — the killer feature) and Intended↔Realized
   (post-practice, reuses compare page). *(Option A.)*
6. **Rep counting from FC25 scripts (resolved 2026-06-01).** Source = `SourceFaces/SCRIPTS/`
   (20 FC25 practice workbooks). Use the `DEF PRAC SCRIPT` sheet (DEF-only convention). Layout
   is two PRINT columns (left c1-9, right c10-18) read sequentially, NOT concurrently.
   - **A rep = one scripted play for The Ones (1's).** GPS pods sit on the Ones, so reps and
     PL/player measure the same population (the join is apples-to-apples).
   - **Accountable = denylist:** count every period EXCEPT individual, unit teach, special
     teams, run-through, walk-through. Robust to mid-camp renames/recolors. (CONTEXT updated.)
   - **Rack = 4 plays.** Tagged rack period → Ones reps = count of "1's" in the `(1's,2's,...)`
     rotation tag × 4.
   - **Untagged standard install period** (plain 7-on-7/9-on-7/TEAM, not situational) → default
     to the modal 1's-lead rotation for that period type, auto-filled from the tagged instances.
   - **Situational periods** (red zone, 2-min, goal line, end-of-half) → no machine-readable
     rotation; flag for a one-time human confirm. Pure clock entries (End Of Half/Game) excluded.
   - **Scrimmages (#09, #14)** → REVISED 2026-06-02: kept in the dataset, tagged
     `format=scrimmage`. Their reps count toward weekly volume but are filtered OUT of the
     band-calibration regression (scripted differently) and out of the modal default.
     **Friday WT (#19), Mock Game (#20)** → excluded (no DEF PRAC sheet).
   - **Workflow = assisted, not full-manual:** auto-generate a QA worksheet (one row per
     accountable period × practice: raw play count, tag found?, auto Ones-reps, confidence
     flag). Tagged + untagged-standard pre-filled & locked; only situational rows need review
     (~1/3, ~30-50 cells, one ~30-min pass). Reviewed sheet = locked calibration dataset, reusable.
   - **Spike result (pre-review), clean tagged days:** P01=24, P02=16, P03=32, P04=32, P05=20,
     P06=20, P07=16, P08=20, P10=28, P11=20, P12=20, P13=24. Late/situational days undercounted
     until the QA pass fills them.

## Philosophy constraint (load-bearing)
**Template-and-guardrails, NOT rigid prescription.** Yancy & Eric both: prescribing exact reps/load
"hamstrings the coaches." Tool gives a template + guardrails and flags drift; it does NOT dictate.
Plan for The Ones (QB baseline); rest follow by substitution. Don't script all 90.

## Open decision branches (resume here — roughly in dependency order)
- **B1. Color guardrail thresholds + calibration source.** APPROACH RESOLVED (2026-06-01): hybrid,
  split by axis. Realized thresholds stay as-is (Baylor GPS, already live: GRN ≤405/YEL 406-459/
  RED >459 PL/p). Scripted thresholds calibrated from Baylor's own FC25 scripts via the rep-count
  method in decision 6. STILL OPEN: the actual threshold-setting once rep/day is joined to PL/p per
  day (regress vs bucket-by-known-color), and the full composite (reps + duration + %two-spot +
  condensation + dress) weighting — reps are one input, not the whole color.
- **B2. Rep model mechanics.** LARGELY RESOLVED by decision 6 (one Ones-rep number per accountable
  period; day total = sum; rep is the planning currency, PL/p the validation). STILL OPEN: exact
  rep↔PL interaction in the composite (parallel axes vs rep-driven-with-PL-check).
- **B3. Macro Phase-1 artifact shape.** What the camp-calendar deliverable looks like (colored grid
  w/ block rep totals + per-day rep targets, à la Yancy's calendar) + the rep-progression schedule table.
- **B4. Actual-rep capture.** Adopt K-State manual student-staff rep counting (Excel→CSV), or skip
  actual reps and validate only via PL? Affects whether Realized-reps exist vs only Realized-PL.
- **B5. Simulator integration.** Does this attach to the existing `'2026 Fall Camp'` season/domain?
  New fields on Practice/Period (intended_color, scripted_reps, day_quality). New macro-planner page.
- **B6. MorphoCycle vs camp reconciliation. [RESOLVED 2026-06-15]** The MC qualities run as the
  mock/game week (a real game week, day-of-week aligned), NOT tiled across camp blocks; camp stays
  block-shaped. Mock week drawn day-by-day on the v3 deck.
- **B7. In-season vs camp scope.** Build for Fall Camp 2026 (August deadline) first; in-season
  game-week morphocycle later? (Implied yes by phase 1 = macro camp, but confirm.)

## Adjacent threads noted (not yet scoped)
- "Two-bucket" practice idea (Fergus Connelly / Cameron Josh) Eric mentioned to Yancy.
- "Match stress with stress": heavy lower-body lifts on hard practice days so light days stay light.
- Recovery mandates + speed maintenance (90% q10min) — likely out of scope for this tool.

## Artifacts created this session
- `CONTEXT.md` (repo root) — domain glossary (MorphoCycle, Block, Rep Ramp, Day Color, Accountable
  Period, The Ones, the color triad, template-and-guardrails, etc.). Single context.
- No ADRs yet (none met the hard-to-reverse + surprising + real-tradeoff bar conclusively; candidates:
  the reps-to-plan/PL-to-validate split, and color-as-single-coarse-axis — offer when resuming).

## Loose Ends (ordered, with resolution) - as of 2026-06-01

Ordered by dependency: each unblocks the next. Items 1-2 are done; resume at 3.

1. **[DONE] Commit + push the rep extractor and QA worksheet.** Pushed as 303f1e2 on main.
2. **[DONE] Reconcile CLAUDE.md / AGENTS.md mirror.** The .githooks/pre-commit requires them
   byte-identical (shared Claude Code + Codex context). Restored CLAUDE.md to a full copy of
   AGENTS.md (commit 8815925). Do NOT reintroduce the one-line @AGENTS.md import; it breaks the hook.
3. **[DONE 2026-06-02] Make the extractor preserve human-confirmed reps on re-run.** PROBLEM: extract_fc25_reps.py
   regenerates fc25_rep_calibration_QA.xlsx from scratch, so re-running AFTER the QA review would
   wipe hand-entered ones_reps_confirmed values. FIX: before writing, read any existing QA xlsx and
   carry forward non-blank ones_reps_confirmed cells (match on file+period); only auto-fill blanks.
   Small code change; do it BEFORE the human QA pass so the pass is durable.
4. **[DONE 2026-06-02] Human QA pass on the flagged situational rows** (6 rows confirmed; day
   totals recomputed, 0 rows still pending). Original note below:
   **Human QA pass on the 8 flagged situational rows** (Aug 15/17/20 worst). Open the xlsx, fill
   ones_reps_confirmed for FLAG rows. ~30 min. Produces the locked calibration rep dataset.
5. **[DONE 2026-06-02, revised] Scrimmage-inclusion decision: INCLUDE, TAGGED.** Best practice
   = don't throw data away. Scrimmages are kept in the dataset tagged `format=scrimmage`; their
   reps count toward weekly volume but are filtered out of band-calibration (and the modal). The
   extractor adds a `format` column to both sheets. Aug 15 human confirmations (TEAM TEMPO=15,
   7 ON 7=8, 2 MIN 1v1=6 → 29 reps) are preserved. Calibration set = 16 install days (r=+0.43
   unchanged). Earlier same-day EXCLUDE approach superseded.
   Original item below:
   **Scrimmage-inclusion decision.** #09 (Aug 09) and #14 (Aug 15) have DEF PRAC sheets so they got
   rep totals (16, 24), but decision 6 said exclude scrimmages. DECIDE: keep or drop. FIX: either add
   a scrimmage denylist (filename contains "Scrimmage") or confirm-keep. Affects 2 of 18 days.
6. **Validate parser accuracy** against 2-3 hand-counted practices before trusting the calibration.
   Compare script output vs a manual rep count on P01, P08, P13. Cheap insurance against a
   systematic miscount poisoning the thresholds.
7. **[ADR] Write docs/adr/0001-scripted-rep-counting.md.** The rep-counting methodology meets the
   ADR bar (hard to reverse, surprising, real tradeoff: assisted-automation vs manual vs pure-auto).
   Capture rule + rationale once the QA pass confirms the method holds.
> **MAJOR REVISION 2026-06-02 (PlanningBrief_AT-JG-ER): composite is DURATION-first, not rep-first.**
> The meeting established duration as "the biggest driver that has all the downstream effect" on
> color. Data confirms it: accountable **Period Count (after stretch)** predicts PL/player at
> r=+0.83 (FC25) / r=+0.54 (all years) and orders the zones monotonically (GREEN 10.2 < YELLOW
> 11.9 < RED 13.3), where reps alone gave r=+0.43 with an inverted RED/YELLOW mean. So reps drop
> to a SECONDARY modifier. Consequences: (a) #8 below is effectively answered — don't set
> standalone rep bands; (b) the TEAM-period rep-precision issue (rack=4 undercount, see #6 note)
> is now LOW priority since reps aren't the primary axis — keep the human-confirm fallback, don't
> over-engineer it; (c) periods are standardized to 5-min blocks so count→duration is faithful;
> (d) color becomes an INTERNAL layer (Aranda is pulling green/yellow/red off the coach face).

> **DURATION BANDS SET 2026-06-03 (true Catapult minutes).** Pulled true per-day active duration
> from Catapult (`simulator/scripts/build-duration-snapshot.ts` -> `docs/fall-camp/fall_camp_duration_thresholds.csv`;
> wall-clock min = avg_pl/pl_per_min summed over accountable periods after stretch). Duration BEATS
> period-count: r(duration,PL)=+0.89 vs +0.54; 74% exact (26/35) with ZERO green<->red misses.
> **BANDS: GREEN <=102 min . YELLOW 102-117 . RED >117.** RED is a clean hard guardrail (11/11
> separated; any day >~117 active min = red). Remaining fuzz is the GREEN<->YELLOW boundary (overlap
> 104-115 min) -> job for secondary modifiers (reps/tempo/two-spot). Period-count bands (GREEN <=11 /
> YELLOW 12 / RED >=13) stay as the coarse planning-time proxy when GPS isn't available. Data quirk to
> sanity-check: FC24 P8 = 192 active min (still correctly RED, but high for 9 periods).

8. **[SUPERSEDED by duration-first revision] B1 finish - set Scripted-color rep bands.** Reps alone
   don't separate zones (r=+0.43, RED/YELLOW inverted). Use reps as a secondary modifier, not a
   standalone band. Original method below kept for reference:
   With confirmed reps/day joined to PL/player, derive rep thresholds per color (bucket by Realized
   zone, set cutoffs at natural gaps, sanity-check vs regression).
9. **B1/B2 - define the DURATION-first composite (now the core #9).** PRIMARY = Period Count /
   duration (after stretch, 5-min blocks). SECONDARY modifiers = reps, %two-spot/good-on-good,
   field condensation, dress.
   > **COMPOSITE RESOLVED 2026-06-03 (`docs/fall-camp/2026-06-03-secondary-modifier-test.md`).**
   > Secondary modifier = REPS, applied as a GATE not a weight. RULE: duration sets the band; if
   > band==YELLOW (102-117 min) AND reps exist AND not scrimmage -> reps <=20 demote to GREEN,
   > reps >=24 keep YELLOW, 21-23 keep duration's call. Result: duration-only 74% -> composite 80%
   > overall; **75% -> 88% on the 16 FC25 install days where reps exist** (fixed P7 + P12, zero
   > breaks). Reps cut the GREEN<->YELLOW seam cleanly and do NOTHING for YELLOW<->RED (by design --
   > the >117 RED guardrail already owns that, kept conservative as a deliberate over-warn).
   > NO weighting needed; %two-spot/condensation/dress NOT required to resolve the seam. Ceiling is
   > rep COVERAGE not the rule: 4 of 7 remaining misses are FC24/scrimmage days with no reps -->
   > capturing FC24 reps (or perch-camera) is the next lever, likely ~91% overall.
   Already have: periods_after_stretch per day in docs/fall-camp/fall_camp_period_count_thresholds.csv.
   REFINEMENT: source true FC25 minutes (face MIN column) — period-count is a proxy that's only
   faithful under 5-min uniformity.
10. **B3 - macro Phase-1 artifact (Aranda late-June deliverable, target 2nd week of June).**
    Camp-calendar grid with per-day **duration/period-count targets** (primary) + per-block rep
    targets (secondary), plus the ramp table framed as **% of game week** (70/100/120/taper,
    week-3 peak, week-4 = mock = game week). NOTE: coach-facing version drops the green/yellow/red
    coding (Aranda's call) — color stays in our internal analysis view only.
11. **B4 - actual-rep capture decision.** Manual rep counting (Excel->CSV) today, but the
    **perch-camera upgrade** ($3k/yr) is aimed at monitoring player reps "particularly for
    quarterbacks" — likely path to camera-assisted Realized-rep capture, relaxing the manual
    constraint. Gate before in-season use.
12. **B5 - simulator integration.** New fields on Practice/Period (intended_color, scripted_reps,
    day_quality); new macro-planner page; attach to the '2026 Fall Camp' season/domain. The build.
13. **[RESOLVED 2026-06-15] B6 - MorphoCycle vs camp reconciliation.** The MC qualities run as the
    mock/game week (not tiled across camp blocks); camp stays block-shaped. Drawn on the v3 deck.
14. **B7 - scope confirmation.** Fall Camp 2026 first (August deadline); in-season morphocycle later.

Adjacent/unscoped (revisit later): two-bucket practice idea; match-stress-with-stress lifting;
recovery mandates + speed maintenance (likely out of tool scope).
