# PFF Data Project — Next Steps

Status as of 2026-06-01: Phase 0 complete; pipeline implemented, live payload
shapes verified, and the 2023-2025 resumable backfill completed into
`data/pff.db`.

Recommended order: use the local DB for analysis/export validation next. Scores
remain nullable because the live NCAA payloads currently do not expose usable
score values.

---

## 1. Real backfill (done)

Completed on 2026-06-01 with:

- `teams`: 957
- `games`: 5,042
- `players`: 12,258
- `player_seasons`: 15,974
- `pff_grades`: 175,559
- `pff_stats`: 4,776,445
- `pff_premium`: 378,505

Season-level premium completion:

- 2023: 111,998 rows
- 2024: 120,344 rows
- 2025: 146,163 rows

Use the normal backfill command for a full rebuild:

```
python run_pipeline.py --backfill
```

If resuming from a partial local DB, use:

```
python run_pipeline.py --backfill --resume
```

Resume mode skips season endpoint groups already present in the DB: grades are
complete when every in-scope game has grade rows, stats are complete when all
configured extended categories exist for the season, and premium is complete when
the season-level premium success log exists.

- Scope is ~13 target franchises → ~129 in-scope games/season × 3 seasons.
- If the inherited Codex/PowerShell proxy vars point at `127.0.0.1:9`, clear
  `HTTP_PROXY`, `HTTPS_PROXY`, and `ALL_PROXY` before running live API commands.
- Sanity-check with `--diagnose` and a few DuckDB queries before handing the DB to
  downstream analysis/export work.

## 2. Game scores (blocked by live PFF payload)

The master-data `games` payload has **no scores**. The local OpenAPI spec shows
`/v1/{league}/game_status` is player availability/injury status, not scoreboard
data. Scores are available on the grade feed's `games[]` objects from
`/v1/grades/{league}/{season}/team_game_grades` in the schema, but a live 2024 NCAA
check returned `0` non-null score rows across `1,682` game ids. The per-game
`team_game_grades` endpoint also has no score fields.

- Added `PFFClient.get_season_team_game_grades(season)`.
- `shape_games(..., scores_payload=...)` now fills `games.home_score` /
  `games.away_score` if PFF starts populating `home_team_score` /
  `away_team_score`.
- `_ingest_dimensions_and_scope` fetches the score payload before upserting games;
  current live result is still nullable score columns.
- Do not block the first backfill on scores. Add scoreboard data later from a
  separate source or if PFF begins populating NCAA score fields.

## 3. Validate premium + extended-stats against live payloads (done)

Live validation used Baylor game `26267` from 2024 week 1 plus 2024 receiving
extended stats.

- `shape_extended_stats` handled 4,868 receiving player rows into 135,411 shaped
  stat rows.
- Premium categories validated: `pass_rush` 218 rows, `pressure` 63 rows,
  `pass_protection` 315 rows, `passing` 51 rows.
- Hardened `shape_premium` for live category-specific identities:
  `pressure` uses `defensive_player_id` first, and `passing` uses
  `passer_player_id` first. Full raw JSON is still retained.
- Hardened `shape_premium` to fill missing row-level `season` / `week` from the
  payload `game` metadata when present.

---

## Lower priority / later

- **Tighten Big 12 matching.** Scope currently resolves to 13 target franchises;
  the 2024+ Big 12 has 16 members. Some may sit in differently-named `groups[].name`
  entries — inspect and adjust `_target_franchises` in `pipeline.py`.
- **Enrich `player_seasons`.** Currently derived from grade rows (no height, weight,
  jersey, class year). The `team_members` / roster endpoint can fill these; confirm
  its real shape first (the live probe returned a team object, not players).
- **Player-tracking feeds.** Deliberately deferred from v1 (see `pff_api_notes.md`).
  Add a `pff_player_tracking` table + client method + shaper when needed.
- **Scores-derived helpers.** Once scores exist, add convenience views (Baylor
  results, opponent-adjusted grade context).

---

## The larger aspiration — AMS layer

Out of scope for this repo (kept standalone by design). Once a second pipeline's DB
is in the same AMS-shaped form, a separate project can union PFF + Catapult + VALD +
Perch facts on `(pff_player_id / athlete_id, source_system, pulled_at)`. The
identity-reconciliation mapping (`roster.athlete_id → pff_player_id`) belongs to that
future project, not here.
