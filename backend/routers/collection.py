from fastapi import APIRouter, HTTPException, Depends, status, Path
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import desc, select
from sqlalchemy.orm import selectinload
from entity.response import Response
from pydantic import BaseModel
from loguru import logger

from model import User, Collection, Category, CollectionDetail
from db import get_db
from ai.PROMPTS import (
    PROMPT_PARSE_CATEGORY_AND_TAGS,
    PROMPT_SUMMARIZE_CONTENT,
    parse_json,
)
from ai.openai_provider import provider_openai
from utils.markdownit_content import markdownit_helper

from typing import Optional

class CollectionDetailUpdate(BaseModel):
    value: Optional[str] = None

class CollectionTagsUpdate(BaseModel):
    tags: list[str]

# Create router instance
router = APIRouter(
    prefix="/collection",
    tags=["collections"],
    responses={404: {"description": "Not found"}},
)


class CollectionUrlCreate(BaseModel):
    url: str


class CollectionUrlResponseDelta(BaseModel):
    type: str
    data: dict


async def streaming_create_collection_url(
    collection: CollectionUrlCreate, db: AsyncSession
):
    """
    Create a new collection which type is url reference
    """
    # step 1: created to collection table
    user_id = 1  # TODO(Soulter): This should be replaced with actual user_id from request context or authentication

    db_collection = Collection(user_id=user_id)
    db.add(db_collection)
    await db.commit()
    await db.refresh(db_collection)

    url_detail = CollectionDetail(
        collection_id=db_collection.id, key="url", value=collection.url
    )
    db.add(url_detail)

    yield CollectionUrlResponseDelta(
        type="collection_created",
        data={
            "id": db_collection.id,
            "user_id": db_collection.user_id,
            "created_at": db_collection.created_at.isoformat(),
            "updated_at": db_collection.updated_at.isoformat(),
        },
    )

    # step 2: fetching the content of the url
    content = await markdownit_helper.markdownit(collection.url)

    content_detail = CollectionDetail(
        collection_id=db_collection.id, key="content", value=content
    )
    db.add(content_detail)

    logger.info(
        f"Fetched content from {collection.url}, length: {len(content)}: {content[:50]}..."
    )

    yield CollectionUrlResponseDelta(
        type="content_fetched",
        data={
            "url": collection.url,
            "content": f"{content[:100]}...",
        },
    )

    # step 2.5: get categories from db
    categories_query = select(Category.name, Category.emoji).order_by(Category.name)
    categories_result = await db.execute(categories_query)
    categories = [row[0] for row in categories_result.all()]
    category_emojis = [row[1] for row in categories_result.all()]

    categories_str = ", ".join(
        [f"{cat}({emoji})" for cat, emoji in zip(categories, category_emojis)]
    )
    cate_sys_prompt = PROMPT_PARSE_CATEGORY_AND_TAGS.format(categories=categories_str)

    # step 3: llm analyze the category and tags
    cate_llm_resp = await provider_openai.text_chat(
        prompt=content,
        system_prompt=cate_sys_prompt,
    )
    cate_json = parse_json(cate_llm_resp.completion_text)
    category: str = cate_json.get("category", "")
    category_emoji: str = cate_json.get("category_emoji", "")
    tags: list = cate_json.get("tags", [])

    # save to category if not exists
    db_category = await db.execute(
        select(Category).where(Category.name == category)
    )
    if category and not db_category.scalar_one_or_none():
        new_category = Category(name=category, emoji=category_emoji, user_id=user_id)
        db.add(new_category)
        await db.commit()
        await db.refresh(new_category)
        logger.info(f"New category created: {new_category.name}")

    yield CollectionUrlResponseDelta(
        type="category_analyzed",
        data={
            "category": category,
            "tags": tags,
        },
    )

    # get category_id
    category_query = select(Category.id).where(Category.name == category)
    category_result = await db.execute(category_query)
    category_id = category_result.scalar_one_or_none()

    # step 2.5: update collection with category and tags
    if not category_id:
        category_id = -1

    db_collection.category_id = category_id # type: ignore
    db_collection.tags = ",".join(tags) # type: ignore
    db.add(db_collection)

    await db.commit()

    # step 3: llm summarize the content, using streaming
    summary_sys_prompt = PROMPT_SUMMARIZE_CONTENT
    summary_llm_resp = provider_openai.text_chat_stream(
        prompt=content,
        system_prompt=summary_sys_prompt,
    )
    full_summary = ""
    async for chunk in summary_llm_resp:
        full_summary += chunk.completion_text
        yield CollectionUrlResponseDelta(
            type="summary_chunk",
            data={
                "summary": chunk.completion_text,
            },
        )
    
    summary_detail = CollectionDetail(
        collection_id=db_collection.id, key="summary", value=full_summary
    )
    db.add(summary_detail)
    await db.commit()

    yield CollectionUrlResponseDelta(
        type="index_completed",
        data={
            "collection_id": db_collection.id,
        },
    )


@router.post(
    "/url",
    response_model=CollectionUrlResponseDelta,
    status_code=status.HTTP_201_CREATED,
)
async def create_collection_url(
    event: CollectionUrlCreate, db: AsyncSession = Depends(get_db)
):
    """
    Create a new collection which type is url reference
    """

    async def steaming():
        async for delta in streaming_create_collection_url(event, db):
            data = delta.model_dump_json()
            yield f"data: {data}\n\n"

    return StreamingResponse(steaming(), media_type="text/event-stream")


# Create user events router
user_events_router = APIRouter(
    prefix="/users/{user_id}/collections",
    tags=["collections"],
    responses={404: {"description": "Not found"}},
)


@user_events_router.get("/", response_model=Response)
async def get_user_collections(user_id: int, category_id: int | None = None, db: AsyncSession = Depends(get_db)):
    """
    Get all collections for a specific user
    """
    # Check if user exists
    user_query = select(User).where(User.id == user_id)
    if category_id:
        user_query = user_query.where(Collection.category_id == category_id)
    user_result = await db.execute(user_query)
    user = user_result.first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found",
        )

    # Get user's collections
    collections_query = (
        select(Collection)
        .where(Collection.user_id == user_id)
        .options(selectinload(Collection.details))
        .order_by(desc(Collection.created_at))
    )
    collections_result = await db.execute(collections_query)
    collections = collections_result.scalars().unique().all()

    return Response(
        status="success",
        message="Collections retrieved successfully",
        data={
            "collections": [
                {
                    "id": collection.id,
                    "category_id": collection.category_id,
                    "tags": collection.tags,
                    "details": {
                        detail.key: detail.value for detail in collection.details
                    },
                    "created_at": collection.created_at.isoformat(),
                    "updated_at": collection.updated_at.isoformat(),
                }
                for collection in collections
            ]
        },
    )

# 详情相关路由
@router.get("/{collection_id}/details", response_model=Response)
async def get_collection_details(collection_id: int, db: AsyncSession = Depends(get_db)):
    details_query = select(CollectionDetail).where(CollectionDetail.collection_id == collection_id)
    details_result = await db.execute(details_query)
    details = details_result.scalars().all()
    return Response(
        status="success",
        message="Collection details fetched successfully",
        data={"details": {d.key: d.value for d in details}}
    )

@router.get("/{collection_id}/details/{key}", response_model=Response)
async def get_collection_detail(collection_id: int, key: str, db: AsyncSession = Depends(get_db)):
    detail_query = select(CollectionDetail).where(CollectionDetail.collection_id == collection_id, CollectionDetail.key == key)
    detail_result = await db.execute(detail_query)
    detail = detail_result.scalar_one_or_none()
    if not detail:
        raise HTTPException(status_code=404, detail="Detail not found")
    return Response(
        status="success",
        message="Collection detail fetched successfully",
        data={"key": detail.key, "value": detail.value}
    )

@router.put("/{collection_id}/details/{key}", response_model=Response)
async def update_collection_detail(collection_id: int, key: str, update: CollectionDetailUpdate, db: AsyncSession = Depends(get_db)):
    detail_query = select(CollectionDetail).where(CollectionDetail.collection_id == collection_id, CollectionDetail.key == key)
    detail_result = await db.execute(detail_query)
    detail = detail_result.scalar_one_or_none()
    if detail:
        detail.value = update.value
        db.add(detail)
        await db.commit()
        await db.refresh(detail)
        msg = "Detail updated successfully"
    else:
        detail = CollectionDetail(collection_id=collection_id, key=key, value=update.value)
        db.add(detail)
        await db.commit()
        await db.refresh(detail)
        msg = "Detail created successfully"
    return Response(
        status="success",
        message=msg,
        data={"key": detail.key, "value": detail.value}
    )

@router.delete("/{collection_id}/details/{key}", response_model=Response)
async def delete_collection_detail(collection_id: int, key: str, db: AsyncSession = Depends(get_db)):
    detail_query = select(CollectionDetail).where(CollectionDetail.collection_id == collection_id, CollectionDetail.key == key)
    detail_result = await db.execute(detail_query)
    detail = detail_result.scalar_one_or_none()
    if not detail:
        raise HTTPException(status_code=404, detail="Detail not found")
    await db.delete(detail)
    await db.commit()
    return Response(
        status="success",
        message="Detail deleted successfully",
        data={"key": key}
    )

@router.get("/{collection_id}/tags", response_model=Response)
async def get_collection_tags(collection_id: int, db: AsyncSession = Depends(get_db)):
    collection_query = select(Collection).where(Collection.id == collection_id)
    collection_result = await db.execute(collection_query)
    collection = collection_result.scalar_one_or_none()
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    tags = collection.tags.split(",") if collection.tags else []
    return Response(
        status="success",
        message="Collection tags fetched successfully",
        data={"tags": tags}
    )

@router.put("/{collection_id}/tags", response_model=Response)
async def update_collection_tags(collection_id: int, update: CollectionTagsUpdate, db: AsyncSession = Depends(get_db)):
    collection_query = select(Collection).where(Collection.id == collection_id)
    collection_result = await db.execute(collection_query)
    collection = collection_result.scalar_one_or_none()
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    collection.tags = ",".join(update.tags)
    db.add(collection)
    await db.commit()
    await db.refresh(collection)
    return Response(
        status="success",
        message="Collection tags updated successfully",
        data={"tags": update.tags}
    )