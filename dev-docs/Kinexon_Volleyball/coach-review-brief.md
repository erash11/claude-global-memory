# Kinexon dashboard prototype — review brief

> **SUPERSEDED — historical record, do not hand this to a coach.**
>
> This brief did its job: it asked the questions, and the answers below became the
> product. It is kept because the reasoning is why the build is what it is, but it
> now describes things that are no longer true.
>
> Three points in particular would mislead anyone reading it today:
>
> - **Question 4 is answered.** "Above your own average" reads as **risk**, and the
>   colours flipped accordingly. This brief still describes it as blue and neutral.
> - **Acute:chronic is gone**, along with the 1.5 / 0.8 thresholds in question 3. It
>   needs about four weeks of history; the block it would have run on is three days.
> - **Variant B won** and became the session debrief. Variants A and C are not built.
>
> For the current coach-facing document, see **`docs/coach-report-explainer.md`**.

**For:** Performance coach, Baylor Volleyball
**Purpose:** Pick a direction before we build anything real.
**Time needed:** ~10 minutes.

---

## What this is

Three **different** answers to "what should the Kinexon dashboard look like?", built as one
page you can flip between. It is a design mock, not a working tool.

**The numbers are fake.** They're synthetic data shaped like a real KINEXON PERFORM export
(jump count, jump height, jump load, landing load, accels, court time) for a made-up
14-athlete roster. No real athlete appears anywhere. Don't read anything into the values —
react to the *layout, the questions being asked, and the language*.

## How to open it

Open `dashboards/PROTOTYPE_coach-dashboard.html` in a browser. Flip variants with the
**← →** arrow keys or the black bar at the bottom. The bar is prototype scaffolding, not
part of any design.

Also on the page: a position filter, a **Table view** button (same numbers as text), and a
**Dark** toggle.

---

## The three variants

### A — Triage list · "Who needs attention before tomorrow's session?"
A ranked list, worst first. Each athlete gets a status, their acute:chronic jump ratio, a
28-day trend line, and one plain-English sentence about what's going on. Click a row to
expand.

*Built for:* a 30-second check before you walk into the gym.

### B — Session debrief · "What happened at yesterday's session?"
One session at a time. Big total up top, then every athlete measured against **their own**
normal for that session type, then where the jumps came from (position) and when in the
session they landed.

*Built for:* the post-practice conversation, and for showing a specific athlete their day.

### C — Squad matrix · "How is the whole squad tracking over six weeks?"
Every athlete × every week as a colour grid, with flagged athletes in a side rail. Dense.

*Built for:* Monday planning, spotting a heavy week before it happens.

---

## What I need from you

Please react to these five things specifically — the answers determine what gets built:

1. **Which variant do you actually open first on a normal Tuesday?** It's fine (and common)
   to want A's list with C's six-week grid underneath. Mixing is a valid answer.

2. **Are these the right questions?** Each variant is organized around one question. If the
   question you actually ask in-season is a different one, that's the most useful thing you
   can tell me.

3. **Are the thresholds right?** I used acute:chronic on jump count — over **1.5** = spike,
   under **0.8** = under-loaded — because it's a common default, not because it's right for
   volleyball or for us. Tell me the numbers you'd defend, or tell me this is the wrong
   metric entirely.

4. **What does "above your own average" mean to you?** In variant B, working above your own
   norm is coloured blue (neutral/positive). If you'd read that as a *risk* signal instead,
   the colours should flip. This one genuinely changes the design.

5. **What's missing?** Landing/impact load, movement density, accel/decel, and court time
   are all in the data but barely shown. If one of those is what you actually manage to,
   it should be on the front page instead of jump count.

## What happens next

Once you pick a direction, the real build is: Kinexon export → local database → this
dashboard, refreshed automatically. We're still waiting on API credentials from Kinexon;
a manual CSV export of one session is enough to start the real ingestion path.

---

*Questions: Applied Performance.*
