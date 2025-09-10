import {
  getCollectionsByCategoryApi,
  getCollectionDetailsApi,
  getPublicCollectionDetailsApi,
  getCollectionTagsApi,
  updateCollectionTagsApi,
  // createUrlCollectionApi,
  createPictureCollectionApi,
  updateCollectionDetailsApi,
  processUrlWithProgressApi,
  deleteCollectionApi,
  healthCheckApi
} from '@/api'
import { uploadAttachment, deleteAttachment, getAttachment } from './attachment'

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
// export const createUrlCollection = async (collectionData) => {
//   try {
//     const response = await createUrlCollectionApi(collectionData)

//     if (response.code !== 200) {
//       throw new Error(response.message || '创建URL收藏失败')
//     }

//     return response.data
//   } catch (error) {
//     throw error.response?.data || error.message
//   }
// }
// 使用 fetch 处理流式 api 响应

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

// 上传图片并创建收藏（支持进度回调）
export const uploadPictureCollection = async (
  file,
  category,
  description = null,
  onProgress = null
) => {
  let uploadedAttachmentId = null

  try {
    // step1：上传文件
    if (onProgress) onProgress('正在上传文件...')
    const uploadResult = await uploadAttachment(file, description)
    uploadedAttachmentId = uploadResult.attachment_id

    // step2：创建收藏
    if (onProgress) onProgress('正在创建收藏...')
    const collectionResult = await createPictureCollection({
      attachment_id: uploadedAttachmentId,
      category: category
    })

    return {
      attachment: uploadResult,
      collection: collectionResult
    }
  } catch (error) {
    // 创建收藏失败且文件已上传，请求清理附件
    if (uploadedAttachmentId) {
      try {
        if (onProgress) onProgress('正在清理附件...')
        await deleteAttachment(uploadedAttachmentId)
        console.log('已清理上传的附件:', uploadedAttachmentId)
      } catch (cleanupError) {
        console.error('清理附件失败:', cleanupError)
      }
    }

    // 重新抛出原始错误
    if (error.message?.includes('上传附件失败')) {
      throw new Error('文件上传失败，请检查网络连接或文件格式')
    } else if (uploadedAttachmentId) {
      throw new Error('创建收藏失败，请检查分类名称是否正确')
    } else {
      throw error
    }
  }
}

// 获取收藏和附件的完整信息（用于详情页面）
export const getCollectionWithAttachment = async (collectionId) => {
  try {
    // 并行获取数据以提高性能
    const [detailsResult, tagsResult] = await Promise.all([
      getCollectionDetails(collectionId),
      getCollectionTags(collectionId)
    ])

    const collectionDetails = detailsResult.details

    // 检查是否有 attachment
    if (!collectionDetails.attachment) {
      throw new Error('此收藏没有关联的附件')
    }

    // 处理标签数据
    const tags =
      tagsResult.code === 200 && tagsResult.data?.tags ? tagsResult.data.tags.join(',') : ''

    // 获取附件信息
    const attachmentId = collectionDetails.attachment
    const attachmentResult = await getAttachment(attachmentId)

    // 构建完整的数据结构
    const collectionData = {
      id: parseInt(collectionId),
      category_id: 'unknown', // 这个信息在当前API中无法获取
      tags: tags,
      details: collectionDetails,
      created_at: attachmentResult.created_at, // 使用附件的创建时间作为参考
      updated_at: attachmentResult.created_at
    }

    return {
      collection: collectionData,
      attachment: attachmentResult
    }
  } catch (error) {
    // 统一的错误处理
    if (error.detail === 'Not authenticated' || error.message?.includes('401')) {
      const authError = new Error('用户未认证，请重新登录')
      authError.code = 'AUTH_REQUIRED'
      throw authError
    }

    throw error
  }
}

// 基于分类获取带有附件的收藏列表
export const getAttachmentCollectionsByCategory = async (categoryId, options = {}) => {
  const { batchSize = 10, includeAttachmentDetails = true } = options

  try {
    const collectionsResult = await getCollectionsByCategory(categoryId)

    if (!collectionsResult?.collections) {
      return []
    }

    // 过滤出有附件的收藏
    const collectionsWithAttachments = collectionsResult.collections.filter(
      (item) => item.details?.attachment
    )

    // 直接返回无详情收藏列表
    if (!includeAttachmentDetails) {
      return collectionsWithAttachments
    }

    // 分批处理附件详情获取，避免过多并发请求
    const collectionsWithDetails = []
    for (let i = 0; i < collectionsWithAttachments.length; i += batchSize) {
      const batch = collectionsWithAttachments.slice(i, i + batchSize)

      const batchResults = await Promise.allSettled(
        batch.map(async (collection) => {
          const attachmentId = collection.details.attachment
          const attachmentDetails = await getAttachment(attachmentId)
          return {
            ...collection,
            description: attachmentDetails.description || '无描述',
            imageUrl: attachmentDetails.url,
            attachmentDetails: attachmentDetails
          }
        })
      )

      // 处理批次结果
      batchResults.forEach((result) => {
        if (result.status === 'fulfilled') {
          collectionsWithDetails.push(result.value)
        } else {
          // 处理失败的情况
          console.warn('获取附件详情失败:', result.reason)
          collectionsWithDetails.push({
            description: '加载失败',
            imageUrl: null
          })
        }
      })
    }

    return collectionsWithDetails
  } catch (error) {
    // 统一的错误处理
    if (error.detail === 'Not authenticated' || error.message?.includes('401')) {
      const authError = new Error('用户未认证，请重新登录')
      authError.code = 'AUTH_REQUIRED'
      throw authError
    }

    throw error
  }
}
