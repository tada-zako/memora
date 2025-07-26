<template>
  <div class="flex-1 flex flex-col bg-gray-50/80">
    <!-- 主内容区 -->
    <div class="bg-white/90 glass-effect border border-gray-100 h-full min-h-0" style="padding: 16px;">


      <!-- 标题区域 -->
          <div class="flex items-center justify-between mb-8">
            <div class="flex items-center">
              <div class="bg-gradient-to-br rounded-lg flex items-center justify-center w-8 h-8 mr-3">
                <span class="text-white text-2xl">🌏</span>
              </div>
              <div>
                <h1 class="text-2xl font-bold text-gray-900">社区</h1>
              </div>
            </div>
          <!-- 刷新按钮 -->
          <button
            @click="refreshPosts"
            :disabled="loading"
            class="bg-gray-100 hover:bg-gray-200 text-gray-700 px-4 py-2 rounded-lg transition-smooth font-medium text-sm btn-hover flex items-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
            title="刷新"
          >
            <RefreshIcon class="w-4 h-4" :class="{ 'animate-spin': loading }" />
            <span>{{ loading ? '刷新中...' : '刷新' }}</span>
          </button>
        </div>

        <!-- 加载状态 -->
        <div v-if="loading && posts.length === 0" class="flex justify-center py-12">
          <div class="flex items-center gap-2 text-gray-500">
            <div class="w-5 h-5 border-2 border-gray-300 border-t-blue-600 rounded-full animate-spin"></div>
            加载中...
          </div>
        </div>

        <!-- 推文列表 -->
        <div v-else-if="posts.length > 0" class="space-y-6">
          <div
            v-for="post in posts"
            :key="post.id"
            class="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition-all duration-200"
          >
            <!-- 推文头部 -->
            <div class="p-4 border-b border-gray-100">
              <div class="flex items-center justify-between">
                <div class="flex items-center gap-3">
                  <div class="w-10 h-10 bg-gray-200 rounded-full flex items-center justify-center overflow-hidden">
                    <img v-if="post.avatar_url" :src="post.avatar_url" alt="Avatar" class="w-full h-full object-cover">
                    <User v-else class="w-6 h-6 text-gray-500" />
                  </div>
                  <div>
                    <div class="font-medium text-gray-900">{{ post.username }}</div>
                    <div class="text-xs text-gray-500">{{ formatDate(post.created_at) }}</div>
                  </div>
                </div>
                <button
                  v-if="isMyPost(post)"
                  @click="deletePostById(post.post_id)"
                  class="text-gray-400 hover:text-red-500 transition-colors"
                >
                  <TrashIcon class="w-4 h-4" />
                </button>
              </div>

              <!-- 推文描述 -->
              <div v-if="post.description" class="mt-3 text-gray-700">
                <div 
                  :class="[
                    'transition-all duration-200',
                    post.showFullDescription || post.description.length <= 150 
                      ? '' 
                      : 'line-clamp-3'
                  ]"
                >
                  {{ post.description }}
                </div>
                <button
                  v-if="post.description.length > 150"
                  @click="post.showFullDescription = !post.showFullDescription"
                  class="text-blue-600 hover:text-blue-700 text-sm mt-1"
                >
                  {{ post.showFullDescription ? '收起' : '展开' }}
                </button>
              </div>
            </div>

            <!-- 收藏内容 -->
            <div class="p-4">
              <div 
                class="bg-gray-50 rounded-lg p-4 cursor-pointer hover:bg-gray-100 transition-colors"
                @click="viewCollectionDetail(post.refer_collection_id)"
              >
                <div class="flex items-center justify-between mb-2">
                  <div class="flex items-center gap-2">
                    <BookmarkIcon class="w-4 h-4 text-gray-500" />
                    <span class="text-sm font-medium text-gray-700">分享的收藏</span>
                    <span v-if="post.category_name" class="px-2 py-0.5 bg-blue-100 text-blue-700 text-xs rounded">
                      {{ post.category_name }}
                    </span>
                  </div>
                  <div class="text-xs text-gray-400 flex items-center gap-1">
                    <span>点击查看详情</span>
                    <ExternalLinkIcon class="w-3 h-3" />
                  </div>
                </div>
                
                <!-- 收藏详情 -->
                <div v-if="post.collection_details" class="mt-2">
                  <h4 v-if="post.collection_details.title" class="font-medium text-gray-900 mb-1 hover:text-blue-700 transition-colors">
                    {{ post.collection_details.title }}
                  </h4>
                  <p v-if="post.collection_details.summary" class="text-sm text-gray-600 line-clamp-2">
                    {{ parseSummary(post.collection_details.summary) }}
                  </p>
                  <div v-if="post.collection_details.url" class="mt-2">
                    <a 
                      :href="post.collection_details.url"
                      target="_blank"
                      rel="noopener noreferrer"
                      class="text-xs text-blue-600 hover:text-blue-700 inline-flex items-center gap-1"
                      @click.stop
                    >
                      <ExternalLinkIcon class="w-3 h-3" />
                      访问原文
                    </a>
                  </div>
                </div>

                <!-- 标签 -->
                <div v-if="post.tags" class="flex flex-wrap gap-1 mt-2">
                  <span
                    v-for="tag in post.tags.split(',')"
                    :key="tag"
                    class="px-2 py-0.5 bg-gray-200 text-gray-700 text-xs rounded"
                  >
                    #{{ tag.trim() }}
                  </span>
                </div>
              </div>
            </div>

            <!-- 操作栏 -->
            <div class="px-4 py-3 border-t border-gray-100 flex items-center justify-between">
              <div class="flex items-center gap-4">
                <!-- 点赞 -->
                <button
                  @click="toggleLike(post)"
                  class="flex items-center gap-1 text-sm transition-colors"
                  :class="post.is_liked_by_me ? 'text-red-500' : 'text-gray-500 hover:text-red-500'"
                >
                  <HeartIcon 
                    class="w-4 h-4" 
                    :class="post.is_liked_by_me ? 'fill-current' : ''"
                  />
                  {{ post.likes_count }}
                </button>

                <!-- 评论 -->
                <button
                  @click="toggleComments(post)"
                  class="flex items-center gap-1 text-sm text-gray-500 hover:text-blue-500 transition-colors"
                >
                  <MessageCircleIcon class="w-4 h-4" />
                  {{ post.comments_count }}
                </button>
              </div>
            </div>

            <!-- 评论区域 -->
            <div v-if="post.showComments" class="border-t border-gray-100">
              <!-- 评论输入 -->
              <div class="p-4">
                <div class="flex gap-3">
                  <div class="w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center flex-shrink-0 overflow-hidden">
                    <img v-if="currentUser && currentUser.avatar_attachment_id" :src="buildAvatarUrl(currentUser.avatar_attachment_id)" alt="My Avatar" class="w-full h-full object-cover">
                    <span v-else class="text-white font-semibold text-xs">我</span>
                  </div>
                  <div class="flex-1">
                    <textarea
                      v-model="post.newComment"
                      placeholder="写下你的评论..."
                      class="w-full p-3 border border-gray-300 rounded-lg resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
                      rows="2"
                    ></textarea>
                    <div class="flex justify-end mt-2">
                      <button
                        @click="submitComment(post)"
                        :disabled="!post.newComment?.trim() || post.commentLoading"
                        class="px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        {{ post.commentLoading ? '发布中...' : '发布评论' }}
                      </button>
                    </div>
                  </div>
                </div>
              </div>

              <!-- 评论列表 -->
              <div v-if="post.comments && post.comments.length > 0" class="px-4 pb-4">
                <div
                  v-for="comment in post.comments"
                  :key="comment.id"
                  class="flex gap-3 mb-4 last:mb-0"
                >
                  <div class="w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center flex-shrink-0 overflow-hidden">
                    <img v-if="comment.avatar_url" :src="comment.avatar_url" alt="Comment Avatar" class="w-full h-full object-cover">
                    <User v-else class="w-6 h-6 text-gray-500" />
                  </div>
                  <div class="flex-1">
                    <div class="bg-gray-50 rounded-lg p-3">
                      <div class="flex items-center justify-between mb-1">
                        <span class="font-medium text-sm text-gray-900">{{ comment.username }}</span>
                        <div class="flex items-center gap-2">
                          <span class="text-xs text-gray-500">{{ formatDate(comment.created_at) }}</span>
                          <button
                            v-if="isMyComment(comment)"
                            @click="deleteCommentById(comment.id)"
                            class="text-gray-400 hover:text-red-500 transition-colors"
                          >
                            <TrashIcon class="w-3 h-3" />
                          </button>
                        </div>
                      </div>
                      <p class="text-sm text-gray-700">{{ comment.content }}</p>
                    </div>
                    
                    <!-- 评论点赞 -->
                    <div class="flex items-center gap-2 mt-2">
                      <button
                        @click="toggleCommentLike(comment)"
                        class="flex items-center gap-1 text-xs transition-colors"
                        :class="comment.is_liked_by_me ? 'text-red-500' : 'text-gray-400 hover:text-red-500'"
                      >
                        <HeartIcon 
                          class="w-3 h-3" 
                          :class="comment.is_liked_by_me ? 'fill-current' : ''"
                        />
                        {{ comment.likes_count }}
                      </button>
                    </div>
                  </div>
                </div>
              </div>

              <!-- 加载更多评论 -->
              <div v-if="post.hasMoreComments" class="px-4 pb-4">
                <button
                  @click="loadMoreComments(post)"
                  :disabled="post.loadingComments"
                  class="w-full py-2 text-sm text-blue-600 hover:text-blue-700 disabled:opacity-50"
                >
                  {{ post.loadingComments ? '加载中...' : '加载更多评论' }}
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- 空状态 -->
        <div v-else class="text-center py-16">
          <div class="w-24 h-24 bg-gradient-to-br from-blue-100 to-purple-100 rounded-full flex items-center justify-center mx-auto mb-6">
            <Earth class="w-12 h-12 text-blue-600" />
          </div>
          <h2 class="text-xl font-semibold text-gray-900 mb-4">还没有人分享内容</h2>
          <p class="text-gray-600 mb-6">
            成为第一个在社区分享收藏的人吧！
          </p>
          <button
            @click="goToCollections"
            class="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2 mx-auto"
          >
            <BookmarkIcon class="w-5 h-5" />
            去看看我的收藏
          </button>
        </div>

        <!-- 加载更多 -->
        <div v-if="posts.length > 0 && hasMore" class="text-center py-6">
          <button
            @click="loadMore"
            :disabled="loadingMore"
            class="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
          >
            {{ loadingMore ? '加载中...' : '加载更多' }}
          </button>
        </div>

        <!-- 无更多内容提示 -->
        <div v-if="posts.length > 0 && !hasMore" class="text-center py-6">
          <div class="text-gray-500 text-sm">
            🎉 没有更多内容了，快去分享一些收藏吧！
          </div>
        </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { 
  Earth, 
  RefreshCw as RefreshIcon,
  Heart as HeartIcon,
  MessageCircle as MessageCircleIcon,
  ExternalLink as ExternalLinkIcon,
  Bookmark as BookmarkIcon,
  Trash2 as TrashIcon,
  User
} from 'lucide-vue-next'
import { 
  getPosts, 
  likeAsset, 
  unlikeAsset, 
  createComment, 
  getPostComments, 
  deletePost, 
  deleteComment 
} from '../services/community'
import { isAuthenticated, buildAvatarUrl } from '../services/auth'

const router = useRouter()

// 状态管理
const posts = ref([])
const loading = ref(false)
const loadingMore = ref(false)
const hasMore = ref(true)
const currentPage = ref(1)
const currentUser = ref(null)

// 解析summary
const parseSummary = (summary) => {
  if (typeof summary !== 'string') {
    return summary
  }

  let currentSummary = summary.trim()

  // 移除 markdown 代码块
  if (currentSummary.startsWith('```json')) {
    currentSummary = currentSummary.replace(/^```json\n/, '').replace(/\n```$/, '').trim()
  }

  // 尝试解析JSON
  try {
    const parsed = JSON.parse(currentSummary)
    // 如果解析成功并且包含summary字段，则递归解析
    if (parsed && typeof parsed.summary === 'string') {
      return parseSummary(parsed.summary)
    }
    return currentSummary
  } catch (e) {
    // 如果不是一个JSON字符串，则按原样返回
    return currentSummary
  }
}

// 初始化
onMounted(async () => {
  if (!isAuthenticated()) {
    console.log('用户未登录，跳转到登录页面')
    router.push('/login')
    return
  }

  // 从localStorage获取用户信息
  const userInfo = localStorage.getItem('user_info')
  if (userInfo) {
    currentUser.value = JSON.parse(userInfo)
  }

  await loadPosts()
})

// 加载推文列表
const loadPosts = async (page = 1) => {
  try {
    if (page === 1) {
      loading.value = true
    } else {
      loadingMore.value = true
    }

    const result = await getPosts(page, 10)
    
    if (result.status === 'success' && result.data && result.data.posts) {
      const newPosts = result.data.posts.map((post) => {
        return {
          ...post,
          showComments: false,
          comments: [],
          newComment: '',
          commentLoading: false,
          loadingComments: false,
          hasMoreComments: post.comments_count > 0,
          commentsPage: 1,
          showFullDescription: false,
          avatar_url: buildAvatarUrl(post.user?.avatar_attachment_id)
        }
      })

      if (page === 1) {
        posts.value = newPosts
      } else {
        posts.value.push(...newPosts)
      }

      hasMore.value = newPosts.length === 10
      currentPage.value = page
    }
  } catch (error) {
    console.error('加载推文失败:', error)
    
    if (error.detail === 'Not authenticated' || error.message?.includes('401')) {
      console.log('认证失败，跳转到登录页面')
      router.push('/login')
    }
  } finally {
    loading.value = false
    loadingMore.value = false
  }
}

// 刷新推文
const refreshPosts = () => {
  currentPage.value = 1
  hasMore.value = true
  loadPosts(1)
}

// 加载更多推文
const loadMore = () => {
  if (!loadingMore.value && hasMore.value) {
    loadPosts(currentPage.value + 1)
  }
}

// 切换点赞状态
const toggleLike = async (post) => {
  try {
    if (post.is_liked_by_me) {
      await unlikeAsset(post.id, 'post')
      post.is_liked_by_me = false
      post.likes_count = Math.max(0, post.likes_count - 1)
    } else {
      await likeAsset(post.id, 'post')
      post.is_liked_by_me = true
      post.likes_count += 1
    }
  } catch (error) {
    console.error('点赞操作失败:', error)
  }
}

// 切换评论显示
const toggleComments = async (post) => {
  post.showComments = !post.showComments
  
  if (post.showComments && post.comments.length === 0) {
    await loadComments(post)
  }
}

// 加载评论
const loadComments = async (post, page = 1) => {
  try {
    post.loadingComments = true
    
    const result = await getPostComments(post.post_id, page, 5)
    
    if (result.status === 'success' && result.data && result.data.comments) {
      const newComments = result.data.comments.map((comment) => {
        return { 
          ...comment, 
          avatar_url: buildAvatarUrl(comment.user?.avatar_attachment_id)
        }
      })

      if (page === 1) {
        post.comments = newComments
      } else {
        post.comments.push(...newComments)
      }
      
      post.hasMoreComments = result.data.comments.length === 5
      post.commentsPage = page
    }
  } catch (error) {
    console.error('加载评论失败:', error)
  } finally {
    post.loadingComments = false
  }
}

// 加载更多评论
const loadMoreComments = (post) => {
  if (!post.loadingComments && post.hasMoreComments) {
    loadComments(post, post.commentsPage + 1)
  }
}

// 提交评论
const submitComment = async (post) => {
  if (!post.newComment?.trim() || post.commentLoading) return

  try {
    post.commentLoading = true
    
    const result = await createComment(post.post_id, post.newComment.trim())
    
    if (result.status === 'success' && result.data && result.data.comment) {
      // 在评论列表顶部添加新评论
      post.comments.unshift(result.data.comment)
      post.comments_count += 1
      post.newComment = ''
    }
  } catch (error) {
    console.error('发布评论失败:', error)
    alert('发布评论失败，请稍后重试')
  } finally {
    post.commentLoading = false
  }
}

// 切换评论点赞
const toggleCommentLike = async (comment) => {
  try {
    if (comment.is_liked_by_me) {
      await unlikeAsset(comment.id, 'comment')
      comment.is_liked_by_me = false
      comment.likes_count = Math.max(0, comment.likes_count - 1)
    } else {
      await likeAsset(comment.id, 'comment')
      comment.is_liked_by_me = true
      comment.likes_count += 1
    }
  } catch (error) {
    console.error('评论点赞操作失败:', error)
  }
}

// 删除推文
const deletePostById = async (postId) => {
  if (!confirm('确定要删除这条推文吗？')) return

  try {
    await deletePost(postId)
    
    // 从列表中移除
    const index = posts.value.findIndex(p => p.post_id === postId)
    if (index !== -1) {
      posts.value.splice(index, 1)
    }
    
    console.log('推文删除成功')
  } catch (error) {
    console.error('删除推文失败:', error)
    alert('删除推文失败，请稍后重试')
  }
}

// 删除评论
const deleteCommentById = async (commentId) => {
  if (!confirm('确定要删除这条评论吗？')) return

  try {
    await deleteComment(commentId)
    
    // 从所有推文的评论列表中移除
    posts.value.forEach(post => {
      const commentIndex = post.comments.findIndex(c => c.id === commentId)
      if (commentIndex !== -1) {
        post.comments.splice(commentIndex, 1)
        post.comments_count = Math.max(0, post.comments_count - 1)
      }
    })
    
    console.log('评论删除成功')
  } catch (error) {
    console.error('删除评论失败:', error)
    alert('删除评论失败，请稍后重试')
  }
}

// 判断是否是我的推文
const isMyPost = (post) => {
  return currentUser.value && post.user_id === currentUser.value.id
}

// 判断是否是我的评论
const isMyComment = (comment) => {
  return currentUser.value && comment.user_id === currentUser.value.id
}

// 跳转到收藏详情页
const viewCollectionDetail = (collectionId) => {
  router.push({
    name: 'CollectionDetail',
    params: { collection_id: collectionId }
  })
}

// 跳转到收藏页面
const goToCollections = () => {
  router.push({ name: 'Home' })
}

// 格式化日期 - 转换为北京时间显示
const formatDate = (dateString) => {
  // 如果后端返回的是UTC时间（没有时区信息），需要手动添加Z标识
  let isoString = dateString
  if (!dateString.includes('Z') && !dateString.includes('+') && !dateString.includes('-', 10)) {
    isoString = dateString + 'Z'
  }
  
  const date = new Date(isoString)
  const now = new Date()
  const diff = now - date
  
  // 少于1分钟
  if (diff < 60000) {
    return '刚刚'
  }
  
  // 少于1小时
  if (diff < 3600000) {
    return `${Math.floor(diff / 60000)}分钟前`
  }
  
  // 少于24小时
  if (diff < 86400000) {
    return `${Math.floor(diff / 3600000)}小时前`
  }
  
  // 超过24小时，显示具体日期（北京时间）
  return date.toLocaleString('zh-CN', {
    timeZone: 'Asia/Shanghai',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>

<style scoped>
.glass-effect {
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
}

.custom-scrollbar {
  scrollbar-width: thin;
  scrollbar-color: rgba(156, 163, 175, 0.3) transparent;
}

.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}

.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
  background: rgba(156, 163, 175, 0.3);
  border-radius: 3px;
  transition: background-color 0.2s ease;
}

.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: rgba(156, 163, 175, 0.5);
}

/* 优化触摸滚动 */
.custom-scrollbar {
  -webkit-overflow-scrolling: touch;
  overscroll-behavior: contain;
}

.btn-hover:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.transition-smooth {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.line-clamp-3 {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
