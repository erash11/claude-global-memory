# Weekly Matchups 2026 — transferred project context

Carried over from the Claude cloud project, Sept 2026.

## Purpose

Week-by-week matchup analysis for each 2026 Baylor football opponent, to identify
tendencies and projected outcomes.

## Sources

Core: CFBD/Dataverse, GameOnPaper, BCFToys, and the CFB_Victory_Model. PFF stats are
included alongside those four.

## Cadence

Pull data at the start of the week, then again midweek. The output is a document written
into that week's opponent folder, not a shareable page. Each opponent has its own folder
under Weekly_Matchups_2026, named `Week_N_OPP`.

## Data rules

Use 2026 data. Fall back to 2025 only until an opponent has played two games in 2026.

Account for new coordinators: where a team changed offensive or defensive coordinators,
read that coordinator's 2025 team rather than the team's own 2025 data.

## EPA-driven tendency method

A separate strand inside this project. Use EPA from play-by-play to drive which plays and
situations to study, then read PFF formation and personnel on those to build tendencies.

Design captured in `docs/epa-driven-tendency-method.md`.

Pilot game: Baylor vs Houston, November 2025.

## Migration note

Project docs moved out of the Claude cloud project onto disk in Sept 2026. The disk
folder is the source of truth. The cloud project retains only
`claude/source-of-truth.md` as a pointer. Structure is CLAUDE.md as entry point, plus
`docs/` and `docs/weeks/`, as a git repo.

Original intended location was `~/DEV/Football/MatchupAnalysis_FB2026`. The current
Windows staging copy sits at `C:\DEV\Weekly_Matchups_2026`. Reconcile the two when
consolidating onto the Mac.

## Related

- CFB_Victory_Model, PFF_Data_Project, file organization conventions
