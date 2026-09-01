# Chat Persistence — Setup Guide

## What changed

Chats are now stored in **PostgreSQL** (two new tables: `chats`, `messages`),
not browser localStorage. This closes the gap flagged earlier — chat
history now survives across devices/browsers and doesn't disappear if
someone clears their browser data.

**New backend endpoints:**
- `POST /chats` — create a new chat
- `GET /chats` — list the current user's chats
- `GET /chats/{chat_id}` — get one chat with full message history
- `DELETE /chats/{chat_id}` — delete a chat

**Changed backend endpoint:**
- `POST /chat/query` — now requires `chat_id` in the request body, verifies
  you own that chat (404 if not), and persists both the user's message and
  the assistant's answer + citations to Postgres automatically during the
  stream.

**Important flow change:** a chat must exist in the database *before*
`/chat/query` will accept a message for it. The frontend's "New chat"
button now calls `POST /chats` first and navigates using the real
database-generated ID — it no longer fabricates a random ID client-side.

---

## 1. Backend: apply file changes

Copy these into your `backend/` folder, **overwriting**:
- `app/db/models.py`
- `app/api/schemas.py`
- `app/api/chat.py`
- `app/main.py`

New file:
- `app/api/chats.py`

## 2. Backend: reset the database (schema changed again)

```powershell
docker exec -it researchmind-pg psql -U researchmind -d researchmind -c "DROP TABLE IF EXISTS messages, chats, chunks, documents CASCADE;"
python -m app.db.init_db
```

This drops documents/chunks too since `chunks`/`documents` reference `users`,
and it's simplest to rebuild everything together. Re-ingest your test PDFs
afterward (`python -m scripts.ingest_documents data/uploads --email you@example.com`),
and sign up again via `/docs` if needed.

## 3. Frontend: apply file changes

Copy into your `frontend/` folder, **overwriting**:
- `lib/api.ts`
- `lib/useChatSession.ts`
- `lib/useChatList.ts`
- `lib/utils.ts`
- `types/chat.ts`
- `components/chat/ChatSidebar.tsx`
- `app/chat/page.tsx`
- `app/chat/[chatId]/page.tsx`

**Deleted file** — remove this if it still exists in your project:
- `lib/chatStore.ts` (the old localStorage-based store, fully replaced)

## 4. Restart both servers and test

```powershell
# backend
uvicorn app.main:app --reload

# frontend (separate terminal)
npm run dev
```

Test sequence:
1. Log in → click **New chat** → confirm it navigates to a real chat URL
   (a proper UUID, created via `POST /chats`).
2. Ask a question, wait for the answer.
3. **Refresh the page** — the conversation should still be there (this is
   the fix — previously this worked too via localStorage, but now it also
   survives clearing browser storage or logging in from a different browser).
4. Log out, log back in (or open an incognito window and log in) — the
   chat should still appear in the sidebar and load correctly. This is
   the real test that it's server-persisted, not browser-persisted.
5. Delete a chat from the sidebar — confirm it's gone after refresh too.

## Verified before delivery

- Backend: full syntax compile-check across the entire codebase, plus an
  end-to-end import of `app.main` confirming all routers (including the
  new `chats` router) wire together with zero errors. Cross-checked the
  OpenAPI schema shows all 9 expected endpoints.
- Backend: round-trip tested the new Pydantic schemas (`ChatDetail`,
  `MessageResponse`, `CitationResponse`, etc.) with realistic data.
- Frontend: `npx tsc --noEmit` passes with zero errors.
- Frontend: full `npm run build` succeeds — all 7 routes compile
  (including the dynamic `/chat/[chatId]` route).
