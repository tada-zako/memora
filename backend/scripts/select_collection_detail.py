import asyncio

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from backend.db import AsyncSessionLocal
from backend.model import Collection, CollectionDetail

async def select_collection_detail(collection_id: int):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(CollectionDetail).where(CollectionDetail.collection_id == collection_id)
        )
        details = result.scalars().all()
        return details
    

async def main():
    collection_id = 22  # 替换为你想查询的 collection_id
    details = await select_collection_detail(collection_id)
    for detail in details:
        logger.info(
            f"ID: {detail.id},"
            f"Key: {detail.key}, "
            f"Value: {detail.value}, " # 访问 value 列
            f"Created At: {detail.created_at}" # 访问 created_at 列
        )


if __name__ == "__main__":
    asyncio.run(main())