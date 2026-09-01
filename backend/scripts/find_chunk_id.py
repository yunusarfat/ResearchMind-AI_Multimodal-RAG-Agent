"""
Helper: find chunk IDs by keyword, so building data/eval/eval_set.json
doesn't require manually querying Postgres.

Usage:
    python -m scripts.find_chunk_id "Table 2" "hyperparameters" --email you@example.com

--email is optional; omit it to search across all users' chunks (only
useful for debugging -- normally you want to scope this to yourself).
"""

import argparse
import asyncio

from sqlalchemy import select

from app.db.database import get_session
from app.db.models import Chunk, User


async def find_chunks(keywords: list[str], email: str | None) -> None:
    async with get_session() as session:
        stmt = select(Chunk)

        if email:
            user = await session.scalar(select(User).where(User.email == email))
            if user is None:
                raise SystemExit(f"No account found for '{email}'.")
            stmt = stmt.where(Chunk.user_id == user.id)

        result = await session.execute(stmt)
        all_chunks = result.scalars().all()

    keywords_lower = [k.lower() for k in keywords]

    matches = [
        c for c in all_chunks
        if all(kw in c.content.lower() for kw in keywords_lower)
    ]

    if not matches:
        print("No chunks matched all keywords. Try fewer/different terms.")
        return

    print(f"Found {len(matches)} matching chunk(s):\n")
    for c in matches:
        preview = c.content[:150].replace("\n", " ")
        print(f"chunk_id: {c.id}")
        print(f"  page={c.page_number}  type={c.content_type}  section={c.section}")
        print(f"  preview: {preview}...\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Find chunk IDs by keyword for building eval_set.json.")
    parser.add_argument("keywords", nargs="+", help="Keywords that must all appear in the chunk")
    parser.add_argument("--email", help="Restrict search to one account's chunks (recommended)")
    args = parser.parse_args()

    asyncio.run(find_chunks(args.keywords, args.email))
