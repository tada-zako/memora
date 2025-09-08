import {
  getCollectionsByCategoryApi,
  getCollectionDetailsApi,
  getPublicCollectionDetailsApi,
  getCollectionTagsApi,
  updateCollectionTagsApi,
  createUrlCollectionApi,
  createPictureCollectionApi,
  updateCollectionDetailsApi,
  processUrlWithProgressApi,
  deleteCollectionApi,
  healthCheckApi
} from '@/api'

// 根据分类ID获取收藏列表
export const getCollectionsByCategory = async (categoryId) => {
  try {
    const response = await getCollectionsByCategoryApi(categoryId)

    if (response.code !== 200) {
      throw new Error(response.message || '获取收藏列表失败')
    }

    return response.data
  } catch (error) {
    throw error.response?.data || error.message
  }
}

// 获取收藏详情
export const getCollectionDetails = async (collectionId) => {
  try {
    const response = await getCollectionDetailsApi(collectionId)

    if (response.code !== 200) {
      throw new Error(response.message || '获取收藏详情失败')
    }

    return response.data
  } catch (error) {
    throw error.response?.data || error.message
  }
}

// 获取公共收藏详情（无需登录）
export const getPublicCollectionDetails = async (collectionId) => {
  try {
    const response = await getPublicCollectionDetailsApi(collectionId)

    if (response.code !== 200) {
      throw new Error(response.message || '获取公共收藏详情失败')
    }

    return response.data
  } catch (error) {
    throw error.response?.data || error.message
  }
}

// 获取收藏标签
export const getCollectionTags = async (collectionId) => {
  try {
    const response = await getCollectionTagsApi(collectionId)

    if (response.code !== 200) {
      throw new Error(response.message || '获取收藏标签失败')
    }

    return response.data
  } catch (error) {
    throw error.response?.data || error.message
  }
}

// 更新收藏标签
export const updateCollectionTags = async (collectionId, tags) => {
  try {
    const response = await updateCollectionTagsApi(collectionId, tags)

    if (response.code !== 200) {
      throw new Error(response.message || '更新收藏标签失败')
    }

    return response.data
  } catch (error) {
    throw error.response?.data || error.message
  }
}

// 创建URL收藏
export const createUrlCollection = async (collectionData) => {
  try {
    const response = await createUrlCollectionApi(collectionData)

    if (response.code !== 200) {
      throw new Error(response.message || '创建URL收藏失败')
    }

    return response.data
  } catch (error) {
    throw error.response?.data || error.message
  }
}

// 创建图片收藏
export const createPictureCollection = async (collectionData) => {
  try {
    const response = await createPictureCollectionApi(collectionData)

    if (response.code !== 200) {
      throw new Error(response.message || '创建图片收藏失败')
    }

    return response.data
  } catch (error) {
    throw error.response?.data || error.message
  }
}

// 更新集合的某个详情，如URL或摘要
export const updateCollectionDetail = async (collectionId, key, value) => {
  try {
    const response = await updateCollectionDetailsApi(collectionId, key, value)

    if (response.code !== 200) {
      throw new Error(response.message || '更新集合详情失败')
    }

    return response.data
  } catch (error) {
    throw error.response?.data || error.message
  }
}

// 使用流式处理URL并获取进度更新
export const processUrlWithStreaming = async (url, onProgress) => {
  try {
    const responseStream = await processUrlWithProgressApi(url)
    const reader = responseStream.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) {
        break
      }

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const jsonStr = line.slice(6)
            if (jsonStr) {
              const data = JSON.parse(jsonStr)
              onProgress(data)
            }
          } catch (error) {
            console.error('Error parsing SSE event:', error, 'raw line:', line)
          }
        }
      }
    }
  } catch (error) {
    throw error.message || '流式处理网页URL失败'
  }
}

// 删除收藏
export const deleteCollection = async (collectionId) => {
  try {
    const response = await deleteCollectionApi(collectionId)

    if (response.code !== 200) {
      throw new Error(response.message || '删除收藏失败')
    }

    return response.data
  } catch (error) {
    throw error.response?.data || error.message
  }
}

// 健康检查
export const healthCheck = async () => {
  try {
    const response = await healthCheckApi()

    if (response.code !== 200) {
      throw new Error(response.message || '健康检查失败')
    }

    return response.data
  } catch (error) {
    throw error.response?.data || error.message
  }
}
