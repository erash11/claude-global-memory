# Handoff — 2026-09-02 — scroll-craft install + first build

Plain markdown. Any harness (Codex, Antigravity, fresh Claude) should be able to
resume from this without the original session.

---

## What this session did

Three things, in order:

1. Installed the third-party **scroll-craft** skill across Claude Code, Codex and
   (packaged for) Claude Cowork.
2. Watched a 16-minute video that is the same author's method for using it, and
   distilled it into redesign notes for Eric's personal site.
3. Ran scroll-craft for real and produced **build #1**, a standalone site.

---

## 1. scroll-craft install

Source: <https://github.com/nateherkai/scroll-craft> (MIT, plugin `nateherk-design`).

Installed with the machine's existing `skills` CLI, which is what owns
`~/.agents/skills/` and `~/.agents/.skill-lock.json`:

```bash
npx -y skills@latest add nateherkai/scroll-craft -g -a claude-code -a codex -s scroll-craft -y
```

**Gotcha:** the `-a` flag rejects a comma-separated list. `-a claude-code,codex`
errors with "Invalid agents" even though both names are valid. Repeat the flag.

Where it landed:

| Path | What |
|---|---|
| `~/.agents/skills/scroll-craft/` | the real files (canonical vendor store) |
| `~/.claude/skills/scroll-craft` | symlink, made by the installer |
| `~/.codex/skills/scroll-craft` | symlink, **made by hand** — the installer reported "universal: Codex" and created nothing |
| `~/Downloads/scroll-craft.zip` | Cowork upload package |

**Cowork is not installed.** Cowork's skills carry server-minted ids
(`skill_01…`) in
`~/Library/Application Support/Claude/local-agent-mode-sessions/skills-plugin/.../manifest.json`,
so a folder dropped in locally is not registered and would be wiped on the next
sync. The only route is uploading the zip via claude.ai → Settings →
Capabilities → Skills. **This is still open — Eric has not done it.**
Expect the design procedure to work in Cowork but not the ffmpeg/Chrome
verification pass.

**Mac readiness:** `node ~/.agents/skills/scroll-craft/scripts/doctor.mjs` passes.
Node 26.6, full ffmpeg (490 filters), Chrome found. Optional gaps: no
`KIE_AI_API_KEY`, no libwebp encoder (posters fall back to JPEG). The README
claims the skill has only ever run on Windows; it runs on this Mac.

**Workspace:** resolves to `~/DEV/Website/scrollcraft` via the nearest `.git`
(which is `~/DEV/Website`). Registry at
`~/DEV/Website/scrollcraft/FINGERPRINTS.md`. Run scroll-craft from inside
`~/DEV/Website/...` or set `SCROLLCRAFT_HOME`, otherwise builds land wherever
cwd happens to be, including inside the skill directory.

---

## 2. The `/watch` skill was broken, and is now patched

`/watch` returned **0 frames with no useful error**. Cause: `frames.py` passes
ffmpeg `-vsync`, which ffmpeg removed. This machine runs ffmpeg 9.0.1.

Fixed by hand in the two live copies (`-vsync` → `-fps_mode`, lines 256 and 615):

- `~/.agents/skills/watch/scripts/frames.py`
- `~/.claude/plugins/cache/claude-video/watch/0.2.0/skills/watch/scripts/frames.py`

Verified after the fix: scene path 8 frames, keyframe path 8 frames, 0 errors.

**This fix is temporary.** Upstream `bradautomates/claude-video` still has
`-vsync` (last commit 2026-06-30), so `skills update watch` or a plugin update
reinstalls the bug. The Cowork copy at
`…/skills-plugin/.../skills/watch/scripts/frames.py` was deliberately **not**
patched: it is server-synced and would revert.

Open, not done: offering an upstream PR. Eric was asked and has not answered.

---

## 3. Design notes from the video

`~/DEV/Website/personal/DESIGN-IDEAS.md` — distilled from
<https://youtu.be/FFWtxjvW2ts> (Nate Herk, "Fable 5.1 FINALLY Kills AI Website
Slop", 16:13). Same author as the skill; the video is the method, the skill is
the method in code.

The load-bearing points: you cannot ask a model for "premium", you must hand it
a **named element from a named reference**; his seven rules; four inspiration
sources (21st.dev, godly.design, Awwwards, motion-sites).

**The finding that matters most for Eric:** his live site
(`~/DEV/Website/personal/index.html`, published as a Claude Artifact) **cannot
run scroll-craft**. `BRIEF-V3.md` forbids external resources, libraries and
anything parked at `opacity: 0`; scroll-craft needs an engine JS/CSS pair,
external video, and scroll-assembled text. Section 6 of DESIGN-IDEAS.md lays
out the two ways forward. Eric chose **build standalone, leave the Artifact
alone** — which is what build #1 is.

Also corrected in that file: an earlier draft wrongly claimed his hero "leads
with role, not pain". It does not. It leads with *"Most performance problems are
not data problems. They are question problems."* and he already has a
scroll-driven jump-trace scrub. Two of the video's seven rules were already
satisfied before this session started.

---

## 4. Build #1 — `~/DEV/Website/scrollcraft/builds/eric-rash/`

Serve it:

```bash
cd ~/DEV/Website/scrollcraft/builds/eric-rash
node ~/.agents/skills/scroll-craft/scripts/serve.mjs --root . --port 4500
```

**Interview answers (his, in-session):** standalone build, distinct scenes,
premium-minimal, no assets and no kie.ai spend, peak = "the question reframe",
CTA = email. Three of the eight answers were **self-authored** from
`BRIEF-V3.md` because he was working at low capacity; they are flagged inline in
the build's `BRIEF.md` and the skill permits this fallback.

**Grammar: split stage.** Chosen because his thesis is literally a two-column
sentence, and the grammar's mandated close (the collapse) *is* the peak he
picked independently. Full reasoning for why the other seven lost is in
`builds/eric-rash/BRIEF.md`.

**Signature move:** the divider between the columns is a live **countermovement
jump force-time curve** in Canvas, full page height, advancing with scroll,
flattening and fading at the close so the last accent on the page is the rule
under his email address. Drawn from the real CMJ phase shape (quiet stance,
unweighting dip, braking rise, propulsion, flight, landing spike) — not a
decorative wiggle, and no numeric value is printed or attributed anywhere.

**Data-handling constraint honoured:** the "data wall" is metric *names* only.
No athlete named, no value attributed, no `count` device anywhere, because none
of those numbers would be real. `~/DEV/PERFORMANCE.md` marks athlete data as
handling-care material.

**The engine was never edited.** `scrollcraft.js` and `scrollcraft.css` in the
build folder are byte-identical to the skill's copies. All bespoke behaviour is
page-level JS driven off `--sc-p`.

### Verification

Three passes, all green after fixes (`lab/shots4`, `lab/mobile4` at 390×844,
`lab/reduced4`): 9.3 viewport-heights, no dead scroll, every cue clears 4.5:1.
Keyboard focus reaches both links, neither parked at opacity 0. Heading order is
clean.

**Two defects the harness passed and reading the frames caught:**

1. The trace was a hairline on desktop — one pixel constant cannot serve a
   1800px vertical axis and a 780px horizontal one. Amplitude is now
   proportional to the axis.
2. **Reduced motion rendered the page collapsed from the first frame**, clipping
   the hero inside an 8vw column. The harness passed it because it grades cues
   and contrast, not layout. Reduced motion now holds the readable 50/50 split.

**Mobile is an authored decision, not a documented one.** Neither `devices.md`
nor `taste.md` has a mobile recipe for split stage. Below 760px the split
rotates to horizontal (data on top, question beneath, trace drawn left to
right); the collapse travels upward instead of leftward. Written up in the
build's BRIEF.md.

**Not verified: a real phone.** All mobile results are headless Chrome. There is
no video in this build so the usual iOS clip traps do not apply, but the rotated
split should be looked at on a handset before this is shown to anyone.

---

## Every file created or modified this session

**Committed to `~/DEV/Website` (this repo, local only — not pushed):**

- `.gitignore` — new. Ignores `node_modules/` and `lab/`; the lab screenshots
  had reached 339MB across 292 PNGs and must never enter git.
- `personal/DESIGN-IDEAS.md` — new, the video notes.

**Deliberately left untracked:** `personal/index.html` and `personal/BRIEF*.md`
were already untracked before this session and were not modified by it. They
were staged and then unstaged rather than swept into git as a side effect of
this closeout — that is Eric's call to make, not a byproduct. See the open
question below.
- `scrollcraft/FINGERPRINTS.md` — new registry, seeded plus the build #1 row.
- `scrollcraft/builds/eric-rash/{BRIEF.md,index.html,scrollcraft.js,scrollcraft.css,package.json,package-lock.json}`
- `docs/handoffs/2026-09-02-scroll-craft-eric-rash.md` — this file.

**Outside any repo:**

- `~/DEV/PERSONAL.md` — router line for `Website/` updated to name the new briefs
  and DESIGN-IDEAS.md.
- `~/.agents/skills/scroll-craft/` — installed.
- `~/.agents/.skill-lock.json` — installer added the scroll-craft entry.
- `~/.claude/skills/scroll-craft`, `~/.codex/skills/scroll-craft` — symlinks.
- `~/.agents/skills/watch/scripts/frames.py` — `-vsync` → `-fps_mode`.
- `~/.claude/plugins/cache/claude-video/watch/0.2.0/skills/watch/scripts/frames.py` — same.
- `~/Downloads/scroll-craft.zip` — Cowork upload package.
- `~/DEV/Website/scrollcraft/builds/eric-rash/lab/` — 292 verification PNGs,
  gitignored, reproducible with the Step 5 commands in the build's BRIEF.md.

---

## Next actions, most important first

1. **Look at build #1 on a real phone.** It is the one thing the verification
   could not cover.
2. **Decide: keep build #1 local, or host it.** Eric's site is currently an
   Artifact and stays that way either way. Recommendation given: leave it local,
   look again with fresh eyes before committing to a direction.
3. **Upload `~/Downloads/scroll-craft.zip` to Cowork** if Cowork parity is still
   wanted. One manual step, claude.ai → Settings → Capabilities → Skills.
4. **Push `~/DEV/Website`** to `origin` (`erash11/AppliedPerformance-Site`) if
   the personal site and the scroll-craft build should be on GitHub. Not pushed
   this session — the repo is not KeystoneOS, so it needs explicit approval, and
   note this commit publishes `personal/index.html` for the first time.
5. **Consider an upstream PR** for the `/watch` `-vsync` fix, else it returns on
   the next update.

## Open questions

- Does Eric want the personal site source on GitHub at all? It has never been
  committed, which may have been deliberate.
- Upstream PR for `/watch`: offered, unanswered.
- Whether build #1's direction is right. It was built from three self-authored
  interview answers; if the vibe is off, that is the first place to look.
