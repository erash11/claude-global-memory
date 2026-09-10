# What is actually in the Kinexon exports

Written against the FA26 camp block sitting in `Box/Kinexon/Session Downloads` as of
2026-08-02. Re-run `python -m kinexon.verify` after any new drop; it re-checks
everything claimed here.

## The block

Six practices over three days — two-a-days, 30 July to 1 August 2026. Sixteen athletes.

| # | Date | Type | Length | Squad jumps | Jumps/min |
|---|------|------|--------|------------:|----------:|
| 1 | Thu 30 Jul, am | Camp, Full | 3h 10m | 946 | 4.97 |
| 2 | Thu 30 Jul, pm | Camp, Serve & Pass | 1h 31m | 529 | 5.83 |
| 3 | Fri 31 Jul, am | Camp, Individual/Skills | 2h 40m | **1,780** | **11.13** |
| 4 | Fri 31 Jul, pm | Camp, Full | 3h 10m | 991 | 5.21 |
| 5 | Sat 1 Aug, am | Camp, Serve & Pass | 3h 46m | 943 | 4.17 |
| 6 | Sat 1 Aug, pm | Camp, Full | 1h 36m | 900 | 9.39 |

Practice 3 is the outlier: nearly twice the jumps of any other session, in the
second-shortest one. An "Individual/Skills" session producing the heaviest jump day of
the block is either the most important finding in here or a labelling problem — worth
confirming before it goes near a coach.

## The three export shapes

The drop folder holds 36 files in three different shapes, and the loader handles each:

| Shape | Files | Grain | Metrics |
|---|---|---|---|
| `roster_wide` | `Practice N/<POS>_N.csv` | one row per athlete per practice | 21 |
| `team_wide` | `FA26_Practices1-6.csv`, `Team Numbers 1-6.csv` | one row per practice, squad totals | 21 |
| `full_export` | `Test.csv` | one row per athlete per **drill** | 68 |

Notes that cost time to work out:

- **`Team Numbers 1-6.csv` and `FA26_Practices1-6.csv` are byte-identical.** Two names
  for one export.
- **All three XLSX files duplicate a CSV.** Two of them (`FA26_Practices1-6.xlsx`,
  `Practice 1/OPP_1.xlsx`) are not real spreadsheets — they are the semicolon CSV opened
  in Excel as a *comma* file, so each line got split on its unquoted commas
  (`Camp,Full` became two cells). The loader detects this and rejoins on the comma.
  Getting that wrong shifts every column by one and silently corrupts the load.
- **Kinexon appends a `Ø All players` row to each per-position file.** It is a *mean*,
  not a total. It is dropped on ingest; leaving it in inflates every squad figure by
  roughly 6–16%.
- **Session descriptions are hand-typed and inconsistent** — `FA26_7.30.26Practice1`,
  `FA26_7.31.26_Practice3`, `FA26_8.1.2026_Practice5`. The practice *number* is the only
  reliable session identity, so that is what the loader keys on.

## Practice 1 is exported at drill level — the others are not

`Test.csv` covers Practice 1 only, but Kinexon recorded each drill as its own session,
so it carries a within-practice breakdown the other five practices do not have. The
drill rows contain no reference to the parent practice; the loader reattaches them by
time containment (a drill belongs to the practice whose window encloses it).

Jump density by drill, Practice 1:

| Drill | Length | Jumps/min |
|---|---|---:|
| Box Drill | 7m | **26.76** |
| Hurricane | 10m | 12.35 |
| Correction Exchange | 20m | 11.41 |
| Bunch Drill | 35m | 6.63 |
| Whirlwind | 35m | 3.92 |
| Dynamic Warm Up | 12m | 1.92 |

A 7× spread between Box Drill and Whirlwind. The session total (946 jumps, 4.97/min)
hides all of it. **Exporting every practice this way is the single highest-value change
available to the data collection** — it is the difference between "yesterday was heavy"
and "the third drill is what made yesterday heavy".

## Metric coverage

21 metrics exist for all six practices; 47 more exist for Practice 1 only, because only
that practice was exported in full. Notably **`Jump Load (J)`, metabolic work, physio
load, and the accel/decel splits are Practice-1-only** — so any report built on jump
load in joules cannot yet run block-wide. `Mechanical Load` is the load metric that *is*
available everywhere.

Heart rate columns are present but **entirely empty** across every row. Five metrics
register — `heart_rate_pct_of_hrr`, `heart_rate_pct_of_max`, `heart_rate_recoveries`,
`heart_rate_recoveries_per_min`, `peak_heart_rate_pct_of_max` — carrying 525
observations between them, every one of which is `0` rather than NULL. So the columns
are populated with a value that means "nothing measured", which is worth knowing before
anyone treats a zero as a reading.

**This is a capability gap, not a collection oversight.** There is no heart-rate
collection in place at present, so these stay empty until that changes — no change to
how a practice is run will populate them. Anything HR-derived (TRIMP, HR zones,
recoveries) is unavailable, and every metric this pipeline reports is therefore
*external* load.

## Data-quality items to resolve with the staff

`python -m kinexon.verify` reports these every run, **with the athlete names**. Names are
left out of this file on purpose — see "A note on names" below. None of the four are
ingestion bugs; all are in the source data.

**Once one of these is decided, record it in `config/data-quality.json`** (gitignored;
`config/data-quality.example.json` shows the format). The post-practice report then
holds that athlete out of the named exceptions and out of its usable count, while
keeping her bar in the ranked chart with the reason printed — so a slipped sensor
cannot masquerade as a training-load finding, and nothing disappears quietly either.

Until an item is recorded there it stays a *suspicion*: the report shows it, labelled
unreviewed, and excludes nothing on its own authority.

1. **Jersey #9 is assigned to two athletes** — one setter and one middle blocker. Every
   join in this pipeline is on name, so nothing is currently mixed up, but the Kinexon
   roster config should be corrected before anything joins on number.
2. **One outside hitter records 23 jumps across the whole block**, against a 379 median
   for the other outside hitters — sixteen times below her group. Sensor, tagging, or a
   modified role, but it is not a normal OH workload.
3. **Two zero-jump sessions**, by two different athletes, in a 2h 40m and a 3h 46m
   session respectively.
4. **One middle blocker appears from Practice 4 onward** (3 of 6). Believed to be a
   genuine late arrival rather than a fault, but her baselines rest on three sessions,
   and the dashboard says so wherever it uses them.

## A note on names

This repository is on GitHub and the roster is real student-athletes, so no athlete name
or per-athlete figure appears in any tracked file. The exports, the database and the
generated dashboard are all gitignored. Run `python -m kinexon.verify` locally to see
which athletes the items above refer to.

## What this data cannot support

**Acute:chronic workload ratio.** The review prototype ranked athletes on it. ACWR needs
roughly 28 days of chronic load; this block is three. It is deliberately absent from the
dashboard rather than computed on a window that cannot carry it. It becomes available
once about four weeks of practices have been ingested — the pipeline does not need to
change for that, only the data.

Everything comparative in the dashboard is therefore **each athlete against her own mean
across these six practices**, with n printed alongside. With n=6 that is a prompt to look,
not a finding.

## Running it

```bash
python -m kinexon.ingest "C:/Users/<you>/Box/Kinexon/Session Downloads" --reset
python -m kinexon.verify
python -m kinexon.build_dashboard
```

Ingest is idempotent — re-running over the same folder, or over a CSV and its XLSX twin,
converges rather than double-counting. The generated dashboard is gitignored because it
carries athlete names in the page.
