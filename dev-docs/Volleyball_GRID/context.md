# Volleyball GRID — transferred workbook context

Carried over Sept 2026. Read before editing or troubleshooting the workbook.

## Where the canonical file lives

Canonical copy is `Volleyball_Revised.xlsx` in `Box\Kinexon\SandBox` (renamed from
Volleyball_GROUP). A working copy sits at
`OneDrive > 00_Primary_Storage_Drive > 02_SPORTS > Volleyball > SandBox`.

Two versions had diverged (Volleyball_GRID vs Volleyball_v2) and were merged into a
single GRID file in Aug 2026.

## Refresh workflow

Drop the source export into the Box source folder, then Refresh All on the dashboard.
Everything else updates from there.

Power Query pulls from the Box folder "Session Exports 8.13" (Kinexon session exports).
A newer data repo lives at `Box\Kinexon\Kinexon Raw Data`; only the Overview tab of each
session file merges into the master dataset, via a `Kinexon_Master` table.

Shared with Michael Wenger, who refreshes it on his own machine. Only the two of them
will ever use this file, so the two hardcoded Power Query fallback paths are sufficient.
No per-user path input is needed.

## Two operational traps

**A workbook open in Excel makes automated saves silently no-op.** Excel serves a
read-only copy. Close it before applying changes.

**Box overrules local file operations on the sync folder.** Renames and deletes get
reverted; rapid repeated writes produce conflict copies and a read-only flag. Work on a
copy outside Box, then upload one new version of the existing file through Box on the web.

## Thresholds

Load thresholds (team, position, individual) are frozen to the Practices 1-18 baseline,
the last practice before the first regular-season match (18 Aug 2026, Honolulu), so
light/medium/hard classifications do not drift as the season adds data. Live percentile
formulas sit parked on Load Thresholds L11:Q45, unapplied.

Matches are deliberately excluded from load thresholds. Revisit once regular-season
matches accumulate.

Note: Kinexon changed the jump-height bands from absolute feet to % of max between
export versions.

## Capacity and layout

- Roster is 16 athletes. The Athlete Load Grid was opened to 24 slots (grid rows 7-30,
  GD-1 block rows 35-58) so new athletes calculate automatically.
- Process Behavior session index raised 100 to 300 sessions, matching Load Monitoring
  rows 51-350. Practice XmR raised 100 to 200.
- An athlete with no frozen individual threshold now falls back to her position band
  instead of returning #N/A.
- Charts are driven by `cs_*` defined names (OFFSET spans off helper cells Ref!B25:B29)
  so each chart sizes to the data instead of plotting empty rows. GD Profile follows the
  two most recent matches with session data via Ref!B21:B24.
- Drill cost map rebuilt as 124 series covering Drill Library rows 8-127, labels and
  values from live helper columns T/U, colored by quadrant, so new drills appear
  automatically.
- Periodization calendar rows 40+ used to need the session ID typed into column E by
  hand. C/D/E now auto-fill from Load Monitoring by date; a date with more sessions than
  calendar rows shows a "(+N more this day)" flag on its last row.

## Known open issue

The Game XmR block on Process Behavior still summarises only its first 100 rows.

## Related

- Kinexon_Volleyball, Football_GRID (which ports design from here), volleyball data hub
