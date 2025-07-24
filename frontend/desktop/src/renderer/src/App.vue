<template>
  <div class="flex h-screen bg-gray-50/80 overflow-hidden">
    <!-- 侧边栏 -->
    <div class="w-56 bg-white/90 glass-effect border-r border-gray-100 flex flex-col flex-shrink-0">
      <!-- Logo区域 -->
      <div class="p-6 border-b border-gray-50">
        <div class="flex items-center space-x-3">
          <div class="w-8 h-8 bg-gradient-to-br from-slate-700 to-slate-900 rounded-lg flex items-center justify-center shadow-minimal">
            <Camera class="w-4 h-4 text-white" />
          </div>
          <div>
            <h1 class="text-base font-semibold text-gray-900">Memora</h1>
            <p class="text-xs text-gray-500 font-light">事件记录管理</p>
          </div>
        </div>
      </div>

      <!-- 导航菜单 -->
      <nav class="flex-1 p-4">
        <ul class="space-y-1">
          <li v-for="item in menuItems" :key="item.id">
            <button
              @click="currentPage = item.id"
              :class="[
                'w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg text-left transition-smooth btn-hover',
                currentPage === item.id 
                  ? 'bg-gray-900 text-white shadow-minimal' 
                  : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
              ]"
            >
              <component :is="item.icon" class="w-4 h-4" />
              <span class="font-medium text-sm">{{ item.name }}</span>
            </button>
          </li>
        </ul>
      </nav>

      <!-- 用户信息 -->
      <div class="p-4 border-t border-gray-50">
        <div class="flex items-center space-x-3">
          <div class="w-8 h-8 bg-gray-100 rounded-lg flex items-center justify-center">
            <User class="w-4 h-4 text-gray-600" />
          </div>
          <div>
            <p class="font-medium text-gray-900 text-sm">用户 {{ currentUserId }}</p>
            <p class="text-xs text-gray-500">{{ todayEvents }} 个事件</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 主内容区域 -->
    <div class="flex-1 flex flex-col overflow-hidden min-w-0">
      <!-- 顶部栏 -->
      <header class="bg-white/80 glass-effect border-b border-gray-100 px-6 py-4 flex-shrink-0">
        <div class="flex items-center justify-between">
          <div>
            <h2 class="text-lg font-semibold text-gray-900">{{ getCurrentPageTitle() }}</h2>
            <p class="text-sm text-gray-500 mt-0.5">{{ getCurrentDate() }}</p>
          </div>
          <div class="flex items-center space-x-2">
            <button class="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-50 transition-smooth btn-hover">
              <Bell class="w-4 h-4" />
            </button>
            <button class="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-50 transition-smooth btn-hover">
              <Settings class="w-4 h-4" />
            </button>
          </div>
        </div>
      </header>

      <!-- 页面内容 -->
      <main class="flex-1 overflow-auto p-6 custom-scrollbar">
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

    <!-- 创建事件模态框 -->
    <div v-if="showCreateEvent" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-xl p-6 max-w-md w-full">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">创建新事件</h3>
        
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">事件描述</label>
            <textarea 
              v-model="newEvent.description" 
              class="w-full border border-gray-200 rounded-lg px-3 py-2 focus:ring-2 focus:ring-gray-900 focus:border-transparent bg-white/80 transition-smooth text-sm resize-none"
              rows="3"
              placeholder="描述这个事件..."
            ></textarea>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">标签（可选）</label>
            <input 
              v-model="newEventTags" 
              type="text" 
              class="w-full border border-gray-200 rounded-lg px-3 py-2 focus:ring-2 focus:ring-gray-900 focus:border-transparent bg-white/80 transition-smooth text-sm"
              placeholder="用逗号分隔多个标签"
            >
          </div>
        </div>

        <div class="flex space-x-3 mt-6">
          <button 
            @click="showCreateEvent = false"
            class="flex-1 bg-gray-100 text-gray-700 py-2.5 rounded-lg hover:bg-gray-200 transition-smooth font-medium text-sm"
          >
            取消
          </button>
          <button 
            @click="createEvent"
            class="flex-1 bg-gray-900 text-white py-2.5 rounded-lg hover:bg-gray-800 transition-smooth font-medium text-sm"
          >
            创建
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { 
  Camera, User, Bell, Settings, Calendar, Upload, Plus, Eye, Edit, Trash2, FileText
} from 'lucide-vue-next'

// 当前页面
const currentPage = ref('events')

// 菜单项
const menuItems = [
  { id: 'events', name: '事件管理', icon: Calendar },
  { id: 'attachments', name: '附件管理', icon: Upload }
]

// 用户信息
const currentUserId = ref(1)
const todayEvents = ref(0)

// 事件数据
const events = ref([
  {
    id: 1,
    user_id: 1,
    description: '今天和朋友一起吃了早餐',
    metadata: { category: '饮食', mood: 'happy' },
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  }
])

// 附件数据
const attachments = ref([])

// 表单数据
const showCreateEvent = ref(false)
const newEvent = ref({
  description: ''
})
const newEventTags = ref('')

// 附件上传
const selectedEventId = ref('')
const selectedFile = ref(null)
const attachmentDescription = ref('')
const isDragging = ref(false)
const fileInput = ref(null)

// 方法
const getCurrentPageTitle = () => {
  const page = menuItems.find(item => item.id === currentPage.value)
  return page ? page.name : '事件管理'
}

const getCurrentDate = () => {
  return new Date().toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    weekday: 'long'
  })
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('zh-CN', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const createEvent = async () => {
  if (!newEvent.value.description.trim()) return

  const metadata = {}
  if (newEventTags.value.trim()) {
    const tags = newEventTags.value.split(',').map(tag => tag.trim())
    metadata.tags = tags
  }

  const event = {
    id: Date.now(),
    user_id: currentUserId.value,
    description: newEvent.value.description,
    metadata: Object.keys(metadata).length > 0 ? metadata : null,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  }

  events.value.unshift(event)
  newEvent.value.description = ''
  newEventTags.value = ''
  showCreateEvent.value = false
  todayEvents.value++
}

const viewEvent = (event) => {
  console.log('查看事件:', event)
}

const editEvent = (event) => {
  console.log('编辑事件:', event)
}

const deleteEvent = (eventId) => {
  events.value = events.value.filter(event => event.id !== eventId)
  todayEvents.value = Math.max(0, todayEvents.value - 1)
}

const handleDrop = (e) => {
  e.preventDefault()
  isDragging.value = false
  const files = Array.from(e.dataTransfer.files)
  if (files.length > 0) {
    selectedFile.value = files[0]
  }
}

const triggerFileInput = () => {
  fileInput.value.click()
}

const handleFileSelect = (e) => {
  const files = Array.from(e.target.files)
  if (files.length > 0) {
    selectedFile.value = files[0]
  }
}

const uploadAttachment = async () => {
  if (!selectedEventId.value || !selectedFile.value) return

  const attachment = {
    id: Date.now(),
    event_id: selectedEventId.value,
    user_id: currentUserId.value,
    url: URL.createObjectURL(selectedFile.value),
    description: attachmentDescription.value || null,
    created_at: new Date().toISOString()
  }

  attachments.value.unshift(attachment)
  selectedFile.value = null
  selectedEventId.value = ''
  attachmentDescription.value = ''
  fileInput.value.value = ''
}

const deleteAttachment = (attachmentId) => {
  attachments.value = attachments.value.filter(attachment => attachment.id !== attachmentId)
}

const isImage = (url) => {
  return url.match(/\.(jpeg|jpg|gif|png|webp)$/i)
}

const getFileName = (url) => {
  if (url.startsWith('blob:')) {
    return '上传的文件'
  }
  return url.split('/').pop()
}

// 初始化今日事件数量
todayEvents.value = events.value.filter(event => {
  const today = new Date().toDateString()
  const eventDate = new Date(event.created_at).toDateString()
  return today === eventDate
}).length
</script>

<style scoped>
/* 心情滑块自定义样式 */
.mood-slider::-webkit-slider-thumb {
  appearance: none;
  height: 18px;
  width: 18px;
  border-radius: 50%;
  background: #1f2937;
  cursor: pointer;
  box-shadow: 0 2px 4px 0 rgba(0, 0, 0, 0.1);
  transition: all 0.2s ease;
}

.mood-slider::-webkit-slider-thumb:hover {
  transform: scale(1.1);
  box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.15);
}

.mood-slider::-moz-range-thumb {
  height: 18px;
  width: 18px;
  border-radius: 50%;
  background: #1f2937;
  cursor: pointer;
  border: none;
  box-shadow: 0 2px 4px 0 rgba(0, 0, 0, 0.1);
  transition: all 0.2s ease;
}

.mood-slider::-moz-range-thumb:hover {
  transform: scale(1.1);
  box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.15);
}

/* 卡片悬停效果 */
.card-hover:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
}

/* 按钮悬停效果 */
.btn-hover:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

/* 图片悬停效果 */
.image-hover:hover img {
  transform: scale(1.02);
}

/* 平滑过渡动画 */
.transition-smooth {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

/* 毛玻璃效果 */
.glass-effect {
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
}

/* 简约风格阴影 */
.shadow-minimal {
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
}

.shadow-minimal-hover:hover {
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

/* 自定义滚动条 */
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
</style>