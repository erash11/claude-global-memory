# Football GRID — transferred workbook context

Carried over Sept 2026. Read before editing or troubleshooting the workbook.

## Data shape

Source is a Catapult GPS export landing in a "Practice" table: 124 columns, including
`Source.Name`, `Activity Name`, `Period Name`, `Is Drill`, `Player Load`.

Fall Camp 2026 covers 14 practices (FC26 P1-P14), 5-21 Aug 2026, roughly 88 athletes
across 10 position groups.

## Tabs

Coaching Guide, Flag Board, Practice, Ref, Drill Library, Practice Planner, Athlete PBC,
Signal Scan, Plan vs Actual, Period Length, Flag Engine, QB Dashboard, Line Dashboard,
plus a hidden Claude Log.

Added Aug 2026 and ported from the volleyball workbook: Periodization, Periodization Viz,
Load Thresholds. Those carry a 126-day calendar (3 Aug - 6 Dec 2026) and the 13-game 2026
schedule driving GD+/GD- numbering.

**The volleyball workbook is the design source.** Football tabs get ported from it, not
the other way round.

## Two separate threshold systems

This is the part that trips people up. Time thresholds and metric thresholds live on
different sheets and answer different questions.

**Practice Length sheet — the in-house time rule.** Team level only.

| Band | Length |
|---|---|
| Blue | Walk-throughs only. A category, not a length. |
| Green | Up to 90 min |
| Yellow | Over 90 up to 105 |
| Red | Over 105, including anything past 120 |

Boundaries are inclusive at the top: 90 is the last green minute, 105 the last yellow.
A short ordinary practice is green.

Counted time excludes the opening run-through, the special-teams run-through, and team
stretch. Only periods after the stretch count. Source of truth is the GPS period output,
not the practice script: Unix start and stop times of post-stretch periods, summed into
total session time.

**Load Thresholds sheet — tertiles.** Individuals and position groups are banded by
tertile only, never by the clock. Frozen to the 14-practice camp baseline.

## Design decisions

- **Explosive Efforts** is the third (intensity) band, chosen because it means something
  for every position. Contact load applies mainly to linemen and may return later as part
  of position-level analysis.
- Analysis is position-level, not squad-only. The Periodization tab bands by a
  position-group dropdown.
- No game benchmark until the first game is played (Auburn, 5 Sep 2026). Until then
  percentages run against the camp practice average. Revisit after.
- On accountable time alone, the two camp scrimmages qualify as yellow days. Accepted
  for now.

## Planned, not built

Weight each period by how live it is and by the dress of the day, so a live full-pads
day skews red on its own account rather than only when the clock runs long. Noted on the
Practice Length sheet.

Tempo/dress weighting is session level, not period level: dress is constant for a whole
practice, and the tempo or theme is set at the start. Daily practice outlines arrive
ahead of time, so both are known before practice, and the practice plan keeps flowing
into the workbook.

## Operational notes

- The file lives on OneDrive, not Box.
- The practice planner build is a prototype. No coach is using it yet.
- For nuanced changes, prefer Claude in the Excel app. Use Cowork sessions for big
  structural items.

## Related

- Volleyball_GRID (the design source), CMJ fatigue traffic light work, GPS/ForceDecks pipelines
