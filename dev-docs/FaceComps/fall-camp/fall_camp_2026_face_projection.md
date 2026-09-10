# Fall Camp 2026 Face Projection

Projection uses the FC24/FC25 Fall Camp period library and Fall Camp daily thresholds: GREEN <= 405, YELLOW 406-459, RED > 459 PL/player.

Period-count thresholds use FC24/FC25 Catapult practice structure after STRETCH: GREEN-count <= 11, YELLOW-count 12-13, RED-count > 13 counted periods.

Count rule for the 2026 face workbook: start after the first TEAM STRETCH/STRETCH label, then count every following drill label unless it contains BREAK.

Note: this is a quick meeting snapshot, not the final app model. Scrimmage blocks are estimated from the weighted average PL/min of historical `(SCRIM)` team periods.

| Practice | Dress | Tempo | Count After Stretch | Count Zone | Matched Min | Est. PL/player | Load Zone | Emphasis |
| --- | --- | --- | ---: | --- | ---: | ---: | --- | --- |
| P1 | HELMETS | TAG | 11 | GREEN | 106.0 | 293 | GREEN | MIXED DOWNS |
| P2 | HELMETS | TAG | 11 | GREEN | 99.0 | 275 | GREEN | MIXED DOWNS |
| P3 | SHELLS | THUD | 14 | RED | 123.0 | 342 | GREEN | MIXED DOWNS |
| P4 | SHELLS | THUD | 14 | RED | 123.0 | 342 | GREEN | 3RD DOWN |
| P5 | SHELLS | THUD | 14 | RED | 129.0 | 357 | GREEN | 3RD DOWN |
| P6 | FULL PADS | THUD | 12 | YELLOW | 117.0 | 327 | GREEN | 3RD DOWN |
| P7 | SHELLS | TUD | 10 | GREEN | 103.0 | 290 | GREEN | RED ZONE / LOW RED |
| P8 | HELMETS | TAG | 10 | GREEN | 101.0 | 284 | GREEN | 2-MINUTE |
| P9 | FULL PADS | LIVE | 9 | GREEN | 85.0 | 237 | GREEN | SCRIMMAGE #1 |
| P10 | FULL PADS | THUD | 13 | YELLOW | 117.0 | 327 | GREEN | SHORT YARDAGE |
| P11 | FULL PADS | THUD | 12 | YELLOW | 115.0 | 319 | GREEN | 4-MINUTE |
| P12 | SHELLS | THUD | 11 | GREEN | 106.0 | 295 | GREEN | GOAL LINE |
| P13 | SHELLS | THUD | 10 | GREEN | 96.0 | 273 | GREEN | RZ / 2-MINUTE / LAST 2 PLAYS |
| P14 | FULL PADS | LIVE | 8 | GREEN | 135.0 | 381 | GREEN | SCRIMMAGE #2 |
| P15 | HELMETS |  | 7 | GREEN | 25.0 | 85 | GREEN | CORRECTIONS / NEW OPP |
| P16 | FULL PADS |  | 12 | YELLOW | 102.0 | 282 | GREEN | MIXED DOWNS |
| P17 | SHELLS |  | 11 | GREEN | 98.0 | 276 | GREEN | 3RD DOWN |
| P18 | Helmets/Spiders |  | 10 | GREEN | 65.0 | 186 | GREEN | SY / GL - REDZONE |

## Unmatched Period Audit

7 rows in the face workbook had minutes but did not map to the quick Fall Camp load library. Review `docs/fall-camp/fall_camp_2026_unmatched_periods.csv` before treating this as final.

## Files

- `docs/fall-camp/fall_camp_2026_face_projection.csv`
- `docs/fall-camp/fall_camp_2026_period_projection.csv`
- `docs/fall-camp/fall_camp_2026_period_count_detail.csv`
- `docs/fall-camp/fall_camp_2026_unmatched_periods.csv`
