import { Category } from './../types/index'
import api from './api'
import type { ApiResponse } from '@/types'

// 获取所有分类
export const getCategoriesApi = async (): Promise<ApiResponse<any>> => {
  return await api.get('/api/v1/category')
}

// 获取指定分类信息
export const getCategoryApi = async (categoryId: string | number): Promise<ApiResponse<any>> => {
  return await api.get(`/api/v1/category/${categoryId}`)
}

// 创建分类
export const createCategoryApi = async (categoryData: any): Promise<ApiResponse<any>> => {
  return await api.post('/api/v1/category', categoryData)
}

// 更新分类
export const updateCategoryApi = async (
  categoryId: string | number,
  categoryData: any
): Promise<ApiResponse<any>> => {
  return await api.put(`/api/v1/category/${categoryId}`, categoryData)
}

// 删除分类
export const deleteCategoryApi = async (categoryId: string | number): Promise<ApiResponse<any>> => {
  return await api.delete(`/api/v1/category/${categoryId}`)
}

// 创建知识库
export const createKnowledgeBaseApi = async (
  categoryId: string | number
): Promise<ApiResponse<any>> => {
  return await api.post('/api/v1/category/create_knowledge_base', null, {
    params: { category_id: categoryId }
  })
}

// 查询知识库
export const queryKnowledgeBaseApi = async (
  categoryId: string | number,
  query: string
): Promise<ApiResponse<any>> => {
  return await api.get(`/api/v1/category/knowledge_base/${categoryId}`, {
    params: { query }
  })
}

// 获取所有分类 (服务层)
export const getCategories = async (): Promise<any> => {
  try {
    const response = await getCategoriesApi()

    if (response.code !== 200) {
      throw new Error(response.message || '获取分类列表失败')
    }

    return response.data
  } catch (error) {
    const err = error as any
    throw err.response?.data || err.message
  }
}

// 获取指定分类信息 (服务层)
export const getCategory = async (categoryId: string | number): Promise<any> => {
  try {
    const response = await getCategoryApi(categoryId)

    if (response.code !== 200) {
      throw new Error(response.message || '获取分类信息失败')
    }

    return response.data
  } catch (error) {
    const err = error as any
    throw err.response?.data || err.message
  }
}

// 创建分类 (服务层)
export const createCategory = async (categoryData: any): Promise<any> => {
  try {
    const response = await createCategoryApi(categoryData)

    if (response.code !== 200) {
      throw new Error(response.message || '创建分类失败')
    }

    return response.data
  } catch (error) {
    const err = error as any
    throw err.response?.data || err.message
  }
}

// 更新分类 (服务层)
export const updateCategory = async (
  categoryId: string | number,
  categoryData: any
): Promise<any> => {
  try {
    const response = await updateCategoryApi(categoryId, categoryData)

    if (response.code !== 200) {
      throw new Error(response.message || '更新分类失败')
    }

    return response.data
  } catch (error) {
    const err = error as any
    throw err.response?.data || err.message
  }
}

// 删除分类 (服务层)
export const deleteCategory = async (categoryId: string | number): Promise<any> => {
  try {
    const response = await deleteCategoryApi(categoryId)

    if (response.code !== 200) {
      throw new Error(response.message || '删除分类失败')
    }

    return response.data
  } catch (error) {
    const err = error as any
    throw err.response?.data || err.message
  }
}

// 创建知识库 (服务层)
export const createKnowledgeBase = async (categoryId: string | number): Promise<any> => {
  try {
    const response = await createKnowledgeBaseApi(categoryId)

    if (response.code !== 200) {
      throw new Error(response.message || '创建知识库失败')
    }

    return response.data
  } catch (error) {
    const err = error as any
    throw err.response?.data || err.message
  }
}

// 查询知识库 (服务层)
export const queryKnowledgeBase = async (
  categoryId: string | number,
  query: string
): Promise<any> => {
  try {
    const response = await queryKnowledgeBaseApi(categoryId, query)

    if (response.code !== 200) {
      throw new Error(response.message || '查询知识库失败')
    }

    return response.data
  } catch (error) {
    const err = error as any
    console.error('查询知识库API错误:', {
      categoryId,
      query,
      error: err.message,
      response: err.response?.data,
      status: err.response?.status
    })

    // 重新抛出更详细的错误信息
    if (err.response?.data) {
      throw err.response.data
    } else if (err.response) {
      throw {
        detail: `HTTP ${err.response.status} 错误`,
        status: err.response.status
      }
    } else {
      throw {
        detail: err.message || '网络请求失败'
      }
    }
  }
}

// 流式查询知识库
export async function* streamQueryKnowledgeBase(categoryId: string | number, query: string) {
  try {
    const params = new URLSearchParams({ query: query })

    const token = localStorage.getItem('access_token')

    const response = await fetch(
      `/api/v1/category/knowledge_base/${categoryId}?${params.toString()}`,
      {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          Authorization: token ? `Bearer ${token}` : ''
        }
      }
    )

    if (!response.ok || !response.body) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const reader = response.body?.getReader()
    const decoder = new TextDecoder('utf-8')

    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      yield decoder.decode(value, { stream: true })
    }
  } catch (error) {
    const err = error as any
    console.error('流式查询知识库API错误:', {
      categoryId,
      query,
      error: err.message,
      response: err.response?.data,
      status: err.response?.status
    })
    throw err.response?.data || err.message
  }
}

// AI search api （API层 + 服务层）
export const aiSearchApi = async (query: string): Promise<ApiResponse<any>> => {
  return await api.get('/api/v1/category/search_collections', { params: { query } })
}

// 返回示例：
// {
//     "code": 200,
//     "message": "Collection found successfully",
//     "data": {
//         "collection": {
//         "id": "collection_id",
//         "user_id": "user_id",
//         "category_id": "category_id",
//         "created_at": "timestamp",
//         "details": {"url": "...", "title": "...", ...}
//         },
//         "category": {
//         "id": "category_id",
//         "name": "category_name",
//         "emoji": "emoji",
//         "knowledge_base_id": "kb_id"
//         },
//         "search_info": {
//         "confidence": "high|medium|low",
//         "reason": "AI匹配理由",
//         "query": "用户查询"
//         }
//     }
// }

export const aiSearch = async (query: string): Promise<any> => {
  try {
    const response = await aiSearchApi(query)

    if (response.code !== 200) {
      throw new Error(response.message || 'AI响应失败')
    }

    return response.data
  } catch (error) {
    throw error
  }
}
