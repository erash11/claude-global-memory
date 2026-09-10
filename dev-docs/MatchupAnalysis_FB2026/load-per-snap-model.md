# Load per snap — game demand model

Built 2026-09-06. Answers "what does a snap actually cost this athlete" by joining PFF
charted snaps to Catapult in-game Player Load.

## The finding that shapes the method

Raw Player Load ÷ snaps is **wrong** and inverts the truth. Measured across 546 player-games
from the 2025 season:

| Snaps played | Player-games | Raw load / snap |
|---|---|---|
| 10-19 | 112 | 17.66 |
| 20-34 | 91 | 11.83 |
| 35-54 | 128 | 8.92 |
| 55-119 | 215 | 6.67 |

Backups are not more intense. Catapult accrues load for the whole quarter period whether or
not the athlete is on the field — warm-up between quarters, sideline movement, standing. A
low-snap athlete divides a large fixed cost by a small number.

## The model

Per position group, regress in-game Player Load on charted snaps:

`PL = intercept + slope × snaps`

- **slope** = marginal cost of one snap
- **intercept** = fixed cost of dressing for a game

Fit on 2025 season, athletes with 10+ snaps, quarter periods only (warm-up excluded):

| Group | Player-games | Load per snap | Fixed game cost | R² |
|---|---|---|---|---|
| Running Back | 34 | 5.27 | 194 | 0.74 |
| Wide Receiver | 69 | 5.81 | 199 | 0.73 |
| Tight End | 36 | 4.62 | 204 | 0.65 |
| Offensive Line | 85 | 3.08 | 184 | 0.75 |
| Defensive Line | 48 | 4.61 | 164 | 0.84 |
| Edge / OLB | 47 | 3.07 | 204 | 0.69 |
| Linebacker | 51 | 4.38 | 196 | 0.88 |
| Defensive Back | 163 | 4.26 | 220 | 0.66 |

QB excluded, only 13 player-games — below the 15 minimum. Add it once 2026 accumulates.

**Independent confirmation of the intercept:** in Week 1 2026, the 19 athletes with zero
charted snaps still finished with a median of 193 Player Load. That is the fixed cost,
measured directly.

## Outputs per athlete

- **Expected** = model prediction for the snaps actually played
- **Diff** = actual minus expected
- **z** = diff on the position group's residual SD
- **Snap-Eq** = diff ÷ slope, i.e. the residual expressed in snaps

Snap-Eq is the coach-facing number: "+41 snaps worth of load above expectation."

## Week 1 2026 result
19 athletes above the line, 9 below, of 64 with 10+ snaps. Ryan Davis +127 PL (+2.8z,
+41 snap-equivalents). The edge group ran hot, 4 of 6 above, which fits a defense that
rushed four and asked those players to chase.

## Data-quality catches the model surfaces for free
This is a side benefit worth keeping. Large negative residuals are usually equipment, not
training:
- **Jamaal Whyce**, 17 PL on 39 snaps, z = −7.6. A unit that failed or was not worn. Correct
  the game file before it enters any baseline.
- **Stilton McKelvey**, 356 PL and the team's fastest speed on zero charted snaps. His role
  is not being captured by the PFF snap join, not a load anomaly.

## Source files
- Historical pull: 12 PFF games (2025 ids 28762, 28893, 28925, 28993, 29083, 29112, 29258,
  29282, 29335, 29437, 29496, 29563) joined to the 12 matching Catapult game activities.
  PFF `/v1/ncaa/2025/games` returns a dict — games live under the `games` key, filter on
  `home_franchise_id` / `away_franchise_id` == 118.
- Catapult game history goes back to 2023 (38 game activities), so the model can be refit on
  three seasons if a larger sample is wanted. Period naming (`1ST QTR` … `4TH QTR`) is
  consistent across seasons; 2025 also carries occasional custom periods, so match on
  `QTR`/`OT` rather than an exact list.
- Report: `~/DEV/Catapult_API/Auburn_G1_LoadPerSnap.pdf`

## Next
Refit weekly as 2026 games accumulate, and eventually replace the 2025 model with a
2026 model once there are ~8 games. Practices have no snap counts, so this metric is
game-only; practice intensity still needs a different denominator.
