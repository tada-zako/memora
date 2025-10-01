from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from backend.db import AsyncSessionLocal
from backend.model import Collection, Category

async def clear_collections():
    """
    清理收藏表中的孤儿数据
    """
    async with AsyncSessionLocal() as session:
        stmt = (
            select(Collection)
            .outerjoin(Category)
            .where(Category.id.is_(None))
        )

        result = await session.execute(stmt)
        orphaned_collections = result.scalars().all()

        orphaned_count = len(orphaned_collections)
        if orphaned_count == 0:
            logger.info("No orphaned collections found.")
            return
        
        for collection in orphaned_collections:
            await session.delete(collection)

        await session.commit()
        logger.info(f"Deleted {orphaned_count} orphaned collections.")

if __name__ == "__main__":
    import asyncio
    asyncio.run(clear_collections())