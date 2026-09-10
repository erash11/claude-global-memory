# V2 Scope — S2 Cognition

**Status:** proposed, not started. V1 shipped 2026-08-11 (null finding, OL room).
**Read first:** `CONTEXT.md` (glossary) and `docs/adr/0001`–`0013`. V2 inherits
every one of them.

---

## Settled in V1 — do not relitigate

Profile Unevenness gates, Room Deviation delivers (0003). Spread computed in
z-space (0004). Per-category deviation, not Mahalanobis (0006). Flag, don't
filter, on selection attributes (0005, 0011). Vendor-invalidated reports
excluded and surfaced for retest (0012).

**The standing rule from 0013:** any threshold whose statistic is a maximum or
range across several measures must be calibrated against a null *before* use.
This bit the project twice. It is not optional in V2.

---

## Five facts that reshape the design

1. **Pooling is valid — verified, not assumed.** If S2 normed within position,
   every room would sit near the 50th percentile. They do not: room composite
   means run from the 42nd (OL) to the 82nd (P/K), team mean 59th. The reference
   group is common across positions, so all athletes share one scale.

2. **Room-by-room does not scale.** Only 3 of 12 rooms clear the n>=10 floor
   (OL 15, WR 13, ILB 10). The other nine hold 5–9 athletes. Twelve rooms times
   nine categories is 108 comparisons — the same trap, larger.

3. **Zero athletes have a second test**, across all 99 reports. Test-retest
   reliability cannot be estimated from this dataset at any n.

4. **The speed/accuracy secondary measures were never used.** They extract
   cleanly from 96 of 99 reports and are arguably more coachable than the nine
   categories: "fast but inaccurate under pressure" is a sentence a position
   coach can act on.

5. **Punters and kickers run a reduced battery.** Three P/K-template reports
   yield 7 values with zero N/A — a structurally different category set, not a
   parse failure. They cannot join a nine-category pooled model.

---

## Three tracks

### Track A — Pooled, position-adjusted analysis  *(unblocked)*

Model each athlete's expected profile from position across all ~92 comparable
athletes, then examine residuals. Two gains over V1: position offsets and
residual spread are estimated from ~92 athletes rather than from a room mean
built on 8–15, and the nine small rooms become analysable instead of excluded.

Add the speed/accuracy measures as a tenth and eleventh dimension.

**Honest expected value.** V1 found the OL room *less* extreme than chance, so
this will probably return nulls too. That is still worth having: a defensible
"all 92 athletes were checked with a calibrated method and no one is an outlier"
closes the question permanently instead of leaving it to be re-asked every
testing cycle. It is cheap now that the machinery exists.

### Track B — Individual reliable-change profiles  *(blocked)*

The analysis that actually delivers the original goal: individualised coaching
cues. Not "is he unusual" but "is his improvisation *reliably* above his decision
complexity" — a within-athlete statement needing no comparison to anyone.

**Blocked on the standard error of measurement.** V1 established that a ~3 SD
range across nine categories arises by chance, so without SEM an athlete's peak
category is indistinguishable from a good day. Building this without reliability
would repeat exactly the error V1 caught.

### Track C — Is the position gradient real?  *(blocked)*

The 42nd-to-82nd spread runs skill-positions-high, big-men-low. That is far more
likely a property of measuring visual and decision speed against an all-comers
norm than a fact about Baylor. Separating the two needs S2's positional norms.

---

## Recommendation: the next action is an email, not an analysis

Both blocked tracks unblock from one request to S2:

1. **Test-retest reliability / SEM for each of the nine categories** (and the
   secondary measures), so within-athlete differences can be given a
   reliable-change threshold.
2. **Positional normative data** — do offensive linemen score lower than
   defensive backs in their reference population generally?
3. Confirmation of what the P/K battery measures and why it differs.
4. Whether the normative database was revised between 2022 and 2026 — five
   athletes tested before this year, and a quietly revised norm would put their
   percentiles on a different scale.

Item 4 matters regardless of which track runs, and V1 could not check it.

If S2 will not supply reliability, retesting 12–15 athletes yields an in-house
estimate and is the cheaper path to Track B.

---

## Decisions needed before V2 starts

- **Run Track A now, or wait for the S2 reply and do A and B together?**
  Recommendation: send the email today, start Track A while waiting. A is
  self-contained and its machinery is reused by B.
- **Does a null Track A result get published like V1's?** Recommendation: yes,
  same pre-commitment, same reasoning.
- **Include P/K on the reduced battery as a separate small analysis, or drop
  them from V2?** Recommendation: drop from the pooled model, note the exclusion.

## Carried forward unchanged

Shape only, no prescription (0002) until a coach is in the room. Sports science
internal remains tier 1. Any new threshold is null-calibrated and committed
before the data is touched. Athlete-level data stays out of version control and
off any published page.
