<template>
  <div class="border border-muted-border rounded-lg bg-primary mb-4">
    <div class="p-6">
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-lg font-semibold text-accent-text">
          {{ isEditing ? t('collection.edit') : t('collection.createNewCollection') }}
        </h3>
        <button
          class="text-primary-text hover:text-accent-text focus:outline-none"
          @click="handleCancel"
        >
          <svg
            class="w-5 h-5"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            viewBox="0 0 24 24"
          >
            <path d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <form @submit.prevent="handleSubmit">
        <!-- Title -->
        <div class="mb-4">
          <label class="block text-sm font-medium text-accent-text mb-2">
            {{ t('collection.title') }} *
          </label>
          <input
            v-model="formData.title"
            type="text"
            required
            class="w-full px-3 py-2 border border-accent-border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-accent-text"
            :placeholder="t('collection.titlePlaceholder')"
          />
        </div>

        <!-- Content -->
        <div class="mb-4">
          <label class="block text-sm font-medium text-accent-text mb-2">
            {{ t('collection.content') }}
          </label>
          <textarea
            v-model="formData.content"
            rows="6"
            class="w-full px-3 py-2 border border-accent-border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-accent-text"
            :placeholder="t('collection.contentPlaceholder')"
          ></textarea>
        </div>

        <!-- URL -->
        <div v-if="!isEditing" class="mb-4">
          <label class="block text-sm font-medium text-accent-text mb-2">
            {{ t('collection.url') }} *
          </label>
          <input
            v-model="formData.url"
            type="url"
            :required="!isEditing"
            class="w-full px-3 py-2 border border-accent-border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-accent-text"
            :placeholder="t('collection.urlPlaceholder')"
          />
        </div>

        <!-- Tags -->
        <div class="mb-4">
          <label class="block text-sm font-medium text-accent-text mb-2">
            {{ t('collection.tags') }}
          </label>
          <input
            v-model="formData.tagsInput"
            type="text"
            class="w-full px-3 py-2 border border-accent-border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-accent-text"
            :placeholder="t('collection.tagsPlaceholder')"
          />
          <div v-if="formData.tagsInput" class="mt-2 flex flex-wrap gap-2">
            <span
              v-for="tag in formData.tagsInput
                .split(',')
                .map((t) => t.trim())
                .filter((t) => t)"
              :key="tag"
              class="px-2 py-1 bg-muted text-accent-text rounded text-xs font-medium"
            >
              {{ tag }}
            </span>
          </div>
        </div>

        <!-- Summary -->
        <div class="mb-6">
          <label class="block text-sm font-medium text-accent-text mb-2">
            {{ t('collection.summary') }}
          </label>
          <textarea
            v-model="formData.summary"
            rows="4"
            class="w-full px-3 py-2 border border-accent-border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-accent-text"
            :placeholder="t('collection.summaryPlaceholder')"
          ></textarea>
        </div>

        <!-- Actions -->
        <div class="flex justify-end gap-3">
          <button
            type="button"
            class="px-4 py-2 text-primary-text hover:text-accent-text border border-accent-border rounded-lg hover:bg-muted transition-colors"
            @click="handleCancel"
          >
            {{ t('collection.cancel') }}
          </button>
          <button
            type="submit"
            :disabled="!formData.title.trim() || loading"
            class="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-white rounded-lg transition-colors flex items-center gap-2"
          >
            <svg
              v-if="loading"
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
            {{
              isEditing
                ? loading
                  ? t('collection.updating')
                  : t('collection.update')
                : loading
                  ? t('collection.creating')
                  : t('collection.create')
            }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

// Props
const props = defineProps({
  modelValue: {
    type: Object,
    default: () => ({
      title: '',
      content: '',
      url: '',
      tagsInput: '',
      summary: ''
    })
  },
  loading: {
    type: Boolean,
    default: false
  },
  isEditing: {
    type: Boolean,
    default: false
  }
})

// Emits
const emit = defineEmits(['update:modelValue', 'submit', 'cancel'])

// Form data
const formData = ref({ ...props.modelValue })

// Watch for prop changes
watch(
  () => props.modelValue,
  (newValue) => {
    formData.value = { ...newValue }
  },
  { deep: true }
)

// Watch for form data changes
watch(
  formData,
  (newValue) => {
    emit('update:modelValue', { ...newValue })
  },
  { deep: true }
)

// Computed
const isEditing = computed(() => props.isEditing)

// Methods
const handleSubmit = () => {
  if (!formData.value.title.trim()) return

  const submitData = {
    title: formData.value.title.trim(),
    content: formData.value.content.trim() || undefined,
    tags: formData.value.tagsInput
      ? formData.value.tagsInput
          .split(',')
          .map((tag) => tag.trim())
          .filter((tag) => tag)
      : undefined,
    summary: formData.value.summary.trim() || undefined
  }

  // 只在创建时包含 URL
  if (!isEditing.value) {
    submitData.url = formData.value.url.trim() || undefined
  }

  emit('submit', submitData)
}

const handleCancel = () => {
  emit('cancel')
}
</script>
