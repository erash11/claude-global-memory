# GPS + PFF post-game report pipeline

Built 2026-09-06 from Auburn G1. Produces AJ Tademy-style session reports and three
coordinator reports off live Catapult and PFF pulls.

## Catapult Connect API — verified working

Reference: `~/DEV/Catapult_API/CATAPULT_CONNECT_API_REFERENCE.md` (4,957 lines, 112 raw
endpoint files in `raw/`).
Token: `~/DEV/DataBase_GPS_Reporting/gps_report/.env`, var `CATAPULT_TOKEN`. Long-lived
bearer, full scope including Sensor Data (10Hz). Base `https://connect-us.catapultsports.com/api/v6`.
Rate limit 1001/min. Never echo the value.

Scope probe 2026-09-06: 200 on athletes, parameters, positions, teams, periods,
`activities/{id}?include=all`, threshold_sets, tags, venues, `/docs/spec`, `POST /stats`,
and 10Hz `/sensor` at activity and period level. `/live` and `/live/info` are 401.
`/efforts` and `/events` return 422 without `effort_types` / `event_types` params (not a
scope problem). `/webhooks` and `/webhook_config` 404 — route name unknown, check
`/docs/spec` if push is ever wanted.

### Units on this account
`max_vel` is **mph**, `total_distance` is **yards**. Confirmed: 0 of 68 athletes exceeded
their stored personal best when read as mph; reading as m/s or yd/s produces impossible
speeds. Athlete profile `velocity_max` is **m/s** — multiply by 2.23694 for mph before
computing % of PB. This matches `bulk_import.py`'s existing assumption.

### Velocity bands are broken on this account
99.6% of all game distance fell in band 1. Band 3 totaled 28 yards team-wide, bands 4-8
returned zero for all 68 athletes. High-speed and sprint distance are unreportable until
the thresholds are rebuilt in OpenField. Omit those metrics rather than printing zeros.

### No snap counts in Catapult
`total_duration` is period wall-clock, not individual field time. Every athlete shares the
same denominator, so `player_load_per_minute` ranks identically to total player load. Snap
counts must come from PFF (below).

## Metric definitions that reproduce AJ's reports
Validated against `Auburn_P5_090426.pdf`: team average PL 193 (exact), impact split
68/21/11 (exact), full volume-trend series exact.

- Team Avg Player Load = mean `total_player_load` across all athletes, **whole activity**
  including warm-up
- Effort = `explosive_ratio_(avg)`
- Impacts = `total_football_impact_count`; Contacts (OL/DL) = `total_lineman_contact_count`
- Physicality pie = `impacts_low` / `impacts_med` / `impacts_high`, normalized
- Volume trend = activities matching `- (P\d+|G\d+|MOCK GAME)`, mean PL per activity
- Position buckets: Skill = WR/S/RB/CB, Mid-Skill = LB/TE/OLB/Quarter Back, Big-Skill = DL/OL
- Page 2 groups: QB, RB, TE, WR, OL / CB, S(SAF/STAR), LB, OLB(DE/JACK), DL
- Workload color key = decile of PL within position group: 1-3 green #2EAA60, 4-5 #F1C40F,
  6-7 #E67E22, 8-9 #D35400, 10 #C0392B
- Design: green #154734, gold #FFB81C, BU mark extracted from AJ's PDF, Archivo Narrow
  headers + Barlow Semi Condensed body (stand-ins for Agency FB)

## PFF joins
- Snaps: `/v1/grades/ncaa/games/{id}/game_grade`, `overall_snaps` by unit.
  Special teams: `/v1/grades/ncaa/games/{id}/special_team_game_grade`,
  `other_special_teams_snaps`.
- Grades: `offense` / `defense` field on the same rows. **Show only at 10+ snaps** — below
  that PFF's grade is too noisy to hand a coach.
- Starters: `/v1/ncaa/franchises/118/package_depth_charts?active=true`, `depth == 1`.
  Base packages are 11 personnel (offense) and 2-4-5 (defense) = 22 starters. Caveat: this
  endpoint returns the CURRENT depth chart, not a frozen game-day card. Snapshot it on
  game morning if Week 1 needs to stay reproducible.
- Name matching: strip accents, punctuation and Jr/Sr/II/III/IV suffixes. 49 of 68 GPS
  athletes matched for Auburn G1; the 19 misses took zero snaps, the 5 PFF-only names are
  specialists who do not wear units.

## Premium play-level data
Empty the morning after the game, populated by ~24h. For game 31098 as of 2026-09-06 PM:
team_play 208, team_main 4575, passing 102, pressure 106, pass_rush 423,
pass_protection 545, rushing 78, team_analysis 395, penalty 14. `all_blocking` and
`quarterback_charting` still 0.

Gotchas found:
- `coverage_name` in the passing feed is the **coverage defender's name**, not a scheme
  label. There is no coverage-scheme field in this feed.
- Team sacks and pressures must be deduped by `play_id`; the pressure feed carries one row
  per credited defender. Baylor: 7 sacks / 14 pressures deduped vs 10 / 40 credits.
- Pressure `defensive_grade_type` values: SK sack, H hit, P hurry, plus BD and UP which
  are not pressures.
- Blitz = 5+ rushers on a play, derived by counting `pass_rush` rows per `play_id`. The
  `blitz` flag on the pressure feed only covers plays that produced pressure.

## Reports built
In `~/DEV/Catapult_API/`:
- `Auburn_G1_090526_v2.pdf` — AJ-style session report, 2 pages, snaps + grades + starter asterisks
- `Auburn_G1_OC_Report.pdf` — offense, 2 pages
- `Auburn_G1_DC_Report.pdf` — defense, 2 pages
- `Auburn_G1_ST_Report.pdf` — special teams, 3 pages

Build scripts live in the session workspace, not yet committed to a repo. Next time,
fold them into `~/DEV/DataBase_GPS_Reporting/` beside the existing `gps_report` and
`coach_report` packages.

## Auburn G1 findings worth carrying
- Nobody reached 85% of personal-best speed. Two corners cleared 80%, 46 of 68 under 50%.
  Games do not supply top-end exposure; practice has to.
- No fourth-quarter fade. Q4 team load was 22% above Q3.
- Offense ran 104 of 115 snaps from shotgun, zero no-huddle, one screen, essentially all
  11 personnel. Inside zone was 31 of 43 carries at 2.0 per attempt.
- Defense generated a 33% pressure rate with 4.19 rushers per dropback and only 6 blitzes.
  Nickel or better on 39 of 43 charted dropbacks.
- 19 base-package starters also played special teams. That group's true snap total is
  undercounted anywhere special teams is excluded.

## OneDrive gotcha
AJ's shared folder files are cloud placeholders. `device_stage_files` fails on them until
they hydrate. `open -a OneDrive` then reading each file (`head -c 8`) through
`Control_your_Mac__osascript` forces the download; wait ~20s after launching the app.
Writing INTO that shared folder is blocked by macOS privacy — deliver to `~/DEV/` instead,
or connect the folder through the desktop app's folder dialog.
