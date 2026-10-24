# Handoff 2026-10-23: weekly review, no-movement warning, ship queue re-dated

## What and why
Ran the Friday `/weekly-review` for 2026-10-23. The main finding: the ship queue
(AP Digest ch1, intern curriculum M1, Research in 5 #002) shipped 0 of 3, and the
output ledger has nothing new since 10-06. Eric asked for (1) a standing
no-movement warning in the weekly review and (2) new dates.

## Decisions (Eric, 10-23)
- No-movement warning lives in the weekly-review skill, not only in this week's note.
  Movement = a commit that changes the work (STATUS-only and closeout-sweep commits
  do not count), a new `output/_ledger.md` line, or a written new date. No movement
  gives a `> ⚠ NO MOVEMENT — week N: <priority>` banner. At week 3 the priority must
  be ship-by-date, re-date, or park.
- Ship queue re-dated: AP Digest ch1 **10/30** (30-day check 11/29); intern M1 and
  Research in 5 #002 **11/13** (30-day check 12/13). Digest first because it is the
  only item with a draft.
- Meeting `Oct 22, 09:30 AM` renamed in Fireflies to `StaffMeet_10222026` (Eric chose
  his past naming style over the name-meetings topic style).
- Friday sweep: all 10 rows kept (out of the sweep for 90 days).
- 14 SAFE sessions deleted.

## Files changed
- `~/SecondBrain/Inbox/weekly-review/2026-10-23-review.md` (new)
- `~/SecondBrain/Inbox/meetings/2026-10-22_StaffMeet_10222026.md` (new export, header prepended)
- `~/SecondBrain/Inbox/meetings/.sync-state.json`
- `~/SecondBrain/Templates/weekly-review.md` (new "Last week's three priorities" section)
- `~/.claude/skills/weekly-review/SKILL.md` (section 0 + no-movement rule, `f708e06`)
- `~/DEV/project-triage/portfolio.json` (sweep `3727442`; next actions `8457105`)
- `~/DEV/project-triage/docs/STATUS.md`
- `~/DEV/RunningTheRoom/docs/STATUS.md` (`b0d32ae`)
- `~/DEV/Performance_Playbook/docs/STATUS.md` (`498512d`)
- `~/.claude/global-memory/MEMORY.md` (ship-queue thread line)

## Next
1. AP Digest ch1 by Fri 10/30: on branch `digest-start`, fill each `[CONFIRM]` in
   `docs/digest/ch01_forcedecks_cmj.md` and make the 3 fixes in
   `~/DEV/TypeSafe_Sandbox/digest_check/REPORT.md` section 1.
2. Send a status report by Fri 10/30 (last one in the vault is 09-07). Put the new dates in it.
3. Databricks: re-affirm the 10-16 pause or end it before the Thu 10/29 Kenny check-in
   (the 10-22 staff meeting gave Eric a Databricks follow-up).

## Mid-flight / known issues
- `fireflies-pp-cli action-items list` and `topics list` return empty `{}` rows (second week).
- Inbox drain deferred a second time: 25 in `~/DEV/_INBOX`, 44 in `~/Downloads` older than 7 days.
- Registry rows still stale: Tech_Inventory_Analysis (next step dated 09-18), SoftwareTech_Review (no next step).
