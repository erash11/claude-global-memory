# CMJ Fatigue Traffic Light Report — Production Development Plan

**Project:** Baylor Volleyball CMJ Fatigue Monitoring System
**Date:** February 27, 2025
**Author:** Eric Rawls, Director of Applied Performance
**Purpose:** Development specification for Claude Code implementation
**Repository:** To be created (or added to existing PT_Dash repo)

---

## What This App Does

Practice ends. Athletes step on the force plates and perform a countermovement jump. Their post-practice data gets exported as a CSV from ForceDecks. You run one command, and within seconds you have a color-coded HTML report showing exactly who's fatigued, how badly, and what to do about it. You email it to the coaching staff and athletic trainers, and everyone is on the same page before the next session.

That's it. No dashboards to log into. No databases to maintain. One CSV in, one report out.

---

## System Architecture

```
ForceDecks Export (.csv)
        │
        ▼
┌─────────────────────┐
│   master_data.csv    │  ← Append-only CSV storing all historical tests
│   (cumulative file)  │
└─────────────────────┘
        │
        ▼
┌─────────────────────┐
│  generate_report.py  │  ← Python script: reads data, runs analysis, builds HTML
│                     │
│  • Loads master CSV  │
│  • Pairs pre/post    │
│  • Calculates deltas │
│  • Applies thresholds│
│  • Renders HTML      │
└─────────────────────┘
        │
        ▼
┌─────────────────────┐
│  report_YYYY-MM-DD   │  ← Self-contained HTML file (no dependencies)
│  .html               │
└─────────────────────┘
        │
        ▼
    Manual email to
    coaching staff &
    athletic trainers
```

---

## File Structure

```
cmj-traffic-light/
│
├── README.md                    # Setup instructions + usage guide
├── requirements.txt             # Python dependencies
├── config.yaml                  # Thresholds, roster, display settings
│
├── data/
│   ├── master_data.csv          # Cumulative test data (append-only)
│   └── imports/                 # Drop raw ForceDecks CSVs here
│
├── scripts/
│   ├── import_data.py           # Reads ForceDecks CSV, appends to master
│   ├── generate_report.py       # Main analysis + HTML generation
│   └── utils.py                 # Shared helpers (threshold logic, color assignment)
│
├── templates/
│   └── report_template.html     # Jinja2 HTML template (based on mockup)
│
├── output/
│   └── (generated reports land here)
│
└── tests/
    ├── test_thresholds.py       # Unit tests for color assignment logic
    ├── test_import.py           # Tests for CSV parsing
    └── sample_data/             # Test fixtures
        └── sample_forcedecks.csv
```

---

## Step-by-Step Workflow

### Step 1: Export from ForceDecks

The practitioner exports a CSV from ForceDecks containing the current session's CMJ test data. This is the standard ForceDecks export format with columns for athlete name, date, test type, and individual metric results.

Drop the file into `data/imports/`.

### Step 2: Run the Import Script

```bash
python scripts/import_data.py
```

This script does three things:

1. Scans the `data/imports/` folder for any new CSV files
2. Parses and validates each file against expected ForceDecks column structure
3. Appends cleaned rows to `data/master_data.csv` with a source-file tag
4. Moves processed files to `data/imports/processed/` so they don't get re-imported

The master CSV is the single source of truth. Every test ever imported lives here. This matters because the system needs both pre-practice and post-practice data from the same session to calculate percent change.

### Step 3: Generate the Report

```bash
python scripts/generate_report.py --date 2025-02-18 --session post-practice
```

Arguments:

| Flag | Required | Description |
|------|----------|-------------|
| `--date` | Yes | Session date (YYYY-MM-DD) |
| `--session` | No | Label for report header (default: "Post-Practice Assessment") |
| `--output` | No | Custom output path (default: `output/report_YYYY-MM-DD.html`) |
| `--config` | No | Path to config file (default: `config.yaml`) |

The script:

1. Loads `master_data.csv`
2. Filters for the specified date
3. Pairs each athlete's pre-practice and post-practice tests
4. Calculates percent change for each metric
5. Applies threshold logic to assign metric-level and overall colors
6. Renders the HTML report using the Jinja2 template
7. Saves a self-contained HTML file to `output/`

### Step 4: Email the Report

Open the HTML file, verify it looks correct, and email it as an attachment to coaching staff and athletic trainers. The file is fully self-contained (all CSS and JS inline), so it opens in any browser without needing a server.

---

## Data Specification

### ForceDecks CSV Expected Format

The import script should handle the standard ForceDecks export. At minimum, it needs to find these columns (exact names may vary by ForceDecks version, so the config file maps them):

```yaml
# config.yaml - column mapping section
column_mapping:
  athlete_name: "Name"              # or "Athlete", "Full Name", etc.
  test_date: "Date"                 # or "Test Date"
  test_time: "Time"                 # or "Test Time"
  test_type: "Test Type"            # filter for "CMJ" only
  jump_height: "Jump Height (Imp-Mom) [cm]"
  rsi_modified: "RSI-modified [m/s]"
  mean_propulsive_force: "Mean Force (Propulsion) [N]"
  ecc_braking_rfd: "Avg. Braking RFD [N/s]"
  time_to_takeoff: "Contraction Time [ms]"
  countermovement_depth: "Countermovement Depth [cm]"
```

**Important:** ForceDecks column names change across software versions. The column mapping in `config.yaml` is the single place to update when column names shift. The import script should validate that all mapped columns exist and throw a clear error if they don't.

### Master Data CSV Schema

After import, every row in `master_data.csv` should follow this structure:

| Column | Type | Description |
|--------|------|-------------|
| athlete_name | string | Full name as it appears in ForceDecks |
| test_date | date | YYYY-MM-DD |
| test_time | time | HH:MM:SS |
| session_tag | string | "pre" or "post" (derived from time or manual tag) |
| jump_height_cm | float | Jump Height (Imp-Mom) in cm |
| rsi_modified | float | RSI-modified in m/s |
| mean_propulsive_force_n | float | Mean Propulsive Force in N |
| ecc_braking_rfd_ns | float | Eccentric Braking RFD in N/s |
| time_to_takeoff_ms | float | Time to Takeoff (Contraction Time) in ms |
| cm_depth_cm | float | Countermovement Depth in cm |
| source_file | string | Original filename for traceability |
| import_timestamp | datetime | When the row was imported |

### Pre/Post Pairing Logic

This is the part that needs to be bulletproof. The script pairs pre and post tests by:

1. Matching on `athlete_name` and `test_date`
2. The earlier test (by `test_time`) is tagged "pre," the later is "post"
3. If only one test exists for an athlete on a given date, that athlete is flagged as "unpaired" and excluded from the report with a note

If ForceDecks exports include a session label or tag field, use that instead of inferring from time. Make this configurable in `config.yaml`:

```yaml
pairing:
  method: "time"          # Options: "time" (infer from test time) or "tag" (use session_tag column)
  pre_window_start: "06:00"  # If using time method, pre-practice tests expected before this
  pre_window_end: "12:00"
  post_window_start: "14:00"
  post_window_end: "22:00"
```

---

## Threshold Configuration

All thresholds live in `config.yaml` so they can be adjusted without touching code:

```yaml
thresholds:
  jump_height:
    metric_label: "Jump Height"
    short_label: "Jump Ht"
    unit: "cm"
    direction: "decrease_is_bad"    # Decline = fatigue
    green_max: -5                    # 0 to -5% = green
    yellow_max: -10                  # -5 to -10% = yellow
                                     # beyond -10% = red

  rsi_modified:
    metric_label: "RSI-modified"
    short_label: "RSImod"
    unit: "m/s"
    direction: "decrease_is_bad"
    green_max: -7
    yellow_max: -15

  mean_propulsive_force:
    metric_label: "Mean Propulsive Force"
    short_label: "Prop Force"
    unit: "N"
    direction: "decrease_is_bad"
    green_max: -5
    yellow_max: -10

  ecc_braking_rfd:
    metric_label: "Eccentric Braking RFD"
    short_label: "Ecc RFD"
    unit: "N/s"
    direction: "decrease_is_bad"
    green_max: -8
    yellow_max: -20

  time_to_takeoff:
    metric_label: "Time to Takeoff"
    short_label: "Time-TO"
    unit: "ms"
    direction: "increase_is_bad"    # Increase = slower = fatigue
    green_max: 5
    yellow_max: 12

  countermovement_depth:
    metric_label: "Countermovement Depth"
    short_label: "CM Depth"
    unit: "cm"
    direction: "increase_is_bad"    # Increase in absolute change = compensating
    green_max: 5
    yellow_max: 12

overall_assignment:
  green: "0-1 metrics outside green range"
  yellow: "2-3 metrics in yellow OR 1 red metric"
  red: "2+ red metrics OR 3+ metrics at yellow or above"
```

---

## Overall Color Assignment Logic

This is the core decision engine. It needs to be its own function in `utils.py` so it can be unit tested independently.

**Rules (from the Volleyball CMJ Fatigue Traffic Light System document):**

- **Green:** 0 or 1 metrics outside the green range
- **Yellow:** 2-3 metrics in yellow, OR 1 metric in red
- **Red:** 2 or more metrics in red, OR 3+ metrics at yellow or above

**Pseudocode:**

```python
def assign_overall_color(metric_colors: dict) -> str:
    """
    metric_colors: dict of {metric_name: "green" | "yellow" | "red"}
    Returns: "green", "yellow", or "red"
    """
    red_count = sum(1 for c in metric_colors.values() if c == "red")
    yellow_count = sum(1 for c in metric_colors.values() if c == "yellow")
    outside_green = red_count + yellow_count

    if red_count >= 2 or (yellow_count + red_count) >= 3:
        return "red"
    elif yellow_count >= 2 or red_count >= 1:
        return "yellow"
    else:
        return "green"
```

---

## Recommendation Engine

Training recommendations map directly to the overall color. These are stored in `config.yaml` so coaches and staff can refine the language without code changes:

```yaml
recommendations:
  green:
    status_label: "Full Go"
    status_short: "No restrictions"
    interpretation: "Fatigue is within expected training response. Force production and jump strategy are preserved."
    actions:
      - "Full practice participation, no restrictions"
      - "Normal jump volume and intensity permitted"
      - "Continue current training load progression"
      - "Standard recovery protocol post-practice"

  yellow:
    status_label: "Modified"
    status_short: "Reduce max-effort jumps"
    interpretation: "Manageable fatigue present. Early changes in jump strategy or force expression."
    actions:
      - "Reduce maximum effort jumps by 20-35%"
      - "Limit repeated block and approach jump sequences"
      - "Emphasize technical and positional quality reps"
      - "Monitor during practice for additional fatigue signs"
      - "Consider extra recovery modalities post-practice"

  red:
    status_label: "Restricted"
    status_short: "Recovery-focused only"
    interpretation: "Significant neuromuscular fatigue. Suppressed force production and slower movement strategy."
    actions:
      - "Eliminate maximum effort jumps entirely"
      - "No repeated high-velocity contacts"
      - "Walkthrough, tactical, or recovery-focused participation only"
      - "Prioritize active recovery and regeneration"
      - "Re-test prior to next high-intensity session"
```

---

## HTML Report Specification

The generated HTML report must match the mockup exactly in functionality. Here is what the template needs to render:

### Header Section
- Baylor branding (BU logo block, gold/green color scheme)
- Report title: "CMJ Fatigue Traffic Light Report"
- Subtitle: "Baylor Volleyball — Applied Performance"
- Date, session label, and data source (ForceDecks)

### Summary Bar
- Three cards showing count of athletes in each zone (Green, Yellow, Red)
- Color-coded icons and counts

### Athlete Rows (collapsed view)
Each athlete appears as a single row containing:
- Traffic light indicator (glowing dot, color-coded)
- Jersey number, name, and position
- Metric pills showing each metric's percent change with color coding
- Status badge ("Full Go" / "Modified" / "Restricted") with short description

### Athlete Rows (expanded view)
Clicking a row expands it to show:
- Detail metric cards with pre and post values, units, and percent change
- Practice recommendations list pulled from the config

### Legend Section
- Threshold reference explaining green, yellow, and red criteria
- Overall color assignment rules

### Footer
- "Baylor Athletics Applied Performance | B.A.I.R. Initiative"
- "Green = Go · Yellow = Be Smart · Red = Protect Tomorrow"

### Technical Requirements
- Fully self-contained HTML (all CSS and JS inline, no external dependencies)
- No CDN links, no external fonts in production (embed or use system fonts)
- Works offline when opened in any modern browser
- Responsive layout (functions on tablet if someone opens it on an iPad)
- Click-to-expand functionality preserved via inline JavaScript
- Print-friendly (consider a `@media print` stylesheet)

---

## Roster Configuration

The config file should include a roster section so the report can display jersey numbers and positions even if ForceDecks doesn't export them:

```yaml
roster:
  - name: "Avery Mitchell"
    number: "4"
    position: "Outside Hitter"
  - name: "Jordan Ellis"
    number: "12"
    position: "Middle Blocker"
  # ... full roster
```

The report script matches athlete names from the CSV against this roster. If an athlete appears in the data but not the roster, display them without number/position and log a warning.

---

## Python Dependencies

```
# requirements.txt
pandas>=2.0
pyyaml>=6.0
jinja2>=3.1
```

Keep it minimal. No web frameworks, no databases, no servers. Just data processing and template rendering.

---

## Testing Strategy

### Unit Tests (test_thresholds.py)

Test every threshold boundary. These are the cases that matter most:

```python
# Jump Height boundary tests
assert get_metric_color("jump_height", -4.9) == "green"
assert get_metric_color("jump_height", -5.0) == "green"   # edge: green boundary
assert get_metric_color("jump_height", -5.1) == "yellow"
assert get_metric_color("jump_height", -10.0) == "yellow"  # edge: yellow boundary
assert get_metric_color("jump_height", -10.1) == "red"

# Overall assignment boundary tests
assert assign_overall("green","green","green","green","green","green") == "green"
assert assign_overall("yellow","green","green","green","green","green") == "green"  # 1 outside = still green
assert assign_overall("yellow","yellow","green","green","green","green") == "yellow" # 2 yellow
assert assign_overall("red","green","green","green","green","green") == "yellow"     # 1 red
assert assign_overall("red","red","green","green","green","green") == "red"          # 2 red
assert assign_overall("yellow","yellow","yellow","green","green","green") == "red"   # 3+ at/above yellow
```

### Integration Tests (test_import.py)

- Parse a sample ForceDecks CSV and verify master data output
- Test pre/post pairing with various edge cases (missing tests, duplicate times, single test only)
- Verify the full pipeline produces valid HTML

### Sample Data

Include a `sample_forcedecks.csv` with realistic but fictional data (14 athletes, pre and post tests) so anyone can run the full pipeline without real data.

---

## Future Enhancements (Not in Scope Now)

These are noted for the roadmap but should not be built in the first version:

1. **ForceDecks API integration** - Replace CSV import with direct API pull (you already have the integration docs in the PT_Dash repo)
2. **Trend view** - Show an athlete's traffic light history across the last 2-4 weeks
3. **Automated email** - Use Python's `smtplib` or a service to auto-send the report
4. **Multi-sport support** - Extend the roster/config to handle Football, Basketball, etc.
5. **PDF export** - Add a `--pdf` flag that uses a headless browser to render the HTML to PDF
6. **Baseline normalization** - Compare against individual athlete baselines rather than universal thresholds

---

## Getting Started with Claude Code

To build this project using Claude Code, upload this document to the repository and use it as the primary specification. Suggested prompting sequence:

1. **"Set up the project structure as described in the development plan."** This creates the folders, empty files, requirements.txt, and config.yaml.

2. **"Build the import script (import_data.py) that reads ForceDecks CSVs and appends to master_data.csv."** Focus on column mapping from config, validation, and the processed-file workflow.

3. **"Build the threshold and color assignment logic in utils.py with the exact rules from the config."** This is the core engine. Get it right and tested before touching the HTML.

4. **"Write unit tests for the threshold logic covering all boundary cases."** Run these before proceeding.

5. **"Build generate_report.py and the Jinja2 HTML template to match the mockup."** Reference the mockup HTML file for the exact CSS, layout, and JavaScript.

6. **"Create sample_forcedecks.csv with 14 athletes and run the full pipeline end to end."** Verify the output HTML matches expectations.

---

## Key Design Decisions

**Why CSV instead of a database?** This tool is meant to be simple enough that any staff member can run it. A CSV file can be opened in Excel, inspected, and fixed by hand if something goes wrong. A database adds complexity without clear benefit at this scale (one team, 14-16 athletes, 2-3 sessions per week).

**Why self-contained HTML instead of a web app?** The report needs to be emailed as an attachment and opened by coaches on any device. A single HTML file works everywhere. No hosting, no logins, no permissions to manage.

**Why Jinja2 instead of string concatenation?** The HTML template is complex enough that building it with f-strings would be fragile and unreadable. Jinja2 keeps the presentation separate from the logic, which makes both easier to maintain.

**Why YAML config instead of hardcoded values?** Thresholds will change as you learn what works for this team. Column names will change when ForceDecks updates their software. Roster changes every year. Putting all of this in a config file means staff can make adjustments without opening Python files.
