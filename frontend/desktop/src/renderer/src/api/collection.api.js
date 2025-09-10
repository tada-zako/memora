import api from './api'

// 根据分类ID获取该分类下的所有收藏夹
export const getCollectionsByCategoryApi = async (categoryId) => {
  return await api.get(`/api/v1/collection/by_category/${categoryId}`)
}

// 获取收藏详情
export const getCollectionDetailsApi = async (collectionId) => {
  return await api.get(`/api/v1/collection/${collectionId}/details`)
}

// 获取公共收藏详情（无需登录）
export const getPublicCollectionDetailsApi = async (collectionId) => {
  return await api.get(`/api/v1/collection/public/${collectionId}/details`)
}

// 获取收藏标签
export const getCollectionTagsApi = async (collectionId) => {
  return await api.get(`/api/v1/collection/${collectionId}/tags`)
}

// 更新收藏标签
export const updateCollectionTagsApi = async (collectionId, tags) => {
  return await api.put(`/api/v1/collection/${collectionId}/tags`, {
    tags: tags
  })
}

// 创建URL收藏
export const createUrlCollectionApi = async (collectionData) => {
  return await api.post('/api/v1/collection/url', collectionData)
}

// 创建图片收藏
export const createPictureCollectionApi = async (collectionData) => {
  return await api.post('/api/v1/collection/picture', collectionData)
}

// 更新集合详情属性
export const updateCollectionDetailsApi = async (collectionId, key, value) => {
  return await api.put(`/api/v1/collection/${collectionId}/details/${key}`, {
    value: value
  })
}

// 使用流式处理URL并获取进度更新
export const processUrlWithProgressApi = async (url) => {
  const token = localStorage.getItem('access_token')
  if (!token) {
    throw new Error('No access token found')
  }

  const response = fetch(`${api.defaults.baseURL}/api/v1/collection/url`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Accept: 'text/event-stream',
      Authorization: `Bearer ${token}`
    },
    body: JSON.stringify({ url })
  })

  if (!response.ok) {
    const errorText = await response.text()
    throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`)
  }

  if (!response.body) {
    throw new Error('Response body is empty')
  }

  // 返回 ReadableStream 供调用者处理
  return response.body
}

// 删除收藏
export const deleteCollectionApi = async (collectionId) => {
  return await api.delete(`/api/v1/collection/${collectionId}`)
}

// 后端运行健康检查
export const healthCheckApi = async () => {
  return await api.get('/api/v1/health')
}
