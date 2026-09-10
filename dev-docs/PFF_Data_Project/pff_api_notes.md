# PFF API Notes — Phase 0 COMPLETE (2026-05-24)

Contract confirmed by reading the authenticated docs (`api.profootballfocus.com/doc`)
and live probing. Full OpenAPI specs saved under `docs/swagger/*.yaml`. The client
(`src/ingest/pff_client.py`), pipeline, and shaper can now be implemented against
this.

---

## Authentication — two-step, JWT bearer

1. **Exchange API key for a JWT:**
   ```
   POST https://api.profootballfocus.com/auth/login
   Header: x-api-key: <PFF_API_KEY>
   → 200 {"jwt": "<JWT>"}
   ```
2. **Call APIs with the JWT:**
   ```
   Authorization: Bearer <JWT>
   ```
3. **Expiry:** JWT is valid **3600s (1 hour)** (`expires_in`, and `exp - iat = 3600`
   in the token payload). On `401 {"errors":{"detail":"Unauthorized"}}`, re-auth via
   step 1. Client should cache the token in memory and refresh ~60s before `exp`
   (mirror `ForcePlate_DecisionSystem/src/ingest/vald_client.py`).
4. **Rate limiting:** real — `429 {"errors":{"detail":"Too many requests"}}`. Back off
   and retry (exponential). Exact limits undocumented; be conservative.
5. **gzip:** supported. Send `Accept-Encoding: gzip`; `requests` decompresses
   automatically.

### This account (key `320599…`, `apikey@baylor.edu`)
- **Permissions / APIs:** `a22, grades, iq, master_data, open_exchange,
  player_tracking, premium, stats_extended, video`
- **Leagues:** `aaf, ncaa, nfl, ufl`  → **use `ncaa`**
- **Constraint:** token carries `constraints.franchise:["118"]`, BUT this does **not**
  restrict reads — master data returns all 931 NCAA teams, and game-grade calls
  succeed for non-Baylor games. **Full Baylor + Big 12 + opponent scope is
  achievable.**

---

## Key identifiers

- **Base URL:** `https://api.profootballfocus.com`
- **League slug:** `ncaa`
- **Season:** integer year, e.g. `2024`
- **Baylor:** team `id` = **118**, `franchise_id` = **118**, abbreviation `BAYLOR`,
  nickname `Bears`, colors `#003015` / `#ffbc19`. (Set as `BAYLOR_TEAM_ID=118` in
  `.env`.) ⚠️ Do not confuse with "Mary Hardin - Baylor" (`id` 1245).
- **Health check (no auth):** `GET /status` → `200 "Hodor"`

---

## Endpoint catalog (NCAA-relevant)

Full specs in `docs/swagger/`. `{league}=ncaa`, `{season}=YYYY`.

### Master Data (`docs/swagger/master-data.yaml`)
| Path | Returns |
|---|---|
| `/v1/leagues` | leagues (NFL=1, NCAA=2, UFL=6) |
| `/v1/{league}/{season}/teams` | all teams that season (931 for NCAA 2024) |
| `/v1/{league}/{season}/games` | all games that season (1686 for NCAA 2024) |
| `/v1/{league}/players` | players |
| `/v1/{league}/players/latest` | latest player snapshot |
| `/v1/{league}/players/export` | bulk player export |
| `/v1/{league}/franchises` | franchises |
| `/v1/{league}/franchises/{franchise_id}/team_members` | franchise's team(s) |
| `/v1/{league}/franchises/{franchise_id}/package_depth_charts` | depth charts |
| `/v1/{league}/depth_charts`, `/v1/{league}/injuries`, `/v1/{league}/game_status`, `/v1/{league}/practice_status` | situational |

### Grades (`docs/swagger/grades-feeds.yaml`) — signature data
| Path | Grain |
|---|---|
| `/v1/grades/{league}/games/{game_id}/game_grade` | **per-player per-game** |
| `/v1/grades/{league}/games/{game_id}/team_game_grades` | per-team per-game |
| `/v1/grades/{league}/games/{game_id}/special_team_game_grade` | ST per-game |
| `/v1/grades/{league}/{season}/game_grade` | all player game-grades, season |
| `/v1/grades/{league}/{season}/season_grade` | per-player season |
| `/v1/grades/{league}/{season_id}/{week_id}/season_grade` | per-player to-date by week |
| `/v1/grades/{league}/{season}/team_season_grades`, `team_game_grades` | team rollups |
| `/v1/grades/{league}/{season}/career_grade` | career |

### Extended Stats (`docs/swagger/stats-extended.yaml`)
`/v1/stats/extended/{league}/{season}/{category}` where category ∈
`offense, defense, receiving, rushing, special, kickoff, kickret, punt, puntret, penalty`.

### Premium (`docs/swagger/premium-feeds.yaml`) — PFF advanced metrics
Per-game: `/v1/premium/{league}/games/{game_id}/{category}` and per-season:
`/v1/premium/{league}/{season}/{category}`, category ∈ `passing, rushing,
pass_protection, pass_rush, pressure, quarterback_charting, all_blocking, penalty,
team_main, team_play, team_analysis`.
**Note — corrected 2026-09-09.** An earlier version of this line called these
"aggregated advanced stats per player/team per game — not raw play-by-play". That is
wrong, and it cost a later project real time. **These feeds are play-level.** Every row
carries a `play_id`, and rows join to each other on it.

- `team_play` is the master play list: `down`, `distance`, `field_position`, `offense`,
  `defense`, `offense_players`, `defense_players`, `shotgun`, `pistol`, `play_action`,
  `screen`, `draw`, `no_huddle`, `shift`, `trick`, `redzone`, `st_play_type`.
- `quarterback_charting` carries per-play `coverage_type` — **dropbacks only**
  (93% filled on the game sampled).
- `rushing` carries `def_package`, so run plays get defensive context from there
  instead. The two are different fields and must not be pooled.
- `passing` carries `target_name`, `route`, `pass_depth`, `blitz`, `press_coverage`.

Verified against the 2026-09-07 probe in `data/week1_auburn/`. What PFF does *not*
provide is a single canonical play-by-play endpoint; the play grain is assembled by
joining these category feeds on `play_id`.

---

## Confirmed response shapes

### `/v1/ncaa/2024/games` → `{teams[], leagues[], games[], stadiums[]}`
Game row:
```json
{"id":26200,"start":"2024-08-24T16:00:00Z","week":0,"season":2024,
 "league_id":2,"league":"NCAA","gsis_id":"403791",
 "away_franchise_id":167,"home_franchise_id":176,
 "stadium_id":195,"neutral_stadium":true,"kickoff_time":null}
```
Note: home/away keyed by **`franchise_id`**, not team_id. No score in this payload.
The grade feed schema includes `games[].home_team_score` / `games[].away_team_score`,
but a live 2024 NCAA `team_game_grades` check returned zero non-null score rows.
The pipeline keeps nullable score columns and fills them if PFF starts populating
those fields. `week` 0 = week zero.

### `/v1/ncaa/2024/teams` → `{teams[]}`
```json
{"id":118,"franchise_id":118,"league_id":2,"league":"NCAA",
 "abbreviation":"BAYLOR","nickname":"Bears","slug":"baylor-bears",
 "primary_color":"#003015","secondary_color":"#ffbc19","start_season":1980,
 "end_season":3000,"groups":[{...conference/division...}]}
```
Conference membership is inside `groups[]` (e.g. for D1 teams; the Buffalo State
sample showed `NCAA D3`). Big 12 filtering → inspect `groups[].name`.

### `/v1/grades/ncaa/games/{game_id}/game_grade` → `{game_grade[]}`
Per-player row (**wide**, columns vary by `unit`/`position`):
```json
{"player_id":142476,"player":"Clemente Ojinnaka","position":"DI","unit":"defense",
 "team":"PADU","team_id":155,"game_id":26212,"week":1,"season":2024,
 "game":"PADU@OHTO","overall_snaps":22,
 "run_defense_snaps":6,"run_defense":61,"pass_rush_snaps":7,"pass_rush":72.1,
 "defense":69.4,"discipline":71.7}
```
Grade columns observed: `overall`/`offense`/`defense`, `pass_rush`, `run_defense`,
`discipline`, plus `*_snaps`. Offensive units will expose `pass`, `run_block`,
`pass_block`, `receiving`, etc. **Shaper must melt these wide grade columns into long
`(grade_type, grade_value, snap_count)` rows** for the `pff_grades` table.

---

## Pagination
Not yet observed in responses (season endpoints returned full arrays: 931 teams,
1686 games in one call). Likely **no pagination** on these collection endpoints, or
very high page sizes. Confirm in spec `parameters` during impl; handle a `limit`/
`offset` if present but don't assume it's required.

---

## SCHEMA IMPLICATION — needs a decision before implementation

The approved plan modeled `plays` + `play_participation` tables for raw play-by-play
**with PFF tags (pressure, coverage, pass_rush_moves)**. The API exposes no single
canonical play-by-play endpoint. Instead it offers **Premium feeds**.

**Corrected 2026-09-09:** this section previously described those feeds as "aggregated
advanced stats per player/team per game". They are not aggregates — they are
**play-level**, keyed by `play_id`, and the play grain is recovered by joining the
category feeds on that key. See the corrected note under *Premium* above. The
`pff_premium` design below still holds; only the reason given for it was wrong.

**Proposed adjustment:** drop `plays` / `play_participation`; replace with a
`pff_premium` long-format fact table:
`(game_id, pff_player_id, category, stat_name, stat_value, source_system, pulled_at)`
keyed like `pff_stats`. This captures pressure/pass-rush/coverage at the grain PFF
actually provides, and stays AMS-shaped. (Player-tracking feeds may offer finer data —
out of scope for v1.)

---

## Decisions locked after Phase 0
- **Auth pattern:** `POST /auth/login` + `x-api-key` → JWT; Bearer for all calls;
  cache + refresh on 1h expiry / 401. (Mirror VALD client.)
- **Endpoints v1:** master-data (teams, games, players), grades (game_grade +
  season_grade), stats-extended, premium.
- **Deferred:** video, a22, iq, open_exchange, player_tracking, play diagrams.
- **plays/play_participation:** REPLACE with `pff_premium` (pending user OK).
