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
        <div v-if="!capturedUrl && !statusMessage" class="greeting-section">
          <div class="greeting-content">
            <span class="greeting-emoji">👋</span>
            <div class="greeting-texts">
              <div class="greeting-text">下午好，</div>
              <div class="greeting-question">有什么想收集的吗？</div>
            </div>
          </div>
        </div>
        
        <!-- 居中容器，包含链接显示、输入和捕获按钮 -->
        <div class="center-container">
          <!-- 链接显示区域 -->
          <div v-if="capturedUrl" class="captured-url-section">
            <div class="url-status">
              <div class="status-indicator"></div>
              <span class="status-text">已捕获链接</span>
            </div>
            <div class="url-display">
              {{ capturedUrl }}
            </div>
            <div class="url-actions">
              <button @click="copyUrl" class="action-btn copy-btn">
                复制链接
              </button>
              <button @click="openUrl" class="action-btn open-btn">
                打开链接
              </button>
              <button @click="saveAsEvent" class="action-btn save-btn">
                保存事件
              </button>
            </div>
          </div>
          
          <!-- 手动输入区域 -->
          <div v-if="!capturedUrl && !statusMessage" class="input-section">
            <input 
              v-model="manualUrl"
              type="url"
              class="url-input"
              placeholder="输入或粘贴网页链接..."
              @keydown.enter="useManualUrl"
            />
          </div>
          
          <!-- 捕获按钮区域 -->
          <div class="capture-section">
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
  }
  
  const closeQuickWindow = async () => {
    resetQuickWindowState()
    if (window.electronAPI && window.electronAPI.invoke) {
      await window.electronAPI.invoke('hide-quick-window')
    }
  }
  
  // 新增方法
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
      user_id: 1,
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
    
    setTimeout(() => {
      statusMessage.value = null
    }, 2000)
  }
  
  const useManualUrl = () => {
    if (!manualUrl.value.trim()) return
    
    try {
      new URL(manualUrl.value)
      capturedUrl.value = manualUrl.value
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
      justify-content: center;
      flex: 1;
      padding: 0 24px;
      min-height: 100vh;
      
      .greeting-section {
        width: 100%;
        display: flex;
        justify-content: flex-start;
        margin: 0;
        padding-right: 40px; // 为退出按钮留出空间
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
        min-height: 340px;
        margin: 0;
        padding-top: 50px;
        gap: 4px;
        
        // 链接显示区域
        .captured-url-section {
          background: #f0fdfc;
          border: 1px solid #9ce0d9;
          border-radius: 12px;
          padding: 16px;
          width: 100%;
          display: flex;
          flex-direction: column;
          gap: 12px;
          
          .url-status {
            display: flex;
            align-items: center;
            gap: 8px;
            
            .status-indicator {
              width: 8px;
              height: 8px;
              background: #9ce0d9;
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
          
          .url-actions {
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
              
              &.open-btn {
                background: #9ce0d9;
                color: white;
                &:hover { background: #7dd3d8; }
              }
              
              &.save-btn {
                background: #9ce0d9;
                color: white;
                &:hover { background: #7dd3d8; }
              }
            }
          }
        }
        
        // 输入区域
        .input-section {
          width: 100%;
          
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
        z-index: 9999;
        animation: easterEggPop 0.3s ease-out;
        border: 2px solid #ff4757;
      }
    }
  }
  
  @keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
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
  