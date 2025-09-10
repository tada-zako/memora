import api from './api'
import type {
  ApiResponse,
  Collection,
  // CreateUrlCollectionData,
  CreatePictureCollectionData,
  CollectionDetail
} from '@/types'

// 根据分类ID获取该分类下的所有收藏夹
export const getCollectionsByCategoryApi = async (categoryId: string | number) => {
  const response: ApiResponse<Collection> = await api.get(
    `/api/v1/collection/by_category/${categoryId}`
  )
  return response
}

// 获取收藏详情
export const getCollectionDetailsApi = async (collectionId: string | number) => {
  const response: ApiResponse<{ details: CollectionDetail[] }> = await api.get(
    `/api/v1/collection/${collectionId}/details`
  )
  return response
}

// 获取公共收藏详情（无需登录）
export const getPublicCollectionDetailsApi = async (collectionId: string | number) => {
  const response: ApiResponse<Collection> = await api.get(
    `/api/v1/collection/public/${collectionId}/details`
  )
  return response
}

// 获取收藏标签
export const getCollectionTagsApi = async (collectionId: string | number) => {
  const response: ApiResponse<{ tags: string }> = await api.get(
    `/api/v1/collection/${collectionId}/tags`
  )
  return response
}

// 更新收藏标签
export const updateCollectionTagsApi = async (collectionId: string | number, tags: string[]) => {
  const response: ApiResponse<{ tags: string }> = await api.put(
    `/api/v1/collection/${collectionId}/tags`,
    {
      tags: tags
    }
  )
  return response
}

// 创建URL收藏
// export const createUrlCollectionApi = async (collectionData: CreateUrlCollectionData) => {
//   const response = await api.post('/api/v1/collection/url', collectionData)
//   return response
// }
// 使用 fetch 处理流式 api 响应

// 创建图片收藏
export const createPictureCollectionApi = async (collectionData: CreatePictureCollectionData) => {
  const response = await api.post('/api/v1/collection/picture', collectionData)
  return response
}
// 当前 api 后端不支持

// 更新集合详情属性
export const updateCollectionDetailsApi = async (
  collectionId: string | number,
  key: string,
  value: any
) => {
  const response: ApiResponse<CollectionDetail> = await api.put(
    `/api/v1/collection/${collectionId}/details/${key}`,
    {
      value: value
    }
  )
  return response
}

// 使用流式处理URL并获取进度更新
export const processUrlWithProgressApi = async (
  url: string
): Promise<ReadableStream<Uint8Array>> => {
  const token = localStorage.getItem('access_token')
  if (!token) {
    throw new Error('No access token found')
  }

  const response: Response = await fetch(`${api.defaults.baseURL}/api/v1/collection/url`, {
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
export const deleteCollectionApi = async (collectionId: string | number) => {
  const response: ApiResponse<{ key: string }> = await api.delete(
    `/api/v1/collection/${collectionId}`
  )
  return response
}

// 后端运行健康检查
export const healthCheckApi = async () => {
  const response: ApiResponse<{ message: string; status: string; version: string }> =
    await api.get('/api/v1/health')
  return response
}
