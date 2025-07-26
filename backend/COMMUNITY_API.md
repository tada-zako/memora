# 社区功能API文档

## 概述

本文档描述了新添加的社区功能API，允许用户分享收藏、点赞和评论其他用户的分享内容。

## 数据库迁移

在使用新功能之前，请先运行数据库迁移脚本：

```bash
cd backend
python migrate_community_features.py
```

## API 端点

所有API端点都需要用户认证（Bearer Token）。

### 1. 分享收藏

#### 分享收藏到社区
```
POST /api/v1/community/{collection_id}/share
```

**请求体：**
```json
{
  "description": "这是一篇很有用的技术文章分享"  // 可选
}
```

**响应：**
```json
{
  "status": "success",
  "message": "收藏已成功分享到社区",
  "data": {
    "collection_id": 123,
    "shared_description": "这是一篇很有用的技术文章分享"
  }
}
```

#### 取消分享收藏
```
DELETE /api/v1/community/{collection_id}/share
```

**响应：**
```json
{
  "status": "success",
  "message": "已取消分享该收藏",
  "data": {
    "collection_id": 123
  }
}
```

### 2. 获取社区内容

#### 获取已分享的收藏列表（社区页面）
```
GET /api/v1/community/shared?page=1&limit=20
```

**响应：**
```json
{
  "status": "success",
  "message": "已分享收藏列表获取成功",
  "data": {
    "collections": [
      {
        "id": 123,
        "user_id": 456,
        "username": "张三",
        "category_id": 1,
        "category_name": "技术文章",
        "tags": "Python,FastAPI,后端",
        "shared_description": "这是一篇很有用的技术文章分享",
        "likes_count": 5,
        "comments_count": 3,
        "is_liked_by_me": false,
        "details": {
          "url": "https://example.com/article",
          "summary": "文章摘要..."
        },
        "created_at": "2024-01-01T12:00:00Z",
        "updated_at": "2024-01-01T12:00:00Z"
      }
    ],
    "page": 1,
    "limit": 20
  }
}
```

### 3. 点赞功能

#### 点赞收藏
```
POST /api/v1/community/{collection_id}/like
```

**响应：**
```json
{
  "status": "success",
  "message": "点赞成功",
  "data": {
    "collection_id": 123
  }
}
```

#### 取消点赞
```
DELETE /api/v1/community/{collection_id}/like
```

**响应：**
```json
{
  "status": "success",
  "message": "取消点赞成功",
  "data": {
    "collection_id": 123
  }
}
```

#### 获取点赞列表
```
GET /api/v1/community/{collection_id}/likes
```

**响应：**
```json
{
  "status": "success",
  "message": "点赞列表获取成功",
  "data": {
    "likes": [
      {
        "id": 1,
        "user_id": 456,
        "username": "张三",
        "created_at": "2024-01-01T12:00:00Z"
      }
    ],
    "total_count": 1
  }
}
```

### 4. 评论功能

#### 添加评论
```
POST /api/v1/community/{collection_id}/comment
```

**请求体：**
```json
{
  "content": "这个分享很有用，谢谢！"
}
```

**响应：**
```json
{
  "status": "success",
  "message": "评论添加成功",
  "data": {
    "comment": {
      "id": 1,
      "content": "这个分享很有用，谢谢！",
      "user_id": 456,
      "username": "张三",
      "created_at": "2024-01-01T12:00:00Z",
      "updated_at": "2024-01-01T12:00:00Z"
    }
  }
}
```

#### 获取评论列表
```
GET /api/v1/community/{collection_id}/comments?page=1&limit=20
```

**响应：**
```json
{
  "status": "success",
  "message": "评论列表获取成功",
  "data": {
    "comments": [
      {
        "id": 1,
        "content": "这个分享很有用，谢谢！",
        "user_id": 456,
        "username": "张三",
        "created_at": "2024-01-01T12:00:00Z",
        "updated_at": "2024-01-01T12:00:00Z"
      }
    ],
    "page": 1,
    "limit": 20
  }
}
```

#### 删除评论
```
DELETE /api/v1/community/comment/{comment_id}
```

**注意：只能删除自己的评论**

**响应：**
```json
{
  "status": "success",
  "message": "评论删除成功",
  "data": {
    "comment_id": 1
  }
}
```

## 现有API的更新

### 用户收藏列表
```
GET /api/v1/collections/
```

现在在返回的收藏数据中包含了分享状态信息：

```json
{
  "collections": [
    {
      "id": 123,
      "category_id": 1,
      "tags": "Python,FastAPI",
      "is_shared": true,  // 新增：是否已分享
      "shared_description": "这是一篇很有用的技术文章分享",  // 新增：分享描述
      "details": { ... },
      "created_at": "2024-01-01T12:00:00Z",
      "updated_at": "2024-01-01T12:00:00Z"
    }
  ]
}
```

## 错误码

- `404` - 收藏不存在或未分享
- `400` - 重复操作（如重复点赞、重复分享等）
- `401` - 未认证
- `403` - 无权限（如删除他人评论）

## 使用流程示例

1. **分享收藏**：用户在自己的收藏页面选择一个收藏，点击分享按钮，调用分享API
2. **浏览社区**：用户访问社区页面，获取所有已分享的收藏列表
3. **互动**：用户可以对感兴趣的分享进行点赞和评论
4. **管理**：用户可以取消自己的分享，删除自己的评论 