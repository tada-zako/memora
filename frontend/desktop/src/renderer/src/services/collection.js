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

// 获取公共收藏详情（无需登录）
export const getPublicCollectionDetails = async (collectionId) => {
  try {
    const response = await api.get(`/api/v1/collection/public/${collectionId}/details`)
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

// 更新集合的某个详情，如URL或摘要
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

export const processUrlWithStreaming = async (url, onProgress) => {
  const token = localStorage.getItem('access_token')
  const apiBaseUrl = 'https://memora.soulter.top'; // Keep the base URL as you requested

  const response = await fetch(`${apiBaseUrl}/api/v1/collection/url`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'text/event-stream',
      'Authorization': `Bearer ${token}`
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

  const reader = response.body.getReader()
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