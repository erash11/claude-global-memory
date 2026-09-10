# Scheduled task rebinding — 2026-09-07

Both matchup tasks were created without a computer binding, so they run in the cloud and
fail at step 1. Confirmed from the trigger records themselves, not inferred:

| Task | ID | Cron | Bound device |
|---|---|---|---|
| Matchup: Monday opponent profile | `trig_0179YtyutturpeBikVsc4XHb` | `0 11 * * 1` | none |
| Matchup: Thursday game-week delta | `trig_01KC8sqM7pLpSNkhoveD6JW4` | `0 11 * * 4` | none |

The binding is set at creation and cannot be added afterward. Editing the prompt or the
schedule does not attach it. Both tasks have to be recreated from the Claude desktop app
on the Mac, choosing the computer at the moment of scheduling, and the two old IDs
deleted once the replacements exist.

The Thursday task was still enabled with `next_run_at` 2026-09-10 and would have failed
the same way.

Paste-ready prompts for the manual Week 2 run and for both replacement tasks are in
`mac-session-handoff.md`. Both replacement prompts open with a STEP 0 that stops the run
and sends a push notification if the `mcp__remote-devices__*` tools are missing, so a lost
binding announces itself instead of producing a quiet empty run.

## Week 2 status — RESOLVED 2026-09-07

The Week 2 Prairie View A&M profile was produced by hand and is written to
`Week_2_PVAM/2026-09-07_PrairieViewAM-Baylor_Opponent-Profile.md`. Also filed here as
`docs/weeks/week2-prairie-view-profile.md`.

The pull ran clean: 12 CFBD calls, 65/700 for the month, basis 2026 (two completed games).

### The second failure mode, and the fix

A bound session having `mcp__remote-devices__*` tools is not sufficient. The session also
needs the right **folders connected**, and by default none are. Two grants are required
before `matchup_pull.py` can run:

1. `~/DEV` — the script itself and `frozen_predictions_2026.csv`
2. `~/Library/CloudStorage/OneDrive-BaylorUniversity/00_Primary_Storage_Drive/01_PROJECTS/_ACTIVE/Weekly_Matchups_2026`
   — mounts as `~/mnt/Weekly_Matchups_2026`, which is the first path in the script's
   `_matchup_base()` candidate list

Without grant 2 the script resolves the output root to the raw OneDrive path, which does
not exist inside the sandboxed shell, and dies with a `PermissionError` on `/Users`.

Folder grants show a consent prompt on the Mac itself. A 6:00 AM scheduled run has nobody
there to answer it. **Both replacement tasks should be created from a desktop session that
already has these two folders connected**, so the grant carries rather than being requested
at fire time. Add a STEP 0.5 to each prompt: verify `~/mnt/DEV` and
`~/mnt/Weekly_Matchups_2026` both exist, and push-notify and stop if either is missing.
