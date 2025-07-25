<template>
  <!-- 快速窗口模式 -->
  <div class="quick-window" :class="{ 'mac-style': platform === 'darwin', 'win-style': platform === 'win32' }">
    <!-- 退出按钮 -->
    <button @click="closeQuickWindow" class="exit-button" title="退出">
      <svg class="exit-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
      </svg>
    </button>

    <!-- 主要内容区域 -->
    <div class="main-content" :class="mainContentClass">
      <!-- 问候语，居于最上方 -->
      <div v-if="!capturedUrl && !statusMessage && !isProcessing && !showCaptureAnimation" class="greeting-section">
        <div class="greeting-content">
          <span class="greeting-emoji">👋</span>
          <div class="greeting-texts">
            <div class="greeting-text">下午好，</div>
            <div class="greeting-question">有什么想收集的吗？</div>
          </div>
        </div>
      </div>

      <!-- 居中容器，包含链接显示、输入和捕获按钮 -->
      <div class="center-container" :class="centerContainerClass">
        <!-- 抓取动画界面 -->
        <div v-if="showCaptureAnimation" class="capture-animation-section">
          <div class="animation-container">
            <!-- 主要动画区域 -->
            <div class="main-animation">
              <div class="capture-loading-icon">
                <svg class="loading-animation" viewBox="0 0 100 100">
                  <circle class="loading-circle" cx="50" cy="50" r="45" fill="none" stroke="#3b82f6" stroke-width="4" stroke-linecap="round"/>
                </svg>
              </div>
              
              <!-- 浮动粒子效果 -->
              <div class="particles">
                <div v-for="i in 12" :key="i" class="particle" :style="{ '--delay': `${i * 0.1}s`, '--angle': `${i * 30}deg` }"></div>
              </div>
              
              <!-- 脉冲波纹 -->
              <div class="pulse-waves">
                <div class="pulse-wave"></div>
                <div class="pulse-wave"></div>
                <div class="pulse-wave"></div>
              </div>
            </div>
            
            <!-- 文字动画 -->
            <div class="capture-text">
              <div class="text-line">
                <span class="text-char" v-for="(char, index) in '正在抓取'" :key="index" :style="{ '--delay': `${0.3 + index * 0.1}s` }">{{ char }}</span>
              </div>
              <div class="text-line">
                <span class="text-char" v-for="(char, index) in '请稍候'" :key="index" :style="{ '--delay': `${0.7 + index * 0.1}s` }">{{ char }}</span>
              </div>
            </div>
            
            <!-- 进度指示器 -->
            <div class="progress-dots">
              <div class="dot" :class="{ 'active': true }" style="--delay: 1.0s"></div>
              <div class="dot" :class="{ 'active': true }" style="--delay: 1.1s"></div>
              <div class="dot" :class="{ 'active': true }" style="--delay: 1.2s"></div>
            </div>
          </div>
        </div>

        <!-- 解析进度和结果显示区域 -->
        <div v-if="isProcessing || processedData" class="processing-section">
          <!-- 处理中状态 -->
          <div v-if="isProcessing" class="processing-state">
            <div class="url-info">
              <div class="url-header">
                <div class="status-indicator processing"></div>
                <span class="status-text">正在解析链接</span>
              </div>
              <div class="url-display">
                {{ capturedUrl }}
              </div>
            </div>

            <!-- 优化的进度步骤显示 -->
            <div class="progress-container">
              <div class="progress-steps">
                <div v-for="step in 5" :key="step" class="step-item" :class="{
                  'active': currentStep === step,
                  'completed': stepCompleted[step],
                  'pending': currentStep < step
                }">
                  <div class="step-indicator">
                    <div v-if="currentStep === step && !stepCompleted[step]" class="spinner"></div>
                    <svg v-else-if="stepCompleted[step]" class="check-icon" viewBox="0 0 20 20">
                      <path fill="currentColor"
                        d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" />
                    </svg>
                    <span v-else class="step-number">{{ step }}</span>
                  </div>
                  <span class="step-text">{{ stepTextMap[step] }}</span>
                </div>
              </div>

              <!-- 进度条 -->
              <div class="progress-bar">
                <div class="progress-fill"
                  :style="{ width: `${(Object.values(stepCompleted).filter(Boolean).length / 5) * 100}%` }"></div>
              </div>
            </div>
          </div>

          <!-- 处理完成结果 -->
          <div v-if="processedData && !isProcessing" class="processed-result">
                      <div class="result-header">
            <div class="url-section">
              <!-- URL显示/编辑区域 -->
              <div v-if="!isEditingUrl" class="url-display-container">
                <div class="url-display">
                  {{ capturedUrl }}
                </div>
                <button @click="startEditingUrl" class="edit-btn" title="编辑URL">
                  <svg class="edit-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                      d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                  </svg>
                </button>
              </div>
              <!-- URL编辑状态 -->
              <div v-else class="url-edit-container">
                <input 
                  v-model="editingUrl" 
                  type="url" 
                  class="url-edit-input"
                  placeholder="输入URL..."
                  @keydown.enter="confirmAllChanges"
                  @keydown.esc="cancelEditing"
                />
                <div class="edit-actions">
                  <button @click="cancelEditing" class="cancel-btn" title="取消">
                    <svg class="btn-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              </div>
            </div>
          </div>

            <div class="result-content">
              <div v-if="processedData.category" class="info-card category-card">
                <div class="card-header">
                  <div class="card-title-group">
                    <svg class="card-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                        d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
                    </svg>
                    <span class="card-title">分类</span>
                  </div>
                  <button v-if="!isEditingTags" @click="startEditingTags" class="edit-btn small" title="编辑标签">
                    <svg class="edit-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                        d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                    </svg>
                  </button>
                </div>
                <div class="category-content">
                  <span class="category-tag">{{ processedData.category }}</span>
                  <!-- 标签显示/编辑区域 -->
                  <div v-if="!isEditingTags" class="tags-container">
                    <span v-if="processedData.tags && processedData.tags.length === 0" class="no-tags-hint">暂无标签</span>
                    <span v-else-if="processedData.tags && processedData.tags.length" v-for="tag in processedData.tags" :key="tag" class="tag">{{ tag }}</span>
                  </div>
                  <div v-else-if="isEditingTags" class="tags-edit-container">
                    <div class="tags-edit-area">
                      <div class="editing-tags">
                        <span 
                          v-for="(tag, index) in editingTags" 
                          :key="index" 
                          class="editing-tag"
                        >
                          {{ tag }}
                          <button @click="removeTag(index)" class="remove-tag-btn" title="删除标签">
                            <svg class="remove-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                            </svg>
                          </button>
                        </span>
                        <input 
                          ref="tagInput"
                          type="text" 
                          class="tag-input"
                          placeholder="输入标签并按回车..."
                          @keydown="handleTagKeydown($event)"
                          maxlength="20"
                        />
                      </div>
                    </div>
                    <div class="edit-actions">
                      <button @click="cancelEditing" class="cancel-btn" title="取消">
                        <svg class="btn-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                        </svg>
                      </button>
                    </div>
                  </div>
                </div>
              </div>

              <div v-if="processedData.summary" class="info-card summary-card">
                <div class="card-header">
                  <div class="card-title-group">
                    <svg class="card-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                        d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    <span class="card-title">摘要</span>
                  </div>
                  <button v-if="!isEditingSummary" @click="startEditingSummary" class="edit-btn small" title="编辑摘要">
                    <svg class="edit-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                        d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                    </svg>
                  </button>
                </div>
                <!-- 摘要显示/编辑区域 -->
                <div v-if="!isEditingSummary" class="summary-content">{{ processedData.summary }}</div>
                <div v-else class="summary-edit-container">
                  <textarea 
                    v-model="editingSummary" 
                    class="summary-edit-textarea"
                    placeholder="输入摘要..."
                    @keydown.esc="cancelEditing"
                    rows="4"
                  ></textarea>
                  <div class="edit-actions">
                    <button @click="cancelEditing" class="cancel-btn" title="取消">
                      <svg class="btn-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <div class="result-actions">
              <div v-if="showCompletionMessage" class="completion-message">
                <div class="status-indicator completed"></div>
                <span class="completion-text">解析完成</span>
              </div>
              <button v-else @click="startNewCollection" class="action-btn primary-btn" :disabled="isUpdating">
                <svg v-if="!isUpdating" class="btn-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                </svg>
                <div v-else class="spinner btn-spinner"></div>
                {{ isEditingUrl || isEditingSummary || isEditingTags ? (isUpdating ? '保存中...' : '确认修改') : '开始新收集' }}
              </button>
            </div>
          </div>
        </div>

        <!-- 手动输入区域 -->
        <div v-if="!capturedUrl && !statusMessage && !isProcessing && !processedData && !showCaptureAnimation" class="input-section">
          <input v-model="manualUrl" type="url" class="url-input" placeholder="输入或粘贴网页链接..."
            @keydown.enter="useManualUrl" />
        </div>

        <!-- 捕获按钮区域 -->
        <div v-if="!isProcessing && !processedData && !showCaptureAnimation" class="capture-section">
          <!-- Detecting State -->
          <div v-if="isDetectingBrowser" class="detecting-state">
            <div class="spinner"></div>
            <span>检测中...</span>
          </div>

          <!-- Has Browser State -->
          <div v-else-if="hasBrowser" class="button-group">
            <button @click="captureEdgeUrl" :disabled="isCapturing" class="capture-btn" :class="{ 'disabled': isCapturing }">
              <Zap class="capture-icon" />
              <span>抓取{{ getBrowserDisplayName(detectedBrowser) }}</span>
            </button>
          </div>
        </div>

        <!-- 截图按钮 -->
        <!-- <div style="display: flex; align-items: start; justify-content: start; width: 100%;">
          <button class="screenshot-btn" title="截图">
            <svg class="screenshot-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
          </button>
        </div> -->

      </div>

      <!-- 状态信息 -->
      <div v-if="statusMessage" class="status-message" :class="statusMessage.type">
        {{ statusMessage.text }}
      </div>

      <!-- 彩蛋消息 -->
      <div v-if="showEasterEgg" class="easter-egg-message">
        rnm，老子都把F11禁用了你还按
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { Zap } from 'lucide-vue-next'

// 快速窗口相关状态
const capturedUrl = ref('')
const statusMessage = ref(null)
const manualUrl = ref('')
const isCapturing = ref(false)
const showCaptureAnimation = ref(false)

// 浏览器检测状态
const detectedBrowser = ref('NONE')
const hasBrowser = ref(false)
const isDetectingBrowser = ref(true)

// 操作系统检测
const platform = ref('win32')

// 新增：解析相关状态
const isProcessing = ref(false)
const processedData = ref(null)
const currentStep = ref(0)
const stepCompleted = ref({
  1: false, // 创建集合
  2: false, // 获取内容
  3: false, // 分析分类
  4: false, // 生成摘要
  5: false  // 完成索引
})

// 解析完成提示状态
const showCompletionMessage = ref(false)

// 新增：编辑相关状态
const isEditingUrl = ref(false)
const isEditingSummary = ref(false)
const isEditingTags = ref(false)
const editingUrl = ref('')
const editingSummary = ref('')
const editingTags = ref([])
const isUpdating = ref(false)

// 新增：测试后端连接
const isTesting = ref(false)

// 事件数据 (简化版，只用于保存事件)
const events = ref([])

// 彩蛋：F11按键计数器
const f11PressCount = ref(0)
const showEasterEgg = ref(false)

// 步骤文本映射
const stepTextMap = {
  1: '创建集合',
  2: '获取内容',
  3: '分析分类',
  4: '生成摘要',
  5: '完成索引'
}

// 只有初始状态（问候语/输入）时padding-top为50px，其余为0
const centerContainerClass = computed(() => {
  const isInitial = !capturedUrl.value && !statusMessage.value && !isProcessing.value && !processedData.value && !showCaptureAnimation.value
  return {
    'center-vertically': isInitial,
    'no-padding-top': !isInitial
  }
})

// main-content动态padding
const mainContentClass = computed(() => {
  if (isProcessing.value || processedData.value) {
    return 'compact-padding';
  }
  return '';
});

const resetQuickWindowState = () => {
  capturedUrl.value = ''
  manualUrl.value = ''
  statusMessage.value = null
  isCapturing.value = false
  showCaptureAnimation.value = false
  isDetectingBrowser.value = true
  isProcessing.value = false
  processedData.value = null
  currentStep.value = 0
  isTesting.value = false
  showCompletionMessage.value = false
  // 重置编辑相关状态
  isEditingUrl.value = false
  isEditingSummary.value = false
  isEditingTags.value = false
  editingUrl.value = ''
  editingSummary.value = ''
  editingTags.value = []
  isUpdating.value = false
  stepCompleted.value = {
    1: false,
    2: false,
    3: false,
    4: false,
    5: false
  }
}

const closeQuickWindow = async () => {
  resetQuickWindowState()
  if (window.electronAPI && window.electronAPI.invoke) {
    await window.electronAPI.invoke('hide-quick-window')
  }
}

// 新增：测试后端连接
const testBackendConnection = async () => {
  try {
    console.log('测试后端连接...')
    const testResponse = await fetch('/api/v1/health', {
      method: 'GET',
      headers: {
        'Accept': 'application/json'
      }
    })

    console.log('测试连接响应:', {
      status: testResponse.status,
      statusText: testResponse.statusText
    })

    return testResponse.ok
  } catch (error) {
    console.error('后端连接测试失败:', error)
    return false
  }
}

// 新增：调用API解析链接
const processUrlWithAPI = async (url) => {
  try {
    console.log('=== 开始处理URL ===')
    console.log('URL:', url)
    console.log('API Endpoint: /api/v1/collection/url')

    // 先测试后端连接
    const isBackendReachable = await testBackendConnection()
    if (!isBackendReachable) {
      throw new Error('无法连接到后端服务器 (localhost:8000)')
    }

    // 重置抓取状态，开始解析
    isCapturing.value = false
    isProcessing.value = true
    currentStep.value = 0

    // 重置步骤状态
    Object.keys(stepCompleted.value).forEach(key => {
      stepCompleted.value[key] = false
    })

    // 添加更详细的请求配置
    const requestOptions = {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'text/event-stream',
      },
      body: JSON.stringify({ url: url })
    }

    console.log('请求配置:', requestOptions)
    console.log('请求体:', requestOptions.body)

    // 添加超时处理
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), 60000) // 60秒超时

    requestOptions.signal = controller.signal

    console.log('发送fetch请求...')
    const response = await fetch('/api/v1/collection/url', requestOptions)

    clearTimeout(timeoutId)
    console.log('收到响应:', {
      status: response.status,
      statusText: response.statusText,
      headers: Object.fromEntries(response.headers.entries())
    })

    if (!response.ok) {
      const errorText = await response.text()
      console.error('HTTP错误响应:', errorText)
      throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`)
    }

    if (!response.body) {
      throw new Error('响应体为空')
    }

    console.log('开始读取流数据...')
    const reader = response.body.getReader()
    const decoder = new TextDecoder()

    let buffer = ''
    const tempData = {
      collectionId: null,
      category: null,
      tags: null,
      summary: ''
    }

    let chunkCount = 0

    while (true) {
      const { done, value } = await reader.read()
      chunkCount++
      console.log(`读取数据块 ${chunkCount}:`, { done, valueLength: value?.length })

      if (done) {
        console.log('流数据读取完成')
        break
      }

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''

      console.log(`处理 ${lines.length} 行数据`)

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const jsonStr = line.slice(6)
            console.log('解析SSE数据:', jsonStr)
            const data = JSON.parse(jsonStr)
            console.log('解析结果:', data)

            switch (data.type) {
              case 'collection_created':
                console.log('收到: collection_created')
                currentStep.value = 1
                stepCompleted.value[1] = true
                tempData.collectionId = data.data.id
                break

              case 'content_fetched':
                console.log('收到: content_fetched')
                currentStep.value = 2
                stepCompleted.value[2] = true
                break

              case 'category_analyzed':
                console.log('收到: category_analyzed')
                currentStep.value = 3
                stepCompleted.value[3] = true
                tempData.category = data.data.category
                tempData.tags = data.data.tags
                break

              case 'summary_chunk':
                console.log('收到: summary_chunk')
                if (currentStep.value < 4) {
                  currentStep.value = 4
                }
                tempData.summary += data.data.summary
                break

              case 'index_completed':
                console.log('收到: index_completed')
                currentStep.value = 5
                stepCompleted.value[4] = true
                stepCompleted.value[5] = true

                // 清理摘要数据
                let cleanSummary = tempData.summary
                try {
                  // 尝试解析JSON格式的摘要
                  const jsonMatch = cleanSummary.match(/\{[^}]*"summary":\s*"([^"]*)"[^}]*\}/)
                  if (jsonMatch && jsonMatch[1]) {
                    cleanSummary = jsonMatch[1]
                  } else {
                    // 移除JSON标记符号
                    cleanSummary = cleanSummary.replace(/```json\n?/g, '').replace(/```\n?/g, '').replace(/^\{?\s*"?\s*/, '').replace(/\s*"?\s*\}?$/g, '')
                  }
                } catch (e) {
                  console.error('清理摘要时出错:', e)
                }

                processedData.value = {
                  collectionId: tempData.collectionId,
                  category: tempData.category,
                  tags: tempData.tags,
                  summary: cleanSummary
                }

                console.log('处理完成，最终数据:', processedData.value)

                isProcessing.value = false
                showCompletionMessage.value = true

                setTimeout(() => {
                  showCompletionMessage.value = false
                }, 2000)
                break

              default:
                console.log('未知事件类型:', data.type)
            }
          } catch (error) {
            console.error('解析SSE数据时出错:', error, '原始数据:', line)
          }
        }
      }
    }

    console.log('=== URL处理完成 ===')

  } catch (error) {
    console.error('=== 处理URL时出错 ===')
    console.error('错误类型:', error.name)
    console.error('错误消息:', error.message)
    console.error('错误堆栈:', error.stack)

    isProcessing.value = false
    currentStep.value = 0

    let errorMessage = '解析失败'

    if (error.name === 'AbortError') {
      errorMessage = '请求超时，请检查网络连接'
    } else if (error.message.includes('fetch')) {
      errorMessage = '网络连接失败，请确认后端服务是否启动'
    } else if (error.message.includes('CORS')) {
      errorMessage = '跨域请求被阻止'
    } else {
      errorMessage = `解析失败: ${error.message}`
    }

    statusMessage.value = {
      type: 'error',
      text: errorMessage
    }

    setTimeout(() => {
      statusMessage.value = null
    }, 5000)
  }
}

// 修改：抓取URL后自动处理
const captureEdgeUrl = async () => {
  if (isCapturing.value) return // 防止重复点击
  
  if (window.electronAPI && window.electronAPI.send) {
    window.electronAPI.send('capture-url-start')
  }

  try {
    // 立即显示动画和设置抓取状态
    isCapturing.value = true
    showCaptureAnimation.value = true
    statusMessage.value = null

    console.log('Starting URL capture for browser:', detectedBrowser.value)

    if (window.electronAPI && window.electronAPI.invoke) {
      const result = await window.electronAPI.invoke('capture-edge-url')

      if (result.success) {
        capturedUrl.value = result.url
        console.log('Successfully captured URL:', result.url)

        // 等待动画播放完成后开始处理URL（动画从点击开始计算，这里再等1.5秒）
        setTimeout(() => {
          showCaptureAnimation.value = false
          processUrlWithAPI(result.url)
        }, 1500)

      } else {
        statusMessage.value = {
          type: 'error',
          text: result.error || '获取失败'
        }
        console.log('URL capture failed:', result.error)
        setTimeout(() => {
          statusMessage.value = null
          isCapturing.value = false
        }, 3000)
      }
    } else {
      statusMessage.value = { type: 'error', text: 'API 不可用' }
      setTimeout(() => {
        statusMessage.value = null
        isCapturing.value = false
      }, 3000)
    }
  } catch (error) {
    console.error('Error capturing URL:', error)
    statusMessage.value = {
      type: 'error',
      text: '获取链接时出错: ' + error.message
    }
    setTimeout(() => {
      statusMessage.value = null
      isCapturing.value = false
    }, 3000)
  } finally {
    if (window.electronAPI && window.electronAPI.send) {
      window.electronAPI.send('capture-url-end')
    }
  }
}

// 新增：获取集合标签的API调用
const fetchCollectionTags = async (collectionId) => {
  try {
    console.log(`=== 获取集合标签 ===`)
    console.log('Collection ID:', collectionId)

    const response = await fetch(`/api/v1/collection/${collectionId}/tags`, {
      method: 'GET',
      headers: {
        'Accept': 'application/json'
      }
    })

    console.log('获取标签响应:', {
      status: response.status,
      statusText: response.statusText
    })

    if (!response.ok) {
      const errorText = await response.text()
      console.error('获取标签失败:', errorText)
      throw new Error(`获取标签失败: ${response.status} ${response.statusText}`)
    }

    const result = await response.json()
    console.log('获取标签成功:', result)
    return result.data.tags
  } catch (error) {
    console.error('获取集合标签失败:', error)
    statusMessage.value = {
      type: 'error',
      text: `获取标签失败: ${error.message}`
    }
    setTimeout(() => {
      statusMessage.value = null
    }, 5000)
    return []
  }
}

// 新增：更新集合标签的API调用
const updateCollectionTags = async (collectionId, tags) => {
  try {
    console.log(`=== 更新集合标签 ===`)
    console.log('Collection ID:', collectionId)
    console.log('Tags:', tags)

    const response = await fetch(`/api/v1/collection/${collectionId}/tags`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify({ tags: tags })
    })

    console.log('更新标签响应:', {
      status: response.status,
      statusText: response.statusText
    })

    if (!response.ok) {
      const errorText = await response.text()
      console.error('更新标签失败:', errorText)
      throw new Error(`更新标签失败: ${response.status} ${response.statusText}`)
    }

    const result = await response.json()
    console.log('更新标签成功:', result)
    return result.data.tags
  } catch (error) {
    console.error('更新集合标签失败:', error)
    statusMessage.value = {
      type: 'error',
      text: `更新标签失败: ${error.message}`
    }
    setTimeout(() => {
      statusMessage.value = null
    }, 5000)
    return null
  }
}

// 新增：更新集合详情的API调用
const updateCollectionDetail = async (key, value) => {
  try {
    isUpdating.value = true
    console.log(`=== 更新集合详情 ===`)
    console.log('Collection ID:', processedData.value.collectionId)
    console.log('Key:', key)
    console.log('Value:', value)

    const response = await fetch(`/api/v1/collection/${processedData.value.collectionId}/details/${key}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify({ value: value })
    })

    console.log('更新响应:', {
      status: response.status,
      statusText: response.statusText
    })

    if (!response.ok) {
      const errorText = await response.text()
      console.error('更新失败:', errorText)
      throw new Error(`更新失败: ${response.status} ${response.statusText}`)
    }

    const result = await response.json()
    console.log('更新成功:', result)

    // 更新本地数据
    if (key === 'url') {
      // 这里我们不更新capturedUrl，因为那是原始抓取的URL
      // processedData中也不包含url字段，所以我们可能需要添加一个显示用的字段
    } else if (key === 'summary') {
      processedData.value.summary = value
    }

    return true
  } catch (error) {
    console.error('更新集合详情失败:', error)
    statusMessage.value = {
      type: 'error',
      text: `更新失败: ${error.message}`
    }
    setTimeout(() => {
      statusMessage.value = null
    }, 5000)
    return false
  } finally {
    isUpdating.value = false
  }
}

// 新增：开始编辑URL
const startEditingUrl = () => {
  isEditingUrl.value = true
  editingUrl.value = capturedUrl.value
}

// 新增：开始编辑摘要
const startEditingSummary = () => {
  isEditingSummary.value = true
  editingSummary.value = processedData.value.summary
}

// 新增：开始编辑标签
const startEditingTags = async () => {
  isEditingTags.value = true
  // 获取最新的标签数据
  const tags = await fetchCollectionTags(processedData.value.collectionId)
  editingTags.value = Array.isArray(tags) ? [...tags] : [] // 创建副本以避免直接修改原数据
}

// 新增：取消编辑
const cancelEditing = () => {
  isEditingUrl.value = false
  isEditingSummary.value = false
  isEditingTags.value = false
  editingUrl.value = ''
  editingSummary.value = ''
  editingTags.value = []
}

// 新增：标签编辑相关函数
const addNewTag = (tagText) => {
  if (tagText && tagText.trim() && !editingTags.value.includes(tagText.trim())) {
    editingTags.value.push(tagText.trim())
  }
}

const removeTag = (index) => {
  editingTags.value.splice(index, 1)
}

const handleTagKeydown = (event, inputRef) => {
  if (event.key === 'Enter' && event.target.value.trim()) {
    event.preventDefault()
    addNewTag(event.target.value)
    event.target.value = ''
  } else if (event.key === 'Backspace' && !event.target.value && editingTags.value.length > 0) {
    // 当输入框为空时按退格键删除最后一个标签
    removeTag(editingTags.value.length - 1)
  }
}

// 新增：确认所有修改
const confirmAllChanges = async () => {
  let allSuccess = true

  // 更新URL（如果正在编辑且有变化）
  if (isEditingUrl.value && editingUrl.value !== capturedUrl.value) {
    const success = await updateCollectionDetail('url', editingUrl.value)
    if (success) {
      capturedUrl.value = editingUrl.value
    } else {
      allSuccess = false
    }
  }

  // 更新摘要（如果正在编辑且有变化）
  if (isEditingSummary.value && editingSummary.value !== processedData.value.summary) {
    const success = await updateCollectionDetail('summary', editingSummary.value)
    if (!success) {
      allSuccess = false
    }
  }

  // 更新标签（如果正在编辑且有变化）
  if (isEditingTags.value) {
    const currentTags = processedData.value.tags || []
    const tagsChanged = JSON.stringify(editingTags.value.sort()) !== JSON.stringify(currentTags.sort())
    if (tagsChanged) {
      const updatedTags = await updateCollectionTags(processedData.value.collectionId, editingTags.value)
      if (updatedTags !== null) {
        processedData.value.tags = updatedTags
      } else {
        allSuccess = false
      }
    }
  }

  if (allSuccess) {
    // 退出编辑模式
    cancelEditing()
    
    // 显示完成消息并自动关闭窗口
    showCompletionMessage.value = true
    statusMessage.value = {
      type: 'success',
      text: '修改保存成功'
    }
    
    setTimeout(() => {
      showCompletionMessage.value = false
      statusMessage.value = null
      // 自动关闭窗口
      closeQuickWindow()
    }, 2000)
  }
}

// 修改：原来的确认修改函数
const startNewCollection = () => {
  // 如果有任何编辑状态，先确认修改
  if (isEditingUrl.value || isEditingSummary.value || isEditingTags.value) {
    confirmAllChanges()
  } else {
    resetQuickWindowState()
  }
}

// 新增：测试后端连接
const testConnection = async () => {
  try {
    isTesting.value = true
    console.log('=== 手动测试后端连接 ===')

    // 测试基本连接
    const isReachable = await testBackendConnection()
    if (!isReachable) {
      statusMessage.value = {
        type: 'error',
        text: '无法连接到后端服务器 (localhost:8000)'
      }
      setTimeout(() => {
        statusMessage.value = null
      }, 5000)
      return
    }

    // 测试API端点
    console.log('测试API端点...')
    const testResponse = await fetch('/api/v1/collection/url', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'text/event-stream'
      },
      body: JSON.stringify({ url: 'https://example.com' })
    })

    console.log('API测试响应:', {
      status: testResponse.status,
      statusText: testResponse.statusText,
      headers: Object.fromEntries(testResponse.headers.entries())
    })

    if (testResponse.ok) {
      statusMessage.value = {
        type: 'success',
        text: '后端连接测试成功！'
      }
    } else {
      const errorText = await testResponse.text()
      console.error('API测试失败:', errorText)
      statusMessage.value = {
        type: 'error',
        text: `API测试失败: ${testResponse.status} ${testResponse.statusText}`
      }
    }

    setTimeout(() => {
      statusMessage.value = null
    }, 3000)

  } catch (error) {
    console.error('连接测试失败:', error)
    statusMessage.value = {
      type: 'error',
      text: `连接测试失败: ${error.message}`
    }
    setTimeout(() => {
      statusMessage.value = null
    }, 5000)
  } finally {
    isTesting.value = false
  }
}

// 修改：手动输入URL后自动处理
const useManualUrl = () => {
  if (!manualUrl.value.trim()) return

  try {
    new URL(manualUrl.value)
    capturedUrl.value = manualUrl.value
    const url = manualUrl.value
    manualUrl.value = ''
    statusMessage.value = { type: 'success', text: '链接已设置' }

    // 自动开始处理URL
    setTimeout(() => {
      statusMessage.value = null
      processUrlWithAPI(url)
    }, 1000)
  } catch (error) {
    statusMessage.value = { type: 'error', text: '请输入有效的网页链接' }
    setTimeout(() => {
      statusMessage.value = null
    }, 2000)
  }
}

const detectBrowser = async () => {
  try {
    console.log('Re-starting browser detection from renderer...')
    isDetectingBrowser.value = true
    if (window.electronAPI && window.electronAPI.invoke) {
      const result = await window.electronAPI.invoke('detect-active-browser')
      console.log('Re-detection result:', result)
      isDetectingBrowser.value = false
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
    isDetectingBrowser.value = false
    detectedBrowser.value = 'NONE'
    hasBrowser.value = false
    statusMessage.value = { type: 'error', text: '刷新检测出错' }
    setTimeout(() => {
      statusMessage.value = null
    }, 2000)
  }
}

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

onMounted(() => {
  // 检测操作系统
  if (window.electronAPI && window.electronAPI.getPlatform) {
    platform.value = window.electronAPI.getPlatform()
    console.log('Detected platform:', platform.value)
  }

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

  // 监听F11事件，实现彩蛋
  if (window.electronAPI && window.electronAPI.on) {
    window.electronAPI.on('f11-pressed', () => {
      console.log('F11 pressed! Count:', f11PressCount.value + 1) // 调试日志
      f11PressCount.value++

      if (f11PressCount.value >= 10) {
        console.log('Easter egg triggered!') // 调试日志
        showEasterEgg.value = true
        f11PressCount.value = 0 // 重置计数器

        // 3秒后隐藏彩蛋
        setTimeout(() => {
          showEasterEgg.value = false
        }, 3000)
      }
    })
  }
})
</script>

<style lang="scss" scoped>
  @import '../assets/QuickWindow.scss';
</style>
