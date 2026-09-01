# ResearchMind Frontend — Setup Guide

## What this is

A Next.js 14 + TypeScript + Tailwind frontend implementing:
- Home page (hero, features, how-it-works)
- Manual signup/login + Google Sign-In (Firebase)
- 3-column research workspace: chat sidebar / conversation / sources panel
- Real-time streaming answers (Server-Sent Events) with live agent status
  (shows whether the planner routed to RETRIEVE / WEB_SEARCH / PAPER_SEARCH)
- File upload with real progress tracking
- Citation cards with type-specific previews (tables render as actual
  tables, charts show their extracted description)
- Settings page

**Verified before delivery:** `npx tsc --noEmit` passes with zero errors,
and `npm run build` completes successfully (all 7 routes compile, static
pages generate, the dynamic `/chat/[chatId]` route builds correctly).

## Important note on chat history

Your backend's `/chat/query` is single-shot — there's no persisted "chat
session" concept server-side yet. Chat history here lives in the
**browser's localStorage**, namespaced per logged-in user (see
`lib/chatStore.ts`). This means:
- Chats don't sync across devices/browsers.
- Clearing browser storage clears chat history.
- If you later add a `/chats` backend endpoint, `lib/chatStore.ts` is the
  only file that needs to change — everything else calls through it.

This was a deliberate scope decision, not an oversight — flagging it so
it's not a surprise later.

## 1. Install dependencies

```powershell
cd frontend
npm install
```

## 2. Configure environment variables

```powershell
copy .env.local.example .env.local
```

Edit `.env.local`:
```
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```
(Change this to your deployed backend URL once you deploy to Render.)

## 3. Firebase config (for Google Sign-In)

You already created a Firebase project for the backend's token verification.
Now get the **web app** config for the frontend:

1. Firebase Console → your project → gear icon → **Project settings**
2. Scroll to **Your apps** → click **Add app** → Web (`</>`  icon)
3. Register the app (any nickname) → copy the `firebaseConfig` values
4. Fill them into `.env.local`:
   ```
   NEXT_PUBLIC_FIREBASE_API_KEY=...
   NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=...
   NEXT_PUBLIC_FIREBASE_PROJECT_ID=...
   NEXT_PUBLIC_FIREBASE_APP_ID=...
   ```

These are all client-safe public values (not secrets) — Firebase's own
docs confirm this; the real security boundary is your backend verifying
the ID token server-side, which you already built.

## 4. Run it

```powershell
npm run dev
```

Open `http://localhost:3000`.

## 5. Test the full flow

1. Backend running (`uvicorn app.main:app --reload`) and reachable at
   the URL in `NEXT_PUBLIC_API_URL`.
2. Home page → **Sign up** → create an account (manual).
3. You're redirected to `/chat` → **New chat**.
4. Upload a PDF (clip icon) → watch real progress → wait for "Indexed".
5. Ask a question → watch the agent status badge (Searching your
   documents / the web / arXiv) → watch the answer stream in → sources
   populate in the right panel.
6. Log out (top-right menu) → log back in with **Continue with Google**
   → confirm it creates/links your account correctly.

## Known items (documented, not blocking)

- **`npm audit`** flags vulnerabilities nested inside Next.js's own
  bundled PostCSS build tooling. The only fix npm offers is a forced
  jump to Next.js 16 (a major version, breaking-change migration) —
  deliberately not done automatically here since it risks destabilizing
  the whole app without review. Worth doing as a deliberate, separate
  upgrade pass later.
- **Google Fonts fetch at build time**: `next/font/google` fetches Inter
  and JetBrains Mono from Google's CDN during `npm run build`. This
  requires outbound internet access at build time (works fine locally
  and on Vercel/Render, just noting it as a build-environment
  requirement, not a bug).

## Design tokens reference

Defined in `app/globals.css` as CSS variables (light + dark mode):
- Accent: `#3B5BDB` (used sparingly — primary buttons, links, active states)
- Surfaces: white/near-black backgrounds, light-gray/dark-gray panels
- Borders: hairline, low-contrast
- Radii: 6–12px (small, consistent)
- Font: Inter (UI text), JetBrains Mono (citation badges, code)
