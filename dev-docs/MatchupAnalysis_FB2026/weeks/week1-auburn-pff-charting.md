# Week 1 Auburn: PFF charting analysis (v3, 2026-09-07)

Current deliverables:
- `Week_1_AUB/2026-09-07_Auburn-Baylor_PFF-Charting-Review-v3_Baylor-Design_AgencyFB.docx`
- `Weekly_Matchups_2026/2026-09-07_Keys-To-Victory-Framework-v3_Baylor-Design_AgencyFB.docx`

**Superseded, safe to delete:** the original `..._PFF-Charting-Analysis_...docx`,
`..._Addendum-01_...docx`, and both v2 files.

Scripts: `keys_grader.py` plus `data/week1_auburn/` (`off2.py`, `def2.py`, `sup.py`, `roll.py`,
`third.py`, `turnovers.py`, `scoring.py`, `audit.py`, `recompute.py`, `allkeys.py`,
`blocking.py`, `qb.py`, `build_report.py` + `v3_a-d.py` / `kf3_a-b.py`).

## What v3 added
`all_blocking` (1,099 rows) and `quarterback_charting` (38 rows) populated on 2026-09-07.

### Run game: answered, and it is not assignments
| | blocks | missed assignments | rate | unblocked |
|---|---|---|---|---|
| Baylor | 557 | 9 | **2%** | 49 (9%) |
| Auburn | 542 | 7 | 1% | 54 (10%) |

On the 31 inside-zone carries (2.0 ypc): **6 missed assignments across 245 block rows, zero
unblocked defenders.** Mean Baylor blocker grade -0.31 on inside zone, -0.38 on gap schemes.
**The linemen are executing the right assignment and losing the block.** Technique and
personnel, not install or communication. Gap schemes grade no better than zone, so the 5.3 ypc
on gap may be scheme fit rather than better blocking; Week 2 separates those.

Short yardage, all four runs on 3rd/4th and 3 or less: 32 block rows, **one missed assignment
(Koltin Sieracki), zero unblocked.** The Power run that lost 2 yards had every assignment
correct. Auburn defenders winning blocks: Cody Sigler 5, Murray 3, Crawford 3, Walker 3,
Darrion Smith 3. Spread across the interior.

### Baylor coverage profile (from Auburn's QB charting)
| Coverage | n | share | y/att |
|---|---|---|---|
| Hole in Zone | 12 | 39% | 7.2 |
| Underneath | 11 | 35% | 3.9 |
| Single (man) | 5 | 16% | 8.2 |
| Zone Carry / Top / Single w help | 3 | 9% | - |

**Baylor is a zone team, 77% of charted dropbacks.** Underneath was the best call (3.9),
Hole in Zone the most used and worse (7.2), man the worst (8.2 on five).
**Separation allowed was Open on 20 of 31 (65%).** The 81.5 coverage grade is being carried by
the pass rush and Auburn's inaccuracy, not by tight coverage.

### Lagway accuracy: still unavailable
`quarterback_charting` populated with **38 rows, all Auburn, all Byrum Brown. Zero Baylor
rows, 0 of Baylor's 54 attempts charted.** Not a filter artifact: 2025 game 28762 returns both
teams. `pass_accuracy`, `throw_type`, `qb_decision`, `receiver_separation` for Lagway remain
missing. **The 52% catchable rate is still the best evidence and is still a proxy.**

## The five findings
1. **Catchable rate 52%** (28 of 54). Auburn 77%. One drop. 1H 68%, 2H 38%.
2. **1 for 5 on 3rd-and-3 or less**, three failures in Auburn territory. Blocking data shows
   losses at the point of attack, not assignment errors.
3. **Auburn converted 9 of 12 on 3rd-and-6 or less** against a 13% pressure rate; Baylor
   pressured on all six 3rd-and-7+ dropbacks and allowed one conversion.
4. **Auburn blitzed 48%, above their 40.4% baseline, and it worked.** Baylor 4.8 y/db and 1
   explosive against the blitz, 7.0 and 4 without.
5. **Best rushers took fewest rush snaps.** Ponder 50% on 16, Mack 43% on 14, Mitchell 4-for-4.
   Kyler Jordan 0% on 22, Davis 15% on 27, Whyce 6% on 17.

## Third down
Auburn: 3rd-and-6 or less 9 of 12 (75%) with 13% pressure; 3rd-and-7+ 1 of 6 with 100%
pressure. Baylor: 3rd-and-3 or less 1 of 5; 4-6 3 of 6; 7-9 0 of 3; 10+ 3 of 8.

## Offense
- 27/54, 333 pass yards; 43 rushes, 125, 2.9. Five explosive passes, zero explosive rushes.
- 11 personnel 101 of 104. Shotgun 103 of 103. **Motion 24% and it costs 1.4 y/play**
  (3.6 vs 5.0; runs 2.4 vs 3.1 ypc). Auburn is better with motion (6.7 vs 4.7).
- Right half of the field: 12 att, 32 yds, 2.7, 17% success. Deep center 4 for 78 at 19.5.
- vs blitz (27): 4.8 y/db, 50% catchable, 1 explosive. Not blitzed (29): 7.0, 54%, 4.
- vs press (13): **0 explosives**, 46% catchable.
- Protection held against 48% blitz: 2 sacks on 56 dropbacks. Logan Moore 0 pressures on 56.
- Inside zone 31 at 2.0; power 8 at 4.6; counter 2 at 6.0; man 2 at 7.5.
- Pendergrass 25 att, 88 yds, 75 after contact, 4 MTF, 76.2.
- Freeman 18 tgt / 12 / 154 / 3 explosives, 85.0. Options 4-8: 10 tgt, 2 catches, 23 yds.

## Defense
- 33% pressure, 7 sacks. **Blitzing does not help**: 36% vs 31% pressure, 5.8 vs 6.1 y/db.
- Thornton 7 targets, 57% success allowed, 57.3 cov grade. Bush II 4-for-4, both deep
  completions, 22 snaps. Devon Jordan avoided. Gifford untargeted, 92.4 cov.
- Auburn's right (Baylor's left): outside zone 5.6, pull lead 5.5, counter 5.3.
- Brown charted 14 for 45, 3.2, 29% success.

## Turnovers and scoring (PFF-native)
Baylor 2 giveaways / 3 takeaways, margin +1. Baylor 12 drives 16 pts (1.33), Auburn 13 drives
17 pts (1.31). Scoreboard reconstructs exactly.

## Recommendations
Week 2: Freeman 6-8 touches then sit; test Pendergrass yards before contact; script short
yardage; target WR4-7 15+ times; run power and counter; **coach first-contact technique and
pad level, not install**; fix or shelve motion; Rhett series at LT. Defense: Ponder toward 30
rush snaps, Mack toward 25, Mitchell toward 30, snaps to Gifford, pressure package for
3rd-and-6 or less.

Season: Ponder and Mack as passing-down edges; Gifford starts at safety; help Thornton;
solve blitz pickup and separation vs press; WR2 must become real; LT unresolved; **interior OL
is a technique and personnel project**; tighten coverage or accept the rush is carrying it.

## Load crosscheck
Edge swap load-neutral (snaps from Davis +2.77z and Kyler Jordan +2.19z). **Gifford's increase
is not free**: +2.55z, +43.4 snap-eq on 35 def snaps plus team-high 17 ST; take ST off first,
Bo Onu (-1.04z) absorbs. Mitchell 12 to 30 snaps costs ~83 PL; Washington (-0.69z) pays.
Klopfenstein -0.83z and 48.6 grade. Porter -1.82z worth tape. Freeman +0.36z.

## Open items
- Baylor's quarterback charting rows. Re-pull; the scheduled task
  (`trig_015CzdAateSppPyLv7mzcsCM`, 2026-09-08 9:00am CT) **never bound to the Mac
  (`no_signed_approval`)**, so it will run in the cloud and cannot read the key or write files.
  Approve on the MacBook or run manually.
- Defensive/return TDs and safeties not implemented in the scoring reconstruction.
- Whyce Catapult file is bad (17 PL on 39 snaps, z = -7.6).
- **Three lessons:** never grade a key on a mean when the distribution is available; never
  enumerate a PFF feed's schema from the first row; never assume a feed covers both teams.
