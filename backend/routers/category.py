import uuid
import asyncio
from fastapi import APIRouter, HTTPException, Depends, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from typing import Optional
from pydantic import BaseModel
from loguru import logger

from backend.entity.response import Response
from backend.model import Category, User, CollectionDetail, Collection
from backend.db import get_db, AsyncSessionLocal
from backend.routers.auth import get_current_user
from backend.knowledge_base.chromadb_mgr import chroma_db_manager
from backend.ai.openai_provider import provider_openai
from backend.ai.PROMPTS import KNOWLEDGE_BASE_QUERY_PROMPT, COLLECTION_SEARCH_PROMPT
from backend.utils.text_splitter import recursive_text_splitter

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
        code=200,
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

    stmt = (
        select(Category, func.count(Collection.id))
        .outerjoin(Collection, Category.id == Collection.category_id)
        .where(Category.user_id == user_id)
        .group_by(Category.id)
        .order_by(Category.name)
    )
    result = await db.execute(stmt)
    categories_with_counts = result.all()

    return Response(
        code=200,
        message="Categories retrieved successfully",
        data={
            "categories": [
                {
                    "id": category.id,
                    "user_id": category.user_id,
                    "name": category.name,
                    "emoji": category.emoji,
                    "knowledge_base_id": category.knowledge_base_id,
                    "collection_count": collection_count,
                }
                for category, collection_count in categories_with_counts
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
        code=200,
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
        code=200,
        message="Category deleted successfully",
        data=None,
    )


# 创建知识库
@router.post("/create_knowledge_base")
async def create_knowledge_base(
    background_tasks: BackgroundTasks,
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
            detail=f"Category with id {category_id} not found",
        )

    if category.knowledge_base_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Knowledge base already exists for category {category_id}",
        )

    # 立即返回响应
    background_tasks.add_task(create_knowledge_base_task, category_id, current_user.id)

    return Response(code=200, message="Knowledge base creation started", data=None)


async def create_knowledge_base_task(category_id: int, user_id: int):
    """
    Background task to create knowledge base
    """
    async with AsyncSessionLocal() as db:
        try:
            category = await db.get(Category, category_id)
            if not category:
                logger.error(f"Category {category_id} not found during background task")
                return

            collection_name = f"kb_{uuid.uuid4()}"

            # 将 ChromaDB 创建集合操作放到线程池
            await asyncio.to_thread(
                chroma_db_manager.create_collection, collection_name
            )

            # TODO(Soulter): 优化 SQL
            stmt = (
                select(CollectionDetail)
                .join(Collection, CollectionDetail.collection_id == Collection.id)
                .where(
                    Collection.category_id == category_id,
                    Collection.user_id == user_id,
                    CollectionDetail.key == "content",
                )
            )
            result = await db.execute(stmt)
            details = result.scalars().all()
            content_list = [str(detail.value) for detail in details]

            # 将文本分割操作放到线程池
            def split_texts():
                chunked_content_list = []
                for content in content_list:
                    if isinstance(content, str) and content.strip():
                        chunked_content_list.extend(
                            recursive_text_splitter.split_text(content)
                        )
                return chunked_content_list

            chunked_content_list = await asyncio.to_thread(split_texts)

            logger.info(
                f"Creating knowledge base for category {category_id} with {len(chunked_content_list)} chunks"
            )

            # 将 ChromaDB upsert 操作放到线程池
            def upsert_documents():
                chroma_db_manager.upsert(
                    collection_name=collection_name,
                    documents=chunked_content_list,
                    ids=[str(uuid.uuid4()) for _ in chunked_content_list],
                )

            await asyncio.to_thread(upsert_documents)

            # Update the category with the knowledge base ID
            category.knowledge_base_id = collection_name  # type: ignore
            db.add(category)
            await db.commit()
            await db.refresh(category)

            logger.info(
                f"Knowledge base created successfully for category {category_id}"
            )
        except Exception as e:
            logger.error(
                f"Failed to create knowledge base for category {category_id}: {e}"
            )
            # TODO: 可以添加错误状态到数据库或通知机制


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
    try:
        # Get the category to find its knowledge base ID
        category = await db.get(Category, category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category {category_id} not found",
            )

        if not category.knowledge_base_id:  # type: ignore
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Knowledge base for category {category_id} not found. Please create knowledge base first.",
            )

        collection_name = category.knowledge_base_id

        # Query the knowledge base (放到线程池中执行)
        results = await asyncio.to_thread(
            chroma_db_manager.query,
            collection_name=collection_name,
            query=query,
            n_results=5,
        )

        logger.info(
            f"Querying knowledge base '{collection_name}' with query: {query}, found {len(results.get('documents', [[]])[0])} documents"
        )

        documents = (
            results["documents"][0]
            if results.get("documents") and len(results["documents"]) > 0
            else []
        )

        if not documents:
            logger.warning(
                f"No documents found for query: {query} in collection: {collection_name}"
            )
            return Response(
                code=200,
                message="No relevant documents found",
                data={
                    "response": "抱歉，在知识库中没有找到相关信息。请尝试使用不同的关键词或创建更多内容。",
                    "documents": [],
                },
            )

        documents_str = ""
        for doc in documents:
            if doc and doc.strip():
                documents_str += f"{doc}\n\n"

        if not documents_str.strip():
            logger.warning(f"All documents are empty for query: {query}")
            return Response(
                code=200,
                message="Documents found but all are empty",
                data={
                    "response": "找到了一些内容，但内容为空。请检查知识库中的文档。",
                    "documents": documents,
                },
            )

        system_prompt = KNOWLEDGE_BASE_QUERY_PROMPT.format(documents=documents_str)

        # Ask AI
        ai_response = await provider_openai.text_chat(
            prompt=query,
            system_prompt=system_prompt,
        )

        if not ai_response or not ai_response.completion_text:
            logger.error(f"AI response is empty for query: {query}")
            return Response(
                code=500,
                message="AI response is empty",
                data={
                    "response": "AI暂时无法生成回答，请稍后重试。",
                    "documents": documents,
                },
            )

        return Response(
            code=200,
            message="Knowledge base queried successfully",
            data={
                "response": ai_response.completion_text.strip(),
                "documents": documents,
            },
        )

    except HTTPException:
        # 重新抛出 HTTP 异常
        raise
    except Exception as e:
        logger.error(f"Unexpected error in query_knowledge_base: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )


# AI查找用户需要的收藏
@router.get("/search_collections")
async def search_collections(
    query: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Search for collections that match the user's query using AI

    返回示例：
    {
        "code": 200,
        "message": "Collection found successfully",
        "data": {
            "collection": {
            "id": "collection_id",
            "user_id": "user_id",
            "category_id": "category_id", 
            "created_at": "timestamp",
            "details": {"url": "...", "title": "...", ...}
            },
            "category": {
            "id": "category_id",
            "name": "category_name",
            "emoji": "emoji",
            "knowledge_base_id": "kb_id"
            },
            "search_info": {
            "confidence": "high|medium|low",
            "reason": "AI匹配理由",
            "query": "用户查询"
            }
        }
    }
    """
    try:
        user_id = current_user.id

        # 查询用户的所有collection和相关的details
        stmt = (
            select(Collection)
            .where(Collection.user_id == user_id)
            .options(selectinload(Collection.details))
        )

        result = await db.execute(stmt)
        collections_data = result.scalars().all()

        if not collections_data:
            return Response(
                code=404,
                message="No collections found",
                data={
                    "collection": None,
                    "category": None,
                    "message": "您还没有任何收藏，请先添加一些内容。",
                },
            )

        # 构建上下文字符串
        collections_context = ""
        for item in collections_data:
            # 获取URL
            url_detail = next(
                (detail.value for detail in item.details if detail.key == "url"), None
            )
            # 获取Title
            title_detail = next(
                (detail.value for detail in item.details if detail.key == "title"), None
            )
            # 获取Summary
            summary_detail = next(
                (detail.value for detail in item.details if detail.key == "summary"),
                None,
            )

            collections_context += f"Collection ID: {item.id}\n"
            collections_context += f"URL: {url_detail or 'N/A'}\n"
            collections_context += f"Title: {title_detail or 'N/A'}\n"
            collections_context += f"Summary: {summary_detail or 'N/A'}\n"
            collections_context += "---\n"

        # 使用AI分析查询
        system_prompt = COLLECTION_SEARCH_PROMPT.format(
            query=query, collections_context=collections_context
        )

        ai_response = await provider_openai.text_chat(
            prompt=f"Please find the most relevant collection for this query: {query}",
            system_prompt=system_prompt,
        )

        if not ai_response or not ai_response.completion_text:
            logger.error(f"AI response is empty for search query: {query}")
            return Response(
                code=500,
                message="AI search failed",
                data={
                    "collection": None,
                    "category": None,
                    "message": "AI搜索暂时不可用，请稍后重试。",
                },
            )

        # 解析AI响应
        try:
            from backend.ai.PROMPTS import parse_json

            ai_result = parse_json(ai_response.completion_text)
            collection_id = ai_result.get("collection_id")
            confidence = ai_result.get("confidence", "unknown")
            reason = ai_result.get("reason", "No reason provided")

            if not collection_id or collection_id == "null":
                return Response(
                    code=200,
                    message="No relevant collection found",
                    data={
                        "collection": None,
                        "category": None,
                        "message": "没有找到与您查询相关的收藏，请尝试使用不同的关键词。",
                        "confidence": confidence,
                        "reason": reason,
                    },
                )

            # 查询找到的collection及其category信息
            collection = None
            for item in collections_data:
                if item.id.scalar() == int(collection_id):
                    collection = item
                    break

            if not collection:
                return Response(
                    code=404,
                    message="Collection not found",
                    data={
                        "collection": None,
                        "category": None,
                        "message": "找到的收藏不存在或不属于您。",
                    },
                )

            stmt = (
                select(Category)
                .join(Collection)
                .where(Collection.id == collection.id, Collection.user_id == user_id)
            )
            result = await db.execute(stmt)
            category = result.scalar_one_or_none()

            # 获取collection的所有details
            details = collection.details

            # 构建details字典
            details_dict = {}
            for detail in details:
                details_dict[detail.key] = detail.value

            return Response(
                code=200,
                message="Collection found successfully",
                data={
                    "collection": {
                        "id": collection.id,
                        "user_id": collection.user_id,
                        "category_id": collection.category_id,
                        "created_at": (collection.created_at.isoformat()),
                        "details": details_dict,
                    },
                    "category": (
                        {
                            "id": category.id,
                            "name": category.name,
                            "emoji": category.emoji,
                            "knowledge_base_id": category.knowledge_base_id,
                        }
                        if category
                        else None
                    ),
                    "search_info": {
                        "confidence": confidence,
                        "reason": reason,
                        "query": query,
                    },
                },
            )

        except (ValueError, KeyError) as e:
            logger.error(f"Failed to parse AI response: {e}")
            return Response(
                code=500,
                message="Failed to parse AI response",
                data={
                    "collection": None,
                    "category": None,
                    "message": "AI响应解析失败，请稍后重试。",
                },
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in search_collections: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )
