
import {
  createPostApi,
  deletePostApi,
  getPostsApi,
  likeAssetApi,
  unlikeAssetApi,
  createCommentApi,
  getPostCommentsApi,
  deleteCommentApi,
  getPostCollectionDetailsApi,
  getUserPostsApi
} from '@/api'

// 创建推文（发布收藏到社区）
export const createPost = async (referCollectionId, description) => {
  try {
    const response = await createPostApi(referCollectionId, description)

    if (response.code !== 200) {
      throw new Error(response.message || '创建推文失败')
    }

    return response.data
  } catch (error) {
    console.error('创建推文失败:', error)
    throw error.response?.data || error
  }
}

// 删除推文
export const deletePost = async (postId) => {
  try {
    const response = await deletePostApi(postId)

    if (response.code !== 200) {
      throw new Error(response.message || '删除推文失败')
    }

    return response.data
  } catch (error) {
    console.error('删除推文失败:', error)
    throw error.response?.data || error
  }
}

// 获取社区推文列表
export const getPosts = async (page = 1, limit = 20) => {
  try {
    const response = await getPostsApi(page, limit)

    if (response.code !== 200) {
      throw new Error(response.message || '获取推文列表失败')
    }

    return response.data
  } catch (error) {
    console.error('获取推文列表失败:', error)
    throw error.response?.data || error
  }
}

// 点赞推文或评论
export const likeAsset = async (assetId, assetType) => {
  try {
    // 目前API层的likePostApi只接受post_id，未来可能需要扩展支持asset_type
    const response = await likeAssetApi(assetId, assetType)

    if (response.code !== 200) {
      throw new Error(response.message || '点赞失败')
    }

    return response.data
  } catch (error) {
    console.error('点赞失败:', error)
    throw error.response?.data || error
  }
}

// 取消点赞推文或评论
export const unlikeAsset = async (assetId, assetType) => {
  try {
    const response = await unlikeAssetApi(assetId, assetType)

    if (response.code !== 200) {
      throw new Error(response.message || '取消点赞失败')
    }

    return response.data
  } catch (error) {
    console.error('取消点赞失败:', error)
    throw error.response?.data || error
  }
}

// 为推文添加评论
export const createComment = async (postId, content) => {
  try {
    const response = await createCommentApi(postId, content)

    if (response.code !== 200) {
      throw new Error(response.message || '添加评论失败')
    }

    return response.data
  } catch (error) {
    console.error('添加评论失败:', error)
    throw error.response?.data || error
  }
}

// 获取推文的评论列表
export const getPostComments = async (postId, page = 1, limit = 20) => {
  try {
    const response = await getPostCommentsApi(postId, page, limit)

    if (response.code !== 200) {
      throw new Error(response.message || '获取评论列表失败')
    }

    return response.data
  } catch (error) {
    console.error('获取评论列表失败:', error)
    throw error.response?.data || error
  }
}

// 删除评论
export const deleteComment = async (commentId) => {
  try {
    const response = await deleteCommentApi(commentId)

    if (response.code !== 200) {
      throw new Error(response.message || '删除评论失败')
    }

    return response.data
  } catch (error) {
    console.error('删除评论失败:', error)
    throw error.response?.data || error
  }
}

// 获取推文关联的收藏详情（公共接口，无需登录）
export const getPostCollectionDetails = async (postId) => {
  try {
    const response = await getPostCollectionDetailsApi(postId)

    // 由于Axios拦截器已经提取了data字段，这里直接返回响应
    return response
  } catch (error) {
    console.error('获取推文收藏详情失败:', error)
    throw error.response?.data || error
  }
}

// 获取当前用户推文列表
export const getUserPosts = async (page = 1, limit = 20) => {
  try {
    const response = await getUserPostsApi(page, limit)

    if (response.code !== 200) {
      throw new Error(response.message || '获取我的推文失败')
    }

    return response.data
  } catch (error) {
    console.error('获取我的推文失败:', error)
    throw error.response?.data || error
  }
}
