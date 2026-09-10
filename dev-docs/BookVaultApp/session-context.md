# Book Vault — Session Context

Running log of what has been built, what remains, and where to resume. Update this file at the end of each session.

---

## Session 1 — 2026-04-01

### What was built

- Next.js project scaffolded (App Router, Tailwind, Supabase, TypeScript)
- Supabase client/server setup (`lib/supabase/client.ts`, `lib/supabase/server.ts`)
- TypeScript types (`lib/types.ts`) — `Book`, `Quote`, `UserSettings`, `BookWithQuoteCount`
- Auth middleware (`middleware.ts`) — protects `(app)` routes, redirects to `/login`
- **Login screen** (`app/(auth)/login/page.tsx`) — sign in + create account toggle, Supabase Auth
- **Dashboard screen** (`app/(app)/dashboard/page.tsx` + `components/DashboardView.tsx`)
  - Stats strip (total books, total quotes, currently reading count)
  - Currently reading shelf with BookCard links
  - Pending Book Close alerts (finished books without a summary — danger red)
  - 5 most recent captures
  - Add New Book button (opens AddBookModal)
- **Library screen** (`app/(app)/library/page.tsx` + `components/LibraryClient.tsx`)
  - Search by title/author/topic
  - Horizontally scrollable topic filter tags
  - Books grouped by status: Currently Reading → Finished → Queue
- **Book Detail screen** (`app/(app)/books/[id]/page.tsx` + `components/BookDetailClient.tsx`)
  - Overview tab: view + edit (status, rating, summary, application, due date, topics) + delete book
  - Quotes tab: list all quotes, add quote form (type, text, page, channels, topics), delete quote
  - Book Close tab: 5-step wizard (Rate & Reflect → The Big Ideas → Your Summary → One Application → Session Complete)
- **Quote Vault screen** (`app/(app)/vault/page.tsx` + `components/VaultClient.tsx`)
  - Full-text search across quote text and book title
  - Scrollable channel filter row with "All Channels" reset chip
  - Scrollable topic filter row, combinable with channel filters
  - Results list — each quote links to `books/[id]?tab=quotes`
- **Settings screen** (`app/(app)/settings/page.tsx` + `components/SettingsClient.tsx`)
  - Claude API key masked input — saves via `updateSettings`, never exposed to browser
  - Channels editor — add/remove tags, auto-saves on change
  - Topics editor — add/remove tags, auto-saves on change
  - Export All Data → `GET /api/export` → downloads `book-vault-export.json`
  - Import Existing Vault → file upload → `POST /api/import` → deduplicates by title+author / text
  - Clear All Data — bottom-sheet confirmation modal
  - Sign Out button
- **Scanner screen** (`app/(app)/scanner/page.tsx` + `components/ScannerClient.tsx`)
  - Photo Scanner tab: book selector, camera/photo upload → `/api/scan` → Claude vision → checkbox review → save selected as quotes
  - Kindle Import tab: `My Clippings.txt` upload → parse on `==========` delimiter → fuzzy match to existing books → per-book import via `importKindleBook` action
  - No-API-key notice with link to Settings when key is not set
- **Server actions** (`app/actions.ts`) — `signOut`, `addBook`, `updateBook`, `deleteBook`, `addQuote`, `deleteQuote`, `updateSettings`, `clearAllData`, `importKindleBook`
- **API routes**
  - `app/api/export/route.ts` — GET, dumps all books + quotes as JSON download
  - `app/api/import/route.ts` — POST, remaps IDs and deduplicates on import
  - `app/api/scan/route.ts` — POST, reads `claude_api_key` server-side, calls Claude vision API (`claude-sonnet-4-6`), returns `{ extractions: string[] }`
- **Shared components** — `BottomNav`, `BookCard`, `AddBookModal`

### Git
- Commit `2d18070` — initial production rebuild (Login, Dashboard, Library, Book Detail scaffolding)
- Commit `922bd4d` — Book Close 5-step wizard
- Commit `f38666e` — Quote Vault screen
- Commit `9a50e9e` — session context update after Quote Vault
- Commit `3f3c83d` — Settings screen + export/import API routes
- Note: a previous session accidentally committed `node_modules`. Fixed by soft-resetting to `origin/main` and making one clean commit.

---

## Session 2 — 2026-04-02

### What was built

- **Settings screen** (`app/(app)/settings/page.tsx` + `components/SettingsClient.tsx`) — Claude API key input, channels/topics editors (auto-save on change), Export All Data, Import Existing Vault, Clear All Data (confirmation modal), Sign Out
- **Scanner screen** (`app/(app)/scanner/page.tsx` + `components/ScannerClient.tsx`) — Photo Scanner tab (book selector → camera/photo → Claude vision → checkbox review → save) + Kindle Import tab (`My Clippings.txt` → parse → fuzzy match → per-book import)
- **API routes** — `app/api/scan/route.ts` (Claude vision, server-side key), `app/api/export/route.ts` (JSON download), `app/api/import/route.ts` (deduplicated insert)
- **Server actions** — added `clearAllData` and `importKindleBook` to `app/actions.ts`
- **Supabase migration file** — `supabase/migration.sql` written and committed (creates `books`, `quotes`, `user_settings` tables with RLS and indexes)
- Attempted Supabase MCP setup — MCP authenticated but tools did not expose in session; migration must be run manually

### Git
- Commit `3f3c83d` — Settings screen + export/import API routes
- Commit `8de7eb2` — Scanner screen + scan API route
- Commit `37e0f70` — Supabase migration SQL file
- Commit `94c5f27` — Vercel project config added to .gitignore

### Infrastructure completed this session
- Supabase project `bookvault` created via MCP (us-east-1, free tier)
- Migration applied via MCP — `books`, `quotes`, `user_settings` tables + RLS + indexes
- `.env.local` written with live project URL and anon key
- Vercel project created (`erashs-projects/bookvault`), linked to GitHub repo
- Env vars added to Vercel project (production environment)
- Production deploy live at `https://bookvault-alpha.vercel.app` (deployment `AWSM2Kz4omVp3sXnAz72CKctN2rm`)
- Note: subsequent CLI and GitHub-triggered deploys failed instantly (0ms, no build logs) — root cause unknown. `vercel redeploy <deployment-id> --target production --scope erashs-projects` on the original successful deployment is the workaround for future deploys.

### Auth bugs fixed post-deploy
- **Login redirect loop** — `router.push('/dashboard')` fired before session cookie propagated; middleware saw no user and bounced back to `/login`. Fixed by replacing with `window.location.href = '/dashboard'`.
- **Signup hang** — Supabase's default "Confirm email" setting meant `signUp` returned no session. Fixed by: (1) adding a check for `data.session` and showing a message if null, and (2) disabling email confirmation in Supabase dashboard (Authentication → Sign In / Providers → Confirm email: OFF).
- App is fully working end-to-end as of commit `eeddea6`.

---

## What Remains

### The app is fully live — no pending infrastructure work.

**Production URL:** https://bookvault-alpha.vercel.app  
**Supabase:** `iulkpdqwpueowjqsqfhv.supabase.co` (us-east-1, free tier)

To use the Photo Scanner, Kevin needs to add his Claude API key in Settings → Claude API Key.  
On iPhone: Safari → the URL above → Share → Add to Home Screen.

---

## Design Decisions Made

- All mutations go through Next.js server actions in `app/actions.ts` — no client-side Supabase writes except login
- `BookWithQuoteCount` type extends `Book` with `quote_count: number` for display without fetching all quote records
- Book Detail page passes `initialTab` from `?tab=` search param so other screens can deep-link to the Quotes or Book Close tab
- `VaultQuote` type exported from `vault/page.tsx` and imported by `VaultClient.tsx` — co-located with the page that defines it
- Settings page sends `hasApiKey: boolean` to client, never the key value itself — the actual key stays server-side only
- Scanner page sends `hasApiKey: boolean` to client for the same reason; scan API route reads key fresh from DB on each request
- Import deduplication: books matched by `title + author + user_id`, quotes matched by `book_id + text + user_id`; old export IDs remapped via `bookIdMap`
- `clearAllData` deletes quotes before books to respect the FK constraint
- Kindle fuzzy match: first 20 chars of Kindle book title tested against `.toLowerCase().includes()` on each existing book title
- `importKindleBook` creates the book if no match, then inserts all highlights as `type: 'Quote'` with empty channels/topics (user tags later)
- Scan API uses `fetch` directly (no SDK) since `@anthropic-ai/sdk` is not installed — just raw POST to `https://api.anthropic.com/v1/messages`
- `node_modules` must never be committed — `.gitignore` is in place
