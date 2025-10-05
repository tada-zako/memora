import asyncio

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from backend.db import AsyncSessionLocal
from backend.model import Category


async def delete_category(category_id: int):
    async with AsyncSessionLocal() as session:
        # Check if the category to be deleted exists
        result = await session.execute(
            select(Category).where(Category.id == category_id)
        )
        category_to_delete = result.scalar_one_or_none()
        if not category_to_delete:
            logger.warning(f"Category with id {category_id} does not exist.")
            return

        # delete the category
        await session.delete(category_to_delete)
        await session.commit()

        logger.info(f"Category with id {category_id} deleted successfully.")


async def main():
    category_id_to_delete = [
        10,
        8,
        7,
    ]  # Replace with the actual category ID you want to delete

    asyncio_tasks = [delete_category(cat_id) for cat_id in category_id_to_delete]
    await asyncio.gather(*asyncio_tasks)


if __name__ == "__main__":
    asyncio.run(main())
