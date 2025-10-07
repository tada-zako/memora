from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import desc, select, and_, func
from pydantic import BaseModel
from typing import Optional
from datetime import timezone, datetime
from loguru import logger

from backend.entity.response import Response
from backend.model import (
    User,
    Collection,
    Category,
    CollectionDetail,
    Post,
    Comment,
    Like,
    AssetType,
)
from backend.db import get_db
from backend.routers.auth import get_current_user
from backend.ai.openai_provider import provider_openai
from backend.ai.PROMPTS import (
    PROMPT_PARSE_CATEGORY_AND_TAGS,
    ADDITIONAL_PROMPT_USER_LANGUAGE_PREFERENCE,
    PROMPT_RECOMMEND_POSTS,
    parse_json,
)

# 推荐缓存：存储每个用户的推荐结果
# 格式：{user_id: {"posts": [...], "timestamp": datetime}}
_recommendation_cache = {}
CACHE_DURATION_SECONDS = 300  # 5分钟缓存

# Create router instance
router = APIRouter(
    prefix="/community",
    tags=["community"],
    responses={404: {"description": "Not found"}},
)


# Request/Response Models
class CreatePostRequest(BaseModel):
    refer_collection_id: int
    description: Optional[str] = None


class CreateCommentRequest(BaseModel):
    content: str


class LikeRequest(BaseModel):
    asset_id: int
    asset_type: str  # 'post' or 'comment'


class UserInfo(BaseModel):
    id: int
    username: str
    avatar_attachment_id: Optional[str] = None


class CommentResponse(BaseModel):
    id: int
    content: str
    user_id: int
    username: str
    avatar_attachment_id: Optional[str] = None
    likes_count: int
    is_liked_by_me: bool
    created_at: str
    updated_at: str
    user: Optional[UserInfo] = None


class PostResponse(BaseModel):
    id: int
    post_id: str  # UUID
    description: Optional[str]
    user_id: int
    username: str
    avatar_attachment_id: Optional[str] = None
    refer_collection_id: int
    collection_details: dict
    category_id: Optional[int]
    category_name: Optional[str]
    tags: Optional[str]
    likes_count: int
    comments_count: int
    is_liked_by_me: bool
    created_at: str
    updated_at: str
    user: Optional[UserInfo] = None


# 辅助函数：获取推文详细信息
async def _fetch_post_details(
    post_ids: list[int],
    current_user: User,
    db: AsyncSession
) -> list[PostResponse]:
    """
    根据post IDs获取完整的推文详细信息
    """
    if not post_ids:
        return []

    # 获取推文详细信息
    posts_query = (
        select(
            Post,
            User,
            Collection,
            Category.name.label("category_name"),
            func.count(Like.id.distinct()).label("likes_count"),
            func.count(Comment.id.distinct()).label("comments_count"),
        )
        .join(User, Post.user_id == User.id)
        .join(Collection, Post.refer_collection_id == Collection.id)
        .outerjoin(Category, Collection.category_id == Category.id)
        .outerjoin(Like, and_(Like.asset_id == Post.id, Like.asset_type == AssetType.post))
        .outerjoin(Comment, Comment.post_id == Post.id)
        .where(Post.id.in_(post_ids))
        .group_by(
            Post.id, User.id, User.username, User.avatar_attachment_id, Collection.id, Category.name
        )
    )

    posts_result = await db.execute(posts_query)
    posts_data = posts_result.all()

    # 按照提供的顺序排序
    posts_dict = {}
    for row in posts_data:
        posts_dict[row[0].id] = row

    posts = []
    for post_id in post_ids:
        if post_id not in posts_dict:
            continue

        row = posts_dict[post_id]
        post = row[0]
        user = row[1]
        collection = row[2]
        category_name = row[3]
        likes_count = row[4]
        comments_count = row[5]

        # 检查当前用户是否已点赞
        like_query = select(Like).where(
            and_(
                Like.asset_id == post.id,
                Like.asset_type == AssetType.post,
                Like.user_id == current_user.id,
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

        posts.append(
            PostResponse(
                id=post.id,
                post_id=post.post_id,
                description=post.description,
                user_id=post.user_id,
                username=user.username,
                avatar_attachment_id=user.avatar_attachment_id,
                refer_collection_id=post.refer_collection_id,
                collection_details={detail.key: detail.value for detail in details},
                category_id=collection.category_id,
                category_name=category_name,
                tags=collection.tags,
                likes_count=likes_count,
                comments_count=comments_count,
                is_liked_by_me=is_liked_by_me,
                created_at=post.created_at.replace(tzinfo=timezone.utc).isoformat(),
                updated_at=post.updated_at.replace(tzinfo=timezone.utc).isoformat(),
                user=UserInfo(
                    id=user.id,
                    username=user.username,
                    avatar_attachment_id=user.avatar_attachment_id,
                ),
            )
        )

    return posts


@router.post("/posts", response_model=Response)
async def create_post(
    request: CreatePostRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    创建推文（发布收藏到社区）
    支持同一收藏多次分享
    """
    # 检查收藏是否属于当前用户
    collection_query = select(Collection).where(
        Collection.id == request.refer_collection_id, Collection.user_id == current_user.id
    )
    collection_result = await db.execute(collection_query)
    collection = collection_result.scalar_one_or_none()

    if not collection:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="收藏不存在或您无权访问")

    # 创建推文（允许同一收藏多次分享）
    new_post = Post(
        user_id=current_user.id,
        refer_collection_id=request.refer_collection_id,
        description=request.description,
    )
    db.add(new_post)
    await db.commit()
    await db.refresh(new_post)

    return Response(
        code=200,
        message="推文发布成功",
        data={
            "post_id": new_post.post_id,
            "refer_collection_id": new_post.refer_collection_id,
            "description": new_post.description,
        },
    )


@router.delete("/posts/{post_id}", response_model=Response)
async def delete_post(
    post_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),  # 使用UUID字符串
):
    """
    删除推文（只能删除自己的推文）
    """
    post_query = select(Post).where(Post.post_id == post_id, Post.user_id == current_user.id)
    post_result = await db.execute(post_query)
    post = post_result.scalar_one_or_none()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="推文不存在或您无权删除")

    await db.delete(post)
    await db.commit()

    return Response(code=200, message="推文删除成功", data={"post_id": post_id})


@router.get("/posts-latest", response_model=Response)
async def get_latest_posts(
    page: int = 1,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    获取社区最新推文列表
    """
    offset = (page - 1) * limit

    # 获取推文列表，包含用户信息、收藏信息、分类信息、点赞数、评论数
    posts_query = (
        select(
            Post,
            User,
            Collection,
            Category.name.label("category_name"),
            func.count(Like.id.distinct()).label("likes_count"),
            func.count(Comment.id.distinct()).label("comments_count"),
        )
        .join(User, Post.user_id == User.id)
        .join(Collection, Post.refer_collection_id == Collection.id)
        .outerjoin(Category, Collection.category_id == Category.id)
        .outerjoin(Like, and_(Like.asset_id == Post.id, Like.asset_type == AssetType.post))
        .outerjoin(Comment, Comment.post_id == Post.id)
        .group_by(
            Post.id, User.id, User.username, User.avatar_attachment_id, Collection.id, Category.name
        )
        .order_by(desc(Post.created_at))
        .offset(offset)
        .limit(limit)
    )

    posts_result = await db.execute(posts_query)
    posts_data = posts_result.all()

    posts = []
    for row in posts_data:
        post = row[0]
        user = row[1]
        collection = row[2]
        category_name = row[3]
        likes_count = row[4]
        comments_count = row[5]

        # 检查当前用户是否已点赞
        like_query = select(Like).where(
            and_(
                Like.asset_id == post.id,
                Like.asset_type == AssetType.post,
                Like.user_id == current_user.id,
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

        posts.append(
            PostResponse(
                id=post.id,
                post_id=post.post_id,
                description=post.description,
                user_id=post.user_id,
                username=user.username,
                avatar_attachment_id=user.avatar_attachment_id,
                refer_collection_id=post.refer_collection_id,
                collection_details={detail.key: detail.value for detail in details},
                category_id=collection.category_id,
                category_name=category_name,
                tags=collection.tags,
                likes_count=likes_count,
                comments_count=comments_count,
                is_liked_by_me=is_liked_by_me,
                created_at=post.created_at.replace(tzinfo=timezone.utc).isoformat(),
                updated_at=post.updated_at.replace(tzinfo=timezone.utc).isoformat(),
                user=UserInfo(
                    id=user.id,
                    username=user.username,
                    avatar_attachment_id=user.avatar_attachment_id,
                ),
            )
        )

    return Response(
        code=200, message="推文列表获取成功", data={"posts": posts, "page": page, "limit": limit}
    )


@router.get("/posts-recommended", response_model=Response)
async def get_recommended_posts(
    page: int = 1,
    limit: int = 20,
    top_k_categories: int = 5,
    top_m_posts: int = 50,
    max_n_recommendations: int = 10,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    获取社区推荐推文列表（基于用户收藏分类的LLM推荐）

    参数：
    - page: 分页页码
    - limit: 每页数量
    - top_k_categories: 获取用户收藏数量最多的前k个分类 (默认5)
    - top_m_posts: 从最新的m个推文中选择 (默认50)
    - max_n_recommendations: LLM最多推荐n个推文 (默认10)

    缓存策略：每个用户的推荐结果缓存300秒
    """
    try:
        # 检查缓存
        user_id = current_user.id
        now = datetime.now(timezone.utc)

        if user_id in _recommendation_cache:
            cached_data = _recommendation_cache[user_id]
            cache_age = (now - cached_data["timestamp"]).total_seconds()

            if cache_age < CACHE_DURATION_SECONDS:
                logger.info(f"Recommendations cache used for user {user_id}, age: {cache_age:.0f}s")
                cached_post_ids = cached_data["post_ids"]

                # 应用分页
                offset = (page - 1) * limit
                paginated_post_ids = cached_post_ids[offset:offset + limit]

                if not paginated_post_ids:
                    return Response(
                        code=200,
                        message="推荐推文列表获取成功（来自缓存）",
                        data={"posts": [], "page": page, "limit": limit, "from_cache": True}
                    )

                # 获取推文详细信息（使用缓存的post_ids）
                posts = await _fetch_post_details(paginated_post_ids, current_user, db)

                return Response(
                    code=200,
                    message="推荐推文列表获取成功（来自缓存）",
                    data={"posts": posts, "page": page, "limit": limit, "from_cache": True}
                )
            else:
                logger.info(f"Recommendations cache expired for user {user_id}")

        # 1. 获取用户收藏数量最多的前k个分类
        user_categories_query = (
            select(Category.name, func.count(Collection.id).label("collection_count"))
            .join(Collection, Collection.category_id == Category.id)
            .where(Collection.user_id == current_user.id)
            .group_by(Category.id, Category.name)
            .order_by(desc("collection_count"))
            .limit(top_k_categories)
        )
        user_categories_result = await db.execute(user_categories_query)
        user_categories_data = user_categories_result.all()

        # 如果用户没有任何分类，返回最新推文作为默认推荐
        if not user_categories_data:
            logger.info(f"User {current_user.id} has no categories, returning latest posts")
            return await get_latest_posts(page, limit, current_user, db)

        # 构建用户分类信息字符串
        user_categories_str = "\n".join([
            f"- {row[0]} ({row[1]} collections)"
            for row in user_categories_data
        ])

        # 2. 获取最新的m个推文的基本信息
        latest_posts_query = (
            select(
                Post.id,
                Post.post_id,
                Collection.tags,
                CollectionDetail.value.label("title")
            )
            .join(Collection, Post.refer_collection_id == Collection.id)
            .outerjoin(
                CollectionDetail,
                and_(
                    CollectionDetail.collection_id == Collection.id,
                    CollectionDetail.key == "title"
                )
            )
            .order_by(desc(Post.created_at))
            .limit(top_m_posts)
        )
        latest_posts_result = await db.execute(latest_posts_query)
        latest_posts_data = latest_posts_result.all()

        if not latest_posts_data:
            return Response(
                code=200,
                message="暂无推荐推文",
                data={"posts": [], "page": page, "limit": limit}
            )

        # 构建推文信息字符串
        posts_info_str = "\n\n".join([
            f"Post ID: {row[0]}\nTitle: {row[3] or 'No title'}\nTags: {row[2] or 'No tags'}"
            for row in latest_posts_data
        ])

        # 3. 使用LLM进行推荐
        recommendation_prompt = PROMPT_RECOMMEND_POSTS.format(
            user_categories=user_categories_str,
            posts_info=posts_info_str,
            max_recommendations=max_n_recommendations
        )
        recommendation_prompt += f"\n\n{ADDITIONAL_PROMPT_USER_LANGUAGE_PREFERENCE}"

        llm_resp = await provider_openai.text_chat(
            prompt="Please analyze and provide recommendations.",
            system_prompt=recommendation_prompt,
        )

        recommendation_json = parse_json(llm_resp.completion_text)
        recommended_post_ids = recommendation_json.get("recommended_post_ids", [])

        logger.info(f"LLM recommended post IDs: {recommended_post_ids}")

        if not recommended_post_ids:
            logger.warning("LLM returned no recommendations, falling back to latest posts")
            return await get_latest_posts(page, limit, current_user, db)

        # 保存到缓存
        _recommendation_cache[user_id] = {
            "post_ids": recommended_post_ids,
            "timestamp": now
        }
        logger.info(f"Recommendations cache added for user {user_id}")

        # 4. 根据推荐的post IDs获取完整的推文信息
        # 应用分页
        offset = (page - 1) * limit
        paginated_post_ids = recommended_post_ids[offset:offset + limit]

        if not paginated_post_ids:
            return Response(
                code=200,
                message="推荐推文列表获取成功",
                data={"posts": [], "page": page, "limit": limit, "from_cache": False}
            )

        # 使用辅助函数获取推文详细信息
        posts = await _fetch_post_details(paginated_post_ids, current_user, db)

        return Response(
            code=200,
            message="推荐推文列表获取成功",
            data={"posts": posts, "page": page, "limit": limit, "from_cache": False}
        )

    except Exception as e:
        logger.error(f"Failed to get recommendations: {e}")
        # 如果推荐失败，返回最新推文作为降级方案
        return await get_latest_posts(page, limit, current_user, db)


@router.get("/my-posts", response_model=Response)
async def get_my_posts(
    page: int = 1,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    获取当前用户发送的推文列表
    """
    offset = (page - 1) * limit

    posts_query = (
        select(
            Post,
            User,
            Collection,
            Category.name.label("category_name"),
            func.count(Like.id.distinct()).label("likes_count"),
            func.count(Comment.id.distinct()).label("comments_count"),
        )
        .join(User, Post.user_id == User.id)
        .join(Collection, Post.refer_collection_id == Collection.id)
        .outerjoin(Category, Collection.category_id == Category.id)
        .outerjoin(Like, and_(Like.asset_id == Post.id, Like.asset_type == AssetType.post))
        .outerjoin(Comment, Comment.post_id == Post.id)
        .where(Post.user_id == current_user.id)
        .group_by(
            Post.id, User.id, User.username, User.avatar_attachment_id, Collection.id, Category.name
        )
        .order_by(desc(Post.created_at))
        .offset(offset)
        .limit(limit)
    )

    posts_result = await db.execute(posts_query)
    posts_data = posts_result.all()

    posts = []
    for row in posts_data:
        post = row[0]
        user = row[1]
        collection = row[2]
        category_name = row[3]
        likes_count = row[4]
        comments_count = row[5]

        # 检查当前用户是否已点赞
        like_query = select(Like).where(
            and_(
                Like.asset_id == post.id,
                Like.asset_type == AssetType.post,
                Like.user_id == current_user.id,
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

        posts.append(
            PostResponse(
                id=post.id,
                post_id=post.post_id,
                description=post.description,
                user_id=post.user_id,
                username=user.username,
                avatar_attachment_id=user.avatar_attachment_id,
                refer_collection_id=post.refer_collection_id,
                collection_details={detail.key: detail.value for detail in details},
                category_id=collection.category_id,
                category_name=category_name,
                tags=collection.tags,
                likes_count=likes_count,
                comments_count=comments_count,
                is_liked_by_me=is_liked_by_me,
                created_at=post.created_at.replace(tzinfo=timezone.utc).isoformat(),
                updated_at=post.updated_at.replace(tzinfo=timezone.utc).isoformat(),
                user=UserInfo(
                    id=user.id,
                    username=user.username,
                    avatar_attachment_id=user.avatar_attachment_id,
                ),
            )
        )

    return Response(
        code=200,
        message="当前用户推文列表获取成功",
        data={"posts": posts, "page": page, "limit": limit},
    )


@router.post("/like", response_model=Response)
async def like_asset(
    request: LikeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    点赞推文或评论
    """
    # 验证 asset_type
    if request.asset_type not in ["post", "comment"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="资产类型必须是 'post' 或 'comment'"
        )

    asset_type = AssetType(request.asset_type)

    # 验证资产是否存在
    if asset_type == AssetType.post:
        asset_query = select(Post).where(Post.id == request.asset_id)
    else:
        asset_query = select(Comment).where(Comment.id == request.asset_id)

    asset_result = await db.execute(asset_query)
    asset = asset_result.scalar_one_or_none()

    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{'推文' if asset_type == AssetType.post else '评论'}不存在",
        )

    # 检查是否已点赞
    existing_like_query = select(Like).where(
        and_(
            Like.asset_id == request.asset_id,
            Like.asset_type == asset_type,
            Like.user_id == current_user.id,
        )
    )
    existing_like_result = await db.execute(existing_like_query)
    existing_like = existing_like_result.scalar_one_or_none()

    if existing_like:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="您已经点赞过该内容")

    # 创建点赞记录
    new_like = Like(user_id=current_user.id, asset_id=request.asset_id, asset_type=asset_type)
    db.add(new_like)
    await db.commit()

    return Response(
        code=200,
        message="点赞成功",
        data={"asset_id": request.asset_id, "asset_type": request.asset_type},
    )


@router.delete("/like", response_model=Response)
async def unlike_asset(
    request: LikeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    取消点赞推文或评论
    """
    # 验证 asset_type
    if request.asset_type not in ["post", "comment"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="资产类型必须是 'post' 或 'comment'"
        )

    asset_type = AssetType(request.asset_type)

    # 查找现有点赞记录
    like_query = select(Like).where(
        and_(
            Like.asset_id == request.asset_id,
            Like.asset_type == asset_type,
            Like.user_id == current_user.id,
        )
    )
    like_result = await db.execute(like_query)
    like = like_result.scalar_one_or_none()

    if not like:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="您还未点赞该内容")

    # 删除点赞记录
    await db.delete(like)
    await db.commit()

    return Response(
        code=200,
        message="取消点赞成功",
        data={"asset_id": request.asset_id, "asset_type": request.asset_type},
    )


@router.post("/posts/{post_id}/comments", response_model=Response)
async def create_comment(
    post_id: str,  # 使用UUID字符串
    request: CreateCommentRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    为推文添加评论
    """
    # 检查推文是否存在
    post_query = select(Post).where(Post.post_id == post_id)
    post_result = await db.execute(post_query)
    post = post_result.scalar_one_or_none()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="推文不存在")

    # 创建评论
    new_comment = Comment(
        post_id=post.id, user_id=current_user.id, content=request.content
    )  # 使用数据库ID
    db.add(new_comment)
    await db.commit()
    await db.refresh(new_comment)

    return Response(
        code=200,
        message="评论添加成功",
        data={
            "comment": CommentResponse(
                id=new_comment.id,
                content=new_comment.content,
                user_id=new_comment.user_id,
                username=current_user.username,
                avatar_attachment_id=current_user.avatar_attachment_id,
                likes_count=0,
                is_liked_by_me=False,
                created_at=new_comment.created_at.replace(tzinfo=timezone.utc).isoformat(),
                updated_at=new_comment.updated_at.replace(tzinfo=timezone.utc).isoformat(),
                user=UserInfo(
                    id=current_user.id,
                    username=current_user.username,
                    avatar_attachment_id=current_user.avatar_attachment_id,
                ),
            )
        },
    )


@router.get("/posts/{post_id}/comments", response_model=Response)
async def get_post_comments(
    post_id: str,  # 使用UUID字符串
    page: int = 1,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    获取推文的评论列表
    """
    # 检查推文是否存在
    post_query = select(Post).where(Post.post_id == post_id)
    post_result = await db.execute(post_query)
    post = post_result.scalar_one_or_none()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="推文不存在")

    offset = (page - 1) * limit

    # 获取评论列表
    comments_query = (
        select(Comment, User, func.count(Like.id).label("likes_count"))
        .join(User, Comment.user_id == User.id)
        .outerjoin(Like, and_(Like.asset_id == Comment.id, Like.asset_type == AssetType.comment))
        .where(Comment.post_id == post.id)
        .group_by(Comment.id, User.id, User.username, User.avatar_attachment_id)
        .order_by(desc(Comment.created_at))
        .offset(offset)
        .limit(limit)
    )
    comments_result = await db.execute(comments_query)
    comments_data = comments_result.all()

    comments = []
    for row in comments_data:
        comment = row[0]
        user = row[1]
        likes_count = row[2]

        # 检查当前用户是否已点赞该评论
        like_query = select(Like).where(
            and_(
                Like.asset_id == comment.id,
                Like.asset_type == AssetType.comment,
                Like.user_id == current_user.id,
            )
        )
        like_result = await db.execute(like_query)
        is_liked_by_me = like_result.scalar_one_or_none() is not None

        comments.append(
            CommentResponse(
                id=comment.id,
                content=comment.content,
                user_id=comment.user_id,
                username=user.username,
                avatar_attachment_id=user.avatar_attachment_id,
                likes_count=likes_count,
                is_liked_by_me=is_liked_by_me,
                created_at=comment.created_at.replace(tzinfo=timezone.utc).isoformat(),
                updated_at=comment.updated_at.replace(tzinfo=timezone.utc).isoformat(),
                user=UserInfo(
                    id=user.id,
                    username=user.username,
                    avatar_attachment_id=user.avatar_attachment_id,
                ),
            )
        )

    return Response(
        code=200,
        message="评论列表获取成功",
        data={"comments": comments, "page": page, "limit": limit},
    )


@router.delete("/comments/{comment_id}", response_model=Response)
async def delete_comment(
    comment_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    删除评论（只能删除自己的评论）
    """
    # 查找评论
    comment_query = select(Comment).where(
        Comment.id == comment_id, Comment.user_id == current_user.id
    )
    comment_result = await db.execute(comment_query)
    comment = comment_result.scalar_one_or_none()

    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="评论不存在或您无权删除")

    # 删除评论
    await db.delete(comment)
    await db.commit()

    return Response(code=200, message="评论删除成功", data={"comment_id": comment_id})


@router.get("/posts/{post_id}/collection", response_model=Response)
async def get_post_collection_details(
    post_id: str, db: AsyncSession = Depends(get_db)
):  # 使用UUID字符串
    """
    获取推文关联的收藏详情（公共接口，无需登录）
    """
    # 检查推文是否存在
    post_query = select(Post).where(Post.post_id == post_id)
    post_result = await db.execute(post_query)
    post = post_result.scalar_one_or_none()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="推文不存在")

    # 获取收藏信息
    collection_query = select(Collection).where(Collection.id == post.refer_collection_id)
    collection_result = await db.execute(collection_query)
    collection = collection_result.scalar_one_or_none()

    if not collection:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="收藏不存在")

    # 获取收藏详情
    details_query = select(CollectionDetail).where(CollectionDetail.collection_id == collection.id)
    details_result = await db.execute(details_query)
    details = details_result.scalars().all()

    # 获取分类信息
    category_name = None
    if collection.category_id:
        category_query = select(Category).where(Category.id == collection.category_id)
        category_result = await db.execute(category_query)
        category = category_result.scalar_one_or_none()
        if category:
            category_name = category.name

    return Response(
        code=200,
        message="收藏详情获取成功",
        data={
            "collection": {
                "id": collection.id,
                "category_id": collection.category_id,
                "category_name": category_name,
                "tags": collection.tags,
                "details": {detail.key: detail.value for detail in details},
                "created_at": collection.created_at.replace(tzinfo=timezone.utc).isoformat(),
                "updated_at": collection.updated_at.replace(tzinfo=timezone.utc).isoformat(),
            }
        },
    )


@router.post("/posts/{post_id}/copy-to-my-collection", response_model=Response)
async def copy_post_to_my_collection(
    post_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    将社区推文的收藏复制到当前用户的收藏中
    除了分类需要重新AI生成外，其他字段直接复制
    """
    # 检查推文是否存在
    post_query = select(Post).where(Post.post_id == post_id)
    post_result = await db.execute(post_query)
    post = post_result.scalar_one_or_none()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="推文不存在")

    # 获取原收藏信息
    collection_query = select(Collection).where(Collection.id == post.refer_collection_id)
    collection_result = await db.execute(collection_query)
    original_collection = collection_result.scalar_one_or_none()

    if not original_collection:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="收藏不存在")

    # 获取原收藏详情
    details_query = select(CollectionDetail).where(
        CollectionDetail.collection_id == original_collection.id
    )
    details_result = await db.execute(details_query)
    original_details = details_result.scalars().all()

    # 将详情转换为字典
    details_dict = {detail.key: detail.value for detail in original_details}

    # 获取内容用于AI分类
    content = details_dict.get("content", "")
    title = details_dict.get("title", "")
    summary = details_dict.get("summary", "")

    # 使用内容、标题和摘要生成新的分类
    analysis_text = f"标题: {title}\n\n摘要: {summary}\n\n内容: {content[:500]}"

    # 获取当前用户的所有分类
    categories_query = select(Category.name, Category.emoji).where(
        Category.user_id == current_user.id
    )
    categories_result = await db.execute(categories_query)
    categories = [row[0] for row in categories_result.all()]
    category_emojis = [row[1] for row in categories_result.all()]

    categories_str = ", ".join(
        [f"{cat}({emoji})" for cat, emoji in zip(categories, category_emojis)]
    )
    cate_sys_prompt = PROMPT_PARSE_CATEGORY_AND_TAGS.format(categories=categories_str)
    cate_sys_prompt += f"\n\n{ADDITIONAL_PROMPT_USER_LANGUAGE_PREFERENCE}"

    # 使用AI生成新的分类
    cate_llm_resp = await provider_openai.text_chat(
        prompt=analysis_text,
        system_prompt=cate_sys_prompt,
    )
    cate_json = parse_json(cate_llm_resp.completion_text)
    category: str = cate_json.get("category", "")
    category_emoji: str = cate_json.get("category_emoji", "")

    # 保存或获取分类
    category_id = None
    if category:
        db_category_query = select(Category).where(
            Category.name == category, Category.user_id == current_user.id
        )
        db_category_result = await db.execute(db_category_query)
        db_category = db_category_result.scalar_one_or_none()

        if not db_category:
            # 创建新分类
            new_category = Category(name=category, emoji=category_emoji, user_id=current_user.id)
            db.add(new_category)
            await db.commit()
            await db.refresh(new_category)
            category_id = new_category.id
            logger.info(f"New category created: {new_category.name}")
        else:
            category_id = db_category.id

    # 创建新的收藏（复制标签，但使用新的分类）
    new_collection = Collection(
        user_id=current_user.id,
        category_id=category_id,
        tags=original_collection.tags,  # 直接复制标签
    )
    db.add(new_collection)
    await db.commit()
    await db.refresh(new_collection)

    # 复制所有详情字段
    for key, value in details_dict.items():
        new_detail = CollectionDetail(
            collection_id=new_collection.id,
            key=key,
            value=value
        )
        db.add(new_detail)

    await db.commit()

    return Response(
        code=200,
        message="收藏复制成功",
        data={
            "collection_id": new_collection.id,
            "category_id": category_id,
            "category": category,
        },
    )
