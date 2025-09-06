import api from './api'

// 获取所有分类
export const getCategories = async () => {
  try {
    const response = await api.get('/api/v1/category')
    return response.data
  } catch (error) {
    throw error.response?.data || error.message
  }
}

// 获取指定分类信息
export const getCategory = async (categoryId) => {
  try {
    const response = await api.get(`/api/v1/category/${categoryId}`)
    return response.data
  } catch (error) {
    throw error.response?.data || error.message
  }
}

// 创建分类
export const createCategory = async (categoryData) => {
  try {
    const response = await api.post('/api/v1/category', categoryData)
    return response.data
  } catch (error) {
    throw error.response?.data || error.message
  }
}

// 更新分类
export const updateCategory = async (categoryId, categoryData) => {
  try {
    const response = await api.put(`/api/v1/category/${categoryId}`, categoryData)
    return response.data
  } catch (error) {
    throw error.response?.data || error.message
  }
}

// 删除分类
export const deleteCategory = async (categoryId) => {
  try {
    const response = await api.delete(`/api/v1/category/${categoryId}`)
    return response.data
  } catch (error) {
    throw error.response?.data || error.message
  }
}

// 创建知识库
export const createKnowledgeBase = async (categoryId) => {
  try {
    const response = await api.post('/api/v1/category/create_knowledge_base', null, {
      params: { category_id: categoryId }
    })
    return response.data
  } catch (error) {
    throw error.response?.data || error.message
  }
}

// 查询知识库
export const queryKnowledgeBase = async (categoryId, query) => {
  try {
    const response = await api.get(`/api/v1/category/knowledge_base/${categoryId}`, {
      params: { query }
    })
    return response.data
  } catch (error) {
    console.error('查询知识库API错误:', {
      categoryId,
      query,
      error: error.message,
      response: error.response?.data,
      status: error.response?.status
    })

    // 重新抛出更详细的错误信息
    if (error.response?.data) {
      throw error.response.data
    } else if (error.response) {
      throw {
        detail: `HTTP ${error.response.code} 错误`,
        status: error.response.code
      }
    } else {
      throw {
        detail: error.message || '网络请求失败'
      }
    }
  }
}
