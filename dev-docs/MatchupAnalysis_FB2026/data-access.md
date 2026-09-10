# Data access — MatchupAnalysis_FB2026

## Credential handling
Never ask Eric to paste API keys into chat. Keys live on his Mac and are read into a shell
variable inside a command, never echoed and never printed in tool output.

- CFBD key: `~/DEV/CFB_Victory_Model/.env`, variable `CFBD_API_KEY`
- Requires folder access to `/Users/kristinarash/DEV` (request it, then read from
  `$HOME/mnt/DEV/...` inside `device_bash`)
- Reference doc: `~/DEV/CFBD_API_Access_Verification_2026-08-13.md` (full 74-endpoint probe)

## CFBD account limits (verified 2026-09-05)
Free tier. 1,000 calls per month, hard cap, shared with the college basketball product.
Resets the 1st of the month UTC.

**CFBD cannot do live in-game data on this tier.** These are 401-gated:
`/live/plays`, `/scoreboard`, `/games/weather`, and all four `/wepa/*` opponent-adjusted
endpoints. Treat CFBD as pull-once-and-persist for historical and season-level work,
not as a live feed.

Known traps: `/plays/stats` silently caps at exactly 2000 rows with no error or pagination,
so always filter by `gameId` or `team` and assert `len(rows) != 2000`. `/game/box/advanced`
takes `id`, not `gameId`.

## The three-layer split
- **Live, in-game:** GameOnPaper (no auth) for advanced metrics, ESPN's public site API for
  score, clock, drive state, win probability, and betting lines
- **Historical and season context:** CFBD, cached locally
- **Pre-registered baseline:** `~/DEV/CFB_Victory_Model/frozen_predictions_2026.csv`,
  full-season Baylor predictions frozen 2026-07-26

## GameOnPaper scraping
Pages render server-side at `https://gameonpaper.com/cfb/game/{espn_game_id}` and parse
cleanly with `pandas.read_html`. There is no public JSON API; `api.gameonpaper.com` 404s.
Table layout: 0 overall, 1 expected points, 3 rushing, 4 explosiveness, 5 situational,
6 drives, 8 turnovers, 9 and 12 player EPA, 18 drives with start WP%, 19 all plays with
EPA and WPA. Unnamed columns are away team then home team.

ESPN blocks the container's default urllib user agent. Use `curl` via subprocess.

Tracker script: `~/watch/gop.py <espn_game_id>` in the session workspace.

## Prior art
`~/DEV/CFB_Victory_Model/` has `cfbd_pull.py`, `weekly_capture.py`, `evaluate_all_games.py`,
`compare_snapshots.py`, and 102 cached CFBD CSVs under `data/cfbd/`. Read before building
any new ingest layer.
