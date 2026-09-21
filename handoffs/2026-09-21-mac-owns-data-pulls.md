# Handoff — 2026-09-21 — The Mac owns the GPS, Perch and VALD pulls

## What and why

The session started with a Mac `/dev-sync`. Eric then made the Mac the one machine that pulls the three
athlete data feeds: Catapult GPS, Perch (1RM) and VALD ForceDecks (CMJ + IMTP). Before this, Perch was
decided as Windows-owned (09-20), VALD had no working pull anywhere since 2026-08-02, and GPS ran on the
Mac at 06:30 and failed when the Mac slept.

## Decisions (with the reasoning)

- **All three pulls live on the Mac.** Eric briefly chose Windows for GPS, then reversed the same
  afternoon. One writer per database: two gitignored caches drift apart without any conflict warning.
- **Pull times moved to business hours:** GPS 10:00 + 16:30, Perch 10:05 + 16:35, VALD 10:10 + 16:40.
  The Mac is awake then, so the `pmset` wake question is dropped. The jobs are 5 minutes apart so they
  do not overlap.
- **Perch was refilled from the API, not copied from Windows.** `perch_ingest.py` upserts by
  athlete/exercise/date, and each run re-derives from the API, so the Windows copy was not needed.
  Result: 13,436 rows through 2026-09-21, more than the Windows copy (13,346 on 09-19).
- **Scheduled runs pull a short window:** Perch = the last 14 days from the newest stored test_date. VALD =
  from 3 days before the last successful run (the VALD API filters by `modifiedFromUtc`).
- **Token and secret rotation skipped for now** (Catapult token, VALD client secret). Eric's call; the
  repos are private and the pulls work.

## Root cause of the VALD failure

`src/ingest/pipeline.py` had `client: "VALDClient" | None`. Python evaluates that at import time and
raises TypeError before 3.14, so every entry point crashed on import. Fixed by quoting the whole hint.
Separately, the Windows `.bat` called `pipeline.py`, which has no entry point; the real one is
`run_pipeline.py`.

## Files created or modified

- `~/DEV/DataBase_GPS_Reporting/ops/com.keystone.gpspull.plist` (times), `gps_report/pull.sh` (comment),
  `docs/STATUS.md`
- `~/DEV/PlayerProfiles_FB_03-28-2026/pull_perch.sh` (new), `ops/com.keystone.perchpull.plist` (new),
  `.gitignore`, `docs/STATUS.md`; `.venv/` (new, uv); `data/backups/perch_pre-backfill_2026-09-21.duckdb`
- `~/DEV/ForcePlate_DecisionSystem/src/ingest/pipeline.py` (fix), `pull_vald.sh` (new),
  `ops/com.keystone.valdpull.plist` (new), `.gitignore`, `docs/STATUS.md`; `.venv/` (new, uv);
  `data/backups/forceplate_pre-mac-pull_2026-09-21.db`
- `~/DEV/_INBOX/refresh_all_data.bat` (step 1 REM'd; step 3 was REM'd by the Windows session in PR #3,
  merged), `docs/STATUS.md`
- `~/Library/LaunchAgents/com.keystone.{gpspull,perchpull,valdpull}.plist` (installed and loaded)
- `~/.claude/global-memory/MEMORY.md` (GPS and VALD+Perch lines),
  `transcripts/2026-09-19.md` and `2026-09-21.md` (merge conflicts resolved by keeping both sides)
- Drive: `02_SPORTS/Football/FA2026/_Mark_for_Deletion/gps_db_handoff_2026-09-21/` (the unused GPS DB
  copy, safe to delete)

## Next actions

1. Check today's 16:30 / 16:35 / 16:40 receipts: each `logs/last_run.json` should say `"status": "ok"`
   (GPS: `DataBase_GPS_Reporting/gps_report/logs/`; Perch: `PlayerProfiles_FB_03-28-2026/logs/`;
   VALD: `ForcePlate_DecisionSystem/logs/`).
2. The Perch and VALD failure alerts have not fired yet. Treat the first real failure as the test.
3. Optional: add scipy to ForcePlate requirements (`tests/test_heterogeneity.py` needs it).
4. Optional: have `claude-stack-doctor` read the three receipts.

## Gotchas

- VALD pipeline stdout prints athlete names in `FLAG:` lines. Filter them out of anything that reaches
  chat or a transcript. `logs/` is gitignored in both new repos.
- The log line "IMTP: 0 new metric rows" undercounts (DuckDB rowcount with ON CONFLICT DO NOTHING).
  Trust the table count.
- Perch sometimes answers 502 mid-pagination. The ingest writes nothing until every page is in, so a
  retry is safe. `pull_perch.sh` tries 3 times.
- A context-mode hook blocks inline HTTP calls in Bash. Put the request in a script file instead.
