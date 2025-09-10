import api from './api'

// 获取所有分类
export const getCategoriesApi = async () => {
  return await api.get('/api/v1/category')
}

// 获取指定分类信息
export const getCategoryApi = async (categoryId) => {
  return await api.get(`/api/v1/category/${categoryId}`)
}

// 创建分类
export const createCategoryApi = async (categoryData) => {
  return await api.post('/api/v1/category', categoryData)
}

// 更新分类
export const updateCategoryApi = async (categoryId, categoryData) => {
  return await api.put(`/api/v1/category/${categoryId}`, categoryData)
}

// 删除分类
export const deleteCategoryApi = async (categoryId) => {
  return await api.delete(`/api/v1/category/${categoryId}`)
}

// 创建知识库
export const createKnowledgeBaseApi = async (categoryId) => {
  return await api.post('/api/v1/category/create_knowledge_base', null, {
    params: { category_id: categoryId }
  })
}

// 查询知识库
export const queryKnowledgeBaseApi = async (categoryId, query) => {
  return await api.get(`/api/v1/category/query_knowledge_base/${categoryId}`, {
    params: { query }
  })
}
