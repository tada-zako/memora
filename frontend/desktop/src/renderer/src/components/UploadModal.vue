<template>
  <div
    v-if="show"
    class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
    @click.self="closeModal"
  >
    <div class="bg-white rounded-xl p-6 w-96 max-w-90vw shadow-2xl">
      <!-- 标题栏 -->
      <div class="flex items-center justify-between mb-4">
        <div>
          <h2 class="text-xl font-bold text-gray-900">上传图片</h2>
          <p class="text-sm text-gray-500 mt-1">支持连续上传多张图片到不同分类</p>
        </div>
        <button @click="closeModal" class="p-1 hover:bg-gray-100 rounded-lg transition-colors">
          <X class="w-5 h-5 text-gray-500" />
        </button>
      </div>

      <!-- 表单内容 -->
      <div class="space-y-4 mt-6">
        <!-- 分类输入 -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2"> 分类 * </label>
          <input
            v-model="category"
            type="text"
            placeholder="请输入分类名称，如：food, travel, art..."
            class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
            :class="{ 'border-red-300': errors.category }"
          />
          <p v-if="errors.category" class="text-red-500 text-sm mt-1">
            {{ errors.category }}
          </p>
        </div>

        <!-- 图片选择 -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2"> 选择图片 * </label>
          <div
            @click="triggerFileInput"
            @drop="handleDrop"
            @dragover.prevent
            @dragenter.prevent
            :class="[
              'border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-all',
              isDragging ? 'border-blue-400 bg-blue-50' : 'border-gray-300 hover:border-gray-400',
              errors.file ? 'border-red-300' : '',
              selectedFile ? 'border-green-400 bg-green-50' : ''
            ]"
          >
            <Upload class="w-8 h-8 text-gray-400 mx-auto mb-2" />
            <p v-if="!selectedFile" class="text-gray-600 text-sm">点击或拖拽图片到此处</p>
            <p v-else class="text-green-600 text-sm font-medium">已选择：{{ selectedFile.name }}</p>
            <p class="text-gray-400 text-xs mt-1">支持 JPG, PNG, GIF 格式，最大 10MB</p>
          </div>
          <input
            ref="fileInput"
            type="file"
            accept="image/*"
            @change="handleFileSelect"
            class="hidden"
          />
          <p v-if="errors.file" class="text-red-500 text-sm mt-1">
            {{ errors.file }}
          </p>
        </div>

        <!-- 描述 (可选) -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2"> 描述 (可选) </label>
          <textarea
            v-model="description"
            placeholder="为这张图片添加描述..."
            rows="3"
            class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all resize-none"
          ></textarea>
        </div>

        <!-- 操作按钮 -->
        <div class="flex space-x-3 pt-4">
          <button
            @click="closeModal"
            class="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
            :disabled="isUploading"
          >
            取消
          </button>
          <button
            @click="handleUpload"
            :disabled="!canUpload || isUploading"
            class="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors flex items-center justify-center"
          >
            <div
              v-if="isUploading"
              class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"
            ></div>
            {{ isUploading ? uploadStatus : '上传' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 自定义提示弹窗 -->
    <div v-if="notification.show" class="fixed top-4 right-4 z-[60] max-w-sm">
      <div
        :class="[
          'p-4 rounded-lg shadow-lg border-l-4 transition-all duration-300 transform',
          notification.type === 'success'
            ? 'bg-green-50 border-green-400 text-green-800'
            : 'bg-red-50 border-red-400 text-red-800',
          notification.show ? 'translate-x-0 opacity-100' : 'translate-x-full opacity-0'
        ]"
      >
        <div class="flex items-start">
          <div class="flex-shrink-0">
            <CheckCircle v-if="notification.type === 'success'" class="w-5 h-5 text-green-400" />
            <AlertCircle v-else class="w-5 h-5 text-red-400" />
          </div>
          <div class="ml-3 flex-1">
            <h3 class="text-sm font-medium">
              {{ notification.title }}
            </h3>
            <p class="text-sm mt-1 opacity-90">
              {{ notification.message }}
            </p>
          </div>
          <button
            @click="hideNotification"
            class="ml-4 flex-shrink-0 text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X class="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { X, Upload, CheckCircle, AlertCircle } from 'lucide-vue-next'
import { uploadAttachment } from '../services/attachment'
import { createPictureCollection } from '../services/collection'

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['close', 'success'])

// 表单数据
const category = ref('')
const description = ref('')
const selectedFile = ref(null)
const isDragging = ref(false)
const isUploading = ref(false)
const uploadStatus = ref('上传')

// 验证错误
const errors = ref({
  category: '',
  file: ''
})

// 文件输入引用
const fileInput = ref(null)

// 通知状态
const notification = ref({
  show: false,
  type: 'success', // 'success' 或 'error'
  title: '',
  message: ''
})

const USER_ID = 1

// 计算属性
const canUpload = computed(() => {
  return category.value.trim() && selectedFile.value && !isUploading.value
})

// 验证表单
const validateForm = () => {
  errors.value = {
    category: '',
    file: ''
  }

  if (!category.value.trim()) {
    errors.value.category = '请输入分类名称'
  }

  if (!selectedFile.value) {
    errors.value.file = '请选择图片文件'
  }

  return !errors.value.category && !errors.value.file
}

// 触发文件选择
const triggerFileInput = () => {
  fileInput.value?.click()
}

// 处理文件选择
const handleFileSelect = (event) => {
  const file = event.target.files?.[0]
  if (file) {
    validateFile(file)
  }
}

// 处理拖拽上传
const handleDrop = (event) => {
  event.preventDefault()
  isDragging.value = false

  const file = event.dataTransfer.files?.[0]
  if (file) {
    validateFile(file)
  }
}

// 验证文件
const validateFile = (file) => {
  // 检查文件类型
  if (!file.type.startsWith('image/')) {
    errors.value.file = '请选择图片文件'
    return
  }

  // 检查文件大小 (10MB)
  if (file.size > 10 * 1024 * 1024) {
    errors.value.file = '文件大小不能超过 10MB'
    return
  }

  selectedFile.value = file
  errors.value.file = ''
}

// 显示通知
const showNotification = (type, title, message) => {
  notification.value = {
    show: true,
    type,
    title,
    message
  }

  // 3秒后自动隐藏
  setTimeout(() => {
    hideNotification()
  }, 3000)
}

// 隐藏通知
const hideNotification = () => {
  notification.value.show = false
}

// 上传处理
const handleUpload = async () => {
  if (!validateForm()) {
    return
  }

  isUploading.value = true
  uploadStatus.value = '上传中...'

  try {
    // 第一步：上传文件
    uploadStatus.value = '正在上传文件...'
    const uploadResult = await uploadAttachment(
      selectedFile.value,
      description.value.trim() || null
    )
    const attachmentId = uploadResult.attachment_id

    // 第二步：创建收藏
    uploadStatus.value = '正在创建收藏...'
    const collectionResult = await createPictureCollection({
      attachment_id: attachmentId,
      category: category.value.trim()
    })

    if (collectionResult.code === 200) {
      // 显示成功通知
      showNotification(
        'success',
        '上传成功！',
        `图片已添加到"${category.value}"分类中。表单已重置，您可以立即上传下一张图片。`
      )

      // 通知父组件刷新数据
      emit('success', collectionResult.data)

      // 重置表单而不关闭模态窗口，方便继续上传
      resetForm()
    } else {
      throw new Error(collectionResult.message || '创建收藏失败')
    }
  } catch (error) {
    console.error('上传失败:', error)

    // 显示错误通知
    let errorMessage = '上传过程中发生错误，请重试。'
    if (error.message.includes('文件上传失败')) {
      errorMessage = '文件上传失败，请检查网络连接或文件格式。'
    } else if (error.message.includes('创建收藏失败')) {
      errorMessage = '创建收藏失败，请检查分类名称是否正确。'
    }

    showNotification('error', '上传失败', errorMessage)
  } finally {
    isUploading.value = false
    uploadStatus.value = '上传'
  }
}

// 关闭模态框
const closeModal = () => {
  if (!isUploading.value) {
    fullReset()
    emit('close')
  }
}

// 重置表单
const resetForm = () => {
  category.value = ''
  description.value = ''
  selectedFile.value = null
  errors.value = {
    category: '',
    file: ''
  }
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

// 完全重置（包括隐藏通知）
const fullReset = () => {
  resetForm()
  hideNotification()
}

// 监听拖拽事件
watch(
  () => props.show,
  (newVal) => {
    if (newVal) {
      fullReset()
    }
  }
)
</script>

<style scoped>
.max-w-90vw {
  max-width: 90vw;
}
</style>
