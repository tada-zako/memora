<template>
  <!-- 快速窗口模式 -->
  <div v-if="isQuickMode" class="h-screen bg-gradient-to-br from-gray-50 to-white border border-gray-200 rounded-xl overflow-hidden shadow-2xl">
    <!-- 简约头部 -->
    <div class="bg-gradient-to-r from-gray-900 to-gray-800 px-4 py-3 flex items-center justify-between">
      <div class="flex items-center space-x-3">
        <div class="w-2 h-2 bg-blue-400 rounded-full animate-pulse"></div>
        <span class="text-white font-medium text-sm">Memora</span>
        <div v-if="detectedBrowser && detectedBrowser !== 'NONE'" class="text-xs bg-blue-500/20 text-blue-200 px-2 py-1 rounded-full">
          {{ getBrowserDisplayName(detectedBrowser) }}
        </div>
      </div>
      <button 
        @click="closeQuickWindow"
        class="p-1.5 text-white/70 hover:text-white rounded-lg hover:bg-white/10 transition-all duration-200"
        title="关闭"
      >
        <X class="w-4 h-4" />
      </button>
    </div>

    <!-- 主要内容区域 -->
    <div class="flex-1 p-6 space-y-6">
      <!-- 链接显示区域 -->
      <div v-if="capturedUrl" class="bg-blue-50 border border-blue-200 rounded-xl p-4 space-y-3">
        <div class="flex items-center space-x-2">
          <div class="w-2 h-2 bg-green-500 rounded-full"></div>
          <span class="text-sm font-medium text-gray-700">已捕获链接</span>
        </div>
        <div class="text-sm text-gray-900 bg-white rounded-lg p-3 border break-all font-mono">
          {{ capturedUrl }}
        </div>
        <div class="flex items-center space-x-2">
          <button 
            @click="copyUrl"
            class="flex-1 text-xs bg-blue-600 hover:bg-blue-700 text-white px-3 py-2 rounded-lg transition-colors font-medium"
          >
            复制链接
          </button>
          <button 
            @click="openUrl"
            class="flex-1 text-xs bg-gray-600 hover:bg-gray-700 text-white px-3 py-2 rounded-lg transition-colors font-medium"
          >
            打开链接
          </button>
          <button 
            @click="saveAsEvent"
            class="flex-1 text-xs bg-green-600 hover:bg-green-700 text-white px-3 py-2 rounded-lg transition-colors font-medium"
          >
            保存事件
          </button>
        </div>
      </div>

      <!-- 手动输入区域 -->
      <div class="space-y-4">
        <div class="flex items-center space-x-2">
          <Globe class="w-4 h-4 text-gray-400" />
          <span class="text-sm font-medium text-gray-700">快速输入链接</span>
        </div>
        
        <div class="space-y-3">
          <input 
            v-model="manualUrl"
            type="url"
            class="w-full border border-gray-200 rounded-xl px-4 py-3 text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white transition-all duration-200"
            placeholder="输入或粘贴网页链接..."
            @keydown.enter="useManualUrl"
          />
          <button 
            @click="useManualUrl"
            :disabled="!manualUrl.trim()"
            class="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 text-white py-3 px-4 rounded-xl transition-colors font-medium disabled:cursor-not-allowed"
          >
            使用此链接
          </button>
        </div>
      </div>

      <!-- 快速记录 -->
      <div class="space-y-4">
        <div class="flex items-center space-x-2">
          <Edit class="w-4 h-4 text-gray-400" />
          <span class="text-sm font-medium text-gray-700">快速记录</span>
        </div>
        
        <div class="space-y-3">
          <textarea 
            v-model="quickNote" 
            class="w-full border border-gray-200 rounded-xl px-4 py-3 text-sm resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white transition-all duration-200"
            rows="3"
            placeholder="记录今天发生的事情..."
            @keydown.ctrl.enter="saveQuickNote"
          ></textarea>
          <div class="flex items-center justify-between">
            <span class="text-xs text-gray-400">Ctrl+Enter 快速保存</span>
            <button 
              @click="saveQuickNote"
              :disabled="!quickNote.trim()"
              class="text-sm bg-gray-900 hover:bg-gray-800 disabled:bg-gray-300 text-white px-4 py-2 rounded-lg transition-colors font-medium disabled:cursor-not-allowed"
            >
              保存记录
            </button>
          </div>
        </div>
      </div>

      <!-- 状态信息 -->
      <div v-if="statusMessage" 
           class="text-sm text-center py-3 px-4 rounded-xl transition-all duration-300" 
           :class="statusMessage.type === 'success' ? 'bg-green-50 text-green-700 border border-green-200' : 'bg-red-50 text-red-700 border border-red-200'">
        {{ statusMessage.text }}
      </div>
    </div>

    <!-- 底部操作栏 -->
    <div class="border-t border-gray-100 bg-gray-50/50 p-4 flex items-center justify-between">
      <!-- 左下角：浏览器抓取按钮 -->
      <div class="flex items-center space-x-2">
        <!-- Detecting State -->
        <div
          v-if="isDetectingBrowser"
          class="flex items-center space-x-2 text-xs text-gray-500 bg-gray-100 px-3 py-2 rounded-lg"
        >
          <div
            class="w-3 h-3 border border-gray-400 border-t-transparent rounded-full animate-spin"
          ></div>
          <span>检测中...</span>
        </div>

        <!-- Has Browser State -->
        <button
          v-else-if="hasBrowser"
          @click="captureEdgeUrl"
          :disabled="isCapturing"
          class="flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white px-4 py-2 rounded-lg transition-colors text-sm font-medium shadow-sm"
        >
          <div
            v-if="isCapturing"
            class="w-3 h-3 border border-white border-t-transparent rounded-full animate-spin"
          ></div>
          <Zap v-else class="w-4 h-4" />
          <span v-if="!isCapturing">抓取{{ getBrowserDisplayName(detectedBrowser) }}</span>
          <span v-else>获取中...</span>
        </button>

        <!-- No Browser State -->
        <div v-else class="flex items-center space-x-2">
          <div class="text-xs text-gray-400 bg-gray-100 px-3 py-2 rounded-lg">
            无活跃浏览器
          </div>
          <button
            @click="detectBrowser"
            class="text-xs text-blue-600 hover:text-blue-800 bg-blue-50 hover:bg-blue-100 px-2 py-1 rounded-lg transition-colors"
            title="重新检测浏览器"
          >
            刷新
          </button>
        </div>
      </div>
      
      <!-- 右下角：主应用链接 -->
      <button 
        @click="openMainWindow"
        class="text-sm text-gray-600 hover:text-gray-900 bg-white hover:bg-gray-50 px-4 py-2 rounded-lg border border-gray-200 transition-all duration-200 font-medium"
      >
        打开主应用
      </button>
    </div>
  </div>

  <!-- 主应用模式 -->
  <div v-else class="flex h-screen bg-gray-50/80 overflow-hidden">
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
            <div class="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">
              Ctrl + Space 快速访问
            </div>
            <button 
              @click="testQuickWindow"
              class="text-xs text-blue-600 hover:text-blue-800 bg-blue-50 hover:bg-blue-100 px-2 py-1 rounded transition-colors"
              title="测试快速窗口"
            >
              测试小窗
            </button>
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
import { ref, computed, onMounted } from 'vue'
import { 
  Camera, User, Bell, Settings, Calendar, Upload, Plus, Eye, Edit, Trash2, FileText,
  X, ExternalLink, RotateCcw, Globe, Zap
} from 'lucide-vue-next'

// 检测是否为快速窗口模式
const isQuickMode = ref(false)

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

// 快速窗口相关状态
const isCapturing = ref(false)
const capturedUrl = ref('')
const quickNote = ref('')
const statusMessage = ref(null)
const showManualInput = ref(false)
const manualUrl = ref('')

// 浏览器检测状态
const detectedBrowser = ref('NONE')
const hasBrowser = ref(false)
const isDetectingBrowser = ref(true)

// 计算属性
const todayEventsQuick = computed(() => {
  const today = new Date().toDateString()
  return events.value.filter(event => {
    const eventDate = new Date(event.created_at).toDateString()
    return today === eventDate
  }).sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
})

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

const formatTimeQuick = (dateString) => {
  const now = new Date()
  const date = new Date(dateString)
  const diffMinutes = Math.floor((now - date) / (1000 * 60))
  
  if (diffMinutes < 60) {
    return `${diffMinutes}分钟前`
  } else if (diffMinutes < 1440) {
    return `${Math.floor(diffMinutes / 60)}小时前`
  } else {
    return date.toLocaleDateString('zh-CN', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }
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

const createQuickEvent = async () => {
  if (!quickEventDescription.value.trim()) return

  const event = {
    id: Date.now(),
    user_id: currentUserId.value,
    description: quickEventDescription.value,
    metadata: null,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  }

  events.value.unshift(event)
  quickEventDescription.value = ''
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

const deleteEventQuick = (eventId) => {
  deleteEvent(eventId)
}

const updateTodayEventsCount = () => {
  const today = new Date().toDateString()
  todayEvents.value = events.value.filter(event => {
    const eventDate = new Date(event.created_at).toDateString()
    return today === eventDate
  }).length
}

// 快速窗口操作
const openMainWindow = async () => {
  if (window.electronAPI && window.electronAPI.invoke) {
    await window.electronAPI.invoke('show-main-window')
  }
}

const closeQuickWindow = async () => {
  if (window.electronAPI && window.electronAPI.invoke) {
    await window.electronAPI.invoke('hide-quick-window')
  }
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

// 新增方法
const captureEdgeUrl = async () => {
  try {
    isCapturing.value = true
    statusMessage.value = null
    
    console.log('Starting URL capture for browser:', detectedBrowser.value)
    
    if (window.electronAPI && window.electronAPI.invoke) {
      // 根据检测到的浏览器类型进行抓取
      const result = await window.electronAPI.invoke('capture-edge-url')
      
      if (result.success) {
        capturedUrl.value = result.url
        statusMessage.value = { 
          type: 'success', 
          text: `成功抓取${getBrowserDisplayName(detectedBrowser.value)}链接!` 
        }
        console.log('Successfully captured URL:', result.url)
      } else {
        statusMessage.value = { 
          type: 'error', 
          text: result.error || '获取失败' 
        }
        console.log('URL capture failed:', result.error)
      }
    } else {
      statusMessage.value = { type: 'error', text: 'API 不可用' }
    }
  } catch (error) {
    console.error('Error capturing URL:', error)
    statusMessage.value = { 
      type: 'error', 
      text: '获取链接时出错: ' + error.message 
    }
  } finally {
    isCapturing.value = false
    
    // 3秒后清除状态消息
    if (statusMessage.value && statusMessage.value.type !== 'success') {
      setTimeout(() => {
        statusMessage.value = null
      }, 3000)
    } else if (statusMessage.value) {
      setTimeout(() => {
        statusMessage.value = null
      }, 2000)
    }
  }
}

const copyUrl = async () => {
  try {
    if (capturedUrl.value) {
      await navigator.clipboard.writeText(capturedUrl.value)
      statusMessage.value = { type: 'success', text: '链接已复制到剪贴板' }
      setTimeout(() => {
        statusMessage.value = null
      }, 2000)
    }
  } catch (error) {
    console.error('Error copying URL:', error)
    statusMessage.value = { type: 'error', text: '复制失败' }
  }
}

const openUrl = () => {
  if (capturedUrl.value) {
    window.open(capturedUrl.value, '_blank')
  }
}

const saveAsEvent = async () => {
  if (!capturedUrl.value) return
  
  const event = {
    id: Date.now(),
    user_id: currentUserId.value,
    description: `网页链接: ${capturedUrl.value}`,
    metadata: { 
      type: 'url',
      url: capturedUrl.value,
      source: 'edge_capture'
    },
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  }

  events.value.unshift(event)
  statusMessage.value = { type: 'success', text: '已保存为事件' }
  updateTodayEventsCount()
  
  setTimeout(() => {
    statusMessage.value = null
  }, 2000)
}

const saveQuickNote = async () => {
  if (!quickNote.value.trim()) return

  const event = {
    id: Date.now(),
    user_id: currentUserId.value,
    description: quickNote.value,
    metadata: { source: 'quick_note' },
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  }

  events.value.unshift(event)
  quickNote.value = ''
  statusMessage.value = { type: 'success', text: '笔记已保存' }
  updateTodayEventsCount()
  
  setTimeout(() => {
    statusMessage.value = null
  }, 2000)
}

const useManualUrl = () => {
  if (!manualUrl.value.trim()) return
  
  // 简单的URL验证
  try {
    new URL(manualUrl.value)
    capturedUrl.value = manualUrl.value
    showManualInput.value = false
    manualUrl.value = ''
    statusMessage.value = { type: 'success', text: '链接已设置' }
    
    setTimeout(() => {
      statusMessage.value = null
    }, 2000)
  } catch (error) {
    statusMessage.value = { type: 'error', text: '请输入有效的网页链接' }
    setTimeout(() => {
      statusMessage.value = null
    }, 2000)
  }
}

// 检测活跃浏览器
const detectBrowser = async () => {
  try {
    console.log('Re-starting browser detection from renderer...')
    isDetectingBrowser.value = true // Show loading state for manual refresh
    if (window.electronAPI && window.electronAPI.invoke) {
      const result = await window.electronAPI.invoke('detect-active-browser')
      console.log('Re-detection result:', result)

      isDetectingBrowser.value = false // Hide loading state
      if (result.success) {
        detectedBrowser.value = result.browser
        hasBrowser.value = result.hasBrowser

        if (result.hasBrowser) {
          statusMessage.value = {
            type: 'success',
            text: `刷新成功: ${getBrowserDisplayName(result.browser)}`
          }
        } else {
          statusMessage.value = { type: 'info', text: '仍未检测到浏览器' }
        }
      } else {
        detectedBrowser.value = 'NONE'
        hasBrowser.value = false
        statusMessage.value = { type: 'error', text: '刷新检测失败' }
      }
      setTimeout(() => {
        statusMessage.value = null
      }, 2000)
    }
  } catch (error) {
    console.error('Error re-detecting browser:', error)
    isDetectingBrowser.value = false // Hide loading state
    detectedBrowser.value = 'NONE'
    hasBrowser.value = false
    statusMessage.value = { type: 'error', text: '刷新检测出错' }
    setTimeout(() => {
      statusMessage.value = null
    }, 2000)
  }
}

// 获取浏览器显示名称
const getBrowserDisplayName = (browser) => {
  const names = {
    'EDGE': 'Edge',
    'CHROME': 'Chrome', 
    'FIREFOX': 'Firefox',
    'IE': 'IE',
    'OPERA': 'Opera',
    'BRAVE': 'Brave',
    'VIVALDI': 'Vivaldi',
    'UNKNOWN_BROWSER': '未知浏览器',
    'NONE': '无浏览器'
  }
  return names[browser] || browser
}

// 测试快速窗口
const testQuickWindow = async () => {
  try {
    console.log('Testing quick window...')
    if (window.electronAPI && window.electronAPI.invoke) {
      const result = await window.electronAPI.invoke('test-quick-window')
      console.log('Test quick window result:', result)
    } else {
      console.error('electronAPI not available')
      alert('electronAPI 不可用，请检查 preload 脚本')
    }
  } catch (error) {
    console.error('Error testing quick window:', error)
    alert('测试快速窗口失败: ' + error.message)
  }
}

// 初始化
onMounted(() => {
  // 监听主进程发送的浏览器检测结果
  if (window.electronAPI && window.electronAPI.on) {
    window.electronAPI.on('browser-detection-start', () => {
      console.log('Received browser-detection-start event')
      isDetectingBrowser.value = true
      hasBrowser.value = false
    })

    window.electronAPI.on('browser-detected', (result) => {
      console.log('Received browser-detected event:', result)
      isDetectingBrowser.value = false

      if (result && result.success) {
        detectedBrowser.value = result.browser
        hasBrowser.value = result.hasBrowser
      } else {
        detectedBrowser.value = 'NONE'
        hasBrowser.value = false
      }
    })
  }

  // 初始化模式
  isQuickMode.value = window.location.hash === '#/quick'
  
  // 监听 hash 变化
  window.addEventListener('hashchange', () => {
    isQuickMode.value = window.location.hash === '#/quick'
  })
  
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
</style>