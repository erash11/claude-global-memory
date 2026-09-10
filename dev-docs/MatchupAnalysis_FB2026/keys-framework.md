# Keys to Victory framework and auto-grader (v3, 2026-09-07)

Tool: `~/DEV/Football/PFF_Data_Project/keys_grader.py`
Run: `python3 keys_grader.py <game_id> <TEAM> --pull --qb "<opp QB>" [--json out.json]`
Reads PFF_API_KEY from `.env` inside the command, never prints it.

**Every key grades from PFF. Nothing needs the box score.** Validated on game 31098: the
grader reconstructs the final score exactly (TXBA 16, ALAU 17) and the turnover margin (+1).

Docs: `Weekly_Matchups_2026/2026-09-07_Keys-To-Victory-Framework-v3_Baylor-Design_AgencyFB.docx`
(v2 superseded).

## THE BUG THAT CAUSED A WRONG ANSWER — read before any feed audit

**PFF omits zero-valued fields from its JSON.** A field is present on a row only when it has
a non-zero value. Enumerating a feed's schema from `rows[0].keys()` misses every sparse field.

| Feed | keys in row 0 | keys anywhere | missed |
|---|---|---|---|
| passing | 62 | **87** | 25 |
| team_main | 32 | **93** | 61 |
| team_play | 26 | **45** | 19 |
| rushing | 49 | 58 | 9 |
| game_grade | 17 | 40 | 23 |

```python
keys=set()
for r in rows: keys |= set(r)
```

## Second trap: a feed can populate ONE TEAM AT A TIME
Game 31098's `quarterback_charting` arrived on 2026-09-07 with **38 rows, all Auburn, zero
Baylor**, days after every other feed completed. The same endpoint on 2025 game 28762 returns
both teams (58 Robertson, 27 Arnold), so this is real partial population, not a filter.
**Check `set(r["team"] for r in rows)` before concluding anything.** Do not read an absent
team as an absent statistic.

## Where everything lives
- **Interceptions:** `passing.interception`, `interceptor_name`, `interceptor_player_id`
- **Fumbles:** `rushing.fumbles` / `forced_fumbles`; `team_main.off_fumbles`,
  `off_fumble_recovery`, `def_fumble_recovery`, `def_forced_fumble`
- **Touchdowns:** `passing.touchdown`, `rushing.touchdown`, team_main `pass/rush/rec_touchdown`
- **Kicks and tries:** `team_play.st_play_type`
- **Drives:** possession changes across the ordered play sequence
- **Blitz:** `passing.blitz`, a superset of 5+ rushers, not limited to pressure plays
- **Press coverage:** `passing.press_coverage`
- **Motion / option / personnel:** `team_play.motion`, `.option`, `.offense_package`,
  `.defense_package`
- **Blocking detail:** `all_blocking` — `missed_assignment`, `unblocked`, `block_type`,
  `block_level`, `gap1`/`gap2`, `primary_run_concept`, blocked player and `player_grade`
- **QB accuracy:** `quarterback_charting` — `pass_accuracy`, `throw_type`, `qb_decision`,
  `qb_look`, `rhythm`, `receiver_separation`, `pocket_movement`, `hit_while_throwing`
- **Coverage scheme:** `quarterback_charting.coverage_type` (see below)

## Coverage scheme DOES exist (corrects v2)
`quarterback_charting.coverage_type`. Values seen: Hole in Zone, Underneath, Single, Single
with help, Zone Carry, Top. **It describes the coverage the charted QB FACED**, so it tells
you about the opposing defense and only for a team whose QB is charted.
`coverage_name` is still the defender's NAME; `team_main.def_cover` is still a 0/1 in-coverage
flag (3,876 zeros / 699 ones, matching role=Coverage exactly).

## Fumble attribution gotcha
The `off_`/`def_` prefix on the recovery flags is unreliable; game 31098 has a row where an
Auburn safety carries both. Decide possession by joining the recovering player's `player_id`
to the grades roster and comparing his team to the play's offense. Gives Baylor 2 giveaways
and 3 takeaways, matching the box.

## Changes from the original sheet
| # | Change | Reason |
|---|---|---|
| 1 | ADD catchable throw rate, 70%+ | 52% decided Week 1, nothing measured it |
| 2 | ADD pressure rate on 3rd-and-6 or less, 40%+ | The real money-down failure, 13% |
| 3 | REPLACE opp avg 3rd down distance with share of opp 3rd downs at 7+ yds, 50%+ | The mean was satisfied by four disaster downs |
| 4 | ADD conversion on 3rd-and-3 or less, 60%+ | 1 for 5 in Week 1 |
| 5 | REDEFINE explosives vs man coverage as vs blitz (2+) and vs press (1+) | No offensive coverage data for this game |
| 6 | REPLACE red zone TD rate with red zone success rate, 50%+ | Cleaner, unaffected by kicking |
| 7 | ADD motion rate, 25%+ | Motion is charted and Baylor barely uses it |
| 8 | Blitz rate uses PFF's flag, 30%+ | The correct football definition |
| 9 | Giveaways, takeaways, points per drive move from box to PFF | Always were in the feeds |

Average third down distance demoted to reference on both sides.

## Week 1 result: 3 of 10 non-negotiables

## Implementation notes
- Incompletions must be set to 0 yards or every success rate inflates.
- Sacks and pressures dedupe by `play_id`.
- Opponent QB rushing uses charted attempts (Brown 45 charted vs 66 official).
- A 200 with zero rows means not processed yet; the grader refuses to run.
- Thresholds live in the `KEYS` registry at the bottom of the file.
- The grader prints the reconstructed score every run. Cross-check once per game. Defensive
  and return TDs and safeties are not implemented.

## Reading a diagnostic game
Do not trust: overall pressure rate, explosives allowed, opp yards per carry, takeaways.
**Trust:** conversion on 3rd-and-3 or less, catchable throw rate, pressure rate on 3rd-and-6
or less, motion rate, yards before contact per carry.
