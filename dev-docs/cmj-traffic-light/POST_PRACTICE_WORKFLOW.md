# CMJ Traffic Light - Post-Practice Report Workflow
**Baylor Volleyball | Applied Performance**

---

## Overview

After practice, the full pipeline now runs with a single double-click:

1. Export two CSV files from VALD (pre-practice and post-practice)
2. Copy them into the `data/imports/` folder
3. Double-click `run_report.bat`

The script imports the data, generates the report, and opens it automatically in your browser. **Total time: under 2 minutes.**

---

## Step 1 - Export from VALD (twice)

You need **two separate CSV exports** — one for the pre-practice session and one for the post-practice session.

In VALD ForceDecks:
1. Filter to today's date + pre-practice tests → click **Export** → save as a CSV file
2. Filter to today's date + post-practice tests → click **Export** → save as a CSV file

You will end up with two `.csv` files. Name them whatever you like.

---

## Step 2 - Copy the CSV files into the imports folder

Open **File Explorer** and navigate to:

```
OneDrive - Baylor University
  └── 00_Primary_Storage_Drive
      └── 03_SPORTS_PROGRAMS
          └── Volleyball
              └── cmj-traffic-light
                  └── data
                      └── imports   <- PUT BOTH FILES HERE
```

Copy and paste both CSV files into the `imports` folder.

---

## Step 3 - Double-click run_report.bat

Navigate to the `cmj-traffic-light` folder in File Explorer and double-click:

```
run_report.bat
```

A black terminal window will open and you will see the pipeline running:

```
============================================================
  CMJ Fatigue Traffic Light - Pipeline
  Date: 2026-03-03  |  Session: Post-Practice Assessment
============================================================

[1/2] Importing CSV files...
  Processing: pre-practice-03-03-2026.csv
    OK: 15 CMJ rows appended
    Moved to imports/processed/

  Processing: post-practice-03-03-2026.csv
    OK: 15 CMJ rows appended
    Moved to imports/processed/

Import complete. 30 rows added to master_data.csv.

[2/2] Generating report for 2026-03-03...
Found 30 CMJ rows. Pairing pre/post tests...
  Paired:   15 athletes
  Unpaired: 0 athletes

Report saved: ...\output\report_2026-03-03.html
  Green: 9  Yellow: 4  Red: 2

============================================================
  Done. Opening report in browser...
============================================================

Press any key to continue . . .
```

The report will open automatically in your browser. Press any key to close the terminal window.

---

## Advanced Options

You can pass optional flags to the script by running it from a terminal instead of double-clicking:

```
# Override the session label in the report header
python scripts/run_pipeline.py --session "Pre-Practice Assessment"

# Generate a report for a past date (skips import step if no new CSVs)
python scripts/run_pipeline.py --date 2026-03-02
```

---

## Troubleshooting

| What you see | What it means | What to do |
|---|---|---|
| "No new CSV files found" | The imports folder is empty | Make sure both CSVs are in `data/imports/` (not a subfolder) |
| `Unpaired: 2 athletes` | Those athletes are missing a pre or post test | They appear at the bottom of the report. Check for absent athletes or check VALD tags. |
| "Email authentication failed" | Password in email_config.yaml is wrong | Re-generate your App Password at mysignins.microsoft.com |
| `ERROR` during import | Something wrong with the CSV file | Screenshot the window and contact Eric Rawls |
| Terminal says "python is not recognized" | Python is not installed or configured | Contact Eric Rawls |
| Report opens as a blank white page | Browser issue | Right-click the file → Open with → Google Chrome or Edge |

---

## Manual Fallback

If the automated script has issues, you can still run the two steps manually. Open the VS Code terminal in the `cmj-traffic-light` folder and run:

```
python scripts/import_data.py
python scripts/generate_report.py --date YYYY-MM-DD
```

Replace `YYYY-MM-DD` with today's date (example: `2026-03-03`).

---

*Questions or issues? Contact Eric Rawls, Director of Applied Performance.*
