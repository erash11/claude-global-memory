# PFF API Reference (verified live 2026-09-06)

Account: `apikey@baylor.edu`, key stored in `~/DEV/Football/PFF_Data_Project/.env`
as `PFF_API_KEY`. Base URL `https://api.profootballfocus.com`. Never paste the key
into chat; read it from that file.

Answer to "do we have all the endpoints": yes for the four APIs with saved specs
(master data, grades, extended stats, premium) — 61 endpoints, all reachable and
returning 2026 data. The key also carries permissions for `a22`, `iq`,
`open_exchange`, `player_tracking`, `translations`, and `video`, but no OpenAPI
spec for those is saved locally and the docs portal (`/doc`) sits behind a browser
login, so those paths are unknown.

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
- Baylor: `team_id` 118, `franchise_id` 118, abbreviation `BAYLOR`. Not to be
  confused with Mary Hardin-Baylor, id 1245.
- Games are keyed home/away by `franchise_id`, not `team_id`
- `gsis_id` on a game row is the ESPN game id, which is the join key to
  GameOnPaper and the CFBD work
- Token carries `constraints.franchise:["118"]` but this does not restrict reads.
  All 958 NCAA teams and every opponent game come back fine.

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

All accept `?format=`. Grade rows are wide: `overall`, `offense`, `defense`,
`coverage`, `pass_rush`, `run_defense`, `discipline`, matching `*_snaps` and
`*_rank` columns, keyed by `player_id`, `unit`, `position`, `team_id`, `game_id`.
Melt to long form before storing.

## Premium (22 endpoints) — this is the play-by-play

Correction to the old Phase 0 note: premium feeds are **not** aggregated
season stats. They are play-level and player-play-level, with PFF's charting tags.
This is the layer that matters for tendency work.

Per game: `GET /v1/premium/{league}/games/{game_id}/{category}`
Per season: `GET /v1/premium/{league}/{season}/{category}`

| Category | Grain | What is in it |
|---|---|---|
| `team_play` | one row per play | down, distance, field position, quarter, clock, offense/defense, `shotgun`, `pistol`, `play_action`, `no_huddle`, `screen`, `draw`, `trick`, `trick_look`, `shift`, `pre_kick_motion`, `pump_fake`, `redzone`, personnel counts |
| `team_main` | one row per player per play | `role`, `position`, `motion`, `on_los`, `bunched`, `creeper`, `def_coverage`, `def_pass_rush`, `off_pass_route`, `off_run_block`, `off_pass_block`, per-play grades by phase |
| `passing` | one row per dropback | `route`, `pass_depth`, `pass_direction`, `coverage_scheme`, `coverage_name`, `mofo_coverage_shown` vs `mofo_coverage_played`, `off_package`, `def_package`, `time_to_throw`, `big_time_throw`, `turnover_worthy_play`, `yards_after_catch` |
| `pressure` | one row per pressure | rusher and blocker identity, `blitz`, `tech`, `shade`, `stance`, `dropback_type`, `time_to_throw_group` |
| `pass_rush` | one row per rusher per dropback | alignment `tech`/`shade`/`side`, `defensive_backs` count, `third_down_group` |
| `pass_protection` | pass-pro assignments | blocker side |
| `all_blocking` | one row per block | `block_type`, blocked player and technique, `missed_assignment`, `unblocked`, `cut`, `looper`, `spy` |
| `quarterback_charting` | one row per attempt | `pass_accuracy`, `throw_type`, `qb_look`, `rhythm`, `quick_game`, `receiver_separation`, `hit_while_throwing`, `coverage_type` |
| `rushing` | rush detail | |
| `penalty` | penalty detail | |
| `team_analysis` | play-level notes and ratings | `rps` (run/pass/special), `comment` |

Volume reference, one 2025 Baylor game (id 28762): team_play 180, team_main 3,960,
all_blocking 1,838, pass_rush 355, pressure 115, passing 86, qb_charting 85,
team_analysis 394. Season-level 2026 `team_play` is 33,553 rows and climbing.

## Extended Stats (10 endpoints)

`GET /v1/stats/extended/{league}/{season}/{category}`, optional `player_id`.
Categories: `offense`, `defense`, `receiving`, `rushing`, `special`, `kickoff`,
`kickret`, `punt`, `puntret`, `penalty`. Grain is player by game.
2026 offense returned 7,688 rows.

## Data availability and lag (checked 2026-09-06)

- Grades post first. Baylor at Auburn (game 31098, played 9/5) already had 116
  game_grade rows the next morning.
- Premium lags grades. That same game returned 0 premium rows; week 0 and the
  9/3 week 1 games were fully populated. Expect roughly one to three days.
- A `200` with an empty array means not processed yet, not an error. Always check
  row count before treating a pull as complete.
- 2025 and prior seasons are complete and safe to backfill.

## Pagination

Season collections return in full with no pagination (958 teams, 1,614 games,
33k plays in one response). Only `/v1/{league}/players` documents `page` and
`page_size`. Don't assume paging elsewhere, but assert row counts.

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

- CFBD: free tier, 1,000 calls a month, no live endpoints. Historical and
  season context only.
- GameOnPaper: live EPA and win probability, scraped, no auth.
- PFF: the only source here with charted formation, coverage, alignment, and
  pass-rush tags. Use it for tendencies, not for live in-game.
- Join on `gsis_id` (game) which is the ESPN game id used by the other two.

## Existing code

`~/DEV/Football/PFF_Data_Project/` — `src/ingest/pff_client.py`, `run_pipeline.py`,
`scripts/phase0_probe.py`, SQLite at `data/pff.db`. Specs in `docs/swagger/`.
