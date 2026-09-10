# Weekly routine — MatchupAnalysis_FB2026

Two scheduled tasks produce the week's opponent read. Both write a Markdown doc into
that week's folder under `Weekly_Matchups_2026/`.

## The two runs

**Monday 6:00 AM CT** — `Matchup: Monday opponent profile` (`trig_0179YtyutturpeBikVsc4XHb`)
Full opponent profile. Output: `YYYY-MM-DD_{Opponent}-Baylor_Opponent-Profile.md`
Costs ~15 CFBD calls.

**Thursday 6:00 AM CT** — `Matchup: Thursday game-week delta` (`trig_01KC8sqM7pLpSNkhoveD6JW4`)
What changed since Monday, one page. Output: `YYYY-MM-DD_{Opponent}-Baylor_Midweek-Delta.md`
Costs 2 CFBD calls, reuses Monday's cached bundle.

Cron is evaluated in UTC (`0 11 * * 1` and `0 11 * * 4`). That is 6:00 AM during
Central Daylight Time. After the November 1 switch to Standard Time the runs land at
5:00 AM CT until the cron is shifted to `0 12`.

## The collection script

`~/DEV/CFB_Victory_Model/matchup/matchup_pull.py`, modes `--mode monday` and
`--mode midweek`. It does the deterministic part only: fetch, parse, and write a JSON
bundle. Writing the narrative doc is the scheduled session's job, reading that bundle.

Prints `BUNDLE_PATH=` and `WEEK_FOLDER=` as its last two lines.

What it resolves and pulls:
- **Which week it is** — reads `data/cfbd/games_2026_regular.csv` for the next Baylor
  game whose kickoff is still ahead (6-hour grace so a Saturday night game still
  resolves to itself). Folder name follows the existing `Week_1_AUB` convention.
- **CFBD** — opponent season stats, advanced stats, per-game stats, roster, returning
  production, SP+, talent; Baylor's equivalents; betting lines.
- **GameOnPaper** — the opponent's last two games, tables 0/1/3/4/5/6/8 per the
  data-access doc. Fetched with `curl` because ESPN and GOP reject the default UA.
  Each scraped game carries a `season` field.
- **BCFToys** — `2026-fei` (carries FEI, OFEI, DFEI and SFEI together) and `2026-gp`
  (this week's game projection: win probability, margin, projected score, total),
  both trimmed to Baylor and the opponent.
- **Frozen prediction** — the pre-registered line from `frozen_predictions_2026.csv`.

Bundles land in `<week folder>/_data/YYYY-MM-DD_<mode>_bundle.json`. A second run the
same day writes `_2`, `_3`; nothing is ever overwritten.

### The two-game rule
An opponent needs **two completed 2026 games** before this season counts as a usable
sample. The script sets `basis` and `basis_note` accordingly, and those fields govern
how the document is written.

- `basis: "2026"` — two or more completed 2026 games. Current season only. The script
  does not touch 2025 at all.
- `basis: "2025"` — fewer than two. Last season is the profile: GameOnPaper pulls the
  opponent's last two 2025 games, and CFBD adds 2025 season and advanced stats. Every
  number taken from it must be labeled as 2025 in the written doc.

When the opponent has played exactly one 2026 game, that game is carried in the bundle
alongside the 2025 profile rather than blended into it. The doc treats it as a
single-game early look and says so. Blending one game of this season with last
season's rates was the failure mode this rule exists to prevent.

Most opponents cross the threshold around week 4.

### CFBD budget guard
Free tier is 1,000 calls a month, hard cap, shared with basketball, resetting the 1st
UTC. Every call is counted in `data/cfbd_budget.json`. The script refuses to start if
the run would push the month past `SAFE_CEILING` (700), and pulls nothing rather than
half a bundle. Two runs a week across the season lands near 250.

## PFF
Blitz rate, pressure package and coverage shares come from PFF Ultimate on the Baylor
account, which is login-gated and not scriptable. The Monday task reads it through
Claude's browser, strictly read-only, and pulls whichever season matches the bundle's
`basis`. If the browser is not signed in, the task records the gap in the doc's
data-quality section rather than substituting a public source or estimating. A missing
PFF section is expected some weeks.

## Known limits
- Both tasks must be bound to Eric's Mac. An unbound task runs in the cloud, cannot
  reach the OneDrive folder, and will fail at step 1.
- Betting lines are often empty more than a week out; the `lines` array comes back
  with an empty `lines` list rather than an error.
- BCFToys `2026-fpv` (field position value) does not parse with the same reader and
  was left out.

## Run log

**2026-09-07, Monday profile (Week 2, Prairie View A&M) — did not run.**
The scheduled session had no `mcp__remote-devices__*` tools at all, meaning the task
was created without computer access rather than losing the connection mid-run. Nothing
on the Mac was reachable: no `matchup_pull.py`, no bundle, no
`frozen_predictions_2026.csv`, no `Weekly_Matchups_2026` folder, no PFF browser. No
CFBD calls were spent and no files were written, so the week is recoverable by hand.

This is the "Known limits" failure above, confirmed live. Both scheduled tasks need to
be recreated from the Claude desktop app **on that Mac**, choosing the computer when
the app offers it at scheduling. A task created from the web or a phone can never
reach the machine, and the binding cannot be added after the fact.
