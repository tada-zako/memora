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