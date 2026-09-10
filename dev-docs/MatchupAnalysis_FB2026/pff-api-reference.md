# PFF API Reference (verified live 2026-09-06, field audit corrected 2026-09-07)

Account: `apikey@baylor.edu`, key stored in `~/DEV/Football/PFF_Data_Project/.env`
as `PFF_API_KEY`. Base URL `https://api.profootballfocus.com`. Never paste the key
into chat; read it from that file.

Answer to "do we have all the endpoints": yes for the four APIs with saved specs
(master data, grades, extended stats, premium) — 61 endpoints, all reachable and
returning 2026 data. The key also carries permissions for `a22`, `iq`,
`open_exchange`, `player_tracking`, `translations`, and `video`, but no OpenAPI
spec for those is saved locally and the docs portal (`/doc`) sits behind a browser
login, so those paths are unknown.

## READ FIRST: PFF omits zero-valued fields

**A field appears on a row only when its value is non-zero.** Enumerating a feed's
schema from `rows[0].keys()` silently misses most of the interesting fields. This
caused a wrong conclusion on 2026-09-07 ("PFF has no turnover or scoring data") that
took a full re-audit to catch.

Measured on game 31098:

| Feed | keys in row 0 | keys anywhere | missed |
|---|---|---|---|
| `passing` | 62 | **87** | 25 |
| `team_main` | 32 | **93** | 61 |
| `team_play` | 26 | **45** | 19 |
| `rushing` | 49 | 58 | 9 |
| `game_grade` | 17 | 40 | 23 |

Always enumerate as a union:

```python
keys = set()
for r in rows: keys |= set(r)
```

The saved OpenAPI specs in `docs/swagger/` are the authoritative field list, not any
sample response. `docs/swagger/locate.py` maps schema fields to endpoints.

## Turnovers, scoring and drives are all available

Contrary to an earlier note, none of this needs a box score.

- **Interceptions:** `premium/passing` → `interception`, `interceptor_name`,
  `interceptor_player_id`, `interceptor_player_gsis_id`
- **Fumbles:** `premium/rushing` → `fumbles`, `forced_fumbles`;
  `premium/team_main` → `off_fumbles`, `off_fumble_recovery`, `def_fumble_recovery`,
  `def_forced_fumble`, `rush_fumble`, `rush_forced_fumble`
- **Touchdowns:** `passing.touchdown`, `rushing.touchdown`, and in `team_main`
  `pass_touchdown` / `rush_touchdown` / `rec_touchdown`
- **Kicks and tries:** `team_play.st_play_type` → `fg_made`, `fg_missed`,
  `extra_point`, `two_point_pass`, `punt_*`, `kickoff_*`
- **Drives:** derive from possession changes across the ordered play sequence

Validated: this reconstructs game 31098 exactly (Baylor 16, Auburn 17) and the
turnover margin (+1 Baylor, 2 giveaways, 3 takeaways).

**Fumble attribution gotcha.** The `off_`/`def_` prefix on the recovery flags is not
reliable; 31098 has a row where an Auburn safety carries both `off_fumble_recovery`
and `def_fumble_recovery`. Decide possession by joining the recovering player's
`player_id` to the grades roster and comparing his team to the play's offense.

**Not yet implemented in `keys_grader.py`:** defensive/return touchdowns and safeties.
Game 31098 had none. The grader prints its reconstructed score every run; a mismatch
against the box means one of these occurred.

## Blitz: use `passing.blitz`, not a derived rusher count

`passing.blitz` is a **superset** of five-or-more rushers. On 31098 all 20 five-plus
plays are flagged, plus 19 four-rusher plays where a defender blitzed and someone
dropped out. It is **not** limited to plays that produced pressure (13 of 39 did).
Baylor's true blitz rate for that game is 25.6%, not the 14% a rusher count gives.

## Coverage: no scheme field exists, but `press_coverage` does

There is no Cover 1/2/3 field anywhere in these feeds. Confirmed:
- `passing.coverage_name` is the coverage **defender's name**, not a scheme label
- `team_main.def_cover` is a 0/1 flag for "was in coverage", not what coverage
  (3,876 zeros and 699 ones, matching the count of `role="Coverage"` rows exactly)
- `coverage_scheme` does not exist

`passing.press_coverage` IS charted (14 plays in 31098) and is the closest available
man-coverage proxy. `quarterback_charting.coverage_type` may add more once that feed
populates.

## Auth

1. `POST /auth/login` with header `x-api-key: <key>` returns `{"jwt": "..."}`
2. Send `Authorization: Bearer <jwt>` on every call
3. JWT lives 3600s. On `401 {"errors":{"detail":"Unauthorized"}}`, re-auth.
4. `429 {"errors":{"detail":"Too many requests"}}` is real. Back off exponentially.
5. Health check, no auth: `GET /status` returns `"Hodor"`

**Gotcha:** the default Python urllib user agent gets a `403` at the edge. Use
curl (or set a browser User-Agent on requests). Same trap as ESPN.

Send `Accept-Encoding: gzip` / curl `--compressed`; season feeds are large.

## Identifiers

- League slug: `ncaa` (also `nfl`, `ufl`, `aaf` on this key)
- Season: integer year, e.g. `2026`
- Baylor: `team_id` 118, `franchise_id` 118, abbreviation `BAYLOR`, and the play
  feeds use `TXBA`. Auburn is `ALAU`. Not to be confused with Mary Hardin-Baylor,
  id 1245.
- Games are keyed home/away by `franchise_id`, not `team_id`
- `gsis_id` on a game row is the ESPN game id, the join key to GameOnPaper and CFBD
- Token carries `constraints.franchise:["118"]` but this does not restrict reads.

## Master Data (15 endpoints)

| Path | Returns |
|---|---|
| `GET /v1/leagues` | leagues (NFL=1, NCAA=2, UFL=6) |
| `GET /v1/{league}/{season}/teams` | teams (958 for NCAA 2026); conference is in `groups[]` |
| `GET /v1/{league}/{season}/games` | games (1,614 for NCAA 2026, weeks 0-13 and 15) |
| `GET /v1/{league}/players` | players; `page`, `page_size` |
| `GET /v1/{league}/players/latest` | latest snapshot; `q`, `id`, `sort`, `dir`, `updated_since` |
| `GET /v1/{league}/players/export` | bulk player CSV |
| `GET /v1/{league}/franchises` | franchises |
| `GET /v1/{league}/franchises/{franchise_id}/team_members` | roster; `effective_date` |
| `GET /v1/{league}/franchises/{franchise_id}/package_depth_charts` | depth chart by package; `active` |
| `GET /v1/{league}/depth_charts` | all depth charts (25,732 rows NCAA) |
| `GET /v1/{league}/injuries` | injury detail (7,228 rows) |
| `GET /v1/{league}/game_status` | game availability (4,874 rows) |
| `GET /v1/{league}/practice_status` | practice status (229 rows) |
| `GET /v1/player_combine_results` | combine; `player_id` |
| `GET /v1/player_pro_day` | pro day; `player_id` |

## Grades (12 endpoints)

Per game:
- `GET /v1/grades/{league}/games/{game_id}/game_grade` — per player per game
- `GET /v1/grades/{league}/games/{game_id}/team_game_grades`
- `GET /v1/grades/{league}/games/{game_id}/special_team_game_grade`

Per season:
- `GET /v1/grades/{league}/{season}/game_grade` — every player game grade
- `GET /v1/grades/{league}/{season}/special_team_game_grade`
- `GET /v1/grades/{league}/{season}/season_grade` (27,333 rows for 2026)
- `GET /v1/grades/{league}/{season}/special_team_season_grade`
- `GET /v1/grades/{league}/{season}/career_grade`
- `GET /v1/grades/{league}/{season}/team_season_grades`
- `GET /v1/grades/{league}/{season}/team_game_grades`

Season to date by week:
- `GET /v1/grades/{league}/{season_id}/{week_id}/season_grade`
- `GET /v1/grades/{league}/{season_id}/{week_id}/special_team_season_grade`

Grade rows are wide and sparse: `overall`, `offense`, `defense`, `coverage`,
`pass_rush`, `run_defense`, `discipline`, `pass_block`, `run_block`, `receiving`,
`pass`, `run`, with matching `*_snaps` and `*_rank` columns. Forty distinct keys
across rows, seventeen on row 0. Melt to long form before storing.
`game_grade` + `special_team_game_grade` together give a complete `player_id -> team`
roster map, which is what the fumble attribution join needs.

## Premium (22 endpoints) — the play-by-play

Per game: `GET /v1/premium/{league}/games/{game_id}/{category}`
Per season: `GET /v1/premium/{league}/{season}/{category}`

| Category | Grain | What is in it |
|---|---|---|
| `team_play` | one row per play | down, distance, `field_position`, quarter, clock, offense/defense, `shotgun`, `pistol`, `play_action`, `no_huddle`, `screen`, `draw`, `trick`, `trick_look`, `shift`, `pump_fake`, `redzone`, **`motion`**, **`option`**, **`offense_package`**, **`defense_package`**, `route`, `run_concept_1..3`, `poa_actual`, `pass_zone`, `timeout`, `st_play_type` |
| `team_main` | one row per player per play | `role`, `position`, `on_los`, `bunched`, per-play grades, plus a full per-player box: `def_tackle`, `def_missed_tackle`, `def_stop`, `def_sack`, `def_pressure`, `def_forced_fumble`, `def_fumble_recovery`, `rec_target`, `rec_drop`, `rec_touchdown`, `rush_yards_after_contact`, `pass_interception`, `off_fumbles` |
| `passing` | one row per dropback | `route`, `pass_depth`, `pass_direction`, `coverage_name` (defender), `off_package`, `def_package`, `time_to_throw`, `big_time_throw`, `turnover_worthy_play`, `yards_after_catch`, **`interception`**, **`touchdown`**, **`blitz`**, **`press_coverage`**, `stunt`, `contested`, `drop`, `sack`, `incompletion_type`, `passer_grade` |
| `pressure` | one row per credited defender per pressure | rusher and blocker identity, `blitz`, `tech`, `shade`, `stance`, `dropback_type`, `defensive_grade_type` (SK/H/P, plus BD and UP which are not pressures) |
| `pass_rush` | one row per rusher per dropback | alignment `tech`/`shade`/`side`, `defensive_backs` count, `stance` |
| `pass_protection` | pass-pro assignments | blocker `side`, `dropback_type` |
| `all_blocking` | one row per block | `block_type`, blocked player, `missed_assignment`, `unblocked`, `cut` |
| `quarterback_charting` | one row per attempt | `pass_accuracy`, `throw_type`, `qb_look`, `rhythm`, `quick_game`, `receiver_separation`, `hit_while_throwing`, `coverage_type` |
| `rushing` | rush detail | `run_concept_1/2`, `run_direction`, `yards_after_contact`, `first_contact_name`, `tackler_name`, **`fumbles`**, **`forced_fumbles`**, **`touchdown`**, `tackles_avoided` |
| `penalty` | penalty detail | `pen_type`, `pen_detail`, `pen_on` |
| `team_analysis` | play-level notes | `rps` (run/pass/special), `comment` (coaching shorthand), `away_type`/`home_type` |

Volume, game 31098: team_play 208, team_main 4,575, pass_protection 545, pass_rush
423, team_analysis 395, pressure 106, passing 102, rushing 78, penalty 14.
`all_blocking` and `quarterback_charting` were still 0 as of 2026-09-07.

## Extended Stats (10 endpoints)

`GET /v1/stats/extended/{league}/{season}/{category}`, optional `player_id`.
Categories: `offense`, `defense`, `receiving`, `rushing`, `special`, `kickoff`,
`kickret`, `punt`, `puntret`, `penalty`. Grain is player by game.
Carries `fumbles`, `fumbles_lost`, `fumble_recoveries`, `forced_fumbles`.
2026 offense returned 7,688 rows.

## Data availability and lag

- Grades post first, within about 12 hours.
- Premium lags grades by roughly one to three days.
- `all_blocking` and `quarterback_charting` lag the rest of premium.
- A `200` with an empty array means not processed yet, not an error. Always check
  row count before treating a pull as complete.
- 2025 and prior seasons are complete and safe to backfill.

## Pagination

Season collections return in full with no pagination. Only `/v1/{league}/players`
documents `page` and `page_size`. Don't assume paging elsewhere, but assert row counts.

## Baylor 2026 game ids

| Wk | Game id | Date (UTC) | ESPN id |
|---|---|---|---|
| 1 | 31098 | 2026-09-05 | 411396 |
| 2 | 31122 | 2026-09-13 | 411504 |
| 3 | 31257 | 2026-09-19 | 411571 |
| 4 | 31278 | 2026-09-26 | 411683 |
| 5 | 31348 | 2026-10-03 | 411698 |

Twelve games total. Pull the full list from `/v1/ncaa/2026/games` filtered on
`franchise_id` 118.

## Where PFF fits next to the other sources

- CFBD: free tier, 1,000 calls a month, no live endpoints. Historical only.
- GameOnPaper: live EPA and win probability, scraped, no auth.
- PFF: charted formation, alignment, pressure and personnel, **plus turnovers and
  scoring**. Use it for tendencies and for keys grading, not for live in-game.
- Join on `gsis_id` (game) which is the ESPN game id used by the other two.

## Existing code

`~/DEV/Football/PFF_Data_Project/` — `keys_grader.py` (Keys to Victory auto-grader,
see `docs/keys-framework.md`), `src/ingest/pff_client.py`, `run_pipeline.py`,
`scripts/phase0_probe.py`, SQLite at `data/pff.db`. Specs in `docs/swagger/`,
with `scan.py` and `locate.py` for auditing fields against endpoints.
Week 1 analysis scripts in `data/week1_auburn/`.
