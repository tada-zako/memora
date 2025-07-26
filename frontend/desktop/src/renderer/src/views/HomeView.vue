<template>
  <!-- 只保留主内容区 -->
  <div class="flex-1 flex flex-col overflow-hidden min-w-0">
    <main class="flex-1 overflow-auto custom-scrollbar">
      <!-- 收藏管理页面 -->
      <div v-if="currentPage === 'collections'" class="h-full">
        <!-- 主要内容区域 -->
        <div class="bg-white/90 glass-effect border border-gray-100 h-full min-h-0" style="padding: 16px;">
          <!-- 标题区域 -->
          <div class="flex items-center justify-between mb-8">
            <div class="flex items-center">
              <div class="bg-gradient-to-br rounded-lg flex items-center justify-center w-8 h-8 mr-3">
                <span class="text-white text-2xl">✨</span>
              </div>
              <div>
                <h1 class="text-2xl font-bold text-gray-900">收藏夹</h1>
              </div>
            </div>
            <!-- 刷新按钮 -->
            <button 
              @click="refreshCollections"
              :disabled="isLoadingCollections"
              class="bg-gray-100 hover:bg-gray-200 text-gray-700 px-4 py-2 rounded-lg transition-smooth font-medium text-sm btn-hover flex items-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
              title="刷新收藏列表"
            >
              <RefreshIcon :class="[
                'w-4 h-4',
                isLoadingCollections ? 'animate-spin' : ''
              ]" />
              <span>{{ isLoadingCollections ? '刷新中...' : '刷新' }}</span>
            </button>
          </div>
          <div style="width: 100%; display: flex; gap: 16px;">
            <!-- 收藏卡片 -->
            <div 
              v-for="collection in collections" 
              :key="collection.id"
              @click="viewCollection(collection)"
              :class="[ 
              'h-36 w-64 rounded-xl p-3 flex flex-col justify-between cursor-pointer transition-all duration-300 ease-out text-gray-800 relative overflow-hidden group collection-card',
              ]"
            >
              <!-- 内容 -->
              <div class="relative" style="height: 100%;">
                <div class="text-xl mb-1">{{ collection.icon }}</div>
                <h3 class="text-2xl font-bold mb-0.5 truncate text-gray-1000">{{ collection.name }}</h3>
                <p class="text-gray-600 text-sm truncate leading-tight">{{ collection.collection_count }} 个收藏</p>
              </div>


            </div>
          </div>
          <!-- 空状态 -->
          <div v-if="collections.length === 0 && !isLoadingCollections" class="text-center" style="height: calc(100% - 84px); display: flex; justify-content: center; align-items: center; flex-direction: column;">
            <div class="text-6xl mb-4">📚</div>
            <h3 class="text-lg font-semibold text-gray-900 mb-2">还没有收藏</h3>
          </div>
          <!-- 加载状态 -->
          <div v-if="isLoadingCollections && collections.length === 0" class="text-center" style="height: calc(100% - 84px); display: flex; justify-content: center; align-items: center; flex-direction: column;">
            <div class="w-8 h-8 border-2 border-gray-300 border-t-gray-900 rounded-full animate-spin mb-4"></div>
            <p class="text-gray-500">正在加载收藏...</p>
          </div>
        </div>
      </div>
      <!-- 事件列表页面 -->
      <div v-if="currentPage === 'events'" class="space-y-6 max-w-4xl">
        <!-- 创建事件按钮 -->
        <div class="flex justify-between items-center">
          <div>
            <h3 class="text-lg font-semibold text-gray-900">我的事件</h3>
            <p class="text-sm text-gray-500">管理和查看您的所有事件记录</p>
          </div>
          <button 
            @click="showCreateEvent = true"
            class="bg-gray-900 text-white px-4 py-2 rounded-lg hover:bg-gray-800 transition-smooth font-medium text-sm btn-hover flex items-center space-x-2"
          >
            <Plus class="w-4 h-4" />
            <span>新建事件</span>
          </button>
        </div>
        <!-- 事件列表 -->
        <div class="bg-white/80 glass-effect rounded-xl border border-gray-100">
            <div class="p-4">
              <div class="space-y-3">
                <div v-for="event in events" :key="event.id" class="p-4 border border-gray-100 rounded-lg hover:bg-gray-50/80 transition-smooth">
                  <div class="flex items-start justify-between">
                    <div class="flex-1 min-w-0">
                      <p class="font-medium text-gray-900 truncate">{{ event.description }}</p>
                      <div class="flex items-center space-x-4 mt-2 text-sm text-gray-500">
                        <span>{{ formatDate(event.created_at) }}</span>
                        <span v-if="event.metadata" class="truncate">{{ Object.keys(event.metadata).length }} 个标签</span>
                      </div>
                    </div>
                    <div class="flex items-center space-x-1 ml-4">
                      <button 
                        @click="viewEvent(event)"
                        class="p-1.5 text-gray-400 hover:text-gray-600 rounded hover:bg-gray-100 transition-smooth"
                        title="查看"
                      >
                        <Eye class="w-4 h-4" />
                      </button>
                      <button 
                        @click="editEvent(event)"
                        class="p-1.5 text-gray-400 hover:text-gray-600 rounded hover:bg-gray-100 transition-smooth"
                        title="编辑"
                      >
                        <Edit class="w-4 h-4" />
                      </button>
                      <button 
                        @click="deleteEvent(event.id)"
                        class="p-1.5 text-red-400 hover:text-red-600 rounded hover:bg-red-50 transition-smooth"
                        title="删除"
                      >
                        <Trash2 class="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </div>
                
                <div v-if="events.length === 0" class="text-center py-12">
                  <Calendar class="w-12 h-12 text-gray-300 mx-auto mb-4" />
                  <p class="text-gray-500">暂无事件记录</p>
                  <p class="text-sm text-gray-400 mt-1">点击上方按钮创建您的第一个事件</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      <!-- 附件管理页面 -->
      <div v-if="currentPage === 'attachments'" class="space-y-6 max-w-4xl">
        <!-- 上传区域 -->
        <div class="bg-white/80 glass-effect rounded-xl border border-gray-100 p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">上传附件</h3>
          
          <div class="space-y-4">
            <!-- 事件选择 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">关联事件</label>
              <select v-model="selectedEventId" class="w-full border border-gray-200 rounded-lg px-3 py-2 focus:ring-2 focus:ring-gray-900 focus:border-transparent bg-white/80 transition-smooth text-sm">
                <option value="">选择事件</option>
                <option v-for="event in events" :key="event.id" :value="event.id">
                  {{ event.description }}
                </option>
              </select>
            </div>

            <!-- 文件上传 -->
            <div 
              @drop="handleDrop"
              @dragover.prevent
              @dragenter.prevent
              :class="[
                'border-2 border-dashed rounded-xl p-8 text-center transition-all duration-200',
                isDragging ? 'border-gray-400 bg-gray-50/50' : 'border-gray-200 hover:border-gray-300'
              ]"
            >
              <Upload class="w-10 h-10 text-gray-400 mx-auto mb-3" />
              <h4 class="text-base font-semibold text-gray-900 mb-2">拖拽文件到这里上传</h4>
              <p class="text-gray-500 mb-4 font-light text-sm">支持图片、文档等格式，单个文件不超过 10MB</p>
              <button 
                @click="triggerFileInput"
                class="bg-gray-900 text-white px-4 py-2 rounded-lg hover:bg-gray-800 transition-smooth font-medium text-sm btn-hover"
              >
                选择文件
              </button>
              <input 
                ref="fileInput" 
                type="file" 
                multiple 
                @change="handleFileSelect" 
                class="hidden"
              >
            </div>

            <!-- 描述 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">描述（可选）</label>
              <textarea 
                v-model="attachmentDescription" 
                class="w-full border border-gray-200 rounded-lg px-3 py-2 focus:ring-2 focus:ring-gray-900 focus:border-transparent bg-white/80 transition-smooth text-sm resize-none"
                rows="2"
                placeholder="为此附件添加描述..."
              ></textarea>
            </div>

            <button 
              @click="uploadAttachment"
              :disabled="!selectedEventId || !selectedFile"
              class="w-full bg-blue-600 text-white py-2.5 rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-smooth font-medium text-sm btn-hover"
            >
              上传附件
            </button>
          </div>
        </div>

        <!-- 附件列表 -->
        <div class="bg-white/80 glass-effect rounded-xl border border-gray-100">
          <div class="p-4 border-b border-gray-50">
            <h3 class="text-lg font-semibold text-gray-900">最近上传</h3>
          </div>
          <div class="p-4">
            <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
              <div v-for="attachment in attachments" :key="attachment.id" class="relative group">
                <div class="aspect-square bg-gray-100 rounded-lg border border-gray-200 overflow-hidden">
                  <img 
                    v-if="isImage(attachment.url)"
                    :src="attachment.url" 
                    :alt="attachment.description"
                    class="w-full h-full object-cover"
                  >
                  <div v-else class="w-full h-full flex items-center justify-center">
                    <FileText class="w-6 h-6 text-gray-400" />
                  </div>
                </div>
                <div class="mt-2">
                  <p class="text-xs text-gray-700 truncate font-medium">{{ getFileName(attachment.url) }}</p>
                  <p class="text-xs text-gray-400 mt-0.5">{{ formatDate(attachment.created_at) }}</p>
                </div>
                <div class="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-20 rounded-lg transition-all flex items-center justify-center">
                  <div class="opacity-0 group-hover:opacity-100 transition-opacity flex space-x-1">
                    <button class="p-1.5 bg-white rounded shadow-lg hover:bg-gray-50">
                      <Eye class="w-3 h-3 text-gray-600" />
                    </button>
                    <button 
                      @click="deleteAttachment(attachment.id)"
                      class="p-1.5 bg-white rounded shadow-lg hover:bg-red-50"
                    >
                      <Trash2 class="w-3 h-3 text-red-600" />
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { 
  Camera, User, Bell, Settings, Calendar, Upload, Plus, Eye, Edit, Trash2, FileText,
  X, ExternalLink, RefreshCw as RefreshIcon, Globe, Star, Home
} from 'lucide-vue-next'
import UploadModal from '../components/UploadModal.vue'
import { getCategories, deleteCategory } from '../services/category'
import { getCollectionsByCategory } from '../services/collection'
import { isAuthenticated, getLocalUserInfo, refreshAuthStatus } from '../services/auth'
import '../services/debug' // 引入调试工具

const router = useRouter()

// 侧边栏展开状态
const sidebarExpanded = ref(false)
const sidebarToggleCount = ref(0)
const showAnnoyanceModal = ref(false)

// 当前页面
const currentPage = ref('collections')

// 菜单项
const menuItems = [
  { id: 'collections', name: '收藏', icon: Star },
]

// 用户信息
const currentUserId = ref(1)
const todayEvents = ref(0)

// 其他数据和方法
const events = ref([])
const attachments = ref([])
const collections = ref([])
const isLoadingCollections = ref(false)

// 上传模态窗口状态
const showUploadModal = ref(false)

// 获取收藏列表
const fetchCollections = async () => {
  // 检查用户是否已登录
  if (!isAuthenticated()) {
    console.log('用户未登录，跳转到登录页面')
    router.push('/login')
    return
  }

  try {
    const result = await getCategories()
    
    if (result.status === 'success' && result.data && result.data.categories) {
      collections.value = result.data.categories.map((category, index) => ({
        id: category.id,
        name: category.name,
        icon: category.emoji || '📚',
        description: `${category.name} 相关内容`,
        collection_count: category.collection_count
      }))
    } else {
      console.error('获取分类失败')
    }
  } catch (error) {
    console.error('获取分类失败:', error)
    // 如果是认证错误，重定向到登录页面
    const is401or403 = error.response?.status === 401 || error.response?.status === 403
    const hasAuthError = error.detail === 'Not authenticated' || error.message?.includes('401') || error.message?.includes('403')
    
    if (is401or403 || hasAuthError) {
      console.log('认证失败，跳转到登录页面')
      router.push('/login')
    }
  }
}

// 查看收藏详情 - 根据是否有attachment决定跳转页面
const viewCollection = async (collection) => {
  try {
    // 先获取该分类下的collections来检查是否有attachment
    const result = await getCollectionsByCategory(collection.id)
    
    if (result.status === 'success' && result.data && result.data.collections) {
      const collections = result.data.collections
      
      // 检查是否有任何collection包含attachment
      const hasAttachment = collections.some(item => item.details && item.details.attachment)
      
      if (hasAttachment) {
        // 如果有attachment，跳转到CollectionAttachmentListView
        router.push({ name: 'CollectionAttachmentList', params: { category_id: collection.id } })
      } else {
        // 如果没有attachment，跳转到CollectionListView
        router.push({ name: 'CollectionList', params: { category_id: collection.id } })
      }
    } else {
      // 如果无法获取数据，默认跳转到CollectionListView
      router.push({ name: 'CollectionList', params: { category_id: collection.id } })
    }
  } catch (error) {
    console.error('检查收藏类型失败:', error)
    // 出错时默认跳转到CollectionListView
    router.push({ name: 'CollectionList', params: { category_id: collection.id } })
  }
}

// 刷新收藏
const refreshCollections = async () => {
  isLoadingCollections.value = true
  try {
    await fetchCollections()
  } catch (error) {
    console.error('刷新收藏失败:', error)
  } finally {
    isLoadingCollections.value = false
  }
}

// 其他方法...
const editCollection = (collection) => {
  console.log('编辑收藏:', collection)
}

const deleteCollection = async (collectionId) => {
  try {
    await deleteCategory(collectionId)
    collections.value = collections.value.filter(collection => collection.id !== collectionId)
  } catch (error) {
    console.error('删除分类失败:', error)
  }
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('zh-CN', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 处理上传成功
const handleUploadSuccess = (data) => {
  console.log('上传成功:', data)
  // 刷新收藏列表以显示新上传的内容
  refreshCollections()
}

// 调试功能
const runDebug = async () => {
  if (window.debugAuth) {
    await window.debugAuth.full()
  }
}

// 初始化
onMounted(async () => {
  // 先检查认证状态
  refreshAuthStatus()
  await fetchCollections()
})
</script>

<style scoped>
/* 样式保持不变 */
.glass-effect {
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
}

.shadow-minimal {
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
}

.btn-hover:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.transition-smooth {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
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
}

.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: rgba(156, 163, 175, 0.5);
}

.collection-card {
  background-color: #f7f1f6;
}

.collection-card:hover {
  background: #e5e0e8;
}
</style> 