import {
  getCategoriesApi,
  getCategoryApi,
  createCategoryApi,
  updateCategoryApi,
  deleteCategoryApi,
  createKnowledgeBaseApi,
  queryKnowledgeBaseApi
} from '@/api'

// 获取所有分类
export const getCategories = async () => {
  try {
    const response = await getCategoriesApi()

    if (response.code !== 200) {
      throw new Error(response.message || '获取分类列表失败')
    }

    return response.data
  } catch (error) {
    throw error.response?.data || error.message
  }
}

// 获取指定分类信息
export const getCategory = async (categoryId) => {
  try {
    const response = await getCategoryApi(categoryId)

    if (response.code !== 200) {
      throw new Error(response.message || '获取分类信息失败')
    }

    return response.data
  } catch (error) {
    throw error.response?.data || error.message
  }
}

// 创建分类
export const createCategory = async (categoryData) => {
  try {
    const response = await createCategoryApi(categoryData)

    if (response.code !== 200) {
      throw new Error(response.message || '创建分类失败')
    }

    return response.data
  } catch (error) {
    throw error.response?.data || error.message
  }
}

// 更新分类
export const updateCategory = async (categoryId, categoryData) => {
  try {
    const response = await updateCategoryApi(categoryId, categoryData)

    if (response.code !== 200) {
      throw new Error(response.message || '更新分类失败')
    }

    return response.data
  } catch (error) {
    throw error.response?.data || error.message
  }
}

// 删除分类
export const deleteCategory = async (categoryId) => {
  try {
    const response = await deleteCategoryApi(categoryId)

    if (response.code !== 200) {
      throw new Error(response.message || '删除分类失败')
    }

    return response.data
  } catch (error) {
    throw error.response?.data || error.message
  }
}

// 创建知识库
export const createKnowledgeBase = async (categoryId) => {
  try {
    const response = await createKnowledgeBaseApi(categoryId)

    if (response.code !== 200) {
      throw new Error(response.message || '创建知识库失败')
    }

    return response.data
  } catch (error) {
    throw error.response?.data || error.message
  }
}

// 查询知识库
export const queryKnowledgeBase = async (categoryId, query) => {
  try {
    const response = await queryKnowledgeBaseApi(categoryId, query)

    if (response.code !== 200) {
      throw new Error(response.message || '查询知识库失败')
    }

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
        detail: `HTTP ${error.response.status} 错误`,
        status: error.response.status
      }
    } else {
      throw {
        detail: error.message || '网络请求失败'
      }
    }
  }
}
