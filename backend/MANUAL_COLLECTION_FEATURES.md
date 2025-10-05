# 手动Collection和Category管理功能

## 概述

本次更新为Memora后端添加了手动创建、修改Collection的功能，使用户不再只能通过AI来创建Collection，而可以直接手动管理他们的收藏内容。

## 新增功能

### Collection手动管理

#### 1. 手动创建Collection
- **接口**: `POST /api/v1/collection/create`
- **功能**: 允许用户手动创建收藏，无需通过AI分析
- **请求体**:
```json
{
  "title": "收藏标题",
  "content": "收藏内容（可选）",
  "category_id": 1,
  "tags": ["标签1", "标签2"],
  "url": "https://example.com（可选）",
  "summary": "摘要（可选）"
}
```

#### 2. 获取单个Collection
- **接口**: `GET /api/v1/collection/{id}`
- **功能**: 获取指定ID的收藏详细信息，包括分类信息

#### 3. 更新Collection
- **接口**: `PUT /api/v1/collection/{id}`
- **功能**: 更新收藏的基本信息和详细内容
- **请求体**:
```json
{
  "title": "新标题（可选）",
  "content": "新内容（可选）",
  "category_id": 2,
  "tags": ["新标签"],
  "url": "https://newurl.com（可选）",
  "summary": "新摘要（可选）"
}
```

### Category管理

Category功能已经完备，包括：
- **创建分类**: `POST /api/v1/category/`
- **获取所有分类**: `GET /api/v1/category/`
- **更新分类**: `PUT /api/v1/category/{id}`
- **删除分类**: `DELETE /api/v1/category/{id}`

## 数据模型

### Collection结构
```python
Collection:
  - id: 主键
  - user_id: 用户ID
  - category_id: 分类ID（可为null）
  - tags: 标签（逗号分隔）
  - created_at/updated_at: 时间戳

CollectionDetail:
  - collection_id: 关联的Collection ID
  - key: 详情键名（如'title', 'content', 'url', 'summary'）
  - value: 详情值
```

### Category结构
```python
Category:
  - id: 主键
  - user_id: 用户ID
  - name: 分类名称
  - emoji: 表情符号（可选）
  - knowledge_base_id: 知识库ID（可选）
```

## 使用示例

### 1. 创建手动Collection

```bash
curl -X POST "http://localhost:8000/api/v1/collection/create" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Python学习笔记",
    "content": "记录Python学习过程中的重要知识点",
    "category_id": 1,
    "tags": ["Python", "编程", "学习"],
    "summary": "Python基础知识总结"
  }'
```

### 2. 更新Collection

```bash
curl -X PUT "http://localhost:8000/api/v1/collection/1" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Python高级特性学习",
    "tags": ["Python", "高级", "特性"]
  }'
```

### 3. 创建Category

```bash
curl -X POST "http://localhost:8000/api/v1/category/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "编程学习",
    "emoji": "💻"
  }'
```

## 权限控制

- 所有接口都需要Bearer Token认证
- 用户只能操作自己的Collection和Category
- 在更新Collection时会验证category_id是否属于当前用户

## 测试

项目包含测试脚本 `test_manual_collection.py`，演示了所有新增功能的使用方法。运行前需要：

1. 启动后端服务
2. 获取有效的认证Token
3. 在脚本中替换Token

## 兼容性

- 新增功能不影响现有的AI创建Collection功能
- 所有现有接口保持不变
- 数据库结构无需修改，使用现有表结构

## 注意事项

1. 手动创建的Collection可以没有某些字段（如summary、url等）
2. Tags以逗号分隔存储在数据库中
3. Category可以设置为null（无分类）
4. 删除Category时，相关的Collection不会被删除，但category_id会变为null