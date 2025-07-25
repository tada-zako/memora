<template>
    <!-- 快速窗口模式 -->
    <div class="quick-window">
      <!-- 退出按钮 -->
      <button 
        @click="closeQuickWindow"
        class="exit-button"
        title="退出"
      >
        <svg 
          class="exit-icon"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
      
      <!-- 主要内容区域 -->
      <div class="main-content">
        <!-- 问候语，居于最上方 -->
        <div v-if="!capturedUrl && !statusMessage && !isProcessing" class="greeting-section">
          <div class="greeting-content">
            <span class="greeting-emoji">👋</span>
            <div class="greeting-texts">
              <div class="greeting-text">下午好，</div>
              <div class="greeting-question">有什么想收集的吗？</div>
            </div>
          </div>
        </div>
        
        <!-- 居中容器，包含链接显示、输入和捕获按钮 -->
        <div class="center-container" :class="{ 'center-vertically': !capturedUrl && !statusMessage && !isProcessing && !processedData }">
          <!-- 解析进度和结果显示区域 -->
          <div v-if="isProcessing || processedData" class="processing-section">
            <!-- 处理中状态 -->
            <div v-if="isProcessing" class="processing-state">
              <div class="url-info">
                <div class="url-status">
                  <div class="status-indicator processing"></div>
                  <span class="status-text">正在解析链接</span>
                </div>
                <div class="url-display">
                  {{ capturedUrl }}
                </div>
              </div>
              
              <div class="progress-steps">
                <div class="step" :class="{ active: currentStep >= 1, completed: currentStep > 1 }">
                  <div class="step-indicator">
                    <div v-if="currentStep === 1 && !stepCompleted[1]" class="spinner"></div>
                    <svg v-else-if="stepCompleted[1]" class="check-icon" viewBox="0 0 20 20">
                      <path fill="currentColor" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"/>
                    </svg>
                    <span v-else class="step-number">1</span>
                  </div>
                  <span class="step-text">创建集合</span>
                </div>
                
                <div class="step" :class="{ active: currentStep >= 2, completed: currentStep > 2 }">
                  <div class="step-indicator">
                    <div v-if="currentStep === 2 && !stepCompleted[2]" class="spinner"></div>
                    <svg v-else-if="stepCompleted[2]" class="check-icon" viewBox="0 0 20 20">
                      <path fill="currentColor" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"/>
                    </svg>
                    <span v-else class="step-number">2</span>
                  </div>
                  <span class="step-text">获取内容</span>
                </div>
                
                <div class="step" :class="{ active: currentStep >= 3, completed: currentStep > 3 }">
                  <div class="step-indicator">
                    <div v-if="currentStep === 3 && !stepCompleted[3]" class="spinner"></div>
                    <svg v-else-if="stepCompleted[3]" class="check-icon" viewBox="0 0 20 20">
                      <path fill="currentColor" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"/>
                    </svg>
                    <span v-else class="step-number">3</span>
                  </div>
                  <span class="step-text">分析分类</span>
                </div>
                
                <div class="step" :class="{ active: currentStep >= 4, completed: currentStep > 4 }">
                  <div class="step-indicator">
                    <div v-if="currentStep === 4 && !stepCompleted[4]" class="spinner"></div>
                    <svg v-else-if="stepCompleted[4]" class="check-icon" viewBox="0 0 20 20">
                      <path fill="currentColor" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"/>
                    </svg>
                    <span v-else class="step-number">4</span>
                  </div>
                  <span class="step-text">生成摘要</span>
                </div>
                
                <div class="step" :class="{ active: currentStep >= 5, completed: currentStep > 5 }">
                  <div class="step-indicator">
                    <div v-if="currentStep === 5 && !stepCompleted[5]" class="spinner"></div>
                    <svg v-else-if="stepCompleted[5]" class="check-icon" viewBox="0 0 20 20">
                      <path fill="currentColor" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"/>
                    </svg>
                    <span v-else class="step-number">5</span>
                  </div>
                  <span class="step-text">完成索引</span>
                </div>
              </div>
            </div>
            
            <!-- 处理完成结果 -->
            <div v-if="processedData && !isProcessing" class="processed-result">
              <div class="result-header">
                <div class="url-status">
                  <div class="status-indicator completed"></div>
                  <span class="status-text">解析完成</span>
                </div>
                <div class="url-display">
                  {{ capturedUrl }}
                </div>
              </div>
              
              <div class="result-content">
                <div v-if="processedData.category" class="category-section">
                  <h4>分类信息</h4>
                  <div class="category-info">
                    <span class="category-tag">{{ processedData.category }}</span>
                    <div v-if="processedData.tags && processedData.tags.length" class="tags">
                      <span v-for="tag in processedData.tags" :key="tag" class="tag">{{ tag }}</span>
                    </div>
                  </div>
                </div>
                
                <div v-if="processedData.summary" class="summary-section">
                  <h4>内容摘要</h4>
                  <div class="summary-content">{{ processedData.summary }}</div>
                </div>
              </div>
              
              <div class="result-actions">
                <button @click="copyUrl" class="action-btn copy-btn">
                  复制链接
                </button>
                <button @click="startNewCollection" class="action-btn new-btn">
                  新建收集
                </button>
              </div>
            </div>
          </div>
          
          <!-- 手动输入区域 -->
          <div v-if="!capturedUrl && !statusMessage && !isProcessing && !processedData" class="input-section">
            <input 
              v-model="manualUrl"
              type="url"
              class="url-input"
              placeholder="输入或粘贴网页链接..."
              @keydown.enter="useManualUrl"
            />
            <div class="input-actions">
              <button @click="testConnection" class="test-btn" :disabled="isTesting">
                <div v-if="isTesting" class="test-spinner"></div>
                <span v-if="!isTesting">测试连接</span>
                <span v-else>测试中...</span>
              </button>
            </div>
          </div>
          
          <!-- 捕获按钮区域 -->
          <div v-if="!isProcessing && !processedData" class="capture-section">
            <!-- Detecting State -->
            <div v-if="isDetectingBrowser" class="detecting-state">
              <div class="spinner"></div>
              <span>检测中...</span>
            </div>
            
            <!-- Has Browser State -->
            <div v-else-if="hasBrowser" class="button-group">
              <button
                @click="captureEdgeUrl"
                :disabled="isCapturing"
                class="capture-btn"
                :class="{ 'capturing': isCapturing }"
              >
                <div v-if="isCapturing" class="capture-spinner"></div>
                <Zap v-else class="capture-icon" />
                <span v-if="!isCapturing">抓取{{ getBrowserDisplayName(detectedBrowser) }}</span>
                <span v-else>获取中...</span>
              </button>
              
              <!-- 截图按钮 -->
              <button class="screenshot-btn" title="截图">
                <svg class="screenshot-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
              </button>
            </div>
            
            <!-- No Browser State -->
            <div v-else class="no-browser-state">
              <div class="no-browser-text">无活跃浏览器</div>
              <button @click="detectBrowser" class="refresh-btn" title="重新检测浏览器">
                刷新
              </button>
            </div>
          </div>
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
  import { ref, onMounted } from 'vue'
  import { Zap } from 'lucide-vue-next'
  
  // 快速窗口相关状态
  const isCapturing = ref(false)
  const capturedUrl = ref('')
  const statusMessage = ref(null)
  const manualUrl = ref('')
  
  // 浏览器检测状态
  const detectedBrowser = ref('NONE')
  const hasBrowser = ref(false)
  const isDetectingBrowser = ref(true)
  
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
  
  // 新增：测试连接状态
  const isTesting = ref(false)
  
  // 事件数据 (简化版，只用于保存事件)
  const events = ref([])
  
  // 彩蛋：F11按键计数器
  const f11PressCount = ref(0)
  const showEasterEgg = ref(false)
  
  const resetQuickWindowState = () => {
    capturedUrl.value = ''
    manualUrl.value = ''
    statusMessage.value = null
    isCapturing.value = false
    isDetectingBrowser.value = true
    isProcessing.value = false
    processedData.value = null
    currentStep.value = 0
    isTesting.value = false
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
      const testResponse = await fetch('http://localhost:8000/', {
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
      console.log('API Endpoint: http://localhost:8000/collection/url')
      
      // 先测试后端连接
      const isBackendReachable = await testBackendConnection()
      if (!isBackendReachable) {
        throw new Error('无法连接到后端服务器 (localhost:8000)')
      }
      
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
      const response = await fetch('http://localhost:8000/collection/url', requestOptions)
      
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
                  statusMessage.value = {
                    type: 'success',
                    text: '链接解析完成!'
                  }
                  
                  setTimeout(() => {
                    statusMessage.value = null
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
    if (window.electronAPI && window.electronAPI.send) {
      window.electronAPI.send('capture-url-start')
    }
    
    try {
      isCapturing.value = true
      statusMessage.value = null
      
      console.log('Starting URL capture for browser:', detectedBrowser.value)
      
      if (window.electronAPI && window.electronAPI.invoke) {
        const result = await window.electronAPI.invoke('capture-edge-url')
        
        if (result.success) {
          capturedUrl.value = result.url
          statusMessage.value = {
            type: 'success',
            text: `成功抓取${getBrowserDisplayName(detectedBrowser.value)}链接!`
          }
          console.log('Successfully captured URL:', result.url)
          
          // 自动开始处理URL
          setTimeout(() => {
            statusMessage.value = null
            processUrlWithAPI(result.url)
          }, 1000)
          
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
      if (window.electronAPI && window.electronAPI.send) {
        window.electronAPI.send('capture-url-end')
      }
      if (statusMessage.value && statusMessage.value.type !== 'success') {
        setTimeout(() => {
          statusMessage.value = null
        }, 3000)
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
  
  // 新增：开始新的收集
  const startNewCollection = () => {
    resetQuickWindowState()
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
      const testResponse = await fetch('http://localhost:8000/collection/url', {
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
  .quick-window {
    position: relative;
    height: 100vh;
    width: 100vw;
    background: linear-gradient(135deg, #f0fdfc 0%, #ffffff 100%);
    border: 1px solid #9ce0d9;
    border-radius: 0 0 20px 20px;
    overflow: hidden;
    /* 确保在透明窗口中圆角生效 */
    isolation: isolate;
    transform: translateZ(0);
    -webkit-transform: translateZ(0);
    clip-path: inset(0 round 0 0 20px 20px);
    display: flex;
    flex-direction: column;
    
    // 退出按钮样式
    .exit-button {
      position: absolute;
      top: 12px;
      right: 12px;
      z-index: 1000;
      width: 28px;
      height: 28px;
      display: flex;
      align-items: center;
      justify-content: center;
      background: rgba(255, 255, 255, 0.95);
      border: 1px solid #9ce0d9;
      border-radius: 6px;
      cursor: pointer;
      transition: all 0.2s ease;
      backdrop-filter: blur(8px);
      
      &:hover {
        background: rgba(255, 255, 255, 1);
        border-color: #7dd3d8;
        box-shadow: 0 4px 6px -1px rgba(156, 224, 217, 0.3);
        transform: translateY(-1px);
      }
      
      .exit-icon {
        width: 14px;
        height: 14px;
        color: #6b7280;
        transition: color 0.2s ease;
      }
      
      &:hover .exit-icon {
        color: #374151;
      }
    }
    
    // 主要内容区域
    .main-content {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: flex-start;
      flex: 1;
      padding: 48px 24px 24px 24px; // 为退出按钮留出空间
      min-height: calc(100vh - 48px);
      overflow-y: auto;
      overflow-x: hidden;
      
      // 自定义滚动条样式
      &::-webkit-scrollbar {
        width: 6px;
      }
      
      &::-webkit-scrollbar-track {
        background: rgba(156, 224, 217, 0.1);
        border-radius: 3px;
      }
      
      &::-webkit-scrollbar-thumb {
        background: rgba(156, 224, 217, 0.5);
        border-radius: 3px;
        transition: background 0.2s ease;
        
        &:hover {
          background: rgba(156, 224, 217, 0.7);
        }
      }
      
      .greeting-section {
        width: 100%;
        display: flex;
        justify-content: flex-start;
        margin: 0;
        padding: 0 40px 0 0; // 为退出按钮留出空间
        margin-bottom: 20px; // 与下方内容的间距
      }

      .greeting-content {
        display: flex;
        flex-direction: row;
        align-items: center;
        gap: 16px;
      }

      .greeting-emoji {
        font-size: 36px;
        margin-right: 0;
      }

      .greeting-texts {
        display: flex;
        flex-direction: column;
        justify-content: center;
      }

      .greeting-text {
        font-size: 18px;
        color: #111111;
        font-weight: 700;
        line-height: 1.2;
      }

      .greeting-question {
        font-size: 18px;
        color: #111111;
        font-weight: 700;
        line-height: 1.5;
      }
      
      .center-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: flex-start;
        width: 100%;
        flex: 1;
        margin: 0;
        padding-top: 50px;
        gap: 4px;
        
        // 当没有内容时垂直居中
        &.center-vertically {
          justify-content: center;
          min-height: calc(100vh - 150px); // 为顶部和底部留出空间
        }
        
        // 新增：解析处理区域
        .processing-section {
          background: #f0fdfc;
          border: 1px solid #9ce0d9;
          border-radius: 12px;
          padding: 20px;
          width: 100%;
          display: flex;
          flex-direction: column;
          gap: 16px;
          
          .processing-state {
            .url-info {
              display: flex;
              flex-direction: column;
              gap: 12px;
              margin-bottom: 20px;
              
              .url-status {
                display: flex;
                align-items: center;
                gap: 8px;
                
                .status-indicator {
                  width: 8px;
                  height: 8px;
                  border-radius: 50%;
                  
                  &.processing {
                    background: #fbbf24;
                    animation: pulse 2s infinite;
                  }
                  
                  &.completed {
                    background: #10b981;
                  }
                }
                
                .status-text {
                  font-size: 14px;
                  font-weight: 500;
                  color: #374151;
                }
              }
              
              .url-display {
                font-size: 14px;
                color: #111827;
                background: white;
                border-radius: 8px;
                padding: 12px;
                border: 1px solid #9ce0d9;
                word-break: break-all;
                font-family: 'Monaco', 'Menlo', monospace;
              }
            }
            
            .progress-steps {
              display: flex;
              flex-direction: column;
              gap: 12px;
              
              .step {
                display: flex;
                align-items: center;
                gap: 12px;
                padding: 8px 0;
                opacity: 0.4;
                transition: all 0.3s ease;
                
                &.active {
                  opacity: 1;
                }
                
                &.completed {
                  opacity: 1;
                  
                  .step-indicator {
                    background: #10b981;
                    color: white;
                  }
                }
                
                .step-indicator {
                  width: 28px;
                  height: 28px;
                  border-radius: 50%;
                  background: #e5e7eb;
                  display: flex;
                  align-items: center;
                  justify-content: center;
                  font-size: 12px;
                  font-weight: 600;
                  color: #6b7280;
                  transition: all 0.3s ease;
                  
                  .spinner {
                    width: 16px;
                    height: 16px;
                    border: 2px solid #e5e7eb;
                    border-top-color: #9ce0d9;
                    border-radius: 50%;
                    animation: spin 1s linear infinite;
                  }
                  
                  .check-icon {
                    width: 16px;
                    height: 16px;
                    color: white;
                  }
                }
                
                .step-text {
                  font-size: 14px;
                  font-weight: 500;
                  color: #374151;
                }
              }
            }
          }
          
          .processed-result {
            .result-header {
              display: flex;
              flex-direction: column;
              gap: 12px;
              margin-bottom: 20px;
              
              .url-status {
                display: flex;
                align-items: center;
                gap: 8px;
                
                .status-indicator.completed {
                  width: 8px;
                  height: 8px;
                  background: #10b981;
                  border-radius: 50%;
                }
                
                .status-text {
                  font-size: 14px;
                  font-weight: 500;
                  color: #374151;
                }
              }
              
              .url-display {
                font-size: 14px;
                color: #111827;
                background: white;
                border-radius: 8px;
                padding: 12px;
                border: 1px solid #9ce0d9;
                word-break: break-all;
                font-family: 'Monaco', 'Menlo', monospace;
              }
            }
            
            .result-content {
              display: flex;
              flex-direction: column;
              gap: 16px;
              margin-bottom: 20px;
              
              .category-section, .summary-section {
                h4 {
                  font-size: 14px;
                  font-weight: 600;
                  color: #374151;
                  margin: 0 0 8px 0;
                }
              }
              
              .category-info {
                display: flex;
                flex-direction: column;
                gap: 8px;
                
                .category-tag {
                  display: inline-block;
                  background: #dbeafe;
                  color: #1e40af;
                  padding: 4px 8px;
                  border-radius: 6px;
                  font-size: 12px;
                  font-weight: 500;
                  width: fit-content;
                }
                
                .tags {
                  display: flex;
                  flex-wrap: wrap;
                  gap: 6px;
                  
                  .tag {
                    background: #f3f4f6;
                    color: #6b7280;
                    padding: 2px 6px;
                    border-radius: 4px;
                    font-size: 11px;
                    font-weight: 500;
                  }
                }
              }
              
              .summary-content {
                background: white;
                border: 1px solid #9ce0d9;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
                line-height: 1.5;
                color: #374151;
              }
            }
            
            .result-actions {
              display: flex;
              align-items: center;
              gap: 8px;
              
              .action-btn {
                flex: 1;
                font-size: 12px;
                font-weight: 500;
                padding: 8px 12px;
                border-radius: 8px;
                border: none;
                cursor: pointer;
                transition: all 0.2s ease;
                color: #374151;
                
                &.copy-btn {
                  background: white;
                  border: 1px solid #9ce0d9;
                  &:hover { 
                    background: #f0fdfc; 
                    border-color: #7dd3d8;
                  }
                }
                
                &.new-btn {
                  background: #9ce0d9;
                  color: white;
                  &:hover { background: #7dd3d8; }
                }
              }
            }
          }
        }
        
        // 输入区域
        .input-section {
          width: 100%;
          display: flex;
          flex-direction: column;
          gap: 8px;
          
          .url-input {
            width: 100%;
            height: 90px;
            border: 1px solid #9ce0d9;
            border-radius: 12px;
            padding: 16px;
            font-size: 16px;
            background: white;
            transition: all 0.2s ease;
            border-radius: 15px;
            
            &:focus {
              outline: none;
              ring: 2px;
              ring-color: #9ce0d9;
              border-color: #7dd3d8;
            }
            
            &::placeholder {
              color: #9ca3af;
            }
          }
          
          .input-actions {
            display: flex;
            justify-content: flex-start;
            
            .test-btn {
              display: flex;
              align-items: center;
              gap: 6px;
              background: #f3f4f6;
              color: #374151;
              border: 1px solid #d1d5db;
              padding: 6px 12px;
              border-radius: 6px;
              font-size: 12px;
              font-weight: 500;
              cursor: pointer;
              transition: all 0.2s ease;
              
              &:hover:not(:disabled) {
                background: #e5e7eb;
                border-color: #9ca3af;
              }
              
              &:disabled {
                background: #f9fafb;
                color: #9ca3af;
                border-color: #e5e7eb;
                cursor: not-allowed;
              }
              
              .test-spinner {
                width: 12px;
                height: 12px;
                border: 1px solid #d1d5db;
                border-top-color: #6b7280;
                border-radius: 50%;
                animation: spin 1s linear infinite;
              }
            }
          }
        }
        
        // 捕获按钮区域
        .capture-section {
          width: 100%;
          display: flex;
          justify-content: flex-start;
          margin-top: 8px;
          
          .detecting-state {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 12px;
            color: #6b7280;
            background: #f3f4f6;
            padding: 8px 12px;
            border-radius: 8px;
            
            .spinner {
              width: 12px;
              height: 12px;
              border: 1px solid #9ce0d9;
              border-top-color: transparent;
              border-radius: 50%;
              animation: spin 1s linear infinite;
            }
          }
          
          .button-group {
            display: flex;
            align-items: center;
            gap: 12px;
            
            .capture-btn {
              display: flex;
              align-items: center;
              gap: 8px;
              background: white;
              color: #374151;
              border: 1px solid #9ce0d9;
              padding: 8px 16px;
              border-radius: 8px;
              font-size: 14px;
              font-weight: 500;
              cursor: pointer;
              transition: all 0.2s ease;
              box-shadow: 0 1px 2px 0 rgba(156, 224, 217, 0.1);
              
              &:hover:not(:disabled) {
                background: #f0fdfc;
                border-color: #7dd3d8;
              }
              
              &:disabled {
                background: #f3f4f6;
                color: #9ca3af;
                border-color: #e5e7eb;
                cursor: not-allowed;
              }
              
              &.capturing {
                background: #f3f4f6;
                color: #9ca3af;
                border-color: #e5e7eb;
              }
              
              .capture-spinner {
                width: 12px;
                height: 12px;
                border: 1px solid #9ce0d9;
                border-top-color: transparent;
                border-radius: 50%;
                animation: spin 1s linear infinite;
              }
              
              .capture-icon {
                width: 16px;
                height: 16px;
              }
            }
            
            .screenshot-btn {
              display: flex;
              align-items: center;
              justify-content: center;
              width: 40px;
              height: 40px;
              background: white;
              border: 1px solid #9ce0d9;
              border-radius: 8px;
              cursor: pointer;
              transition: all 0.2s ease;
              
              &:hover {
                background: #f0fdfc;
                border-color: #7dd3d8;
              }
              
              .screenshot-icon {
                width: 18px;
                height: 18px;
                color: #6b7280;
                transition: color 0.2s ease;
              }
              
              &:hover .screenshot-icon {
                color: #374151;
              }
            }
          }
          
          .no-browser-state {
            display: flex;
            align-items: center;
            gap: 8px;
            
            .no-browser-text {
              font-size: 12px;
              color: #9ca3af;
              background: #f3f4f6;
              padding: 8px 12px;
              border-radius: 8px;
            }
            
            .refresh-btn {
              font-size: 12px;
              color: #374151;
              background: #f0fdfc;
              border: 1px solid #9ce0d9;
              padding: 4px 8px;
              border-radius: 8px;
              cursor: pointer;
              transition: all 0.2s ease;
              
              &:hover {
                color: #111827;
                background: #ccfbf1;
                border-color: #7dd3d8;
              }
            }
          }
        }
      }
      
      // 状态信息
      .status-message {
        font-size: 14px;
        text-align: center;
        padding: 12px 16px;
        border-radius: 12px;
        transition: all 0.3s ease;
        margin-top: 16px;
        
        &.success {
          background: #f0fdfc;
          color: #0f766e;
          border: 1px solid #9ce0d9;
        }
        
        &.error {
          background: #fef2f2;
          color: #dc2626;
          border: 1px solid #fecaca;
        }
        
        &.info {
          background: #f0fdfc;
          color: #0f766e;
          border: 1px solid #9ce0d9;
        }
      }
      
      // 彩蛋消息样式
      .easter-egg-message {
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: linear-gradient(135deg, #ff6b6b, #ee5a24);
        color: white;
        padding: 16px 24px;
        border-radius: 12px;
        font-size: 16px;
        font-weight: 600;
        box-shadow: 0 8px 32px rgba(255, 107, 107, 0.3);
        z-index: 10000; // 确保在滚动内容之上
        animation: easterEggPop 0.3s ease-out;
        border: 2px solid #ff4757;
        pointer-events: none; // 不阻挡鼠标事件
      }
    }
  }
  
  @keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
  }
  
  @keyframes pulse {
    0% { opacity: 1; }
    50% { opacity: 0.5; }
    100% { opacity: 1; }
  }
  
  @keyframes easterEggPop {
    0% {
      transform: translate(-50%, -50%) scale(0.8);
      opacity: 0;
    }
    50% {
      transform: translate(-50%, -50%) scale(1.1);
    }
    100% {
      transform: translate(-50%, -50%) scale(1);
      opacity: 1;
    }
  }
  </style>
  