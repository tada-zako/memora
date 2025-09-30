<template>
  <div
    v-if="show"
    class="fixed inset-0 backdrop-blur-xl bg-opacity-50 flex items-center justify-center"
    style="z-index: 9999"
    @click.self="handleCancel"
  >
    <div class="bg-primary rounded-lg shadow-lg max-w-md w-full mx-4">
      <!-- 模态框头部 -->
      <div class="flex items-center justify-between p-6 border-b border-muted-border">
        <h3 class="text-lg font-semibold text-accent-text">
          {{ title }}
        </h3>
        <button
          class="text-primary-text hover:text-primary-text transition-colors"
          @click="handleCancel"
        >
          <XIcon class="w-5 h-5" />
        </button>
      </div>

      <!-- 模态框内容 -->
      <div class="p-6">
        <div class="text-primary-text">
          {{ message }}
        </div>
      </div>

      <!-- 模态框底部 -->
      <div class="flex items-center justify-end gap-3 p-6 border-t border-muted-border">
        <button
          class="px-4 py-2 bg-primary text-accent-text border border-accent-border rounded-lg hover:bg-accent transition-colors font-medium"
          :disabled="loading"
          @click="handleCancel"
        >
          {{ t('modal.cancelText') }}
        </button>
        <button
          class="px-4 py-2 bg-primary text-accent-text rounded-lg border border-accent-border hover:bg-accent transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          :disabled="loading"
          @click="handleConfirm"
        >
          <span
            v-if="loading"
            class="w-4 h-4 border-2 border-muted-border border-t-transparent rounded-full animate-spin"
          ></span>
          {{ loading ? t('modal.loadingText') : t('modal.confirmText') }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { X as XIcon } from 'lucide-vue-next'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

defineProps({
  show: {
    type: Boolean,
    default: false
  },
  title: {
    type: String,
    default: '确认'
  },
  message: {
    type: String,
    required: true
  }
})

const emit = defineEmits(['confirm', 'cancel'])

const handleConfirm = () => {
  emit('confirm')
}

const handleCancel = () => {
  emit('cancel')
}
</script>

<style scoped>
/* 动画效果 */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
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
