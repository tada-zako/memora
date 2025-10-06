<template>
  <div class="w-full">
    <!-- AI添加收藏按钮 - 全宽展示 -->
    <button
      class="w-full bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600 text-white px-6 py-4 rounded-lg transition-all duration-300 font-medium text-sm btn-hover flex items-center justify-center space-x-2 mb-4"
      @click="toggleExpanded"
    >
      <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
        <path
          d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.847a4.5 4.5 0 003.09 3.09L15.75 12l-2.847.813a4.5 4.5 0 00-3.09 3.091zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.456 2.456L21.75 6l-1.035.259a3.375 3.375 0 00-2.456 2.456zM16.894 20.567L16.5 21.75l-.394-1.183a2.25 2.25 0 00-1.423-1.423L13.5 18.75l1.183-.394a2.25 2.25 0 001.423-1.423L16.5 15.75l.394 1.183a2.25 2.25 0 001.423 1.423L19.5 18.75l-1.183.394a2.25 2.25 0 00-1.423 1.423z"
        />
      </svg>
      <span class="text-base">AI添加收藏</span>
      <svg
        class="w-5 h-5 transition-transform duration-300"
        :class="isExpanded ? 'rotate-180' : ''"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        viewBox="0 0 24 24"
      >
        <path d="M19 9l-7 7-7-7" />
      </svg>
    </button>

    <!-- 下拉抽屉区域 -->
    <div
      class="overflow-hidden transition-all duration-300 ease-in-out"
      :class="isExpanded ? 'max-h-96 opacity-100' : 'max-h-0 opacity-0'"
    >
      <div class="bg-primary/80 glass-effect rounded-xl border border-muted-border p-6">
        <p class="text-primary-text mb-6 text-center">
          告诉我收藏的来源细节，让 AI 帮你生成摘要并进行分类~
        </p>

        <!-- 标签页视图 -->
        <div class="mb-6">
          <div class="border-b border-muted-border">
            <nav class="-mb-px flex space-x-8">
              <button
                class="py-2 px-1 border-b-2 font-medium text-sm transition-colors"
                :class="
                  aiAddActiveTab === 'url'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-primary-text hover:text-accent-text hover:border-muted-border'
                "
                @click="aiAddActiveTab = 'url'"
              >
                网页链接
              </button>
              <button
                class="py-2 px-1 border-b-2 font-medium text-sm transition-colors"
                :class="
                  aiAddActiveTab === 'arxiv'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-primary-text hover:text-accent-text hover:border-muted-border'
                "
                @click="aiAddActiveTab = 'arxiv'"
              >
                arXiv
              </button>
              <button
                class="py-2 px-1 border-b-2 font-medium text-sm transition-colors opacity-50 cursor-not-allowed"
                :class="
                  aiAddActiveTab === 'text'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-primary-text hover:text-accent-text hover:border-muted-border'
                "
                disabled
              >
                文本内容
              </button>
            </nav>
          </div>
        </div>

        <!-- 标签页内容 -->
        <div class="mb-6">
          <!-- 网页链接标签页 -->
          <div v-if="aiAddActiveTab === 'url'" class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-accent-text mb-2">网页链接</label>
              <input
                v-model="aiAddUrlInput"
                type="url"
                class="w-full px-3 py-2 border border-muted-border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-accent-text bg-primary"
                placeholder="请输入网页链接..."
                @keydown.enter="handleAIAddCollection"
              />
            </div>
          </div>

          <!-- arXiv标签页 -->
          <div v-else-if="aiAddActiveTab === 'arxiv'" class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-accent-text mb-2">arXiv ID</label>
              <input
                v-model="aiAddArxivInput"
                type="text"
                class="w-full px-3 py-2 border border-muted-border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-accent-text bg-primary"
                placeholder="例如: 1234.5678 或 1234.5678v1"
                @keydown.enter="handleAIAddCollection"
              />
            </div>
          </div>

          <!-- 文本内容标签页 (暂时禁用) -->
          <div v-else-if="aiAddActiveTab === 'text'" class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-accent-text mb-2">文本内容</label>
              <textarea
                v-model="aiAddTextInput"
                class="w-full px-3 py-2 border border-muted-border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-accent-text bg-primary"
                rows="4"
                placeholder="请输入要收藏的文本内容..."
                disabled
              ></textarea>
            </div>
          </div>
        </div>

        <!-- 进度显示区域 -->
        <div v-if="aiAddProcessing" class="mb-6">
          <div class="bg-muted rounded-lg p-4">
            <div class="mb-4">
              <div class="flex items-center gap-2 mb-2">
                <div class="status-indicator processing"></div>
                <span class="text-sm text-accent-text font-medium">正在处理链接</span>
              </div>
              <div class="text-sm text-primary-text break-all">
                {{ aiAddUrlInput }}
              </div>
            </div>

            <!-- 进度条 -->
            <div class="mt-4">
              <div class="w-full bg-gray-200 rounded-full h-2">
                <div
                  class="bg-blue-500 h-2 rounded-full transition-all duration-300"
                  :style="{
                    width: `${(Object.values(aiStepCompleted).filter(Boolean).length / 5) * 100}%`
                  }"
                ></div>
              </div>
            </div>
          </div>
        </div>

        <!-- 对话框底部 -->
        <div class="flex justify-end space-x-3">
          <button
            class="px-4 py-2 text-primary-text hover:text-accent-text transition-colors"
            :disabled="aiAddProcessing"
            @click="closeDrawer"
          >
            取消
          </button>
          <button
            class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            :disabled="getButtonDisabledState() || aiAddProcessing"
            @click="handleAIAddCollection"
          >
            <svg
              v-if="aiAddProcessing"
              class="animate-spin w-4 h-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <circle
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                stroke-width="4"
                class="opacity-25"
              ></circle>
              <path
                fill="currentColor"
                class="opacity-75"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              ></path>
            </svg>
            {{ aiAddProcessing ? '处理中...' : '开始添加' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 轻量通知提示 -->
    <div
      v-if="showSuccessToast"
      class="fixed top-4 right-4 z-50 transform transition-all duration-300 ease-in-out"
      :class="showSuccessToast ? 'translate-y-0 opacity-100' : '-translate-y-2 opacity-0'"
    >
      <div class="bg-green-500 text-white px-6 py-3 rounded-lg shadow-lg flex items-center gap-3">
        <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
          <path
            fill-rule="evenodd"
            d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
            clip-rule="evenodd"
          />
        </svg>
        <span class="font-medium">收藏添加成功！</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { isAuthenticated } from '@/api'
import { processUrlWithStreaming } from '@/api'

// AI 添加收藏相关状态
const isExpanded = ref(false)
const aiAddActiveTab = ref('url')
const aiAddUrlInput = ref('')
const aiAddArxivInput = ref('')
const aiAddTextInput = ref('')
const aiAddProcessing = ref(false)
const aiCurrentStep = ref(0)
const showSuccessToast = ref(false)
const aiStepCompleted = ref({
  1: false, // 创建集合
  2: false, // 获取内容
  3: false, // 分析分类
  4: false, // 生成摘要
  5: false // 完成索引
})

// 新创建的收藏信息
const newCollectionData = ref({
  collectionId: null,
  category: null
})

// 定义事件
const emit = defineEmits(['collection-added', 'navigate-to-collection'])

// arXiv ID 校验函数
const validateArxivId = (id) => {
  // arXiv ID 格式校验
  // 支持格式：1234.5678, 1234.5678v1, hep-th/123456 等
  const arxivPattern = /^(\d{4}\.\d{4,5}(v\d+)?|([a-z-]+\/\d{6,7}))$/
  return arxivPattern.test(id.trim())
}

// 拼接 arXiv URL
const buildArxivUrl = (id) => {
  return `https://arxiv.org/abs/${id.trim()}`
}

// 切换展开状态
const toggleExpanded = () => {
  isExpanded.value = !isExpanded.value
}

// 关闭抽屉
const closeDrawer = () => {
  isExpanded.value = false
  aiAddActiveTab.value = 'url'
  aiAddUrlInput.value = ''
  aiAddArxivInput.value = ''
  aiAddTextInput.value = ''
  aiAddProcessing.value = false
  aiCurrentStep.value = 0
  showSuccessToast.value = false
  // 重置步骤状态
  Object.keys(aiStepCompleted.value).forEach((key) => {
    aiStepCompleted.value[key] = false
  })
}

// 显示成功提示
const showSuccessMessage = () => {
  showSuccessToast.value = true
  // 3秒后自动隐藏
  setTimeout(() => {
    showSuccessToast.value = false
  }, 3000)
}

// 根据当前标签页获取按钮禁用状态
const getButtonDisabledState = () => {
  if (aiAddActiveTab.value === 'url') {
    return !aiAddUrlInput.value.trim()
  } else if (aiAddActiveTab.value === 'arxiv') {
    return !aiAddArxivInput.value.trim()
  }
  return true
}

const handleAIAddCollection = async () => {
  let urlToProcess = ''

  // 根据当前标签页确定要处理的URL
  if (aiAddActiveTab.value === 'url') {
    if (!aiAddUrlInput.value.trim()) return
    // 验证URL格式
    try {
      new URL(aiAddUrlInput.value)
      urlToProcess = aiAddUrlInput.value
    } catch {
      alert('请输入有效的网页链接')
      return
    }
  } else if (aiAddActiveTab.value === 'arxiv') {
    if (!aiAddArxivInput.value.trim()) return
    // 验证arXiv ID格式
    if (!validateArxivId(aiAddArxivInput.value)) {
      alert('请输入有效的 arXiv ID 格式（如：1234.5678 或 1234.5678v1）')
      return
    }
    urlToProcess = buildArxivUrl(aiAddArxivInput.value)
  } else {
    return // 不支持的标签页
  }

  if (aiAddProcessing.value) return

  try {
    // 检查用户认证状态
    if (!isAuthenticated()) {
      alert('请先登录后再使用此功能')
      return
    }

    aiAddProcessing.value = true
    aiCurrentStep.value = 0

    // 重置步骤状态
    Object.keys(aiStepCompleted.value).forEach((key) => {
      aiStepCompleted.value[key] = false
    })

    // 使用流式处理API
    await processUrlWithStreaming(urlToProcess, (data) => {
      console.log('AI添加收藏 - 收到流数据:', data)

      switch (data.type) {
        case 'collection_created':
          console.log('收到: collection_created')
          aiCurrentStep.value = 1
          aiStepCompleted.value[1] = true
          newCollectionData.value.collectionId = data.data?.id
          break

        case 'content_fetched':
          console.log('收到: content_fetched')
          aiCurrentStep.value = 2
          aiStepCompleted.value[2] = true
          break

        case 'category_analyzed':
          console.log('收到: category_analyzed')
          aiCurrentStep.value = 3
          aiStepCompleted.value[3] = true
          newCollectionData.value.category = data.data?.category
          break

        case 'summary_generated':
          console.log('收到: summary_generated')
          if (aiCurrentStep.value < 4) {
            aiCurrentStep.value = 4
          }
          aiStepCompleted.value[4] = true
          break

        case 'completed':
          console.log('收到: completed')
          aiCurrentStep.value = 5
          aiStepCompleted.value[5] = true
          break

        default:
          console.log('未知事件类型:', data.type)
      }
    })

    // 处理完成后发出事件通知父组件刷新收藏列表
    emit('collection-added')

    // 进度条动画显示完成后，停留0.5秒再跳转到收藏页面
    setTimeout(() => {
      // 关闭抽屉
      closeDrawer()

      // 显示轻量成功提示
      showSuccessMessage()

      // 通知父组件跳转到新创建的收藏
      emit('navigate-to-collection', newCollectionData.value)
    }, 500)
  } catch (error) {
    console.error('AI添加收藏失败:', error)
    alert('添加收藏失败: ' + (error.detail || error.message || '未知错误'))
  } finally {
    aiAddProcessing.value = false
  }
}
</script>

<style scoped>
.btn-hover:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.transition-smooth {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

/* AI添加收藏进度显示样式 */
.status-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
}

.status-indicator.processing {
  background-color: #3b82f6;
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

@keyframes pulse {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}
</style>
