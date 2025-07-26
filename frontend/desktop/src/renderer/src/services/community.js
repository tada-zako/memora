import api from './api'

// 创建推文（发布收藏到社区）
export const createPost = async (refer_collection_id, description) => {
  try {
    const response = await api.post('/api/v1/community/posts', {
      refer_collection_id,
      description
    })
    return response.data
  } catch (error) {
    console.error('创建推文失败:', error)
    throw error.response?.data || error
  }
}

// 删除推文
export const deletePost = async (post_id) => {
  try {
    const response = await api.delete(`/api/v1/community/posts/${post_id}`)
    return response.data
  } catch (error) {
    console.error('删除推文失败:', error)
    throw error.response?.data || error
  }
}

// 获取社区推文列表
export const getPosts = async (page = 1, limit = 20) => {
  try {
    const response = await api.get('/api/v1/community/posts', {
      params: { page, limit }
    })
    return response.data
  } catch (error) {
    console.error('获取推文列表失败:', error)
    throw error.response?.data || error
  }
}

// 点赞推文或评论
export const likeAsset = async (asset_id, asset_type) => {
  try {
    const response = await api.post('/api/v1/community/like', {
      asset_id,
      asset_type
    })
    return response.data
  } catch (error) {
    console.error('点赞失败:', error)
    throw error.response?.data || error
  }
}

// 取消点赞推文或评论
export const unlikeAsset = async (asset_id, asset_type) => {
  try {
    const response = await api.delete('/api/v1/community/like', {
      data: {
        asset_id,
        asset_type
      }
    })
    return response.data
  } catch (error) {
    console.error('取消点赞失败:', error)
    throw error.response?.data || error
  }
}

// 为推文添加评论
export const createComment = async (post_id, content) => {
  try {
    const response = await api.post(`/api/v1/community/posts/${post_id}/comment`, {
      content
    })
    return response.data
  } catch (error) {
    console.error('添加评论失败:', error)
    throw error.response?.data || error
  }
}

// 获取推文的评论列表
export const getPostComments = async (post_id, page = 1, limit = 20) => {
  try {
    const response = await api.get(`/api/v1/community/posts/${post_id}/comments`, {
      params: { page, limit }
    })
    return response.data
  } catch (error) {
    console.error('获取评论列表失败:', error)
    throw error.response?.data || error
  }
}

// 删除评论
export const deleteComment = async (comment_id) => {
  try {
    const response = await api.delete(`/api/v1/community/comments/${comment_id}`)
    return response.data
  } catch (error) {
    console.error('删除评论失败:', error)
    throw error.response?.data || error
  }
} 