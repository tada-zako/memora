<template>
  <div 
    v-if="show" 
    class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center"
    style="z-index: 9999;"
    @click.self="closeModal"
  >
    <div class="bg-white rounded-lg shadow-lg max-w-md w-full mx-4">
      <!-- 模态框头部 -->
      <div class="flex items-center justify-between p-6 border-b border-gray-200">
        <h3 class="text-lg font-semibold text-gray-900">发布到社区</h3>
        <button 
          @click="closeModal"
          class="text-gray-400 hover:text-gray-600 transition-colors"
        >
          <XIcon class="w-5 h-5" />
        </button>
      </div>

      <!-- 模态框内容 -->
      <div class="p-6">
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-2">
            分享描述 (可选)
          </label>
          <textarea
            v-model="description"
            placeholder="分享一些想法或心得..."
            class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
            rows="4"
            maxlength="500"
          ></textarea>
          <div class="text-xs text-gray-500 mt-1 text-right">
            {{ description.length }}/500
          </div>
        </div>

        <div class="bg-gray-50 rounded-lg p-4 mb-6">
          <div class="text-sm text-gray-600 mb-2">即将分享的收藏：</div>
          <div class="text-sm font-medium text-gray-900">
            收藏ID: {{ collectionId }}
          </div>
        </div>
      </div>

      <!-- 模态框底部 -->
      <div class="flex items-center justify-end gap-3 p-6 border-t border-gray-200">
        <button
          @click="closeModal"
          class="px-4 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
          :disabled="loading"
        >
          取消
        </button>
        <button
          @click="handlePublish"
          :disabled="loading"
          class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
        >
          <span v-if="loading" class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
          {{ loading ? '发布中...' : '发布到社区' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { X as XIcon } from 'lucide-vue-next'
import { createPost } from '../services/community'

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  collectionId: {
    type: [String, Number],
    required: true
  }
})

const emit = defineEmits(['close', 'success'])

const description = ref('')
const loading = ref(false)

// 监听模态框显示状态，重置表单
watch(() => props.show, (newVal) => {
  if (newVal) {
    description.value = ''
    loading.value = false
  }
})

const closeModal = () => {
  if (!loading.value) {
    emit('close')
  }
}

const handlePublish = async () => {
  if (loading.value) return

  try {
    loading.value = true
    
    const result = await createPost(
      parseInt(props.collectionId), 
      description.value.trim() || null
    )
    
    if (result.status === 'success') {
      emit('success', result)
      closeModal()
      
      // 显示成功提示（如果有全局提示组件）
      console.log('发布成功:', result.message)
    }
  } catch (error) {
    console.error('发布失败:', error)
    
    // 显示错误提示
    let errorMessage = '发布失败，请稍后重试'
    if (error.detail) {
      errorMessage = error.detail
    } else if (error.message) {
      errorMessage = error.message
    }
    
    alert(errorMessage) // 简单的错误提示，可以替换为更好的提示组件
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
/* 动画效果 */
.modal-enter-active, .modal-leave-active {
  transition: opacity 0.3s ease;
}

.modal-enter-from, .modal-leave-to {
  opacity: 0;
}

.modal-enter-active .modal-content,
.modal-leave-active .modal-content {
  transition: transform 0.3s ease;
}

.modal-enter-from .modal-content,
.modal-leave-to .modal-content {
  transform: scale(0.9);
}
</style> 