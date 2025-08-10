import asyncio
import sys
import os

# Add backend root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import db_manager
from app.models.mongo_models import UseCase


async def publish_last_draft():
    await db_manager.init_mongodb()
    try:
        # Find most recently created draft
        draft = await UseCase.find(UseCase.published == False).sort(-UseCase.created_at).first_or_none()
        if not draft:
            print("No draft use cases found.")
            return

        draft.published = True
        await draft.save()
        print(f"Published use case: {str(draft.id)} | {draft.title}")
    finally:
        await db_manager.close_connections()


if __name__ == "__main__":
    asyncio.run(publish_last_draft())


