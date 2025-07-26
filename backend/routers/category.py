from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from pydantic import BaseModel
from loguru import logger
from entity.response import Response

from model import Category, User
from db import get_db
from routers.auth import get_current_user


# Create router instance
router = APIRouter(
    prefix="/category",
    tags=["categories"],
    responses={404: {"description": "Not found"}},
)


class CategoryCreate(BaseModel):
    name: str
    emoji: Optional[str] = None


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    emoji: Optional[str] = None


class CategoryResponse(BaseModel):
    id: int
    user_id: int
    name: str
    emoji: Optional[str] = None

    class Config:
        from_attributes = True


@router.post("/", response_model=Response, status_code=status.HTTP_201_CREATED)
async def create_category(
    category: CategoryCreate, 
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new category
    """
    user_id = current_user.id

    # Check if category name already exists for this user
    stmt = select(Category).where(
        Category.user_id == user_id, Category.name == category.name
    )
    result = await db.execute(stmt)
    existing_category = result.scalar_one_or_none()

    if existing_category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Category with name '{category.name}' already exists",
        )

    db_category = Category(user_id=user_id, name=category.name, emoji=category.emoji)

    db.add(db_category)
    await db.commit()
    await db.refresh(db_category)

    logger.info(f"Created category: {db_category.name} (id: {db_category.id})")
    return Response(
        status="success",
        message="Category created successfully",
        data={
            "id": db_category.id,
            "name": db_category.name,
            "emoji": db_category.emoji,
            "user_id": db_category.user_id,
        },
    )


@router.get("/", response_model=Response)
async def get_categories(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all categories for the current user
    """
    user_id = current_user.id

    stmt = select(Category).where(Category.user_id == user_id).order_by(Category.name)
    result = await db.execute(stmt)
    categories = result.scalars().all()

    return Response(
        status="success",
        message="Categories retrieved successfully",
        data={
            "categories": [
                {
                    "id": category.id,
                    "user_id": category.user_id,
                    "name": category.name,
                    "emoji": category.emoji,
                }
                for category in categories
            ]
        },
    )


@router.put("/{category_id}", response_model=Response)
async def update_category(
    category_id: int,
    category_update: CategoryUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update a specific category
    """
    user_id = current_user.id

    # Get the existing category
    stmt = select(Category).where(
        Category.id == category_id, Category.user_id == user_id
    )
    result = await db.execute(stmt)
    category = result.scalar_one_or_none()

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with id {category_id} not found",
        )

    # Check if the new name conflicts with existing categories (if name is being updated)
    if category_update.name and category_update.name != category.name:
        stmt = select(Category).where(
            Category.user_id == user_id,
            Category.name == category_update.name,
            Category.id != category_id,
        )
        result = await db.execute(stmt)
        existing_category = result.scalar_one_or_none()

        if existing_category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Category with name '{category_update.name}' already exists",
            )

    # Update fields if provided
    update_data = {}
    if category_update.name is not None:
        update_data["name"] = category_update.name
    if category_update.emoji is not None:
        update_data["emoji"] = category_update.emoji

    for field, value in update_data.items():
        setattr(category, field, value)

    await db.commit()
    await db.refresh(category)

    logger.info(f"Updated category: {category.name} (id: {category.id})")
    return Response(
        status="success",
        message="Category updated successfully",
        data={
            "id": category.id,
            "name": category.name,
            "emoji": category.emoji,
            "user_id": category.user_id,
        },
    )


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: int, 
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a specific category
    """
    user_id = current_user.id

    # Get the existing category
    stmt = select(Category).where(
        Category.id == category_id, Category.user_id == user_id
    )
    result = await db.execute(stmt)
    category = result.scalar_one_or_none()

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with id {category_id} not found",
        )

    await db.delete(category)
    await db.commit()

    logger.info(f"Deleted category: {category.name} (id: {category.id})")
    return Response(
        status="success",
        message="Category deleted successfully",
        data=None,
    )
