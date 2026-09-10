# Book Vault — Production Rebuild Design Spec

**Date:** 2026-04-01  
**Status:** Approved

---

## Overview

Rebuild the existing single-file HTML Book Vault app as a production-grade hosted web application. The feature set, design system, and UX are preserved exactly. The rebuild replaces `localStorage` with a cloud database, adds a login screen, and makes the app accessible from any browser without downloading a file.

---

## Goals

- Data persists in the cloud (not tied to one browser/device)
- Accessible via a URL from any browser, including iPhone Safari
- Zero infrastructure to manage — fully managed hosting and database
- Single user (one colleague)
- Claude API key provided by the user, stored server-side

---

## Stack

| Layer | Choice | Rationale |
|---|---|---|
| Frontend | Next.js (App Router) | React, SSR, API routes, Vercel-native |
| Hosting | Vercel | One-click deploy, free tier, CDN |
| Database | Supabase (Postgres) | Managed, free tier, built-in Auth + RLS |
| Auth | Supabase Auth | Email + password, session cookies, no custom users table |
| AI/Scanner | Anthropic Claude API (`claude-sonnet-4-6`) | Called from Next.js API route, user's own key |
| Styling | Tailwind CSS | Utility-first, consistent with existing design tokens |

---

## Database Schema

### `books`
```sql
id           uuid PRIMARY KEY DEFAULT gen_random_uuid()
user_id      uuid NOT NULL REFERENCES auth.users
title        text NOT NULL
author       text NOT NULL
format       text CHECK (format IN ('Physical','Audio','Digital'))
status       text CHECK (status IN ('reading','finished','queue'))
rating       int CHECK (rating BETWEEN 0 AND 5)
topics       text[]
summary      text
application  text
app_due      date
date_finished date
created_at   timestamptz DEFAULT now()
```

### `quotes`
```sql
id           uuid PRIMARY KEY DEFAULT gen_random_uuid()
book_id      uuid NOT NULL REFERENCES books(id) ON DELETE CASCADE
user_id      uuid NOT NULL REFERENCES auth.users
text         text NOT NULL
type         text CHECK (type IN ('Quote','Insight','Story','Conviction','Question'))
page         text
channels     text[]
topics       text[]
created_at   timestamptz DEFAULT now()
```

### `user_settings`
```sql
user_id      uuid PRIMARY KEY REFERENCES auth.users
channels     text[] DEFAULT ARRAY['Social','Podcast','Teaching','Speaking','Writing','Meeting','Personal']
topics       text[] DEFAULT ARRAY['Leadership','Faith','Communication','Culture','Creativity','Business','Discipleship','Personal Growth','Relationships','Scripture']
claude_api_key text
```

Row-level security (RLS) is enabled on all tables. All policies require `auth.uid() = user_id`.

---

## Authentication

- Supabase Auth with email + password
- Sessions managed via httpOnly cookies (Next.js middleware)
- Single user: the colleague creates their account on first load
- No sign-up page needed beyond the initial account creation — login screen only

---

## App Structure (Next.js)

```
app/
  (auth)/
    login/page.tsx          — login form
  (app)/
    layout.tsx              — bottom tab nav, auth guard
    dashboard/page.tsx
    library/page.tsx
    vault/page.tsx          — Quote Vault
    scanner/page.tsx
    settings/page.tsx
    books/[id]/page.tsx     — Book Detail (Overview / Quotes / Book Close tabs)
  api/
    scan/route.ts           — proxies image to Claude API (server-side)
    export/route.ts         — generates book-vault-export.json download
    import/route.ts         — seeds DB from existing export JSON
lib/
  supabase/
    client.ts               — browser Supabase client
    server.ts               — server-side Supabase client
  types.ts                  — Book, Quote, UserSettings TypeScript types
```

---

## Screens & Features

All five screens are direct ports of the existing app. No feature changes.

### Login
Simple email + password form. On first visit, if no account exists, shows a "Create account" toggle. After login, redirects to Dashboard. Session persists indefinitely on iPhone (no re-login on return visits).

### Dashboard
- Stats strip: total books, total quotes, currently reading count
- Currently reading shelf
- Pending Book Close alerts (finished books without summary — red, links to Book Close tab)
- 5 most recent captures
- Add New Book button

### Library
- Search (title, author, topic)
- Horizontally scrollable topic tag filters
- Books grouped by status: Currently Reading → Finished → Queue

### Quote Vault
- Full-text search across all quotes
- Two scrollable filter rows: Output Channels + Topic Tags
- Combinable filters
- Tapping a result opens source book detail

### Scanner
- **Photo Scanner:** Image upload → Next.js API route → Claude vision API → checkbox review → save to book
- **Kindle Import:** `My Clippings.txt` upload → parse → preview → import

### Settings
- Claude API key (masked input, saved to `user_settings.claude_api_key` server-side)
- Output Channels editor (add/remove)
- Topic Tags editor (add/remove)
- Export All Data → `book-vault-export.json`
- Import Existing Vault → one-time seed from export JSON (for migrating from the old app)
- Clear All Data (with confirmation)

### Book Detail
Three-tab layout: Overview, Quotes, Book Close (5-step session). Identical to current app.

---

## Design System

Identical to current app. CSS custom properties ported to Tailwind config:

```js
// tailwind.config.js
colors: {
  forest:       '#1e3a2f',
  'forest-mid': '#2d5040',
  'forest-light':'#3d6b55',
  gold:         '#c9a84c',
  'gold-light': '#e8c97a',
  cream:        '#f7f3ec',
  'cream-dark': '#ede7db',
  ink:          '#1a1a18',
  muted:        '#7a7570',
  danger:       '#b5451b',
  border:       '#e2dbd0',
}
```

Typography: Google Fonts — Playfair Display (display/titles) + DM Sans (body/UI), loaded via `next/font`.

iPhone-specific meta tags preserved: `apple-mobile-web-app-capable`, safe area insets, no user-scalable.

---

## Scanner — API Route

`POST /api/scan`
- Accepts: `{ image: string (base64), bookId: string }`
- Server reads `claude_api_key` from `user_settings` for the authenticated user
- Calls `https://api.anthropic.com/v1/messages` with `claude-sonnet-4-6` vision model
- Returns: `{ extractions: string[] }`
- The API key is never sent to or stored in the browser

---

## Migration Path

The existing `book-vault-export.json` (downloaded from Settings → Export in the current app) maps 1:1 to the new schema. The Settings screen includes a one-time "Import Existing Vault" action that:
1. Accepts the JSON file upload
2. Calls `POST /api/import`
3. Inserts books and quotes into Supabase, skipping duplicates

---

## Deployment Setup (colleague's steps)

1. Fork/clone the GitHub repo
2. Create a free project at supabase.com → run the provided SQL migration file to create tables + RLS policies
3. Copy `NEXT_PUBLIC_SUPABASE_URL` and `NEXT_PUBLIC_SUPABASE_ANON_KEY` from Supabase project settings
4. Click "Deploy to Vercel" button in the README → paste the two environment variables
5. Vercel assigns a URL (e.g. `bookvault.vercel.app`)
6. On iPhone: Safari → that URL → Share → Add to Home Screen

No CLI, no terminal, no config files to edit beyond pasting two env vars.

---

## Included by Default

- **Cross-device sync** — because data lives in Supabase, any device logged into the same account sees the same vault instantly. No additional work required.

---

## Phase 2 Candidates

Features that are buildable after the initial launch:

- **Multi-user support** — the schema already has `user_id` on every row and RLS policies in place. Opening registration is the only change needed.
- **Push notifications** — Web Push API via the PWA to remind about pending Book Close sessions.

---

## Out of Scope (blocked by third party)

- **Direct Kindle/Amazon API integration** — Amazon has no public API for Kindle highlights. File-based `My Clippings.txt` import remains the only available method.
- **Native iOS app** — requires Swift/SwiftUI, Apple Developer account ($99/year), and App Store review. The PWA covers ~90% of the native experience. Revisit only if a specific capability gap emerges.
