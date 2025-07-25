<template>
  <div class="flex h-screen bg-gray-50/80 overflow-hidden">
    <!-- 顶部导航栏 -->
    <div class="flex-1 flex flex-col">
      <!-- 头部 -->
      <header class="bg-white/90 glass-effect border-b border-gray-100 px-6 py-4">
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-4">
            <!-- 返回按钮 -->
            <button 
              @click="goBack"
              class="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-smooth"
              title="返回"
            >
              <ArrowLeft class="w-5 h-5" />
            </button>
            
            <!-- 收藏信息 -->
            <div class="flex items-center space-x-3">
              <div class="text-2xl">{{ collection?.icon || '📚' }}</div>
              <div>
                <h1 class="text-2xl font-bold text-gray-900">{{ collection?.name || '加载中...' }}</h1>
                <p class="text-sm text-gray-500">{{ bookmarks.length }} 个书签</p>
              </div>
            </div>
          </div>
          
          <!-- 操作按钮 -->
          <div class="flex items-center space-x-2">
            <button 
              @click="showAddBookmark = true"
              class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium text-sm transition-smooth flex items-center space-x-2"
            >
              <Plus class="w-4 h-4" />
              <span>添加书签</span>
            </button>
            
            <button 
              @click="refreshBookmarks"
              :disabled="isLoading"
              class="bg-gray-100 hover:bg-gray-200 text-gray-700 px-4 py-2 rounded-lg font-medium text-sm transition-smooth flex items-center space-x-2"
            >
              <RotateCcw :class="[
                'w-4 h-4 transition-transform duration-300',
                isLoading ? 'animate-spin' : ''
              ]" />
              <span>刷新</span>
            </button>
          </div>
        </div>
      </header>
      
      <!-- 主内容区域 -->
      <main class="flex-1 overflow-auto p-6">
        <!-- 加载状态 -->
        <div v-if="isLoading && bookmarks.length === 0" class="flex items-center justify-center h-64">
          <div class="text-center">
            <div class="w-8 h-8 border-2 border-gray-300 border-t-blue-600 rounded-full animate-spin mx-auto mb-4"></div>
            <p class="text-gray-500">正在加载书签...</p>
          </div>
        </div>
        
        <!-- 书签列表 -->
        <div v-else-if="bookmarks.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div 
            v-for="bookmark in bookmarks" 
            :key="bookmark.id"
            class="bg-white/90 glass-effect border border-gray-100 rounded-xl p-4 hover:shadow-lg transition-all duration-300 group"
          >
            <!-- 网站图标和标题 -->
            <div class="flex items-start space-x-3 mb-3">
              <div class="w-10 h-10 bg-gray-100 rounded-lg flex items-center justify-center flex-shrink-0">
                <img 
                  v-if="bookmark.favicon" 
                  :src="bookmark.favicon" 
                  :alt="bookmark.title"
                  class="w-6 h-6 rounded"
                  @error="handleImageError"
                >
                <Globe v-else class="w-5 h-5 text-gray-400" />
              </div>
              <div class="flex-1 min-w-0">
                <h3 class="font-semibold text-gray-900 truncate">{{ bookmark.title }}</h3>
                <p class="text-sm text-gray-500 truncate">{{ getDomain(bookmark.url) }}</p>
              </div>
            </div>
            
            <!-- 描述 -->
            <p v-if="bookmark.description" class="text-sm text-gray-600 mb-3 line-clamp-2">
              {{ bookmark.description }}
            </p>
            
            <!-- 标签 -->
            <div v-if="bookmark.tags && bookmark.tags.length > 0" class="flex flex-wrap gap-1 mb-3">
              <span 
                v-for="tag in bookmark.tags.slice(0, 3)" 
                :key="tag"
                class="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded-full"
              >
                {{ tag }}
              </span>
              <span v-if="bookmark.tags.length > 3" class="px-2 py-1 bg-gray-100 text-gray-500 text-xs rounded-full">
                +{{ bookmark.tags.length - 3 }}
              </span>
            </div>
            
            <!-- 时间和操作 -->
            <div class="flex items-center justify-between">
              <span class="text-xs text-gray-400">{{ formatDate(bookmark.created_at) }}</span>
              <div class="flex items-center space-x-1 opacity-0 group-hover:opacity-100 transition-opacity">
                <button 
                  @click="openBookmark(bookmark.url)"
                  class="p-1.5 text-gray-400 hover:text-blue-600 rounded hover:bg-blue-50 transition-smooth"
                  title="打开链接"
                >
                  <ExternalLink class="w-4 h-4" />
                </button>
                <button 
                  @click="editBookmark(bookmark)"
                  class="p-1.5 text-gray-400 hover:text-gray-600 rounded hover:bg-gray-100 transition-smooth"
                  title="编辑"
                >
                  <Edit class="w-4 h-4" />
                </button>
                <button 
                  @click="deleteBookmark(bookmark.id)"
                  class="p-1.5 text-gray-400 hover:text-red-600 rounded hover:bg-red-50 transition-smooth"
                  title="删除"
                >
                  <Trash2 class="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 空状态 -->
        <div v-else class="text-center py-16">
          <div class="text-6xl mb-4">🔖</div>
          <h3 class="text-xl font-semibold text-gray-900 mb-2">这个收藏还是空的</h3>
          <p class="text-gray-500 mb-6">添加您喜欢的网站链接到这个收藏中</p>
          <button 
            @click="showAddBookmark = true"
            class="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium transition-smooth"
          >
            添加第一个书签
          </button>
        </div>
      </main>
    </div>
    
    <!-- 添加书签模态框 -->
    <div v-if="showAddBookmark" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-xl p-6 max-w-md w-full">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">添加书签</h3>
        
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">网站链接</label>
            <input 
              v-model="newBookmark.url" 
              type="url" 
              class="w-full border border-gray-200 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-600 focus:border-transparent bg-white transition-smooth text-sm"
              placeholder="https://example.com"
              @blur="fetchUrlMetadata"
            >
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">标题</label>
            <input 
              v-model="newBookmark.title" 
              type="text" 
              class="w-full border border-gray-200 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-600 focus:border-transparent bg-white transition-smooth text-sm"
              placeholder="网站标题"
            >
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">描述（可选）</label>
            <textarea 
              v-model="newBookmark.description" 
              class="w-full border border-gray-200 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-600 focus:border-transparent bg-white transition-smooth text-sm resize-none"
              rows="3"
              placeholder="描述这个网站..."
            ></textarea>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">标签（可选）</label>
            <input 
              v-model="newBookmarkTags" 
              type="text" 
              class="w-full border border-gray-200 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-600 focus:border-transparent bg-white transition-smooth text-sm"
              placeholder="用逗号分隔多个标签"
            >
          </div>
        </div>

        <div class="flex space-x-3 mt-6">
          <button 
            @click="showAddBookmark = false"
            class="flex-1 bg-gray-100 text-gray-700 py-2.5 rounded-lg hover:bg-gray-200 transition-smooth font-medium text-sm"
          >
            取消
          </button>
          <button 
            @click="addBookmark"
            :disabled="!newBookmark.url || !newBookmark.title"
            class="flex-1 bg-blue-600 text-white py-2.5 rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-smooth font-medium text-sm"
          >
            添加
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { 
  ArrowLeft, Plus, RotateCcw, Globe, ExternalLink, Edit, Trash2
} from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()

// 收藏ID
const collectionId = computed(() => route.params.id)

// 数据
const collection = ref(null)
const bookmarks = ref([])
const isLoading = ref(false)

// 模态框
const showAddBookmark = ref(false)
const newBookmark = ref({
  url: '',
  title: '',
  description: '',
  favicon: ''
})
const newBookmarkTags = ref('')

// API配置
const API_BASE_URL = 'http://localhost:8000/api/v1'

// 获取收藏信息
const fetchCollection = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/category/${collectionId.value}`)
    const result = await response.json()
    
    if (result.status === 'success' && result.data) {
      collection.value = {
        id: result.data.id,
        name: result.data.name,
        icon: result.data.emoji || '📚'
      }
    }
  } catch (error) {
    console.error('获取收藏信息失败:', error)
  }
}

// 获取书签列表
const fetchBookmarks = async () => {
  isLoading.value = true
  try {
    // 这里需要根据实际API调整
    const response = await fetch(`${API_BASE_URL}/bookmarks?category_id=${collectionId.value}`)
    const result = await response.json()
    
    if (result.status === 'success' && result.data) {
      bookmarks.value = result.data.bookmarks || []
    }
  } catch (error) {
    console.error('获取书签失败:', error)
    // 使用模拟数据
    bookmarks.value = [
      {
        id: 1,
        title: 'Vue.js 官网',
        url: 'https://vuejs.org',
        description: 'Vue.js 渐进式 JavaScript 框架',
        favicon: 'https://vuejs.org/favicon.ico',
        tags: ['Vue', '前端', '框架'],
        created_at: new Date().toISOString()
      }
    ]
  } finally {
    isLoading.value = false
  }
}

// 刷新书签
const refreshBookmarks = async () => {
  await fetchBookmarks()
}

// 返回上一页
const goBack = () => {
  router.push('/')
}

// 打开书签
const openBookmark = (url) => {
  window.open(url, '_blank')
}

// 编辑书签
const editBookmark = (bookmark) => {
  console.log('编辑书签:', bookmark)
}

// 删除书签
const deleteBookmark = async (bookmarkId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/bookmarks/${bookmarkId}`, {
      method: 'DELETE'
    })
    
    if (response.ok) {
      bookmarks.value = bookmarks.value.filter(bookmark => bookmark.id !== bookmarkId)
    }
  } catch (error) {
    console.error('删除书签失败:', error)
  }
}

// 添加书签
const addBookmark = async () => {
  if (!newBookmark.value.url || !newBookmark.value.title) return

  const tags = newBookmarkTags.value.trim() ? 
    newBookmarkTags.value.split(',').map(tag => tag.trim()) : []

  const bookmark = {
    id: Date.now(),
    title: newBookmark.value.title,
    url: newBookmark.value.url,
    description: newBookmark.value.description,
    favicon: newBookmark.value.favicon,
    tags: tags,
    category_id: collectionId.value,
    created_at: new Date().toISOString()
  }

  try {
    const response = await fetch(`${API_BASE_URL}/bookmarks`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(bookmark)
    })

    if (response.ok) {
      bookmarks.value.unshift(bookmark)
      resetNewBookmarkForm()
      showAddBookmark.value = false
    }
  } catch (error) {
    console.error('添加书签失败:', error)
    // 临时添加到本地
    bookmarks.value.unshift(bookmark)
    resetNewBookmarkForm()
    showAddBookmark.value = false
  }
}

// 重置表单
const resetNewBookmarkForm = () => {
  newBookmark.value = {
    url: '',
    title: '',
    description: '',
    favicon: ''
  }
  newBookmarkTags.value = ''
}

// 获取URL元数据
const fetchUrlMetadata = async () => {
  if (!newBookmark.value.url) return
  
  try {
    // 这里可以实现获取网站标题和favicon的功能
    // 暂时使用简单的域名提取
    const domain = getDomain(newBookmark.value.url)
    if (!newBookmark.value.title) {
      newBookmark.value.title = domain
    }
    newBookmark.value.favicon = `https://www.google.com/s2/favicons?domain=${domain}`
  } catch (error) {
    console.error('获取URL元数据失败:', error)
  }
}

// 获取域名
const getDomain = (url) => {
  try {
    return new URL(url).hostname
  } catch {
    return url
  }
}

// 格式化日期
const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('zh-CN', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 处理图片加载错误
const handleImageError = (event) => {
  event.target.style.display = 'none'
}

// 初始化
onMounted(async () => {
  await Promise.all([
    fetchCollection(),
    fetchBookmarks()
  ])
})
</script>

<style scoped>
.glass-effect {
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
}

.transition-smooth {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
