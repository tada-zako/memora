import api from './api'
import type { ApiResponse } from '@/types'

// ================= API 层 =================

// 创建推文（发布收藏到社区）
export const createPostApi = async (
  referCollectionId: string | number,
  description: string
): Promise<ApiResponse<any>> => {
  return await api.post('/api/v1/community/posts', {
    refer_collection_id: referCollectionId,
    description: description
  })
}

// 删除推文
export const deletePostApi = async (postId: string | number): Promise<ApiResponse<any>> => {
  return await api.delete(`/api/v1/community/posts/${postId}`)
}

// 获取社区最新推文列表
export const getLatestPostsApi = async (page = 1, limit = 20): Promise<ApiResponse<any>> => {
  return await api.get('/api/v1/community/posts-latest', {
    params: { page, limit }
  })
}

// 获取社区推荐推文列表
export const getRecommendedPostsApi = async (page = 1, limit = 20): Promise<ApiResponse<any>> => {
  return await api.get('/api/v1/community/posts-recommended', {
    params: { page, limit }
  })
}

// 点赞推文或评论
export const likeAssetApi = async (
  assetId: string | number,
  assetType: string
): Promise<ApiResponse<any>> => {
  return await api.post(`/api/v1/community/like`, {
    asset_id: assetId,
    asset_type: assetType
  })
}

// 取消点赞推文或评论
export const unlikeAssetApi = async (
  assetId: string | number,
  assetType: string
): Promise<ApiResponse<any>> => {
  return await api.delete('/api/v1/community/like', {
    data: {
      asset_id: assetId,
      asset_type: assetType
    }
  })
}

// 为推文添加评论
export const createCommentApi = async (
  postId: string | number,
  content: string
): Promise<ApiResponse<any>> => {
  return await api.post(`/api/v1/community/posts/${postId}/comments`, {
    content
  })
}

// 获取推文的评论列表
export const getPostCommentsApi = async (
  postId: string | number,
  page: number,
  limit: number
): Promise<ApiResponse<any>> => {
  return await api.get(`/api/v1/community/posts/${postId}/comments`, {
    params: { page, limit }
  })
}

// 删除评论
export const deleteCommentApi = async (commentId: string | number): Promise<ApiResponse<any>> => {
  return await api.delete(`/api/v1/community/comments/${commentId}`)
}

// 获取推文关联的收藏详情（公共接口，无需登录）
export const getPostCollectionDetailsApi = async (
  postId: string | number
): Promise<ApiResponse<any>> => {
  return await api.get(`/api/v1/community/posts/${postId}/collection`)
}

// 获取当前用户推文列表
export const getUserPostsApi = async (page: number, limit: number): Promise<ApiResponse<any>> => {
  return await api.get(`/api/v1/community/my-posts`, {
    params: { page, limit }
  })
}

// 将社区推文的收藏复制到我的收藏
export const copyPostToMyCollectionApi = async (postId: string): Promise<ApiResponse<any>> => {
  return await api.post(`/api/v1/community/posts/${postId}/copy-to-my-collection`)
}

// ================= 服务层 =================

// 创建推文 (服务层)
export const createPost = async (
  referCollectionId: string | number,
  description: string
): Promise<any> => {
  try {
    const response = await createPostApi(referCollectionId, description)

    if (response.code !== 200) {
      throw new Error(response.message || '创建推文失败')
    }

    return response.data
  } catch (error) {
    const err = error as any
    console.error('创建推文失败:', err)
    throw err.response?.data || err
  }
}

// 删除推文 (服务层)
export const deletePost = async (postId: string | number): Promise<any> => {
  try {
    const response = await deletePostApi(postId)

    if (response.code !== 200) {
      throw new Error(response.message || '删除推文失败')
    }

    return response.data
  } catch (error) {
    const err = error as any
    console.error('删除推文失败:', err)
    throw err.response?.data || err
  }
}

// 获取社区最新推文列表 (服务层)
export const getLatestPosts = async (page: number = 1, limit: number = 20): Promise<any> => {
  try {
    const response = await getLatestPostsApi(page, limit)

    if (response.code !== 200) {
      throw new Error(response.message || '获取最新推文列表失败')
    }

    return response.data
  } catch (error) {
    const err = error as any
    console.error('获取最新推文列表失败:', err)
    throw err.response?.data || err
  }
}

// 获取社区推荐推文列表 (服务层)
export const getRecommendedPosts = async (page: number = 1, limit: number = 20): Promise<any> => {
  try {
    const response = await getRecommendedPostsApi(page, limit)

    if (response.code !== 200) {
      throw new Error(response.message || '获取推荐推文列表失败')
    }

    return response.data
  } catch (error) {
    const err = error as any
    console.error('获取推荐推文列表失败:', err)
    throw err.response?.data || err
  }
}

// 兼容旧的 API 名称，默认返回最新推文
export const getPosts = getLatestPosts

// 为推文添加评论 (服务层)
export const createComment = async (postId: string | number, content: string): Promise<any> => {
  try {
    const response = await createCommentApi(postId, content)

    if (response.code !== 200) {
      throw new Error(response.message || '添加评论失败')
    }

    return response.data
  } catch (error) {
    const err = error as any
    console.error('添加评论失败:', err)
    throw err.response?.data || err
  }
}

// 获取推文的评论列表 (服务层)
export const getPostComments = async (
  postId: string | number,
  page: number = 1,
  limit: number = 20
): Promise<any> => {
  try {
    const response = await getPostCommentsApi(postId, page, limit)

    if (response.code !== 200) {
      throw new Error(response.message || '获取评论列表失败')
    }

    return response.data
  } catch (error) {
    const err = error as any
    console.error('获取评论列表失败:', err)
    throw err.response?.data || err
  }
}

// 删除评论 (服务层)
export const deleteComment = async (commentId: string | number): Promise<any> => {
  try {
    const response = await deleteCommentApi(commentId)

    if (response.code !== 200) {
      throw new Error(response.message || '删除评论失败')
    }

    return response.data
  } catch (error) {
    const err = error as any
    console.error('删除评论失败:', err)
    throw err.response?.data || err
  }
}

// 获取推文关联的收藏详情 (服务层)
export const getPostCollectionDetails = async (postId: string | number): Promise<any> => {
  try {
    const response = await getPostCollectionDetailsApi(postId)

    // 由于Axios拦截器已经提取了data字段，这里直接返回响应
    return response
  } catch (error) {
    const err = error as any
    console.error('获取推文收藏详情失败:', err)
    throw err.response?.data || err
  }
}

// 获取当前用户推文列表 (服务层)
export const getUserPosts = async (page: number = 1, limit: number = 20): Promise<any> => {
  try {
    const response = await getUserPostsApi(page, limit)

    if (response.code !== 200) {
      throw new Error(response.message || '获取我的推文失败')
    }

    return response.data
  } catch (error) {
    const err = error as any
    console.error('获取我的推文失败:', err)
    throw err.response?.data || err
  }
}

// 点赞推文或评论 (服务层)
export const likeAsset = async (assetId: string | number, assetType: string): Promise<any> => {
  try {
    // 目前API层的likePostApi只接受post_id，未来可能需要扩展支持asset_type
    const response = await likeAssetApi(assetId, assetType)

    if (response.code !== 200) {
      throw new Error(response.message || '点赞失败')
    }

    return response.data
  } catch (error) {
    const err = error as any
    console.error('点赞失败:', err)
    throw err.response?.data || err
  }
}

// 取消点赞推文或评论 (服务层)
export const unlikeAsset = async (assetId: string | number, assetType: string): Promise<any> => {
  try {
    const response = await unlikeAssetApi(assetId, assetType)

    if (response.code !== 200) {
      throw new Error(response.message || '取消点赞失败')
    }

    return response.data
  } catch (error) {
    const err = error as any
    console.error('取消点赞失败:', err)
    throw err.response?.data || err
  }
}

// 将社区推文的收藏复制到我的收藏 (服务层)
export const copyPostToMyCollection = async (postId: string): Promise<any> => {
  try {
    const response = await copyPostToMyCollectionApi(postId)

    if (response.code !== 200) {
      throw new Error(response.message || '复制收藏失败')
    }

    return response.data
  } catch (error) {
    const err = error as any
    console.error('复制收藏失败:', err)
    throw err.response?.data || err
  }
}
