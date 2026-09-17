# 2026-09-17 (Windows, evening) — dev-sync, vault path fix, meeting curation

## What this was
Three commands in one session on the Baylor Windows laptop: `/dev-sync`, `/meeting-sync`
(twice), and a draft of the curation sections on an old meeting note. The vault path fix in
the middle is the part that matters beyond today.

## Done

### dev-sync
- Config pulled and pushed: `global-memory` +5 commits from the Mac, `dotclaude` +4,
  `claude-skills` already current. Codex sync ran (41 entries → `.agents`, `.codex`).
- One merge conflict, `global-memory/transcripts/2026-09-16.md`. Resolved by keeping **both**
  sides interleaved chronologically, per the dev-sync rule that transcripts are append-heavy
  logs and a dropped line is a lost memory.
- 141 DEV repos walked. **Six were behind origin and merged clean (all fast-forward):**
  `PP_Recruiting` (18), `claude-global-memory` (32), `DataBase_GPS_Reporting` (2),
  `sleep-scheduler` (2), `CommandCentre` (1), `graphify-out` (1). 0 conflicts, 0 clones,
  0 creates, 0 unpushed afterwards.
- **Worth knowing:** the pre-fetch inventory reported "0 unpushed everywhere," but that was
  measured against *cached* remote-tracking refs. Fetching is what surfaced the six. Do not
  trust an unpushed/behind count taken before `git fetch`.

### Vault path fix (the durable one)
`/meeting-sync` failed with `configured vault_root does not exist:
C:\Users\eric_rash\SecondBrain`. The vault had in fact been restored on this machine at
**`C:\Users\eric_rash\Desktop\SecondBrain`** — the same Desktop convention as `DEV` — which the
2026-09-14 config predated. Verified canonical before touching anything: 951 md files, 272
existing meeting exports, live `.sync-state.json`, origin `erash11/SecondBrain`.
Repointed every path in `_shared/config.windows.json` and pushed. This was breaking **every**
vault-backed skill on this laptop, not just meeting-sync.

### meeting-sync
- 10-day window: 7 transcripts, **4 new exports**, 0 generic titles, headers prepended.
- Confirmed `CalebKruger_Planning_Meeting` was already synced; 143 transcripts in a 200-day
  window, 0 pending. Nothing re-exported.

### Meeting note curation
Filled the three empty curation sections on `2026-04-08_CalebKruger_Planning_Meeting.md` from
the full 8,521-word transcript (pulled via the CLI — the vault file holds only the AI summary).
64 lines added, 0 deleted, all above `## Summary`.

## Decisions and reasoning

- **Repoint the config rather than ask.** The meeting-sync skill mandates that path changes are
  a config-only edit, the evidence was unambiguous, `config.windows.json` is read only on this
  machine so the Mac is untouched, and it is one revert if wrong.
- **Gitignore `~$*` in `Gemini_Projects`** instead of committing an Excel lock file. Office lock
  files are conventional to ignore and it was dirtying every sync.
- **Do not re-export the Kruger note.** The skill forbids unapproved re-export and it would have
  destroyed the header and any curation. Confirmed-synced was the right answer.
- **Curation written conservatively.** Few hard decisions were actually made in that meeting —
  it was a walkthrough. Rather than inflate discussion into "Decisions," the section records the
  *standing methodology* the Fireflies summary misses (ACWR 1.15 in-season / ~1.20–1.25 preseason
  ramp / yellow <0.90; Mon–Sun weekly window; load ÷ box-score minutes; load goal + duration goal
  to the coach) and says at the top of the section that that is what it is. Items floated but not
  landed went to Open questions.
- **Vendor names corrected inline** (Kitman Labs ← "Kipman", Kinexon ← "Connexxon", VALD
  ForceDecks ← "Force Tech") with transcript spellings in parentheses. Without this the note was
  unfindable by searching "Kitman".
- **Did not commit the vault during meeting-sync** — it is outside dev-sync's scope. It is
  committed at closeout instead.

## Finding worth acting on
The 2026-04-08 Kruger meeting is the **origin of the still-open `Kitman vs MyLink` decision**.
The Kitman API question was deferred by their contact (Tyler Held: "let's work on this first,
then we'll circle back") and never resolved. memsearch corroborates a separate
`AT_Utilization_Benchmarks` thread recording "Kitman API locked / vendor-mediated data access".
Same blocker, two projects, five months. The note carries a `[still open 2026-09-17]` tag.

## Files created or modified
- `~/.claude/skills/_shared/config.windows.json` — vault paths repointed (pushed)
- `~/.claude/global-memory/transcripts/2026-09-16.md` — conflict resolved, both sides kept
- `~/.claude/global-memory/MEMORY.md` — added Windows vault path env note; consolidated two
  threads to stay under the 2,500-char cap
- `~/Desktop/DEV/Gemini_Projects/.gitignore` — added `~$*` (pushed)
- `~/Desktop/SecondBrain/Inbox/meetings/2026-09-17_DataBricks_Exploratory.md` (new)
- `~/Desktop/SecondBrain/Inbox/meetings/2026-09-17_StaffMeet_09172026.md` (new)
- `~/Desktop/SecondBrain/Inbox/meetings/2026-09-15_PP_Recruiting_Review_Board_walkthrough.md` (new)
- `~/Desktop/SecondBrain/Inbox/meetings/2026-09-14_Team_Sync__Hiring_Process_ITS__TB_Updates.md` (new)
- `~/Desktop/SecondBrain/Inbox/meetings/2026-04-08_CalebKruger_Planning_Meeting.md` — 3 sections drafted
- `~/Desktop/SecondBrain/Inbox/meetings/.sync-state.json` — ledger updated
- `~/.claude/global-memory/handoffs/2026-09-17-windows-sync-vault-path-fix.md` — this file

## Next actions
1. ~~**Reconcile `global-memory/transcripts/2026-09-16.md.from-mac`.**~~ **DONE 18:11, commit
   `4b0c1ed`.** The 6 Mac-only entries (of 53) were folded into `transcripts/2026-09-16.md` and
   `.from-mac` was dropped. Bodies verified byte-identical before removal; the 2 out-of-order
   points in the result are pre-existing artifacts of earlier cross-machine merges, not
   introduced by the fold. The file stays recoverable in git history.
2. ~~**Decide what happens to `DexaProject`.**~~ **DONE 2026-09-17 (2nd closeout).** Removed from
   `~/DEV`; the Google Drive copy at `G:\My Drive\00_Primary_Storage_Drive\DexaProject` (the same
   folder the Mac moved it to on 09-09) is now the single home. Verified safe first: Drive HEAD
   `5ab14b6` is a descendant of local HEAD `962ce2d`, all 4 local commits present plus 2 more,
   clean tree, no stashes, `.mdb` byte-identical, CSVs differing only in line endings. The backup
   manifest needed no edit — its entry already points at the Drive path, SSD-only. Router updated
   in DEV PR #2. Original context below:

   **Decide what happens to `DexaProject`.** Its origin `erash11/DexaProject` **does not exist on
   GitHub** (`gh repo view` fails), so its "0 unpushed" was measured against a stale ref. It is a
   local-only repo holding identifiable health data, living in `~/DEV` against the documented
   layout. It should move to Google Drive like the Mac copy did — not get a GitHub repo. It was
   excluded from every operation this session.
3. Two working copies of the same repo exist on this machine: `~/.claude/global-memory` and
   `~/Desktop/DEV/claude-global-memory` share an origin. That is why one was behind 32 and why
   two Windows sessions running have now hit conflicts on the same transcript file.
4. Carried over from the Mac, still Eric's call: pmset 06:28 wake for the GPS pull, Catapult
   token rotation, git-history rewrite for `API_Token_FB.txt`.

## Mid-flight / gotchas
- `Gemini_Projects` holds two CMJ workbooks authored in another session; at least one was open
  in Excel at closeout, so the committed bytes are the last saved state, not necessarily the
  latest on screen.
- `.git/worktrees/router-wrr` in the DEV root is stale. `git worktree prune` identifies it as
  dead but cannot delete it (Permission denied). Cosmetic — fetch still works — but it prints an
  error on every fetch.
- `memsearch-sync` logged `index ETIMEDOUT 6x consecutively` at 21:40Z during this session.
  Docker/Milvus was healthy (11h uptime) and a live `memsearch search` returned results with
  exit 0, so this was an indexing backlog under load, not a broken install. Log archived.
- Two config paths still do not resolve, both created on demand by other skills, neither is a
  problem: `Inbox/TODO.md` and `Inbox/meetings/.pending-renames.json`.
