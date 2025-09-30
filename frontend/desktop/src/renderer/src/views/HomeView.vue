<template>
  <!-- 只保留主内容区 -->
  <div class="flex-1 flex flex-col overflow-hidden min-w-0">
    <main class="flex-1 overflow-auto custom-scrollbar">
      <!-- 收藏管理页面 -->
      <div v-if="currentPage === 'collections'" class="h-full">
        <!-- 主要内容区域 -->
        <div
          class="bg-muted glass-effect h-full min-h-0"
        >
          <!-- 标题区域 -->
          <div
            class="flex items-center justify-between sticky top-0 z-10 bg-muted glass-effect w-full px-4 py-4"
            style="margin-bottom: 40px"
          >
            <div class="flex items-center">
              <div
                class="bg-gradient-to-br rounded-lg flex items-center justify-center w-8 h-8 mr-3"
              >
                <Star class="text-accent-text w-8 h-8" />
              </div>
              <div>
                <h1 class="text-2xl font-bold text-accent-text">{{ t('home.collections') }}</h1>
              </div>
            </div>
            <!-- 刷新按钮 -->
            <button
              :disabled="isLoadingCollections"
              class="bg-muted hover:bg-accent border-2 border-muted-border hover:border-primary-border text-primary-text px-4 py-2 rounded-lg transition-smooth font-medium text-sm btn-hover flex items-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
              title="刷新收藏列表"
              @click="refreshCollections"
            >
              <RefreshIcon :class="['w-4 h-4', isLoadingCollections ? 'animate-spin' : '']" />
              <span>{{ isLoadingCollections ? t('home.refreshing') : t('home.refresh') }}</span>
            </button>
          </div>

          <div style="width: 92%; margin-left: 20px">
            <div
              style="
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 16px;
                max-width: 100%;
              "
            >
              <!-- 收藏卡片 -->
              <div
                v-for="collection in collections"
                :key="collection.id"
                :class="[
                  'h-36 rounded-xl p-3 flex flex-col justify-between cursor-pointer transition-all duration-300 ease-out text-accent-text relative overflow-hidden group collection-card'
                ]"
                style="width: 100%; max-width: 280px"
                @click="viewCollection(collection)"
              >
                <!-- 内容 -->
                <div class="relative flex flex-col justify-between" style="height: 100%">
                  <div>
                    <div class="text-xl mb-1">{{ collection.icon }}</div>
                    <h3 class="text-2xl font-bold mb-0 truncate text-accent-text">
                      {{ collection.name }}
                    </h3>
                  </div>
                  <p class="text-primary-text text-sm truncate leading-tight">
                    {{ collection.collection_count }} {{ t('home.items') }}
                  </p>
                </div>
              </div>
            </div>
          </div>

          <!-- 空状态 -->
          <div
            v-if="collections.length === 0 && !isLoadingCollections"
            class="text-center"
            style="
              height: calc(100% - 84px);
              display: flex;
              justify-content: center;
              align-items: center;
              flex-direction: column;
            "
          >
            <div class="text-6xl mb-4">📚</div>
            <h3 class="text-lg font-semibold text-accent-text mb-2">
              {{ t('home.noCollections') }}
            </h3>
          </div>
          <!-- 加载状态 -->
          <div
            v-if="isLoadingCollections && collections.length === 0"
            class="text-center"
            style="
              height: calc(100% - 84px);
              display: flex;
              justify-content: center;
              align-items: center;
              flex-direction: column;
            "
          >
            <div
              class="w-8 h-8 border-2 border-muted-border border-t-gray-900 rounded-full animate-spin mb-4"
            ></div>
            <p class="text-primary-text">{{ t('home.loadingCollections') }}</p>
          </div>
        </div>
      </div>
      <!-- 事件列表页面 -->
      <div v-if="currentPage === 'events'" class="space-y-6 max-w-4xl">
        <!-- 创建事件按钮 -->
        <div class="flex justify-between items-center">
          <div>
            <h3 class="text-lg font-semibold text-accent-text">{{ t('home.myEvents') }}</h3>
            <p class="text-sm text-primary-text">{{ t('home.manageEvents') }}</p>
          </div>
          <button
            class="bg-accent text-muted-text px-4 py-2 rounded-lg hover:bg-accent transition-smooth font-medium text-sm btn-hover flex items-center space-x-2"
            @click="showCreateEvent = true"
          >
            <Plus class="w-4 h-4" />
            <span>{{ t('home.createEvent') }}</span>
          </button>
        </div>

        <!-- 事件列表 -->
        <div class="bg-primary/80 glass-effect rounded-xl border border-muted-border">
          <div class="p-4">
            <div class="space-y-3">
              <div
                v-for="event in events"
                :key="event.id"
                class="p-4 border border-muted-border rounded-lg hover:bg-muted/80 transition-smooth"
              >
                <div class="flex items-start justify-between">
                  <div class="flex-1 min-w-0">
                    <p class="font-medium text-accent-text truncate">{{ event.description }}</p>
                    <div class="flex items-center space-x-4 mt-2 text-sm text-primary-text">
                      <span>{{ formatDate(event.created_at) }}</span>
                      <span v-if="event.metadata" class="truncate"
                        >{{ Object.keys(event.metadata).length }} {{ t('home.tags') }}</span
                      >
                    </div>
                  </div>
                  <div class="flex items-center space-x-1 ml-4">
                    <button
                      class="p-1.5 text-primary-text hover:text-primary-text rounded hover:bg-muted transition-smooth"
                      title="查看"
                      @click="viewEvent(event)"
                    >
                      <Eye class="w-4 h-4" />
                    </button>
                    <button
                      class="p-1.5 text-primary-text hover:text-primary-text rounded hover:bg-muted transition-smooth"
                      title="编辑"
                      @click="editEvent(event)"
                    >
                      <Edit class="w-4 h-4" />
                    </button>
                    <button
                      class="p-1.5 text-red-400 hover:text-red-600 rounded hover:bg-red-50 transition-smooth"
                      title="删除"
                      @click="deleteEvent(event.id)"
                    >
                      <Trash2 class="w-4 h-4" />
                    </button>
                  </div>
                </div>
                <div class="flex items-center space-x-1 ml-4">
                  <button
                    class="p-1.5 text-primary-text hover:text-primary-text rounded hover:bg-muted transition-smooth"
                    title="查看"
                    @click="viewEvent(event)"
                  >
                    <Eye class="w-4 h-4" />
                  </button>
                  <button
                    class="p-1.5 text-primary-text hover:text-primary-text rounded hover:bg-muted transition-smooth"
                    title="编辑"
                    @click="editEvent(event)"
                  >
                    <Edit class="w-4 h-4" />
                  </button>
                  <button
                    class="p-1.5 text-red-400 hover:text-red-600 rounded hover:bg-red-50 transition-smooth"
                    title="删除"
                    @click="deleteEvent(event.id)"
                  >
                    <Trash2 class="w-4 h-4" />
                  </button>
                </div>
              </div>

              <div v-if="events.length === 0" class="text-center py-12">
                <Calendar class="w-12 h-12 text-muted-text mx-auto mb-4" />
                <p class="text-primary-text">{{ t('home.noEvents') }}</p>
                <p class="text-sm text-primary-text mt-1">{{ t('home.createFirstEvent') }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 附件管理页面 -->
      <div v-if="currentPage === 'attachments'" class="space-y-6 max-w-4xl">
        <!-- 上传区域 -->
        <div class="bg-primary/80 glass-effect rounded-xl border border-muted-border p-6">
          <h3 class="text-lg font-semibold text-accent-text mb-4">
            {{ t('home.uploadAttachments') }}
          </h3>

          <div class="space-y-4">
            <!-- 事件选择 -->
            <div>
              <label class="block text-sm font-medium text-primary-text mb-2">{{
                t('home.associatedEvent')
              }}</label>
              <select
                v-model="selectedEventId"
                class="w-full border border-muted-border rounded-lg px-3 py-2 focus:ring-2 focus:ring-gray-900 focus:border-transparent bg-primary/80 transition-smooth text-sm"
              >
                <option value="">{{ t('home.selectEvent') }}</option>
                <option v-for="event in events" :key="event.id" :value="event.id">
                  {{ event.description }}
                </option>
              </select>
            </div>

            <!-- 文件上传 -->
            <div
              :class="[
                'border-2 border-dashed rounded-xl p-8 text-center transition-all duration-200',
                isDragging
                  ? 'border-primary-border bg-muted/50'
                  : 'border-muted-border hover:border-muted-border'
              ]"
              @drop="handleDrop"
              @dragover.prevent
              @dragenter.prevent
            >
              <Upload class="w-10 h-10 text-primary-text mx-auto mb-3" />
              <h4 class="text-base font-semibold text-accent-text mb-2">
                {{ t('home.dragFilesHere') }}
              </h4>
              <p class="text-primary-text mb-4 font-light text-sm">
                {{ t('home.uploadDescription') }}
              </p>
              <button
                class="bg-accent text-muted-text px-4 py-2 rounded-lg hover:bg-accent transition-smooth font-medium text-sm btn-hover"
                @click="triggerFileInput"
              >
                {{ t('home.selectFile') }}
              </button>
              <input
                ref="fileInput"
                type="file"
                multiple
                class="hidden"
                @change="handleFileSelect"
              />
            </div>

            <!-- 描述 -->
            <div>
              <label class="block text-sm font-medium text-primary-text mb-2">{{
                t('home.description')
              }}</label>
              <textarea
                v-model="attachmentDescription"
                class="w-full border border-muted-border rounded-lg px-3 py-2 focus:ring-2 focus:ring-gray-900 focus:border-transparent bg-primary/80 transition-smooth text-sm resize-none"
                rows="2"
                :placeholder="t('home.addDescription')"
              ></textarea>
            </div>

            <button
              :disabled="!selectedEventId || !selectedFile"
              class="w-full bg-blue-600 text-muted-text py-2.5 rounded-lg hover:bg-blue-700 disabled:bg-muted disabled:cursor-not-allowed transition-smooth font-medium text-sm btn-hover"
              @click="uploadAttachment"
            >
              {{ t('home.uploadAttachment') }}
            </button>
          </div>
        </div>

        <!-- 附件列表 -->
        <div class="bg-primary/80 glass-effect rounded-xl border border-muted-border">
          <div class="p-4 border-b text-muted-text">
            <h3 class="text-lg font-semibold text-accent-text">{{ t('home.recentUploads') }}</h3>
          </div>
          <div class="p-4">
            <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
              <div v-for="attachment in attachments" :key="attachment.id" class="relative group">
                <div
                  class="aspect-square bg-muted rounded-lg border border-muted-border overflow-hidden"
                >
                  <img
                    v-if="isImage(attachment.url)"
                    :src="attachment.url"
                    :alt="attachment.description"
                    class="w-full h-full object-cover"
                  />
                  <div v-else class="w-full h-full flex items-center justify-center">
                    <FileText class="w-6 h-6 text-primary-text" />
                  </div>
                </div>
                <div class="mt-2">
                  <p class="text-xs text-primary-text truncate font-medium">
                    {{ getFileName(attachment.url) }}
                  </p>
                  <p class="text-xs text-primary-text mt-0.5">
                    {{ formatDate(attachment.created_at) }}
                  </p>
                </div>
                <div
                  class="absolute inset-0 bg-inverse bg-opacity-0 group-hover:bg-opacity-20 rounded-lg transition-all flex items-center justify-center"
                >
                  <div class="opacity-0 group-hover:opacity-100 transition-opacity flex space-x-1">
                    <button class="p-1.5 bg-primary rounded shadow-lg hover:bg-muted">
                      <Eye class="w-3 h-3 text-primary-text" />
                    </button>
                    <button
                      class="p-1.5 bg-primary rounded shadow-lg hover:bg-red-50"
                      @click="deleteAttachment(attachment.id)"
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
import { useI18n } from 'vue-i18n'
import {
  Camera,
  User,
  Bell,
  Settings,
  Calendar,
  Upload,
  Plus,
  Eye,
  Edit,
  Trash2,
  FileText,
  X,
  ExternalLink,
  RefreshCw as RefreshIcon,
  Globe,
  Star,
  Home
} from 'lucide-vue-next'
import UploadModal from '../components/UploadModal.vue'
import { getCategories, deleteCategory } from '@/api'
import { getCollectionsByCategory } from '@/api'
import { isAuthenticated, getLocalUserInfo, refreshAuthStatus } from '@/api'
import { uploadAttachment } from '@/api'
import '../api/debug' // 引入调试工具

const { t } = useI18n()
const router = useRouter()

// 侧边栏展开状态
const sidebarExpanded = ref(false)
const sidebarToggleCount = ref(0)
const showAnnoyanceModal = ref(false)

// 当前页面
const currentPage = ref('collections')

// 菜单项
const menuItems = [{ id: 'collections', name: '收藏', icon: Star }]

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

    if (result && result.categories) {
      collections.value = result.categories.map((category, index) => ({
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
    const hasAuthError =
      error.detail === 'Not authenticated' ||
      error.message?.includes('401') ||
      error.message?.includes('403')

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

    if (result && result.collections) {
      const collections = result.collections

      // 检查是否有任何collection包含attachment
      const hasAttachment = collections.some((item) => item.details && item.details.attachment)

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
    collections.value = collections.value.filter((collection) => collection.id !== collectionId)
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
  box-shadow:
    0 1px 3px 0 rgba(0, 0, 0, 0.1),
    0 1px 2px 0 rgba(0, 0, 0, 0.06);
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
  background-color: var(--color-primary);
}

.collection-card:hover {
  background: var(--color-accent);
}
</style>
