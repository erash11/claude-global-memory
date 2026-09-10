# EPA-driven tendency analysis (PFF join) — design note

Status: designed, not built. No data has been pulled. Origin: Eric's idea, discussed 2026-09-06.

## The original idea
Use CFBD play-by-play and GameOnPaper EPA to find plays where a team had very high EPA,
or where high-EPA plays clustered. Look those specific plays up in PFF, read the formation,
and build tendencies from there. EPA decides which plays are worth studying.

## The core insight worth keeping
Frequency tells you what a team does. EPA tells you what actually hurts. Nearly every
tendency report a coach receives is frequency-based and ranks nothing by consequence.
Weighting tendencies by EPA is the part of this idea with real value.

## Why the original mechanism was changed
Single-play EPA is mostly noise. A 45-yard gain may be scheme or may be a missed tackle.
Sorting a season by EPA and pulling the top N plays selects on outcome, which means
scheming against variance. It also leaves roughly 20 plays spread across a dozen
formations, which is not enough to call anything a tendency.

Clustered EPA is less noisy than single spikes, but drive-level clusters often reflect
script, tempo, or field position rather than a scheme the offense is good at.

## The method instead: EPA grades buckets, it does not pick plays
1. Define buckets from PFF charting: personnel, formation, backfield alignment,
   motion yes/no, down and distance band, field zone.
2. Attach EPA to every play, not only the exciting ones.
3. Per bucket, compute frequency, EPA per play, success rate, and sample size.
4. Shrink each bucket's EPA toward the team mean based on sample size (empirical Bayes,
   or a simple sample-weighted blend). A 6-play bucket at +0.8 gets pulled hard toward
   the mean. A 70-play bucket at +0.35 barely moves.
5. Rank by leverage: shrunk EPA multiplied by frequency. That surfaces what a team does
   often AND does well, which is what you game-plan against.

Target output reads like: "On 2nd and medium from 12 personnel with a tight end wing,
they are +0.31 EPA per play on 58 snaps, and it is 19% of their 2nd down calls."

## Known risks
**The join is the hard part.** PFF and CFBD/ESPN share no play ID. Match on game, quarter,
clock, down, distance, and yard line with a fuzzy time window. Expect 90 to 95% clean,
then hand-resolve penalties, no-plays, and clock discrepancies. Budget roughly a week
before a single insight appears. Report the match rate before looking at any result; a
biased join silently drops penalties and no-plays, and those cluster.

**Use one EPA model.** CFBD EPA and GameOnPaper's ESPN-based EPA are different models and
return different values for the same play. Decision: CFBD EPA is the single input.
GameOnPaper becomes a cross-check, not a second source.

**Sample size at one game.** About 65 to 75 offensive snaps, leaving 4 to 8 plays per
bucket. Enough to prove the pipeline works, not enough to call a tendency. If the join
holds, the next step is the opponent's full season, roughly 800 snaps.

**Licensing.** PFF-derived data stays internal to the department.

## Adoption risk
Football analytics products die from workflow fit, not bad math. A tool requiring a coach
to change how he preps on Tuesday loses to a worse tool that fits the existing sheet.
The football staff already has PFF and analysts. If this is built for them, the bar is
beating what the QCs already produce on Sunday night.

An alternative lane worth considering: layer EPA-weighted situational context onto GPS and
workload data (which situations produce the highest-cost snaps, how scheme tendencies map
to practice load and exposure). Eric owns both the customer and the data there.

## Pilot: Baylor vs Houston, November 2025
Chosen because Houston is a conference opponent likely to recur, so the join code and
bucket logic get reused rather than thrown away. Treat the run as a plumbing test, not an
answer about Houston.

Steps: get ESPN and CFBD game IDs (check the 102 cached CSVs in CFB_Victory_Model first)
→ pull play-by-play with EPA → load the PFF export → build and validate the join, report
match rate → bucket, shrink, rank → review top rows.

## Blockers as of 2026-09-06
1. **PFF export.** Unresolved and it gates everything. Needs a play-level CSV for the game
   with formation and personnel. Without it this becomes an EPA-only situational study,
   which does not test the idea.
2. **Folder access.** The macOS folder dialog timed out twice, so `~/DEV` and
   `Weekly_Matchups_2026` were never reachable. Nothing ran on the Mac.
3. **Audience.** Football staff, or Eric's to own? Decides whether the join work is worth
   doing at all.

## Environment note
The cloud container is IP-blocked by ESPN (403 from ESPN's edge, not a user-agent problem).
All ESPN and GameOnPaper work must run on the Mac through the local shell.
