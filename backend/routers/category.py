import uuid
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from pydantic import BaseModel
from loguru import logger
from entity.response import Response

from model import Category, User, CollectionDetail, Collection
from db import get_db
from routers.auth import get_current_user
from knowledge_base.chromadb_mgr import chroma_db_manager
from ai.openai_provider import provider_openai
from ai.PROMPTS import KNOWLEDGE_BASE_QUERY_PROMPT
from utils.text_splitter import recursive_text_splitter

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
    db: AsyncSession = Depends(get_db),
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
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
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
                    "knowledge_base_id": category.knowledge_base_id,
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
    db: AsyncSession = Depends(get_db),
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


# 创建知识库
@router.post("/create_knowledge_base")
async def create_knowledge_base(
    category_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new knowledge base category
    """
    category = await db.get(Category, category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with id {category_id} not found"
        )
    
    collection_name = f"kb_{uuid.uuid4()}"
    _ = chroma_db_manager.create_collection(collection_name)

    # TODO(Soulter): 优化 SQL
    stmt = select(CollectionDetail).join(
        Collection, CollectionDetail.collection_id == Collection.id
    ).where(
        Collection.category_id == category_id,
        Collection.user_id == current_user.id,
        CollectionDetail.key == "content"
    )
    result = await db.execute(stmt)
    details = result.scalars().all()
    content_list = [str(detail.value) for detail in details]

    chunked_content_list = []
    for content in content_list:
        if isinstance(content, str) and content.strip():
            chunked_content_list.extend(recursive_text_splitter.split_text(content))

    logger.info(f"Creating knowledge base for category {category_id} with content: {chunked_content_list}")

    # upsert documents into the knowledge base
    chroma_db_manager.upsert(
        collection_name=collection_name,
        documents=chunked_content_list,
        ids=[str(uuid.uuid4()) for _ in chunked_content_list]
    )

    # Update the category with the knowledge base ID
    category.knowledge_base_id = collection_name # type: ignore
    db.add(category)
    await db.commit()
    await db.refresh(category)

    return Response(
        status="success", message="Knowledge base created successfully", data=None
    )

# query knowledge base
@router.get("/knowledge_base/{category_id}")
async def query_knowledge_base(
    category_id: int,
    query: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Query the knowledge base for a specific category
    """
    # Get the category to find its knowledge base ID
    category = await db.get(Category, category_id)
    if not category or not category.knowledge_base_id: # type: ignore
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Knowledge base for category {category_id} not found"
        )

    collection_name = category.knowledge_base_id

    # Query the knowledge base
    results = chroma_db_manager.query(
        collection_name=collection_name, query=query, n_results=5 # type: ignore
    )

    logger.info(f"Querying knowledge base '{collection_name}' with query: {query}: {results}")

    documents = results["documents"][0]

    documents_str = ""
    for doc in documents:
        documents_str += f"{doc}\n\n"

    system_prompt = KNOWLEDGE_BASE_QUERY_PROMPT.format(
        documents=documents_str
    )

    # Ask AI
    ai_response = await provider_openai.text_chat(
        prompt=query,
        system_prompt=system_prompt,
    )

    return Response(
        status="success",
        message="Knowledge base queried successfully",
        data={
            "response": ai_response.completion_text.strip(),
            "documents": documents,
        },
    )
