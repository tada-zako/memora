import api from './api'

// 创建推文（发布收藏到社区）
export const createPostApi = async (referCollectionId, description) => {
  return await api.post('/api/v1/community/posts', {
    refer_collection_id: referCollectionId,
    description: description
  })
}

// 删除推文
export const deletePostApi = async (postId) => {
  return await api.delete(`/api/v1/community/posts/${postId}`)
}

// 获取社区推文列表
export const getPostsApi = async (page = 1, limit = 20) => {
  return await api.get('/api/v1/community/posts', {
    params: { page, limit }
  })
}

// 点赞推文或评论
export const likeAssetApi = async (assetId, assetType) => {
  return await api.post(`/api/v1/community/like`, {
    asset_id: assetId,
    asset_type: assetType
  })
}

// 取消点赞推文或评论
export const unlikeAssetApi = async (assetId, assetType) => {
  return await api.delete('/api/v1/community/like', {
    data: {
      asset_id: assetId,
      asset_type: assetType
    }
  })
}

// 为推文添加评论
export const createCommentApi = async (postId, content) => {
  return await api.post(`/api/v1/community/posts/${postId}/comments`, {
    content
  })
}

// 获取推文的评论列表
export const getPostCommentsApi = async (postId, page, limit) => {
  return await api.get(`/api/v1/community/posts/${postId}/comments`, {
    params: { page, limit }
  })
}

// 删除评论
export const deleteCommentApi = async (commentId) => {
  return await api.delete(`/api/v1/community/comments/${commentId}`)
}

// 获取推文关联的收藏详情（公共接口，无需登录）
export const getPostCollectionDetailsApi = async (postId) => {
  return await api.get(`/api/v1/community/collections/${postId}/collection`)
}

// 获取当前用户推文列表
export const getUserPostsApi = async (page, limit) => {
  return await api.get(`/api/v1/community/my-posts`, {
    params: { page, limit }
  })
}
