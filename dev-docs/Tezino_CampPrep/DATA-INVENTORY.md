# Data Inventory — Devonte Tezino (as of 2026-06-12)

## 1. Body weight — STRONG
- **Source**: `FootballBodyWeightDevelopment/BodyWeightMaster.csv`
- **Extract**: `data/tezino_bodyweight.csv` — 314 weigh-ins, 6/6/2022 to 4/20/2026
- Covers both target ramps fully (summer 2024, summer 2025) plus current spring baseline
- First look (Jun 1 to Aug 1 window vs Aug camp window):
  - **2024**: summer mean 292.8 (10 weigh-ins, 289-298), camp Aug mean 296.0 (entered camp at 300, n=4 only)
  - **2025**: summer mean 293.1 (17 weigh-ins, 288-304), camp Aug mean 290.4 (20 weigh-ins, 284-298, finished 298)
  - **2026 spring**: mean 291.2 (21 weigh-ins, 287-295, last 292 on 4/20)

## 2. Force plate (CMJ) — STRONG for 2023 through summer 2025; current 2026 now synced
- **Source**: `ForcePlate_DecisionSystem/data/forceplate.db` (DuckDB)
- **Extracts**: `data/tezino_forceplate_raw.csv` (3,346 rows long format),
  `data/tezino_forceplate_classified.csv` (83 tests with mRSI, asymmetry, ecc profile, final_group, prescription)
- **Coverage**: 83 tests, 2023-01-20 to 2026-06-08. Summer coverage good all three historical years; current 2026 CMJ now present.
- First look, summer months (avg mRSI / avg asymmetry % / dominant tier):
  - 2023: Jun 0.560 / -19.3 / gold → Jul 0.626 / -15.9 / purple → Aug 0.538 / -16.1 → Sep 0.567 / -11.1
  - 2024: Jun 0.563 / -3.4 / purple → Jul 0.651 / -7.2 / gold → Sep 0.598 / +0.8 / purple
  - 2025: Apr 0.577 / -7.3 / purple → Jun 0.518 / -2.6 / purple → Jul 0.458 / +1.8 / purple,
    **last test 7/14 dropped to 0.407 / white tier** — his worst test on record, three weeks before camp
  - Note the asymmetry normalization from -19% (2023) to near 0 (late 2024, holds through 2025)
- **Summer 2025 backfill (done 2026-06-10)**: the gap was a modifiedFromUtc coverage seam —
  daily runs (`--from-date 2026-01-01`) never see tests recorded earlier and the May backfills
  stopped at 2024. Ran `--cmj-backfill-only --from-date 2025-04-01 --recorded-from 2025-04-01
  --recorded-to 2025-09-10`: 2,531 tests / 103,769 rows pulled, 0 errors, then
  `--classify-existing` for the window (1,108 tests classified).
  Backup: `forceplate_before_summer2025_cmj_backfill_20260610.db`.
- **June 2026 VALD resync (done 2026-06-12)**: broad `run_pipeline.py --from-date 2026-01-01`
  ran long and was stopped after IMTP updated; then a targeted June CMJ backfill pulled 259
  candidate tests, inserted 10,653 metric rows, and classified 212 tests with 0 trial errors.
  Tezino now has CMJ on 2026-06-03 and 2026-06-08. Both classify as purple with green
  readiness; latest current-ramp mRSI is 0.5637 on 2026-06-08 with -12.2% asymmetry.
- **Remaining true gaps** (athlete absence, not data): no Aug 2025 CMJ (team tested ~105
  athletes that month; he only has the 8/24 IMTP), and no CMJ at all after 2025-07-14 —
  he is absent from Sep 2025 through Apr 2026 testing.
- **GAP investigated 2026-06-10**: the DB itself now extends to 2026-04-28 (155 athletes in
  2025+), so the system-wide backfill already ran. Tezino has zero CMJ tests after 2024-12-19
  under any name variant. The summer 2025 window (Jun-Aug) had near-zero CMJ volume for the
  whole team (only blank-name rows), so a recorded-date backfill of 2025-04-01 → 2025-09-10
  was run on 2026-06-10 to pull whatever VALD has for that window (backup:
  `forceplate_before_summer2025_cmj_backfill_20260610.db`).
- He is absent from CMJ testing Jan-Apr 2026 despite ~100 athletes/month testing, but no
  longer current-unknown after the June 2026 VALD resync.

## 2b. IMTP — STRONG, covers summer 2025 and June 2026
- Same DB, `imtp_tests` table: 49 tests, 2022-09-12 to 2026-06-10
  (4 metrics each: Peak Vertical Force, PVF/BM, RFD-100ms, RFD-200ms).
- **Summer 2025 weekly coverage**: 6/6, 6/11, 6/18, 7/2, 7/9, 7/16, then in-camp 8/24.
  PVF/BM ramp: ~35-38 N/kg in June → 28-32 N/kg in July → **23.9 on Aug 24 (in camp)** —
  the in-camp force drop parallels the 284-lb mid-camp weight nadir.
- Also notable: a late-2024 decline (Nov-Dec 2024 PVF/BM ~20-24 vs ~35-40 in Sep) —
  ask Eric whether there is injury/fatigue context.
- Extract: `data/tezino_imtp.csv` (extract script updated to include imtp_tests).
- June 2026 VALD resync added 8 current-ramp IMTP metric rows, 2026-06-05 to 2026-06-10.

## 3. DEXA — DEAD END (this export)
- **Source**: `DexaProject/2026Export/2026-03-26_PATIENT.csv` + `2026-03-26.mdb`
- Checked 2026-06-10 via pyodbc Access driver: the `.mdb` contains demographics only.
  Every scan/results table (ScanAnalysis, Wbody, WbodyComposition, etc.) has **0 rows**
  across all 3,504 patients. Tezino's PATIENT row exists (key `2004423690Tezinno, `,
  note the double-n typo in the key) but no scan history was exported.
- **Out of scope (per Eric, 2026-06-10)**: the scan-level data lives in a system Eric does
  not have access to. DEXA is dropped from the narrative unless access changes.

## 4. Catapult GPS — EXTRACTED (synced + pulled 2026-06-12)
- Auth resolved (Eric set token), `sync` ran clean: 522 athletes / 2,542 activities /
  1,829 parameters. Tezino athlete ID: `7a8e8546-4e0f-47df-979e-11694f73e70c`.
- **Extract**: `data/tezino_gps_sessions.csv` — 546 sessions, 2022-06-14 to 2026-06-12,
  14 metrics per session (Eric's requested set, added 2026-06-10): total_player_load,
  total_distance, max_vel, avg_player_load_session, player_load_per_minute, PL band
  counts (pl_low/high/veryhigh + their (Avg) variants), impacts_high (+Avg),
  total_high_ima_avg. Script: `scripts/extract_tezino_gps.py` (re-runnable).
- Slug gotchas (verified against live values 2026-06-10): the display name
  "PL_High (Avg)" carries the slug `pl_med_(avg)` but returns HIGH-band values
  (== pl_high on all 546 sessions) — the slug is a fossil of a pre-rename calc, the
  data is correct. The PL bands sum to total (pl_low+pl_med+pl_high+pl_veryhigh ~=
  total_player_load), so pl_med was added to complete the set. `high_load`
  ("High Player Load") is a med+high+veryhigh composite if ever needed. At
  single-athlete, per-activity granularity every (Avg) column equals its base column —
  the averages only diverge in squad-level queries.
- Summer coverage is real, not just camp: SUM22 26, SUM23 31, SUM24 26, SUM25 31
  sessions, SUM26 8 so far through 2026-06-12. Spring ball all four years (SP23-SP26).
- Camp blocks: FC22 5 sessions, FC23 11 sessions Aug 3-16,
  **FC24: ZERO sessions**, FC25: 18 sessions 7/30-8/22.
- **FC24 absence (key finding)**: last SUM24 session is 7/10/24, next session of any
  kind is 9/11/24 (Air Force week). He missed all of Fall Camp 2024 in GPS — exactly
  two months dark. Need injury/availability context from Eric.
- **FC25 mid-camp gap**: present P1-P3 (7/30-8/1), then absent P4-P9 (8/2-8/9),
  returns P10 (8/11) at reduced load (255 vs 405/394/333 in P1-P3). The gap brackets
  the 284-lb weight nadir and the 8/24 IMTP force drop — consistent picture of a
  mid-camp setback.
- **2026 status**: he IS practicing — full SP26 spring ball (Feb-Apr, PL up to 367) and
  SUM26 underway (8 sessions from 6/3 through 6/12 after the 2026-06-12 sync).
- Camp anchor dates from activity names: FC24 P1 = 8/1/2024, FC25 P1 = 7/30/2025.
- CLI gotchas for re-runs: `statistics --filters/--group-by/--parameters` all take JSON
  arrays; the `date` filter is ignored upstream (full history comes back; filter locally).

## 5. Weight room (Perch, set-level) — EXTRACTED (2026-06-11)
- **Source**: Perch API, `api.perch.fit`. Token from `DEV/PlayerProfiles_FB_03-28-2026/.env`
  (`PERCH_API_TOKEN`). Tezino Perch `user_id` = 20043; org/group_id = 959.
- **Extract**: `data/tezino_perch_sets.csv` via `scripts/extract_tezino_perch.py`
  (re-runnable). 2,946 tracked sets, 2022-06-24 to 2026-06-10, one row per set: date,
  session_id, exercise, num_reps, weight_lbs, pct_1rm, tonnage_lbs, set mean/peak
  velocity, total_work. By year: 2022:481, 2023:648, 2024:951, 2025:660, 2026:206.
  Top lifts: Bench, Back Squat, Power Clean, Front Squat, Clean Pull, Push Press,
  Trap Bar Deadlift, Hang Clean.
- **Gotchas (verified live 2026-06-11)**:
  - `/v3/sets` (POST) takes a server-side `user_id` filter AND works WITHOUT
    `exercise_id`, so one paginated stream (`next_token`) returns the athlete's whole
    history across all 116 catalog exercises. `user_ids`/`athlete_id`/`start_date`/
    `end_date` are rejected (HTTP 400); date filtering is client-side (pull all), same
    pattern as the Catapult CLI.
  - Every set reports `weight_unit` "KG" but values are pounds-scale (max Back Squat
    1RM = 525, sane as lbs, absurd as kg). Treated as lbs; the extractor prints a 1RM
    sanity check each run so a future unit change is caught.
  - `session_id` is a per-exercise tracking block, not a whole-workout day (one date can
    hold several session_ids). For training-day counts, use distinct `date`.
- **Injury-window coverage (validated)**: dense lifting both summers. 2024 stops after
  7/8 (last sessions Power Clean / Bench / Incline), consistent with the 7/10 fracture
  ending his lifting; the Acceleration mechanism is an S&C/field movement, not a tracked
  barbell lift (the accel exposure lives in Catapult, not Perch). 2025 shows he TRAINED
  THROUGH the 7/10 hip strain (lifting 7/11, 7/14, 7/16, including squat variants and
  Barbell Step Up) — a real contrast with the 2024 hard stop.
- **Why it matters most here**: the index injury (2024-07-10 left 5th MT fracture)
  occurred during an S&C session. This completes the four total-stress surfaces.

## Priority gaps to close
1. ~~Force plate 2025-2026 backfill~~ — summer 2025 done 2026-06-10; June 2026 VALD
   resync done 2026-06-12
2. ~~DEXA scan history~~ — dropped (no scan-level access)
3. ~~Catapult auth/sync + camp block pull~~ — refreshed 2026-06-12; FC24 is an athlete
   absence (no GPS at all), not a data gap
4. ~~Injury/availability context~~ — pulled 2026-06-09 into `docs/INJURY-TIMELINE.md`
   (index injury = 2024-07-10 left 5th MT fracture; 2025-07-10 hip strain, also
   Acceleration). Still confirm with Eric: the FC25 P4-P9 read, the late-2024 IMTP
   decline context, and surgery date + current clearance status.
5. ~~Perch (weight-room) set-level load~~ — done 2026-06-11 (`data/tezino_perch_sets.csv`,
   2,946 sets 2022-2026; see section 5). All four stress surfaces are now extracted and
   folded into the day-aligned ramp datasets.
