<template>
  <!-- 主应用模式 -->
  <div class="flex h-screen bg-gray-50/80 overflow-hidden">
    <!-- 侧边栏 -->
    <div 
      @mouseenter="handleSidebarEnter"
      @mouseleave="handleSidebarLeave"
      :class="[
        'bg-white/90 glass-effect border-r border-gray-100 flex flex-col flex-shrink-0 transition-all duration-300 ease-in-out',
        sidebarExpanded ? 'w-56' : 'w-24'
      ]"
    >
      <!-- Logo区域 -->
      <div :class="['border-b border-gray-50 transition-all duration-300 ease-in-out', sidebarExpanded ? 'p-6' : 'p-4']">
        <div :class="['flex items-center', sidebarExpanded ? 'space-x-3' : 'justify-center']">
          <div :class="[
            'bg-gradient-to-br from-slate-700 to-slate-900 rounded-lg flex items-center justify-center shadow-minimal flex-shrink-0 transition-all duration-300 ease-in-out',
            sidebarExpanded ? 'w-8 h-8' : 'w-12 h-12'
          ]">
            <Camera :class="[
              'text-white transition-all duration-300 ease-in-out',
              sidebarExpanded ? 'w-4 h-4' : 'w-6 h-6'
            ]" />
          </div>
          <div 
            :class="[
              'transition-all duration-300 ease-in-out overflow-hidden',
              sidebarExpanded ? 'opacity-100 max-w-none' : 'opacity-0 max-w-0'
            ]"
          >
            <h1 class="text-base font-semibold text-gray-900 whitespace-nowrap">Memora</h1>
            <p class="text-xs text-gray-500 font-light whitespace-nowrap">事件记录管理</p>
          </div>
        </div>
      </div>

      <!-- 导航菜单 -->
      <nav :class="['flex-1 transition-all duration-300 ease-in-out', sidebarExpanded ? 'p-4' : 'p-4']">
        <ul :class="[sidebarExpanded ? 'space-y-1' : 'space-y-2']">
          <li v-for="item in menuItems" :key="item.id" :class="[!sidebarExpanded ? 'flex justify-center' : '']">
            <button
              @click="currentPage = item.id"
              :class="[
                'flex items-center rounded-lg text-left transition-all duration-300 ease-in-out btn-hover',
                sidebarExpanded ? 'w-full space-x-3 px-3 py-2.5' : 'w-12 h-12 justify-center',
                currentPage === item.id 
                  ? 'bg-gray-900 text-white shadow-minimal' 
                  : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
              ]"
              :title="!sidebarExpanded ? item.name : ''"
            >
              <component :is="item.icon" :class="[
                'flex-shrink-0 transition-all duration-300 ease-in-out',
                sidebarExpanded ? 'w-4 h-4' : 'w-6 h-6'
              ]" />
              <span 
                :class="[
                  'font-medium text-sm transition-all duration-300 ease-in-out overflow-hidden whitespace-nowrap',
                  sidebarExpanded ? 'opacity-100 max-w-none' : 'opacity-0 max-w-0'
                ]"
              >
                {{ item.name }}
              </span>
            </button>
          </li>
        </ul>
      </nav>

      <!-- 用户信息 -->
      <div :class="['border-t border-gray-50 transition-all duration-300 ease-in-out', sidebarExpanded ? 'p-4' : 'p-3']">
        <div :class="['flex items-center', sidebarExpanded ? 'space-x-3' : 'justify-center']">
          <div :class="[
            'bg-gray-100 rounded-lg flex items-center justify-center flex-shrink-0 transition-all duration-300 ease-in-out',
            sidebarExpanded ? 'w-8 h-8' : 'w-12 h-12'
          ]">
            <User :class="[
              'text-gray-600 transition-all duration-300 ease-in-out',
              sidebarExpanded ? 'w-4 h-4' : 'w-6 h-6'
            ]" />
          </div>
          <div 
            :class="[
              'transition-all duration-300 ease-in-out overflow-hidden',
              sidebarExpanded ? 'opacity-100 max-w-none' : 'opacity-0 max-w-0'
            ]"
          >
            <p class="font-medium text-gray-900 text-sm whitespace-nowrap">用户 {{ currentUserId }}</p>
            <p class="text-xs text-gray-500 whitespace-nowrap">{{ todayEvents }} 个事件</p>
          </div>
        </div>
      </div>

      <!-- 临时清除缓存按钮 -->
      <div :class="['transition-all duration-300 ease-in-out', sidebarExpanded ? 'p-4' : 'p-3']">
        <button
          @click="clearCache"
          :class="[
            'flex items-center rounded-lg text-left transition-all duration-300 ease-in-out btn-hover w-full',
            'bg-red-50 text-red-700 hover:bg-red-100',
            sidebarExpanded ? 'space-x-3 px-3 py-2.5' : 'w-12 h-12 justify-center'
          ]"
          title="清除缓存"
        >
          <Trash2 :class="[
            'flex-shrink-0 transition-all duration-300 ease-in-out',
            sidebarExpanded ? 'w-4 h-4' : 'w-6 h-6'
          ]" />
          <span
            :class="[
              'font-medium text-sm transition-all duration-300 ease-in-out overflow-hidden whitespace-nowrap',
              sidebarExpanded ? 'opacity-100 max-w-none' : 'opacity-0 max-w-0'
            ]"
          >
            清除缓存
          </span>
        </button>
      </div>
    </div>

    <!-- 主内容区域 -->
    <div class="flex-1 flex flex-col overflow-hidden min-w-0">

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

    <!-- 状态消息提示 -->
    <div v-if="statusMessage" class="fixed bottom-5 right-5 bg-gray-900 text-white px-5 py-3 rounded-lg shadow-lg z-50 transition-all duration-300" :class="statusMessage.type === 'success' ? 'bg-green-600' : 'bg-red-600'">
      {{ statusMessage.text }}
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

    <!-- 恼人弹窗 -->
    <div v-if="showAnnoyanceModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-xl p-8 max-w-sm w-full border-4 border-red-500 shadow-2xl animate-bounce">
        <div class="text-center">
          <div class="text-6xl mb-4">😤</div>
          <h3 class="text-2xl font-bold text-red-600 mb-4">你TM在干嘛？！</h3>
          <p class="text-gray-700 mb-6">连续{{ sidebarToggleCount }}次展开收缩侧边栏<br/>你是不是太无聊了？</p>
          <button 
            @click="closeAnnoyanceModal"
            class="bg-red-500 hover:bg-red-600 text-white px-6 py-3 rounded-lg font-bold text-lg transition-colors transform hover:scale-105"
          >
            我错了 🥺
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { 
  Camera, User, Bell, Settings, Calendar, Upload, Plus, Eye, Edit, Trash2, FileText,
  X, ExternalLink, RotateCcw, Globe
} from 'lucide-vue-next'

// 侧边栏展开状态
const sidebarExpanded = ref(false)
const sidebarToggleCount = ref(0)
const showAnnoyanceModal = ref(false)

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

// 状态消息
const statusMessage = ref(null)


// 计算属性

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
  updateTodayEventsCount()
}



const viewEvent = (event) => {
  console.log('查看事件:', event)
}

const editEvent = (event) => {
  console.log('编辑事件:', event)
}

const deleteEvent = (eventId) => {
  events.value = events.value.filter(event => event.id !== eventId)
  updateTodayEventsCount()
}



const updateTodayEventsCount = () => {
  const today = new Date().toDateString()
  todayEvents.value = events.value.filter(event => {
    const eventDate = new Date(event.created_at).toDateString()
    return today === eventDate
  }).length
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


// 清除缓存
const clearCache = async () => {
  if (window.electronAPI && window.electronAPI.invoke) {
    try {
      const result = await window.electronAPI.invoke('clear-cache');
      if (result.success) {
        statusMessage.value = { type: 'success', text: result.message };
        setTimeout(() => { statusMessage.value = null }, 3000);
      } else {
        statusMessage.value = { type: 'error', text: result.message };
        setTimeout(() => { statusMessage.value = null }, 3000);
      }
    } catch (error) {
      statusMessage.value = { type: 'error', text: '调用清除缓存功能失败' };
      setTimeout(() => { statusMessage.value = null }, 3000);
    }
  }
};


// 侧边栏交互处理
const handleSidebarEnter = () => {
  if (!sidebarExpanded.value) {
    sidebarToggleCount.value++
    checkAnnoyanceThreshold()
  }
  sidebarExpanded.value = true
}

const handleSidebarLeave = () => {
  sidebarExpanded.value = false
}

const checkAnnoyanceThreshold = () => {
  if (sidebarToggleCount.value >= 10) {
    showAnnoyanceModal.value = true
  }
}

const closeAnnoyanceModal = () => {
  showAnnoyanceModal.value = false
  sidebarToggleCount.value = 0 // 重置计数
}

// 初始化
onMounted(() => {
  updateTodayEventsCount()
})
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

/* 文本行数限制 */
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* 弹窗动画 */
@keyframes bounce {
  0%, 20%, 53%, 80%, 100% {
    transform: translate3d(0, 0, 0);
  }
  40%, 43% {
    transform: translate3d(0, -15px, 0);
  }
  70% {
    transform: translate3d(0, -7px, 0);
  }
  90% {
    transform: translate3d(0, -2px, 0);
  }
}

.animate-bounce {
  animation: bounce 1s ease-in-out;
}
</style>