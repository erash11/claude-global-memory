# CMJ Force Plate Dashboard — User Manual (V3)

> **Version:** V3 CMJ Hybrid Dashboard — 5-tab layout with SSC staging, phase composites, microcycle prescriptions, and physio flag review.

## Table of Contents

- [Part 1: For the Sport Scientist](#part-1-for-the-sport-scientist)
  - [Running the Pipeline](#running-the-pipeline)
  - [Generating the Dashboard](#generating-the-dashboard)
  - [Distributing to Staff](#distributing-to-staff)
  - [Resetting Baselines](#resetting-baselines)
  - [Roster Diagnostics](#roster-diagnostics)
  - [Troubleshooting](#troubleshooting)
- [Part 2: For the Coach — Dashboard Navigation](#part-2-for-the-coach--dashboard-navigation)
  - [Opening the Report](#opening-the-report)
  - [The Summary Stats Bar](#the-summary-stats-bar)
  - [Tab: Overview](#tab-overview)
  - [Tab: Profiles](#tab-profiles)
  - [Tab: Training Rx](#tab-training-rx)
  - [Tab: Plyo Stages](#tab-plyo-stages)
  - [Tab: Physio Flags](#tab-physio-flags)
  - [Athlete Profile (Drill-Down)](#athlete-profile-drill-down)
- [Part 3: Interpreting the Classifications](#part-3-interpreting-the-classifications)
  - [The Four-Layer Classification Cascade](#the-four-layer-classification-cascade)
  - [Performance Tiers](#performance-tiers)
  - [SSC Regime and Plyo Staging](#ssc-regime-and-plyo-staging)
  - [Archetypes](#archetypes)
  - [Phase Composites](#phase-composites)
  - [Physio Flags](#physio-flags)
- [Part 4: Best-Use Workflows](#part-4-best-use-workflows)

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

**Generate report from existing data (no new pull):**
```bash
python run_pipeline.py --report-only
```

The default start date is `2026-01-01`. All tests from the start date forward are pulled and classified.

### Generating the Dashboard

The report is a single self-contained HTML file at:
```
reports/YYYY-MM-DD_team_dashboard.html
```

It opens automatically in your browser. All CSS, JavaScript, SVG charts, and physio notes functionality are embedded inline — no internet connection or server required.

### Distributing to Staff

The dashboard is a **single HTML file** that works completely offline.

| Method | Notes |
|--------|-------|
| **Email attachment** | Coaches open in any browser. No software needed. |
| **Shared drive** | Copy to Google Drive, OneDrive, or Teams for download. |
| **Print to PDF** | Ctrl+P / Cmd+P → Save as PDF for a hard copy. |

**Physio notes** typed in the Physio Flags tab are saved to the browser's local storage on the device where they were entered. They persist across opens of the same file on the same machine. They do not transfer between devices or staff members — notes are local to the reviewer.

**Recommended cadence:** Generate and distribute after each testing session so staff have current data before practice planning.

### Resetting Baselines

Baseline trend data uses the average of each athlete's first 4 tests in the current season. Baselines never auto-update. Reset when an athlete returns from injury, completes a new training block, or when you start a new season window.

**Reset one athlete:**
```bash
python run_pipeline.py --reset-baseline <ATHLETE_ID>
```

**Reset all athletes:**
```bash
python run_pipeline.py --reset-all-baselines
```

After resetting, re-run the pipeline (`--report`) to pull fresh data and re-establish baselines.

### Roster Diagnostics

Use the `--diagnose` flag to audit who is included or excluded from the dashboard and why:

```bash
python run_pipeline.py --diagnose             # show all athletes and their inclusion status
python run_pipeline.py --diagnose "Smith"     # search by name
```

Output categories:
- **INCLUDED** — athlete has Football tag, recognized position, and maps to a normative threshold group
- **EXCLUDED (no Football tag)** — athlete exists in VALD but is not tagged as Football
- **EXCLUDED (no Position)** — athlete has Football tag but no position attribute in VALD
- **EXCLUDED (unmapped position)** — position string does not match any entry in `config/thresholds.yaml`

Use this when an athlete you expect to see does not appear in the dashboard.

### Troubleshooting

| Issue | Solution |
|-------|----------|
| Report shows no athletes | Run `python run_pipeline.py` first to pull data |
| "Establishing baseline" for all athletes | Fewer than 4 tests in the database — test more frequently or adjust `--from-date` |
| Dashboard looks stale after re-run | Hard refresh the browser (Ctrl+Shift+R) |
| API authentication fails | Verify `.env` has valid `VALD_CLIENT_ID`, `VALD_CLIENT_SECRET`, and `VALD_TEAM_ID` |
| Athlete missing from dashboard | Run `--diagnose "Name"` to find them and the reason for exclusion |
| All athletes show "Balanced" movement type | Check that Eccentric Duration and Countermovement Depth are being pulled — both must be present |
| Training Rx tab shows no microcycles | Athletes may have no `p1p2_quadrant` assigned — ensure full pipeline has run (not just `--report-only` on empty DB) |

---

## Part 2: For the Coach — Dashboard Navigation

### Opening the Report

You will receive an HTML file (e.g., `2026-03-21_team_dashboard.html`). Double-click it to open in any browser. No apps, logins, or internet connection needed.

### The Summary Stats Bar

The bar just below the tab navigation is always visible regardless of which tab you are on. It gives you a squad-wide snapshot at a glance.

| Stat | Color | What It Counts |
|------|-------|----------------|
| **Elite Conc** | Gold | Athletes in the Elite Concentric tier (top 25%, confirmed eccentric strength) |
| **Explosive ECC** | Purple | Athletes in the Explosive ECC tier (top 25%, eccentric-dominant) |
| **Balanced Ath** | Green | Athletes in the Balanced Athletic tier (middle 50%) |
| **Developmental** | Blue | Athletes in the Developmental tier (bottom 25%) |
| **Braking Lim** | Orange | Athletes with a Braking Deficit or High Risk phase status |
| **Propulsive Lim** | Orange-Red | Athletes with a Propulsive Deficit or High Risk phase status |
| **Landing Flag** | Red | Athletes with at least one physio threshold exceeded (asymmetry, PLF/BM, or JH-relative) |
| **Stage 3-5** | Cyan | Athletes cleared for Stage 3 or higher plyometric loading |

**Best use:** Compare these numbers session to session. If "Braking Lim" rises over several weeks, the training block may be accumulating eccentric fatigue. If "Stage 3-5" is low, your plyometric progressions are being capped by SSC readiness — not programming choice.

---

### Tab: Overview

The default landing tab. Shows every athlete as a card organized by position group (skill positions first, then linemen, then special teams).

#### Reading the Cards

| Element | What It Tells You |
|---------|-------------------|
| **Name** | Athlete name — click to open their full profile |
| **Status dot** (top right) | Readiness — green / yellow / orange / red |
| **Tier badge** | Performance classification (EC, EE, BA, DEV) |
| **Movement type badge** | How the athlete loads the jump |
| **Archetype badge** | Elastic / Typical / Grinder — driven by Contraction Time and movement type |
| **Power** (W/kg) | Relative power output |
| **Asym** (%) | Bilateral asymmetry — below 10% is normal; above 15% is flagged |
| **mRSI** | Modified Reactive Strength Index |
| **SSC badge** (bottom right) | Fast / Mixed / Slow SSC — indicates plyometric ceiling |
| **Stage badge** (bottom right) | Assigned plyo stage (S1–S5); red text if locked by SSC ceiling |

#### Readiness Dots

| Color | Meaning | Coaching Action |
|-------|---------|-----------------|
| Green | Within normal range of baseline | No restriction |
| Yellow | Minor deviation — monitoring recommended | No restriction; watch trend |
| Orange | Moderate concern | Reduce load; consult sport scientist |
| Red (pulsing) | Significant flag | Restrict activity; 48h clinical evaluation |

Cards with orange or red flags show a colored left border for rapid visual triage.

#### Filtering and Sorting

- **Filter chips** (ALL / EC / EE / BA / DEV) — narrow the grid to one tier
- **Search box** — type any part of a name to filter in real time
- **Sort dropdown** — reorder by Name, mRSI, Power, or Readiness (most concerning first)

---

### Tab: Profiles

A flat grid of all athletes sorted alphabetically, each card showing:

1. **Mini radar chart** — the full 6-axis percentile shape at a glance
2. **Phase composite mini-bars** — five horizontal bars showing how far above or below position median each phase is

#### Reading the Phase Composite Bars

Each bar has a center line representing the position P50. The bar extends right (gold) if above the median and left (red) if below. The delta number shows by how much, in normalized units:

- `+0.50` means the metric is halfway between P50 and P75 — above average but not elite
- `+1.00` or higher means at or above P75 — a genuine strength
- `-0.50` means halfway between P50 and P25 — a developing area
- `-1.00` or below means at or below P25 — a clear deficit

| Bar | What Phase It Reflects |
|-----|----------------------|
| **Perf** | RSI-modified — overall reactive performance output |
| **Strat** | FT:CT — movement efficiency and SSC expression |
| **ECC** | Eccentric Deceleration RFD — braking quality |
| **Brk** | Eccentric Peak Power — eccentric power output |
| **Land** | Peak Landing Force/BM — landing load (bar goes red when landing forces are high) |

**Note on Landing:** The Landing bar is inverted — a gold bar means lower landing forces (better), a red bar means higher forces (more stress on landing structures). An athlete with a large red Landing bar who also has high asymmetry is the priority physio referral.

**Best use:** Profiles tab is for position coaches or S&C staff who want to quickly scan the squad's shape across phases without opening each individual profile. Athletes with mostly left-leaning (red) bars have a consistent pattern of deficit across phases — a flag for overall load management. Athletes with one dramatically left bar and the rest centered may have a phase-specific training target.

---

### Tab: Training Rx

Two sections built from the classification output.

#### MD-3 Training Stations

Athletes are grouped into 4 training stations based on their classification tier and concentric impulse profile. These stations define the general training modality emphasis for the session 3 days out from competition:

| Station | What It Targets | Who Goes Here |
|---------|-----------------|---------------|
| **Fast ECC & light plyo** | Early-phase RFD; reactive quality | Gold/EE athletes with low P1 concentric impulse |
| **ISO & accelerated jumps** | End-range force and triple-extension finish | Athletes with low P2 impulse |
| **Short QCT & weight gain** | Reactive stiffness; brief ground contact | Balanced athletes with overall moderate concentric output |
| **Weighted plyo & weight gain** | Absolute force base; relative strength | Athletes with low bodyweight-relative output or structural development need |

**Important:** An athlete's station does not change session to session unless their underlying classification changes (i.e., when the pipeline is re-run with new data). Do not manually reassign athletes — the station is a diagnostic output, not a preference.

#### Individual Microcycle Prescriptions

Each athlete has a 4-day training card (MD-4 through MD-1) showing:

| Day | Description |
|-----|-------------|
| **MD-4** | Higher-load stimulus — primary training day (ISOs, plyos, strength work) |
| **MD-3** | Moderate load — reinforce the primary quality from MD-4 |
| **MD-2** | Light maintenance — preserve neural readiness |
| **MD-1** | Recovery — minimal mechanical load, active recovery or pool |

These are generated from the athlete's specific tier (Gold/Purple/White) and P1/P2 concentric impulse quadrant. Two athletes in the same tier will get different prescriptions if one has a P1 deficit and the other has a P2 deficit — the system personalizes to phase-specific needs.

**Best use for S&C staff:** Print or screenshot this tab the morning of MD-4. Each athlete's card tells you what their station is and what exercise selection emphasis applies for that training block. Coaches do not need to interpret classification tiers — the prescription is the output.

---

### Tab: Plyo Stages

The Wilmot Plyo Continuum assigns each athlete to a plyometric readiness stage (1–5) based on their Contraction Time. This gates which plyometric exercises are appropriate for each athlete.

#### SSC Regimes

| Regime | Contraction Time | Ceiling | What It Means |
|--------|-----------------|---------|---------------|
| **Fast SSC** | < 150ms | Stage 5 | Athlete can express elastic energy quickly — full plyometric spectrum is appropriate |
| **Mixed SSC** | 150–250ms | Stage 3 | Moderate reactive capacity — Stage 4–5 exercises are premature |
| **Slow SSC** | > 250ms | Stage 2 | Reliant on force production with limited elastic return — advanced plyos carry injury risk |

**The Wilmot Continuum** defines progression by stage:

| Stage | Plyometric Type | Example Exercises |
|-------|----------------|-------------------|
| 1 | Sub-maximal bilateral jumping | Box step-offs, bilateral squat jumps |
| 2 | Moderate bilateral reactive | Box jumps, countermovement jumps |
| 3 | Loaded or complex reactive | Loaded CMJ, altitude drops |
| 4 | High-demand reactive | Depth jumps, short QCT bounding |
| 5 | Maximal reactive / SSC | Reactive bounding, sprinting mechanics |

#### Reading the Plyo Stages Tab

Athletes are grouped by SSC regime. Within each regime, they are listed by stage from highest to lowest.

- **Athletes with a lock icon** (🔒) have an assigned stage that is at or above their SSC ceiling. They are not ready to train at that stage safely. Their CT needs to decrease before advancing.
- The CT value shown in milliseconds is the raw measure from the most recent test.
- Clicking any athlete pill opens their full profile.

**Why this matters:** Stages 4–5 require fast SSC infrastructure (CT < 150ms) to execute safely and productively. Pushing athletes through advanced plyos when their CT indicates Slow SSC is a mismatch — not a progression. It results in compensation patterns, not adaptation.

**Best use for S&C staff:** Use this tab at the start of a training block to set the plyometric ceiling for each athlete. Revisit when new data is available. As Contraction Time decreases through training, athletes unlock higher stages.

---

### Tab: Physio Flags

Shows only athletes who exceeded at least one landing threshold. Intended for the medical or physio staff to review before high-load sessions.

#### Flagged Thresholds

| Flag | What It Means |
|------|--------------|
| **PLF/BM > threshold** | Peak Landing Force relative to body mass exceeds the position-specific flag value — high landing load, risk of lower-limb stress |
| **JH-rel PLF > threshold** | Jump-height-relative peak landing force exceeds threshold — the athlete is generating a high force relative to how high they jumped, suggesting poor landing mechanics or stiffness |
| **Asym > threshold** | Bilateral asymmetry in braking impulse exceeds the caution level (10%) or flag level (15%) |

An athlete appears on this tab if **any** of these values are exceeded. Athletes with multiple exceeded thresholds are the highest priority.

#### Physio Notes

Each flagged athlete has a text box for physio notes. Click the box and type directly. Notes save automatically when you click away (saved to the browser's local storage on your device). When you reopen the same HTML file on the same device, your notes will reload.

**Use this to:** Record clinical observations, clearance decisions, or follow-up instructions. Because the file is distributed, the sport scientist should collect physio notes from the reviewing clinician and incorporate them into the next report cycle if needed.

---

### Athlete Profile (Drill-Down)

Click any athlete from any tab to open their full profile. Click **Back** to return to the tab you came from.

#### Profile Header

The header badges tell you the full classification picture at a glance:

| Badge | What It Tells You |
|-------|-------------------|
| **Tier** (EC / EE / BA / DEV) | Performance classification |
| **Archetype** (Elastic / Typical / Grinder) | How this athlete's reactive capacity and movement organization combines |
| **Movement type** | Countermovement pattern |
| **SSC regime** | Reactive readiness category |
| **Stage** | Assigned plyo stage; shows lock icon if capped by CT |

#### Plyo / SSC Info Bar

Below the flag banner is a quick-reference row showing SSC regime, raw CT in ms, plyo stage, training station assignment, and archetype side by side. This is designed for quick verbal confirmation during group planning sessions.

#### Prescription Panel

The training prescription is surfaced at the top of the profile (action-first layout). It is generated from the athlete's tier (Gold/Purple/White) and their P1/P2 concentric impulse quadrant. Read it as the **priority training direction** for this athlete — not a full program, but the directional emphasis that should shape exercise selection.

#### Radar Chart

The hexagonal chart overlays three data layers:

| Line | Color | What It Represents |
|------|-------|--------------------|
| **Athlete** | Gold (solid) | This athlete's current values |
| **Team Avg** | Orange (dashed) | Mean of all teammates at the same position |
| **NFL P50** | White (dashed) | NFL 50th percentile for this position |

The further a vertex extends from center, the better the athlete performs on that metric relative to their positional norms. A large, round shape indicates well-rounded high performance. A spiky shape indicates imbalance.

#### Trend vs Baseline

Five key metrics compared to the athlete's baseline (average of their first 4 tests this season):

- **Green arrow up** — metric improved
- **Red arrow down** — metric declined
- **Dash** — no baseline yet

"Establishing baseline (N/4)" means fewer than 4 tests have been recorded. Trends before 4 tests are directional only — not statistically robust.

**Coaching action:** Declining trends in power or RSI-modified over consecutive tests suggest accumulated fatigue. A single decline is not alarming; a consistent downward pattern is.

#### Phase Profile

Breaks down the jump into three phases:

| Phase | What It Reveals |
|-------|-----------------|
| **Braking** | Eccentric absorption quality — how well the athlete decelerates and stores elastic energy |
| **Propulsive** | Concentric force production — how effectively they drive off the ground |
| **Landing** | Impact management — how much force they experience on the way down |

Status badges: **Strong** (≥P75) / **Monitor** (P25–P75) / **Deficit** (<P25) / **High Risk** (<P10 estimate)

A Braking Deficit combined with a slow SSC regime means the athlete cannot effectively use the stretch-shortening cycle AND cannot produce the braking force to compensate — this is the highest risk profile for lower-limb injury.

#### Movement Strategy

Classifies how the athlete organizes the countermovement using eccentric duration and depth:

| Type | Duration | Depth | Profile |
|------|----------|-------|---------|
| **Fast-Deep** | < 450ms | > 38cm | Elastic, spring-like — thrives on reactive plyos |
| **Balanced** | Moderate | Moderate | Versatile — responds to mixed stimuli |
| **Slow-Deep** | > 600ms | Any | Force-dominant, lower elastic return — benefits from RFD work |
| **Slow-Shallow** | > 600ms | < 30cm | Low stiffness, strength-dominant — needs both depth work and speed |
| **Unknown** | — | — | Metric missing — check VALD test quality |

The raw Contraction Time is also shown here (in ms) alongside eccentric duration and CM depth. CT reflects the total time from unweighting to takeoff and is the basis for SSC regime classification.

#### Key Metrics Panel

Ten performance metrics with values and units. Compare across athletes at the same position for relative context. Metrics highlighted in gold are the outputs — the "what happened." The phase profile and movement strategy tell you "how" and "why."

#### Strengths and Weaknesses

Auto-generated from positional thresholds:
- **Strength** (green pill) — metric ≥ P75 for position
- **Weakness** (red pill) — metric < P25 for position

These are the clearest targets for individualized training emphasis and the strongest arguments for a specific prescription direction.

---

## Part 3: Interpreting the Classifications

### The Four-Layer Classification Cascade

The system applies four sequential diagnostic layers. Each layer gates the next. The prescription only emerges from the full cascade — never from a single metric in isolation.

| Layer | Question | Primary Metric |
|-------|----------|---------------|
| **L1** | What type of athlete are they? | mRSI (force-dominant vs. elastic) |
| **L2** | What's their movement strategy? | FT:CT, RSI-mod, Eccentric Peak Velocity, CM Depth |
| **L3** | Where is the limiting phase? | Braking side (ECC absorption) vs. propulsive side (CON force/velocity) |
| **L4** | Any landing flags? | Asymmetry screen + Peak Landing Force |

This sequence reflects the coaching hierarchy: you cannot prescribe effectively without first knowing the athlete's capacity, then their strategy, then their specific limiter. An athlete with excellent mRSI but a braking deficit and high landing asymmetry is a completely different prescription than an athlete with identical mRSI and no phase deficits.

### Performance Tiers

| Tier | Badge | Threshold | Eccentric Condition |
|------|-------|-----------|---------------------|
| **Elite Concentric** | EC | mRSI ≥ P75 | EPF/BM ≥ 2.5× AND Eccentric Peak Power ≥ P75 |
| **Explosive ECC** | EE | mRSI ≥ P75 | Strong eccentric qualities but gold_confirm criteria not fully met |
| **Balanced Athletic** | BA | mRSI P25–P75 | Any eccentric profile |
| **Developmental** | DEV | mRSI < P25 | Any eccentric profile |

Note: A gold (top 25%) athlete who has EPF/BM < 2.0× is **downgraded** to Explosive ECC. The eccentric screen acts as a quality gate — raw reactive output without eccentric strength backing is a vulnerability, not a strength.

### SSC Regime and Plyo Staging

Contraction Time (CT) is the primary gate for plyometric prescription. It measures total time from unweighting through takeoff — shorter CT indicates faster SSC utilization.

**Why CT matters:** Stage 4–5 exercises (depth jumps, reactive bounding) require the athlete to absorb and redirect force in < 150ms. If their CT is 270ms, the mechanical demand of those exercises exceeds their current capacity. The result is compensation at the hip and trunk, not adaptation at the knee and ankle.

Stage assignments integrate three factors:
1. **SSC ceiling** (from CT) — hard upper limit
2. **Classification tier** (mRSI/eccentric) — how close to the ceiling to assign
3. **CI quartile** (P1/P2 concentric impulse) — incremental bump within the ceiling for Q3+ athletes

An athlete with Fast SSC + Gold tier + Q3 CI may reach Stage 5. An athlete with Slow SSC + Gold tier is capped at Stage 2 regardless of mRSI — their CT is the bottleneck.

### Archetypes

| Archetype | SSC Regime | Movement Type | What It Means |
|-----------|-----------|---------------|---------------|
| **Elastic** | Fast SSC | Fast-Deep | True reactive athlete — benefits most from reactive plyometrics and speed-strength work |
| **Grinder** | Slow SSC or any | Slow-Shallow or Slow-Deep | Force-dominant, lower elastic return — benefits from maximal strength, loaded eccentrics |
| **Typical** | Mixed SSC or any | Balanced or unknown | Versatile — can respond to both strength and reactive stimuli |

The archetype is a shorthand label for conversations with positional coaches. "This lineman is a Grinder — his plyometric ceiling is Stage 2 until his CT comes down" is a more useful communication than sharing raw metric values.

### Phase Composites

The delta values on the Profiles tab are normalized z-scores relative to position P50:

```
delta = (value - P50) / (P75 - P25)
```

A delta of +1.0 means the athlete is one inter-quartile range above the median — well into the elite range. A delta of -1.5 means 1.5 IQRs below the median — a significant deficit.

The Landing composite is **inverted**: positive (gold) means lower landing forces, which is better. Red on the Landing bar means elevated forces — a flag, not a weakness to train through.

**Interpreting composite patterns:**

| Pattern | Interpretation |
|---------|---------------|
| All positive | Elite, well-rounded athlete — maintain and monitor |
| Perf + Strat positive, ECC + Brk negative | Good output, poor braking quality — injury risk if training is reactive-dominant |
| ECC positive, Perf negative | Strong eccentric but limited reactive conversion — movement strategy or stiffness issue |
| Land negative (red), Asym elevated | Priority physio referral — do not increase plyometric volume |
| All negative | Foundational capacity issue — structural loading before phase-specific work |

### Physio Flags

Thresholds for the Physio Flags tab are position-specific and derived from NFL normative data:

| Metric | Typical Flag Level | Why It Matters |
|--------|--------------------|----------------|
| **PLF/BM** | ~42–52 N/kg (varies by position) | High peak landing force relative to body mass indicates the athlete is absorbing more impact than their positional peers — risk of lower-limb stress accumulation |
| **JH-relative PLF** | ~98–110 (varies) | Landing force proportional to jump height — if this is high, the athlete is absorbing disproportionate force relative to the energy they generated going up |
| **Asymmetry** | Caution: >10%, Flag: >15% | Bilateral braking impulse imbalance — left/right discrepancy in how force is absorbed |

An athlete can be flagged by PLF/BM without having high asymmetry. Both flags can coexist. Landing force flags warrant physio review before progressing plyometric loading; they do not automatically restrict all training.

---

## Part 4: Best-Use Workflows

### Pre-Practice Check (5 minutes)

1. Open the dashboard — check the **Summary Stats Bar** first
   - Any increase in Landing Flag count from last session? → Physio Flags tab before practice
   - Braking Lim count elevated? → Reduce eccentric loading volume today
2. **Overview tab** → sort by Readiness → address any orange/red dots
3. **Physio Flags tab** → confirm any flagged athletes are cleared or restricted

### Weekly S&C Programming

1. **Training Rx tab** → MD-3 station groups tell you who goes where for the training session
2. Use individual microcycle cards (MD-4 → MD-1) as exercise selection guidance — these update automatically when new test data is ingested
3. If a station group is unexpectedly large or small, check the **Overview tab** to confirm classifications are current

### Plyometric Block Planning

1. **Plyo Stages tab** → note each athlete's stage and regime before designing a plyometric block
2. Athletes in the Slow SSC group (CT > 250ms) — Stage 1–2 only; build SSC capacity before progressing
3. Athletes with a lock icon have a CT-limited ceiling — the prescription can be at that stage level but not above
4. Re-test CT after 4–6 weeks of SSC-specific work and regenerate the report to reassess stage assignments

### Individual Athlete Deep-Dive

1. Click the athlete card from any tab to open their **Profile**
2. Start at the top: tier + archetype + SSC badge → sets the context for everything below
3. Check the **Plyo info bar**: is their stage appropriate for the current block?
4. Read the **Prescription panel** — this is the priority direction, not the full program
5. Review the **Radar** for positional context — where do they fall relative to NFL P50?
6. Check **Trend vs Baseline** — are key metrics moving in the right direction over the season?
7. Review **Phase Profile** — identify the limiting phase
8. Cross-reference **Movement Strategy** with phase profile: a Slow-Deep athlete with a Braking Deficit needs eccentric loading, not more reactive work

### Post-Season Review

1. Run `python run_pipeline.py --report` after the final testing session
2. Export the HTML for archival — it captures the full season's final state
3. Use **Profiles tab** to compare all athletes' composite bar patterns at season end vs. the start — athletes who have shifted from red-dominant to gold-dominant bars made meaningful neuromuscular gains
4. Use **Plyo Stages tab** to assess how many athletes advanced SSC regime across the season — this is a leading indicator of reactive capacity development
5. Use **Physio Flags** history to inform the medical staff's off-season priority list

### Communication to Coaching Staff

| Audience | Best Tab | Key Talking Points |
|----------|----------|--------------------|
| Head Coach | Overview | Tier distribution, readiness flags, who is restricted |
| Position Coach | Overview (filtered by position) | Archetypes, stage badges, movement types |
| S&C Coordinator | Training Rx | Station assignments, microcycle prescriptions |
| Medical Staff | Physio Flags | Exceeded thresholds, physio notes, flag counts |
| Analyst / Sport Scientist | Profiles | Composite bars, radar shapes, trend deltas |
