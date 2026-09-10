# Mac session handoff — rebind the matchup tasks

Read this from a Claude session running ON Eric's Mac with the OneDrive `DEV` folder
connected. It is self-contained: every prompt you need is below, no chat attachments
required.

## Why this doc exists

The two matchup scheduled tasks were created without a binding to the Mac, so they run in
the cloud, cannot reach `~/mnt/DEV/CFB_Victory_Model`, and fail at their first step.
Confirmed from the trigger records on 2026-09-07, both show `bound_device = None`:

- `trig_0179YtyutturpeBikVsc4XHb` — Matchup: Monday opponent profile — `0 11 * * 1`
- `trig_01KC8sqM7pLpSNkhoveD6JW4` — Matchup: Thursday game-week delta — `0 11 * * 4`

The binding is set at creation and cannot be added afterward. Editing the prompt or the
schedule does not attach it. Both have to be recreated from a session on the machine, and
the old two deleted afterward.

The 2026-09-07 Monday run did not happen. Week 2 opponent is Prairie View A&M. No CFBD
calls were spent and no files were written, so nothing needs cleaning up first.

## Order of operations

1. Run Week 2 by hand (JOB 1 below).
2. Create both replacement tasks bound to this computer (JOB 2).
3. Verify both came back bound with the `DEV` folder attached.
4. Only then delete the old pair (JOB 3).

Never do 3 before 4 is verified. Broken tasks that fail loudly beat no tasks at all.

## Block A — run Week 2 by hand, today

Open a session in the Claude desktop app on the Mac with the OneDrive folder connected,
then paste this.

```
Weekly opponent profile for Baylor football, 2026 season. This is the Monday run of the
MatchupAnalysis_FB2026 routine, being run by hand because the scheduled task was not
bound to this computer. Work on my Mac through device_bash. Do not ask questions. Make
the most reasonable call and state any assumption at the top of the document.

STEP 1 - Pull the data.
Run: cd "$HOME/mnt/DEV/CFB_Victory_Model" && python3 matchup/matchup_pull.py --mode monday

It prints BUNDLE_PATH= and WEEK_FOLDER= on its last two lines. Read those. If it exits
on a CFBD budget stop, do not work around it: write a short note in the week folder
saying the budget stopped the run and end there.

STEP 2 - Read the bundle JSON at BUNDLE_PATH. Two fields govern how the entire document
is written. Read them before anything else.

(a) "basis" and "basis_note" - which season is the sample.
- "2026" means two or more completed 2026 games. Use this season. Do not reach back to 2025.
- "2025" means fewer than two, so last season is the sample. Every rate, tendency and
  ranking taken from it must be explicitly labeled as 2025. Never present a 2025 number
  as current form. If the opponent has already played one 2026 game it is carried
  separately: treat it as a single-game early look, say so, and do not average it with
  the 2025 profile.
Each GameOnPaper entry has a "season" field. Check it before quoting anything.

(b) "scheme_reference" - whose 2025 tape actually predicts each side of the ball.
A team that hired a new coordinator does not run its old scheme any more, so that team's
own 2025 data is the wrong predictor. For each side, "use_2025_data_from" names the team
whose 2025 data applies, and "proxy_quality" says how well.
- When "new_for_2026" is true and "use_2025_data_from" names a DIFFERENT team, the
  bundle's "proxy_2025" block holds that team's 2025 season stats and last two
  GameOnPaper games. Build that side of the profile from the proxy and say so plainly.
- proxy_quality "direct" is a clean read. "partial" means expect scheme drift, hedge
  the language. "none" means no usable proxy: describe the coordinator's background
  qualitatively and attach no numbers to it.
- Check "proxy_2025" entries for a "warning" field. An FCS proxy often has empty CFBD
  advanced stats. Use the GameOnPaper boxes and scheme description rather than inventing
  rates.
- This applies to Baylor too. Baylor's 2026 defense is Joe Klanderman's, and Kansas
  State's 2025 defense is the proxy, not Baylor's 2025 under Powledge.
- When basis is "2026" the proxy pull is skipped on purpose, because the team's own 2026
  games already show the new coordinator's scheme. Still use scheme_reference for
  narrative: name the coordinator and note it is a first-year scheme with a small sample.

STEP 3 - PFF blitz and coverage tendencies.
Open PFF Ultimate in Claude's browser at premium.pff.com. The Baylor account may already
be signed in. STRICTLY READ ONLY: navigate and read, never change a saved filter set,
save, or edit anything on PFF.
Pull blitz rate, box blitz %, slot CB blitz %, CB blitz %, sim pressure %, 5/6/7+ rush %,
and coverage shares (Cover 0/1/2/3, Quarters, Cover 6, 2-Man).
Critically: pull these for the team named in scheme_reference's "use_2025_data_from" for
the DEFENSE side, not automatically for the opponent. If the opponent hired a new DC from
another school, pull that school's 2025 defense. Do the same for Baylor's defense. Label
every table with which team and season it came from.
If you are not signed in or the page will not load, DO NOT guess numbers and do not
substitute a public source. Write "PFF: not available this run, not signed in" in the
data-quality section and continue. A missing section is fine, an invented one is not.

STEP 4 - Read the previous week's folder under Weekly_Matchups_2026 for continuity, and
read ~/mnt/DEV/CFB_Victory_Model/frozen_predictions_2026.csv for this week's
pre-registered prediction.

STEP 5 - Write the document.
Save to WEEK_FOLDER as: YYYY-MM-DD_{Opponent}-Baylor_Opponent-Profile.md using today's
date. NEVER overwrite an existing file. If that name exists, append _v2, _v3.

Directly under the title, put a two-line note stating what the profile is built on:
which season, and for each side of the ball whose scheme is being read.

Sections, following the Week 1 analysis in Week_1_AUB:
- Bottom line (3-5 sentences, the actual read on the game)
- Coaching and scheme changes: who is new, where they came from, what changes as a
  result. Short and concrete.
- Opponent offense: identity, tempo, personnel, early downs and third down
- Opponent defense: pressure profile, coverage shell, run fits
- Baylor offense and defense against that specific profile
- Key matchups (the 3-4 interactions that decide it)
- In-game tendencies to track
- Projected outcome: the frozen CFB Victory Model prediction, the BCFToys projection,
  and the market line side by side in a table. Where they disagree, name the outlier
  and say why.
- Data quality warnings: every gap, every proxy substitution, every source that failed
- Sources with URLs

Writing rules: plain and direct, no corporate language, no em dashes. College-freshman
level explanations. Lead with the conclusion. Do not pad. Post-process the draft through
the humanizer and articulation skills before saving.

STEP 6 - Reply with 4-6 lines: opponent, what the profile is built on including any
coordinator proxy, projected outcome, the single biggest thing that decides the game,
and any data that was missing.
```

---

## Block B — replacement Monday task

In the desktop app on the Mac: create a scheduled task, **select the computer when the
app offers it**, confirm the OneDrive folder is attached, then use this.

- Name: `Matchup: Monday opponent profile`
- Schedule: Mondays 6:00 AM CT (`0 11 * * 1` UTC during CDT; becomes `0 12 * * 1`
  after the November 1 switch to Standard Time)

Prompt: use Block A above, with the opening line changed to:

```
Weekly opponent profile for Baylor football, 2026 season. This is the Monday run of the
MatchupAnalysis_FB2026 routine. Work on Eric's Mac through device_bash. Do not ask
questions; nobody is watching. Make the most reasonable call and state any assumption at
the top of the document.
```

Add this as a new first step, before STEP 1:

```
STEP 0 - Confirm you can reach the Mac. If the mcp__remote-devices__* tools are absent
or their calls fail, stop immediately, write nothing, and send a push notification
saying the task lost its computer binding and the week's profile did not run. Do not
substitute cloud data or public sources for anything in this routine.
```

---

## Block C — replacement Thursday task

Same creation path: desktop app on the Mac, select the computer, confirm the folder.

- Name: `Matchup: Thursday game-week delta`
- Schedule: Thursdays 6:00 AM CT (`0 11 * * 4` UTC during CDT; `0 12 * * 4` after
  November 1)

```
Midweek game-week delta for Baylor football, 2026 season. This is the Thursday run of
the MatchupAnalysis_FB2026 routine. Work on Eric's Mac through device_bash. Do not ask
questions; nobody is watching. One page. Make the most reasonable call and state any
assumption at the top.

STEP 0 - Confirm you can reach the Mac. If the mcp__remote-devices__* tools are absent
or their calls fail, stop immediately, write nothing, and send a push notification
saying the task lost its computer binding and the delta did not run. Do not substitute
cloud data or public sources for anything in this routine.

STEP 1 - Pull the data.
Run: cd "$HOME/mnt/DEV/CFB_Victory_Model" && python3 matchup/matchup_pull.py --mode midweek

It prints BUNDLE_PATH= and WEEK_FOLDER= on its last two lines. Read those. This mode
costs 2 CFBD calls and reuses Monday's cached bundle. If it exits on a CFBD budget stop,
write a short note in the week folder saying so and end there.

STEP 2 - Read the midweek bundle at BUNDLE_PATH, and read Monday's profile document in
the same WEEK_FOLDER. The document is
YYYY-MM-DD_{Opponent}-Baylor_Opponent-Profile.md, most recent version if there are
_v2/_v3 files.

If Monday's profile is missing, say so at the top of the delta, build from the bundle
alone, and note that there is no Monday baseline to compare against.

Carry Monday's basis and scheme_reference forward unchanged. Do not re-derive them and
do not switch which team's data reads which side of the ball midweek. Label 2025 numbers
as 2025 exactly as Monday did.

STEP 3 - Write only what CHANGED since Monday. This is a delta, not a second profile.
Cover:
- Line movement: where the market opened Monday, where it is now, which direction and
  how far. Name the number.
- Whether the BCFToys projection moved, and whether the gap to the frozen CFB Victory
  Model prediction widened or closed.
- Injury, availability, depth chart or weather news that changes a key matchup Monday
  named. Say which matchup it changes.
- Anything in Monday's read that now looks wrong, and why.
- If nothing material moved, say that in one line and keep the document short. Do not
  pad it to look substantial.

STEP 4 - Save to WEEK_FOLDER as
YYYY-MM-DD_{Opponent}-Baylor_Midweek-Delta.md using today's date. NEVER overwrite an
existing file. If that name exists, append _v2, _v3.

Writing rules: plain and direct, no corporate language, no em dashes. College-freshman
level explanations. Lead with the conclusion. Post-process through the humanizer and
articulation skills before saving.

STEP 5 - Send a push notification only if something material moved: the line, an
availability change to a named key matchup, or a reason Monday's read now looks wrong.
If the week is quiet, save the document and send nothing.

STEP 6 - Reply with 3-4 lines: opponent, what moved, what did not, and anything missing.
```

---

# JOB 1, 2, 3 as a single instruction

If you would rather drive this as one request, paste the section below into the Mac
session.

I need you to fix a broken scheduled-task setup and run this week's analysis. Three jobs,
in this order. Do not ask me questions between them, just work through it and report at
the end.

Context you need: the MatchupAnalysis_FB2026 project has two scheduled tasks that were
created without a binding to this computer, so they run in the cloud, cannot reach
`~/mnt/DEV/CFB_Victory_Model`, and fail at their first step. Confirmed from the trigger
records, both show `bound_device = None`:

- `trig_0179YtyutturpeBikVsc4XHb` — Matchup: Monday opponent profile — `0 11 * * 1`
- `trig_01KC8sqM7pLpSNkhoveD6JW4` — Matchup: Thursday game-week delta — `0 11 * * 4`

The binding is set at creation and cannot be added afterward, which is why these have to
be recreated rather than edited. You are running on the machine itself, so you can do
what a cloud session could not.

## JOB 1 — Run Week 2 by hand

The Monday 2026-09-07 run never happened. Week 2 opponent is Prairie View A&M. Run the
full Monday routine now, using Block A above. Short version of what matters:

- `cd "$HOME/mnt/DEV/CFB_Victory_Model" && python3 matchup/matchup_pull.py --mode monday`
- Read BUNDLE_PATH and WEEK_FOLDER from its last two lines.
- The bundle's `basis` and `scheme_reference` fields govern how the whole document is
  written.
- Baylor's defense proxies to Kansas State 2025 under Klanderman, not Baylor 2025.
- PFF section is read-only, and if not signed in, record the gap rather than inventing
  numbers.
- Save as `YYYY-MM-DD_{Opponent}-Baylor_Opponent-Profile.md` in WEEK_FOLDER, never
  overwriting.

## JOB 2 — Create the two replacement tasks

Create both as scheduled tasks bound to THIS computer, with the `DEV` folder attached.
Verify after creating that each one actually came back with a bound device and the
folder. If either comes back unbound, stop and tell me rather than moving to Job 3.

Task 1: name `Matchup: Monday opponent profile`, Mondays 6:00 AM CT.
Task 2: name `Matchup: Thursday game-week delta`, Thursdays 6:00 AM CT.

Cron is UTC. During Central Daylight Time that is `4 11 * * 1` and `4 11 * * 4`. After
the November 1 switch to Standard Time they need to move to `4 12 * * 1` and
`4 12 * * 4`, so note that somewhere.

Use Blocks B and C above. Both open with a STEP 0 that checks for the
`mcp__remote-devices__*` tools and, if they are gone, stops without writing anything and
sends a push notification. Keep that step. The 2026-09-07 failure was silent until someone
went looking, and that is what STEP 0 prevents.

Turn on push and email notifications for both.

## JOB 3 — Delete the two broken tasks

Only after Job 2 is verified. Delete `trig_0179YtyutturpeBikVsc4XHb` and
`trig_01KC8sqM7pLpSNkhoveD6JW4`. Do not delete them if Job 2 did not fully succeed, since
broken tasks that fail loudly beat no tasks at all.

## Finally

Update `docs/weekly-routine.md`: replace the two old trigger IDs with the new ones in the
"The two runs" section, and add a line to the run log saying the tasks were rebound on
this date. Also update `docs/task-rebinding-2026-09-07.md` to mark it resolved.

Then report back: whether Week 2 got written and what it said, the two new trigger IDs
and whether they are bound, and confirmation the old two are gone.
