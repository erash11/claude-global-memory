# Week 1 result: Auburn 17, Baylor 16

Final, September 5, 2026. Aflac Kickoff, Mercedes-Benz Stadium, Atlanta. Line was
Auburn -6.5, total 58.5. Baylor covered, the under hit. Baylor lost on a failed
two-point conversion with nine seconds left.

## How the three baselines scored

| Source | Predicted | Result | Miss |
|---|---|---|---|
| Frozen model (7/26) | Baylor 26, Auburn 30, margin -4, 43% Baylor | Auburn by 1 | 3 points on margin |
| DraftKings | Auburn -6.5, total 58.5 | Auburn by 1, total 33 | 5.5 on spread, 25.5 on total |
| ESPN FPI | 27% Baylor | Loss by 1 | Right direction, overconfident |

The frozen model beat the market on margin. Caveat: it got there through two
large offsetting component errors, projecting 26 for Baylor who scored 16 and 30
for Auburn who scored 17. Do not log this as a clean validation without checking
components. Everyone badly missed the total, which means no system saw both
offenses collapsing.

## Headline numbers (Game on Paper final)

| Metric | Baylor | Auburn |
|---|---|---|
| EPA/play | -0.06 | -0.10 |
| Success rate | 41% | 41% |
| Yards | 437 | 371 |
| Scrimmage plays | 98 | 75 |
| Third down | 32% | 53% |
| Red zone success | 31% | 50% |
| Turnover margin | +1 | -1 |
| Havoc rate | 24% (96th %ile) | 19% |
| Sacks | 5 | 1 |
| Special teams EPA | +1.17 | +2.04 |

Baylor won yards, plays, turnovers and total EPA and lost by one. The gap was
finishing, not talent.

## What decided it
1. **Red zone.** Baylor reached the Auburn 22 or closer five times for 16 points.
   Two turnovers on downs inside the 40.
2. **Third down.** 9 of 28 for Baylor, 10 of 19 for Auburn.
3. **Right-side run fit.** Auburn ran 15 times to their right for 116 yards, 7.7
   per carry. Every other direction: 58 yards on 19 carries. The game-winning
   touchdown was a Brown keeper to that side on third and three.
4. **Short right passing.** Baylor threw there 17 times for 59 yards and -8.57
   EPA, the largest negative category in the game for either team.
5. **Second-level rushing.** Line yards were nearly even, 118 to 107.5, so the
   offensive line held up. Highlight yards per rush opportunity was 1.50 for
   Baylor against 4.82 for Auburn. Baylor produced zero explosive rushes.
6. **The middle eight.** Auburn +6.73 EPA at 0.34 per play across the last four
   minutes of the first half and first four of the second. Baylor +1.27 at 0.10.

## Turnover luck: the number that reframes the game
Baylor forced three interceptions against 1.3 expected, worth roughly +14.4
points of turnover luck. They were the beneficiary of a large random swing and
still lost by one. Strip the luck out and this was not close on the merits. Do
not carry "wins the turnover battle" forward as a Baylor strength.

## Keys to Victory grading
Three of six non-negotiables hit cleanly (sacks allowed 1, explosive passes 7,
takeaways 3). Giveaways missed at 2. Brown rushing yards missed by six at 66.
Auburn third down distance could not be graded.

Two key results were ungradeable live: average third down distance and explosives
vs man coverage. Add both to the live capture before Week 2.

## Dependability rating
New metric introduced this week: 50% success rate, 25% catch rate (folds into
success rate for rush-heavy players), 15% volume credibility (full credit at 8+
touches), 10% ball security. EPA reported separately as production.

Baylor had one skill player above 70 (Freeman, 77). Auburn had four above 65.
Baylor's fourth through seventh receiving options combined for 10 targets, 2
catches, 23 yards. That depth gap is why Auburn could bracket Freeman without
consequence.

## Carry forward
- Receiver depth is the roster issue.
- Interior run game: 18 carries, 53 yards. The three new offensive line spots
  showed up where the pre-game brief expected.
- Defense is legitimate. Havoc held at 23% to 24% from the first quarter to the
  whistle, 96th percentile, and never faded against Auburn's no-huddle. The one
  hole is edge setting to the defensive left.
- Lagway needs a second-half adjustment package. He was 17/25 for 199 at half and
  10/29 for 134 after.

## What to watch in Weeks 2 and 3
Prairie View (projected 53-12) and Louisiana Tech (projected 34-24) are
diagnostic games, not competitive ones. Watch process, not score.

1. Highlight yards per rush opportunity. If 1.50 does not climb against a weaker
   front, the run problem is structural rather than an Auburn-defense problem.
2. Third down conversion rate. Still in the 30s against an FCS opponent means
   play-calling or personnel, not matchup.
3. Points per scoring opportunity, defined as any drive reaching the opponent's
   40. Better than red zone touchdown rate for catching the finishing problem.

Discount havoc rate against Prairie View, it will be inflated. Compare Week 3
Louisiana Tech back to the Auburn baseline, not to Week 2.

## Deliverables in the Week 1 folder
- `2026-09-05_Auburn-Baylor_Halftime-Report_Baylor-Design_AgencyFB.docx`
- `2026-09-05_Auburn-Baylor_Postgame-Review.docx`
- `2026-09-05_Auburn-Baylor_Postgame-Advanced-Box.md` (full GameOnPaper advanced
  box, baseline scoring, turnover luck, Week 2 and 3 watch list)

Documents are built to the Baylor design system with Agency FB headers.

## Frozen predictions file
`~/DEV/CFB_Victory_Model/frozen_predictions_2026.csv` has NOT been edited. The
Week 1 row still has empty `actual_pts` and `actual_opp_pts`. Result to log when
ready: Baylor 16, Auburn 17.
