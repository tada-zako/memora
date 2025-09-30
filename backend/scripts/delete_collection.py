import asyncio

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from backend.db import AsyncSessionLocal
from backend.model import Collection

async def delete_collection(collection_id: int):
    async with AsyncSessionLocal() as session:
        # Check if the collection to be deleted exists
        result = await session.execute(select(Collection).where(Collection.id == collection_id))
        collection_to_delete = result.scalar_one_or_none()
        if not collection_to_delete:
            logger.warning(f"Collection with id {collection_id} does not exist.")
            return

        # delete the collection
        await session.delete(collection_to_delete)
        await session.commit()

        logger.info(f"Collection with id {collection_id} deleted successfully.")

    
async def main():
    collection_id_to_delete = [25]  # Replace with the actual collection ID you want to delete

    asyncio_tasks = [delete_collection(col_id) for col_id in collection_id_to_delete]
    await asyncio.gather(*asyncio_tasks)


if __name__ == "__main__":
    asyncio.run(main())