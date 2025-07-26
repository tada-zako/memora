from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import desc, select, and_, func
from sqlalchemy.orm import selectinload
from entity.response import Response
from pydantic import BaseModel
from loguru import logger
from typing import Optional, List

from model import (
    User,
    Collection,
    Category,
    CollectionDetail,
    CollectionLike,
    CollectionComment,
)
from db import get_db
from routers.auth import get_current_user

# Create router instance
router = APIRouter(
    prefix="/community",
    tags=["community"],
    responses={404: {"description": "Not found"}},
)


class ShareCollectionRequest(BaseModel):
    description: Optional[str] = None


class CreateCommentRequest(BaseModel):
    content: str


class CommentResponse(BaseModel):
    id: int
    content: str
    user_id: int
    username: str
    created_at: str
    updated_at: str


class SharedCollectionResponse(BaseModel):
    id: int
    user_id: int
    username: str
    category_id: Optional[int]
    category_name: Optional[str]
    tags: Optional[str]
    shared_description: Optional[str]
    likes_count: int
    comments_count: int
    is_liked_by_me: bool
    details: dict
    created_at: str
    updated_at: str


@router.post("/{collection_id}/share", response_model=Response)
async def share_collection(
    collection_id: int,
    request: ShareCollectionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    分享收藏到社区
    """
    # 检查收藏是否属于当前用户
    collection_query = select(Collection).where(
        Collection.id == collection_id,
        Collection.user_id == current_user.id
    )
    collection_result = await db.execute(collection_query)
    collection = collection_result.scalar_one_or_none()
    
    if not collection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="收藏不存在或您无权访问"
        )
    
    if collection.is_shared:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该收藏已经分享到社区"
        )
    
    # 更新分享状态
    collection.is_shared = True
    collection.shared_description = request.description
    db.add(collection)
    await db.commit()
    
    return Response(
        status="success",
        message="收藏已成功分享到社区",
        data={
            "collection_id": collection_id,
            "shared_description": request.description
        }
    )


@router.delete("/{collection_id}/share", response_model=Response)
async def unshare_collection(
    collection_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    取消分享收藏
    """
    # 检查收藏是否属于当前用户
    collection_query = select(Collection).where(
        Collection.id == collection_id,
        Collection.user_id == current_user.id
    )
    collection_result = await db.execute(collection_query)
    collection = collection_result.scalar_one_or_none()
    
    if not collection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="收藏不存在或您无权访问"
        )
    
    if not collection.is_shared:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该收藏未分享到社区"
        )
    
    # 取消分享状态
    collection.is_shared = False
    collection.shared_description = None
    db.add(collection)
    await db.commit()
    
    return Response(
        status="success",
        message="已取消分享该收藏",
        data={"collection_id": collection_id}
    )


@router.get("/shared", response_model=Response)
async def get_shared_collections(
    page: int = 1,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取所有已分享的收藏（社区页面）
    """
    offset = (page - 1) * limit
    
    # 获取已分享的收藏，包含用户信息、分类信息、点赞数、评论数
    collections_query = (
        select(
            Collection,
            User.username,
            Category.name.label('category_name'),
            func.count(CollectionLike.id).label('likes_count'),
            func.count(CollectionComment.id).label('comments_count')
        )
        .join(User, Collection.user_id == User.id)
        .outerjoin(Category, Collection.category_id == Category.id)
        .outerjoin(CollectionLike, Collection.id == CollectionLike.collection_id)
        .outerjoin(CollectionComment, Collection.id == CollectionComment.collection_id)
        .where(Collection.is_shared == True)
        .group_by(Collection.id, User.username, Category.name)
        .order_by(desc(Collection.updated_at))
        .offset(offset)
        .limit(limit)
    )
    
    collections_result = await db.execute(collections_query)
    collections_data = collections_result.all()
    
    shared_collections = []
    for row in collections_data:
        collection = row[0]
        username = row[1]
        category_name = row[2]
        likes_count = row[3]
        comments_count = row[4]
        
        # 检查当前用户是否已点赞
        like_query = select(CollectionLike).where(
            and_(
                CollectionLike.collection_id == collection.id,
                CollectionLike.user_id == current_user.id
            )
        )
        like_result = await db.execute(like_query)
        is_liked_by_me = like_result.scalar_one_or_none() is not None
        
        # 获取收藏详情
        details_query = select(CollectionDetail).where(
            CollectionDetail.collection_id == collection.id
        )
        details_result = await db.execute(details_query)
        details = details_result.scalars().all()
        
        shared_collections.append(
            SharedCollectionResponse(
                id=collection.id,
                user_id=collection.user_id,
                username=username,
                category_id=collection.category_id,
                category_name=category_name,
                tags=collection.tags,
                shared_description=collection.shared_description,
                likes_count=likes_count,
                comments_count=comments_count,
                is_liked_by_me=is_liked_by_me,
                details={detail.key: detail.value for detail in details},
                created_at=collection.created_at.isoformat(),
                updated_at=collection.updated_at.isoformat()
            )
        )
    
    return Response(
        status="success",
        message="已分享收藏列表获取成功",
        data={
            "collections": shared_collections,
            "page": page,
            "limit": limit
        }
    )


@router.post("/{collection_id}/like", response_model=Response)
async def like_collection(
    collection_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    点赞收藏
    """
    # 检查收藏是否存在且已分享
    collection_query = select(Collection).where(
        Collection.id == collection_id,
        Collection.is_shared == True
    )
    collection_result = await db.execute(collection_query)
    collection = collection_result.scalar_one_or_none()
    
    if not collection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="收藏不存在或未分享"
        )
    
    # 检查是否已点赞
    existing_like_query = select(CollectionLike).where(
        and_(
            CollectionLike.collection_id == collection_id,
            CollectionLike.user_id == current_user.id
        )
    )
    existing_like_result = await db.execute(existing_like_query)
    existing_like = existing_like_result.scalar_one_or_none()
    
    if existing_like:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="您已经点赞过该收藏"
        )
    
    # 创建点赞记录
    new_like = CollectionLike(
        collection_id=collection_id,
        user_id=current_user.id
    )
    db.add(new_like)
    await db.commit()
    
    return Response(
        status="success",
        message="点赞成功",
        data={"collection_id": collection_id}
    )


@router.delete("/{collection_id}/like", response_model=Response)
async def unlike_collection(
    collection_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    取消点赞收藏
    """
    # 查找现有点赞记录
    like_query = select(CollectionLike).where(
        and_(
            CollectionLike.collection_id == collection_id,
            CollectionLike.user_id == current_user.id
        )
    )
    like_result = await db.execute(like_query)
    like = like_result.scalar_one_or_none()
    
    if not like:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="您还未点赞该收藏"
        )
    
    # 删除点赞记录
    await db.delete(like)
    await db.commit()
    
    return Response(
        status="success",
        message="取消点赞成功",
        data={"collection_id": collection_id}
    )


@router.get("/{collection_id}/likes", response_model=Response)
async def get_collection_likes(
    collection_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取收藏的点赞列表
    """
    # 检查收藏是否存在且已分享
    collection_query = select(Collection).where(
        Collection.id == collection_id,
        Collection.is_shared == True
    )
    collection_result = await db.execute(collection_query)
    collection = collection_result.scalar_one_or_none()
    
    if not collection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="收藏不存在或未分享"
        )
    
    # 获取点赞列表
    likes_query = (
        select(CollectionLike, User.username)
        .join(User, CollectionLike.user_id == User.id)
        .where(CollectionLike.collection_id == collection_id)
        .order_by(desc(CollectionLike.created_at))
    )
    likes_result = await db.execute(likes_query)
    likes_data = likes_result.all()
    
    likes = [
        {
            "id": like[0].id,
            "user_id": like[0].user_id,
            "username": like[1],
            "created_at": like[0].created_at.isoformat()
        }
        for like in likes_data
    ]
    
    return Response(
        status="success",
        message="点赞列表获取成功",
        data={
            "likes": likes,
            "total_count": len(likes)
        }
    )


@router.post("/{collection_id}/comment", response_model=Response)
async def create_comment(
    collection_id: int,
    request: CreateCommentRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    添加评论
    """
    # 检查收藏是否存在且已分享
    collection_query = select(Collection).where(
        Collection.id == collection_id,
        Collection.is_shared == True
    )
    collection_result = await db.execute(collection_query)
    collection = collection_result.scalar_one_or_none()
    
    if not collection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="收藏不存在或未分享"
        )
    
    # 创建评论
    new_comment = CollectionComment(
        collection_id=collection_id,
        user_id=current_user.id,
        content=request.content
    )
    db.add(new_comment)
    await db.commit()
    await db.refresh(new_comment)
    
    return Response(
        status="success",
        message="评论添加成功",
        data={
            "comment": CommentResponse(
                id=new_comment.id,
                content=new_comment.content,
                user_id=new_comment.user_id,
                username=current_user.username,
                created_at=new_comment.created_at.isoformat(),
                updated_at=new_comment.updated_at.isoformat()
            )
        }
    )


@router.get("/{collection_id}/comments", response_model=Response)
async def get_collection_comments(
    collection_id: int,
    page: int = 1,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取收藏的评论列表
    """
    # 检查收藏是否存在且已分享
    collection_query = select(Collection).where(
        Collection.id == collection_id,
        Collection.is_shared == True
    )
    collection_result = await db.execute(collection_query)
    collection = collection_result.scalar_one_or_none()
    
    if not collection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="收藏不存在或未分享"
        )
    
    offset = (page - 1) * limit
    
    # 获取评论列表
    comments_query = (
        select(CollectionComment, User.username)
        .join(User, CollectionComment.user_id == User.id)
        .where(CollectionComment.collection_id == collection_id)
        .order_by(desc(CollectionComment.created_at))
        .offset(offset)
        .limit(limit)
    )
    comments_result = await db.execute(comments_query)
    comments_data = comments_result.all()
    
    comments = [
        CommentResponse(
            id=comment[0].id,
            content=comment[0].content,
            user_id=comment[0].user_id,
            username=comment[1],
            created_at=comment[0].created_at.isoformat(),
            updated_at=comment[0].updated_at.isoformat()
        )
        for comment in comments_data
    ]
    
    return Response(
        status="success",
        message="评论列表获取成功",
        data={
            "comments": comments,
            "page": page,
            "limit": limit
        }
    )


@router.delete("/comment/{comment_id}", response_model=Response)
async def delete_comment(
    comment_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    删除评论（只能删除自己的评论）
    """
    # 查找评论
    comment_query = select(CollectionComment).where(
        CollectionComment.id == comment_id,
        CollectionComment.user_id == current_user.id
    )
    comment_result = await db.execute(comment_query)
    comment = comment_result.scalar_one_or_none()
    
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="评论不存在或您无权删除"
        )
    
    # 删除评论
    await db.delete(comment)
    await db.commit()
    
    return Response(
        status="success",
        message="评论删除成功",
        data={"comment_id": comment_id}
    ) 