#!/usr/bin/env python3
"""
测试手动创建、修改Collection和Category的功能
这个脚本演示了新增的API接口的使用方法
"""

import asyncio
import aiohttp
import json


BASE_URL = "http://localhost:8000/api/v1"


async def test_manual_collection_crud():
    """测试手动Collection的CRUD操作"""
    
    # 注意：在实际使用中，需要先登录获取token
    # 这里假设已经有了有效的token
    token = "your_bearer_token_here"  # 替换为实际的token
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    async with aiohttp.ClientSession() as session:
        
        # 1. 先创建一个category用于测试
        print("=== 创建Category ===")
        category_data = {
            "name": "测试分类",
            "emoji": "📚"
        }
        
        async with session.post(
            f"{BASE_URL}/category/",
            headers=headers,
            json=category_data
        ) as response:
            if response.status == 201:
                category_result = await response.json()
                category_id = category_result["data"]["id"]
                print(f"Category创建成功，ID: {category_id}")
            else:
                print(f"Category创建失败: {response.status}")
                return
        
        # 2. 手动创建Collection
        print("\n=== 手动创建Collection ===")
        collection_data = {
            "title": "我的第一个手动收藏",
            "content": "这是一些测试内容，用来验证手动创建功能。",
            "category_id": category_id,
            "tags": ["测试", "手动创建", "API"],
            "url": "https://example.com",
            "summary": "这是一个测试收藏的摘要"
        }
        
        async with session.post(
            f"{BASE_URL}/collection/create",
            headers=headers,
            json=collection_data
        ) as response:
            if response.status == 201:
                collection_result = await response.json()
                collection_id = collection_result["data"]["id"]
                print(f"Collection创建成功，ID: {collection_id}")
                print(f"详细信息: {json.dumps(collection_result['data'], indent=2, ensure_ascii=False)}")
            else:
                error_text = await response.text()
                print(f"Collection创建失败: {response.status}, {error_text}")
                return
        
        # 3. 获取单个Collection
        print(f"\n=== 获取Collection {collection_id} ===")
        async with session.get(
            f"{BASE_URL}/collection/{collection_id}",
            headers=headers
        ) as response:
            if response.status == 200:
                result = await response.json()
                print(f"Collection获取成功:")
                print(json.dumps(result["data"], indent=2, ensure_ascii=False))
            else:
                error_text = await response.text()
                print(f"Collection获取失败: {response.status}, {error_text}")
        
        # 4. 更新Collection
        print(f"\n=== 更新Collection {collection_id} ===")
        update_data = {
            "title": "更新后的标题",
            "tags": ["更新", "测试", "新标签"],
            "summary": "这是更新后的摘要内容"
        }
        
        async with session.put(
            f"{BASE_URL}/collection/{collection_id}",
            headers=headers,
            json=update_data
        ) as response:
            if response.status == 200:
                result = await response.json()
                print(f"Collection更新成功:")
                print(json.dumps(result["data"], indent=2, ensure_ascii=False))
            else:
                error_text = await response.text()
                print(f"Collection更新失败: {response.status}, {error_text}")
        
        # 5. 获取用户所有Collections
        print("\n=== 获取用户所有Collections ===")
        async with session.get(
            f"{BASE_URL}/collections/",
            headers=headers
        ) as response:
            if response.status == 200:
                result = await response.json()
                print(f"找到 {len(result['data']['collections'])} 个收藏")
                for collection in result["data"]["collections"]:
                    print(f"- ID: {collection['id']}, 标题: {collection['details'].get('title', 'N/A')}")
            else:
                error_text = await response.text()
                print(f"获取Collections失败: {response.status}, {error_text}")
        
        # 6. 删除Collection (可选)
        print(f"\n=== 删除Collection {collection_id} ===")
        async with session.delete(
            f"{BASE_URL}/collection/{collection_id}",
            headers=headers
        ) as response:
            if response.status == 200:
                result = await response.json()
                print("Collection删除成功")
            else:
                error_text = await response.text()
                print(f"Collection删除失败: {response.status}, {error_text}")


async def test_category_crud():
    """测试Category的CRUD操作"""
    
    token = "your_bearer_token_here"  # 替换为实际的token
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    async with aiohttp.ClientSession() as session:
        
        # 1. 创建Category
        print("=== 创建Category ===")
        category_data = {
            "name": "编程学习",
            "emoji": "💻"
        }
        
        async with session.post(
            f"{BASE_URL}/category/",
            headers=headers,
            json=category_data
        ) as response:
            if response.status == 201:
                result = await response.json()
                category_id = result["data"]["id"]
                print(f"Category创建成功: {json.dumps(result['data'], indent=2, ensure_ascii=False)}")
            else:
                error_text = await response.text()
                print(f"Category创建失败: {response.status}, {error_text}")
                return
        
        # 2. 获取所有Categories
        print("\n=== 获取所有Categories ===")
        async with session.get(
            f"{BASE_URL}/category/",
            headers=headers
        ) as response:
            if response.status == 200:
                result = await response.json()
                print(f"找到 {len(result['data']['categories'])} 个分类:")
                for category in result["data"]["categories"]:
                    print(f"- ID: {category['id']}, 名称: {category['name']}, Emoji: {category.get('emoji', 'N/A')}")
            else:
                error_text = await response.text()
                print(f"获取Categories失败: {response.status}, {error_text}")
        
        # 3. 更新Category
        print(f"\n=== 更新Category {category_id} ===")
        update_data = {
            "name": "高级编程学习",
            "emoji": "🚀"
        }
        
        async with session.put(
            f"{BASE_URL}/category/{category_id}",
            headers=headers,
            json=update_data
        ) as response:
            if response.status == 200:
                result = await response.json()
                print(f"Category更新成功: {json.dumps(result['data'], indent=2, ensure_ascii=False)}")
            else:
                error_text = await response.text()
                print(f"Category更新失败: {response.status}, {error_text}")
        
        # 4. 删除Category (可选)
        print(f"\n=== 删除Category {category_id} ===")
        async with session.delete(
            f"{BASE_URL}/category/{category_id}",
            headers=headers
        ) as response:
            if response.status == 204 or response.status == 200:
                print("Category删除成功")
            else:
                error_text = await response.text()
                print(f"Category删除失败: {response.status}, {error_text}")


def print_usage():
    """打印使用说明"""
    print("""
=== Memora 手动Collection和Category管理功能测试 ===

新增的API接口：

1. Collection相关：
   - POST /api/v1/collection/create - 手动创建Collection
   - GET /api/v1/collection/{id} - 获取单个Collection
   - PUT /api/v1/collection/{id} - 更新Collection
   - DELETE /api/v1/collection/{id} - 删除Collection（已有）

2. Category相关（已有完整CRUD）：
   - POST /api/v1/category/ - 创建Category
   - GET /api/v1/category/ - 获取所有Categories
   - PUT /api/v1/category/{id} - 更新Category
   - DELETE /api/v1/category/{id} - 删除Category

使用方法：
1. 先启动后端服务: uvicorn backend.main:app --reload
2. 注册/登录获取Bearer Token
3. 使用Token调用API接口

注意：在运行此测试脚本前，请：
1. 确保后端服务正在运行
2. 将 'your_bearer_token_here' 替换为实际的认证token
""")


if __name__ == "__main__":
    print_usage()
    
    # 如果要运行测试，取消注释下面的代码
    # print("\n运行Collection CRUD测试...")
    # asyncio.run(test_manual_collection_crud())
    
    # print("\n运行Category CRUD测试...")
    # asyncio.run(test_category_crud())