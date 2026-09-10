# CMJ Force Plate Dashboard — User Manual

## Table of Contents

- [Part 1: For the Sport Scientist](#part-1-for-the-sport-scientist)
  - [Running the Pipeline](#running-the-pipeline)
  - [Generating the Dashboard](#generating-the-dashboard)
  - [Distributing to Staff](#distributing-to-staff)
  - [Resetting Baselines](#resetting-baselines)
  - [Troubleshooting](#troubleshooting)
- [Part 2: For the Coach](#part-2-for-the-coach)
  - [Opening the Report](#opening-the-report)
  - [Roster View](#roster-view)
  - [Athlete Profile View](#athlete-profile-view)
  - [Quick Reference: What to Look For](#quick-reference-what-to-look-for)

---

## Part 1: For the Sport Scientist

### Running the Pipeline

The pipeline pulls data from VALD ForceDecks, classifies each athlete, and stores results in a local database.

**Pull new data + classify + generate report (most common):**
```bash
python run_pipeline.py --report
```

**Pull new data + classify only (no report):**
```bash
python run_pipeline.py
```

**Verify API connection without writing to the database:**
```bash
python run_pipeline.py --dry-run
```

**Pull data from a specific start date:**
```bash
python run_pipeline.py --from-date 2026-01-15 --report
```

The default start date is `2026-01-01`. All tests from the start date forward are pulled.

### Generating the Dashboard

**Generate a report from existing data (no new data pull):**
```bash
python run_pipeline.py --report-only
```

This creates a self-contained HTML file at:
```
reports/YYYY-MM-DD_team_dashboard.html
```

The file opens automatically in your default browser. It contains all CSS, JavaScript, and SVG graphics inline — no internet connection or external files needed.

### Distributing to Staff

The dashboard is a **single HTML file**. Distribution options:

1. **Email:** Attach the HTML file directly. Coaches open it in any browser (Chrome, Safari, Edge, Firefox). No software installation required.

2. **Shared drive:** Copy to a shared folder (Google Drive, OneDrive, Teams). Staff can download and open locally.

3. **Print:** Open in a browser and print to PDF (Ctrl+P / Cmd+P) if a hard copy is needed.

**Important:** The file works completely offline. Once a coach has the file, they do not need network access to view it.

**Recommended cadence:** Generate and distribute after each testing session so staff have the latest data before practice planning.

### Resetting Baselines

Baseline trend data is computed from the average of each athlete's first 4 tests in the current season. Baselines do not auto-update. If you need to reset an athlete's baseline (e.g., after returning from injury or at the start of a new training block):

**Reset one athlete:**
```bash
python run_pipeline.py --reset-baseline <ATHLETE_ID>
```

**Reset all athletes:**
```bash
python run_pipeline.py --reset-all-baselines
```

After resetting, re-run the pipeline (`--report`) to pull fresh data and re-establish baselines.

### Troubleshooting

| Issue | Solution |
|-------|----------|
| Report shows no athletes | Run `python run_pipeline.py` first to pull data |
| "Establishing baseline" for all athletes | Fewer than 4 tests in the database — test more frequently or adjust `--from-date` |
| Dashboard looks stale after re-run | Hard refresh the browser (Ctrl+Shift+R) to clear cache |
| API authentication fails | Verify `.env` file contains valid `VALD_CLIENT_ID`, `VALD_CLIENT_SECRET`, and `VALD_TEAM_ID` |

---

## Part 2: For the Coach

### Opening the Report

You will receive an HTML file named something like `2026-03-21_team_dashboard.html`. Double-click it to open in your browser. No apps or logins needed — everything is in the file.

### Roster View

The roster view is the first screen you see. It shows every athlete as a card in a grid layout.

#### Alert Banner

If any athletes are flagged for clinical review, a **red alert banner** appears at the top of the page. These athletes have asymmetry or readiness concerns that require follow-up with medical staff before returning to full training.

#### Athlete Cards

Each card shows:

| Element | What It Tells You |
|---------|-------------------|
| **Name** | Athlete name |
| **Status dot** (top right) | Readiness status — green (good), yellow (monitor), orange (caution), red (restricted) |
| **Classification badge** | Performance tier (see table below) |
| **Movement type badge** | How the athlete loads during the jump (see Movement Strategy section) |
| **Power** (W/kg) | Relative power output — higher is better |
| **Force** (%) | Bilateral asymmetry — lower is better (below 10% is normal) |
| **mRSI** | Modified Reactive Strength Index — higher indicates more explosive |
| **Position & body weight** | At the bottom of the card |

#### Classification Tiers

| Badge | What It Means | Coaching Implication |
|-------|---------------|----------------------|
| **ELITE CONCENTRIC** | Top tier (Gold) with confirmed eccentric strength | Athlete is performing at a high level — maintain current training |
| **EXPLOSIVE ECC** | Top tier (Gold) with strong eccentric profile | High reactive/elastic qualities — leverage with plyometric work |
| **BALANCED ATHLETIC** | Mid tier (Purple) — solid across the board | Room to improve — target specific phase deficits |
| **DEVELOPMENTAL** | Below average (White) for their position | Needs foundational strength and power development |

#### Readiness Status Dots

| Color | Meaning | Action |
|-------|---------|--------|
| Green | Ready for full training | No restrictions |
| Yellow | Minor deviation from baseline | Monitor — no restrictions needed |
| Orange | Moderate concern | Reduce training load, check in with sports science |
| Red | Significant flag (high asymmetry or readiness concern) | Restrict activity, 48-hour clinical evaluation required |

**Red and orange cards have a colored left border** to draw your eye to them immediately.

#### Filtering and Sorting

**Filter tabs** at the top let you view athletes by classification tier. Click a tab to show only that group (e.g., "DEVELOPMENTAL" to see who needs the most development).

**Sort dropdown** (top right) lets you reorder cards by:
- **Name** — alphabetical
- **mRSI** — most explosive first
- **Power** — highest relative power first
- **Readiness** — most concerning first

### Athlete Profile View

Click any athlete card to open their full profile. Click **"Back to roster"** at the top to return.

#### Radar Chart (Team Percentile Profile)

The hexagonal radar chart shows how this athlete compares on 6 key metrics:

| Axis | What It Measures |
|------|------------------|
| **Pk Power** | Peak Power relative to body mass |
| **Rel. Force** | Eccentric peak force relative to body mass |
| **ECC Pw** | Eccentric peak power relative to body mass |
| **Jump Ht** | Jump height (impulse-momentum method) |
| **RSI-mod** | Modified reactive strength index |
| **FT:CT** | Flight time to contraction time ratio |

**Three overlaid shapes:**

| Line | Color | What It Represents |
|------|-------|--------------------|
| **Athlete** | Green (solid) | This athlete's current values |
| **Team Avg** | Orange (dashed) | Average of all teammates at the same position |
| **NFL P50** | White (dashed) | NFL 50th percentile for this position |

**How to read it:**
- The further a green vertex extends from center, the better the athlete performs on that metric
- If green extends beyond orange, the athlete is above their team's position average
- If green extends beyond white, the athlete exceeds the NFL median for their position
- A "spiky" shape means uneven development — strong in some areas, weak in others
- A round, large shape means well-rounded high performance

#### Key Metrics Panel

10 performance metrics with values and units. These are the primary numbers that define the athlete's force plate output. Compare across athletes at the same position to identify relative strengths.

#### Phase Profile (Tier 2)

Breaks down performance into three phases of the countermovement jump:

| Phase | What It Tells You |
|-------|-------------------|
| **Braking** | How well the athlete decelerates and absorbs force during the eccentric loading phase |
| **Propulsive** | How effectively the athlete produces force during the concentric (push-off) phase |
| **Landing** | How well the athlete manages impact forces when returning to the ground |

Each phase has a status badge:

| Status | Meaning |
|--------|---------|
| **Strong** | Performing at or above the 75th percentile for their position |
| **Monitor** | Within normal range (25th to 75th percentile) |
| **Deficit** | Below the 25th percentile — area for targeted improvement |
| **High Risk** | Significantly below norms — injury risk concern |

**Coaching action:** Focus training interventions on phases showing "Deficit" or "High Risk." For example, a braking deficit suggests the athlete needs more eccentric strength work; a landing deficit may warrant landing mechanics coaching.

#### Movement Strategy (Tier 3)

Describes how the athlete organizes their jump movement:

| Type | What It Means | Typical Profile |
|------|---------------|-----------------|
| **Fast-Deep** | Quick loading with large countermovement | High reactive/elastic qualities — responds well to plyometrics |
| **Balanced** | Moderate loading speed and depth | Versatile — responds to varied training stimuli |
| **Slow-Deep** | Slow loading with large countermovement | Strong but less reactive — benefits from rate of force development work |
| **Slow-Shallow** | Slow loading with limited depth | Strength-dominant, low stiffness — needs both depth and speed work |
| **Unknown** | Data unavailable for classification | Check that test was recorded correctly |

The raw values for eccentric duration (ms) and countermovement depth (cm) are shown below the classification.

#### Trend vs Baseline

Shows how 5 key metrics have changed compared to the athlete's baseline (average of their first 4 tests this season):

- **Green arrow up** — metric improved from baseline
- **Red arrow down** — metric declined from baseline
- **Dash** — no baseline established yet

The baseline value and current value are shown with the percentage change. If the header says "Establishing baseline (N/4 tests)," the athlete hasn't completed 4 tests yet — the trend is preliminary.

**Coaching action:** Declining trends in power or jump height may indicate accumulated fatigue. Discuss with the sport scientist whether training load adjustments are needed.

#### Strengths and Weaknesses

Auto-generated list of metrics where the athlete significantly exceeds (strength) or falls below (weakness) their positional norms. These are the clearest targets for individualized training.

#### Prescription and Interventions

Training recommendations generated by the classification system based on the athlete's tier, phase profile, and identified deficits. Use these as a starting point for programming decisions.

#### Clinical Notes

Any clinical observations or restrictions from medical staff. If the athlete has a red or orange flag, this section will contain the reason.

---

### Quick Reference: What to Look For

**Before practice — check the roster view:**
1. Is there a red alert banner? If yes, those athletes need clinical clearance first.
2. Are any status dots orange or red? Adjust their training load.
3. Sort by "Readiness" to quickly see who needs attention.

**For training design — check athlete profiles:**
1. Look at Phase Profile status badges — where are the deficits?
2. Check Movement Strategy — what type of training will this athlete respond to best?
3. Review Trend vs Baseline — is the athlete improving, maintaining, or declining?

**For position group planning:**
1. Use filter tabs to view one classification tier at a time.
2. Compare radar charts across athletes at the same position.
3. Athletes below the NFL P50 line (white dashed) on multiple axes have the most room for development.

**Red flags that need immediate attention:**
- Asymmetry (Force %) above 15% on the roster card
- Red status dot
- Phase Profile showing "High Risk" in any phase
- Multiple declining trends across baseline metrics
