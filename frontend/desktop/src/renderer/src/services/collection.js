import api from './api'

// 根据分类ID获取收藏列表
export const getCollectionsByCategory = async (categoryId) => {
  try {
    const response = await api.get(`/api/v1/collection/by_category/${categoryId}`)
    return response.data
  } catch (error) {
    throw error.response?.data || error.message
  }
}

// 获取收藏详情
export const getCollectionDetails = async (collectionId) => {
  try {
    const response = await api.get(`/api/v1/collection/${collectionId}/details`)
    return response.data
  } catch (error) {
    throw error.response?.data || error.message
  }
}

// 获取收藏标签
export const getCollectionTags = async (collectionId) => {
  try {
    const response = await api.get(`/api/v1/collection/${collectionId}/tags`)
    return response.data
  } catch (error) {
    throw error.response?.data || error.message
  }
}

// 更新收藏标签
export const updateCollectionTags = async (collectionId, tags) => {
  try {
    const response = await api.put(`/api/v1/collection/${collectionId}/tags`, {
      tags: tags
    })
    return response.data
  } catch (error) {
    throw error.response?.data || error.message
  }
}

// 创建URL收藏
export const createUrlCollection = async (collectionData) => {
  try {
    const response = await api.post('/api/v1/collection/url', collectionData)
    return response.data
  } catch (error) {
    throw error.response?.data || error.message
  }
}

// 创建图片收藏
export const createPictureCollection = async (collectionData) => {
  try {
    const response = await api.post('/api/v1/collection/picture', collectionData)
    return response.data
  } catch (error) {
    throw error.response?.data || error.message
  }
}

// 更新收藏详情
export const updateCollectionDetail = async (collectionId, key, value) => {
  try {
    const response = await api.put(`/api/v1/collection/${collectionId}/details/${key}`, {
      value: value
    })
    return response.data
  } catch (error) {
    throw error.response?.data || error.message
  }
}

// 删除收藏
export const deleteCollection = async (collectionId) => {
  try {
    const response = await api.delete(`/api/v1/collection/${collectionId}`)
    return response.data
  } catch (error) {
    throw error.response?.data || error.message
  }
}

// 健康检查
export const healthCheck = async () => {
  try {
    const response = await api.get('/api/v1/health')
    return response.data
  } catch (error) {
    throw error.response?.data || error.message
  }
} 