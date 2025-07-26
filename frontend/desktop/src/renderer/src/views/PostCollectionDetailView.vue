<template>
  <div class="min-h-screen bg-white">
    <!-- Header -->
    <header class="border-b border-gray-200">
      <div class="max-w-4xl mx-auto px-6 py-8">
        <button @click="$router.back()" class="mb-4 px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded text-gray-700 font-medium flex items-center gap-2">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M15 19l-7-7 7-7"/></svg>
          返回
        </button>
        <div class="flex items-center gap-3 mb-2">
          <BookmarkIcon class="w-6 h-6 text-black" />
          <h1 class="text-2xl font-bold text-black">推文收藏详情</h1>
        </div>
        <p class="text-gray-600">查看推文分享的收藏内容</p>
      </div>
    </header>

    <!-- Main Content -->
    <main class="max-w-4xl mx-auto px-6 py-12">
      <!-- 加载状态 -->
      <div v-if="loading" class="flex justify-center py-12">
        <div class="flex items-center gap-2 text-gray-500">
          <div class="w-5 h-5 border-2 border-gray-300 border-t-blue-600 rounded-full animate-spin"></div>
          加载中...
        </div>
      </div>

      <!-- 错误状态 -->
      <div v-else-if="error" class="text-center py-16">
        <div class="w-24 h-24 bg-gradient-to-br from-red-100 to-red-200 rounded-full flex items-center justify-center mx-auto mb-6">
          <AlertCircle class="w-12 h-12 text-red-600" />
        </div>
        <h2 class="text-xl font-semibold text-gray-900 mb-4">加载失败</h2>
        <p class="text-gray-600 mb-6">{{ error }}</p>
        <button
          @click="fetchCollectionDetails"
          class="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          重试
        </button>
      </div>

      <!-- 内容 -->
      <div v-else-if="collection" class="border border-gray-200 shadow-sm rounded-lg bg-white">
        <div class="p-6 pb-6">
          <div class="flex items-start justify-between gap-4">
            <div class="flex-1">
              <h2 class="text-2xl font-bold text-black mb-3 leading-tight">{{ collection.details.title || '无标题' }}</h2>
              <p class="text-base text-gray-600 leading-relaxed">{{ collection.details.summary || '无摘要' }}</p>
            </div>
            <div class="flex gap-2">
              <button
                @click="openOriginalLink"
                class="shrink-0 px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50 bg-transparent transition-colors flex items-center gap-2 text-sm"
              >
                <ExternalLinkIcon class="w-4 h-4" />
                访问原文
              </button>
            </div>
          </div>

          <div class="border-t border-gray-200 my-6"></div>

          <!-- Meta Information -->
          <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <div class="flex items-center gap-2">
              <CalendarIcon class="w-4 h-4 text-gray-500" />
              <span class="text-sm text-gray-600">创建于:</span>
              <span class="text-sm font-medium text-gray-900">{{ formatDate(collection.created_at) }}</span>
            </div>
            <div class="flex items-center gap-2">
              <ClockIcon class="w-4 h-4 text-gray-500" />
              <span class="text-sm text-gray-600">更新于:</span>
              <span class="text-sm font-medium text-gray-900">{{ formatDate(collection.updated_at) }}</span>
            </div>
            <div class="flex items-center gap-2">
              <TagIcon class="w-4 h-4 text-gray-500" />
              <span class="text-sm text-gray-600">分类:</span>
              <span class="text-sm font-medium text-gray-900">{{ collection.category_name || '未分类' }}</span>
            </div>
            <div class="flex items-center gap-2">
              <HashIcon class="w-4 h-4 text-gray-500" />
              <span class="text-sm text-gray-600">标签:</span>
              <span class="text-sm font-medium text-gray-900">{{ collection.tags ? collection.tags.split(',').length : 0 }}个</span>
            </div>
          </div>

          <!-- Tags -->
          <div class="flex items-center gap-2 pt-4">
            <span class="text-sm font-medium text-black">标签:</span>
            <div class="flex flex-wrap gap-2">
              <span
                v-for="(tag, index) in tagList"
                :key="index"
                class="px-2 py-1 border border-gray-300 text-gray-700 rounded text-xs hover:bg-gray-50"
              >
                #{{ tag }}
              </span>
              <span v-if="tagList.length === 0" class="text-sm text-gray-500">无标签</span>
            </div>
          </div>
        </div>

        <div class="p-6 pt-0">
          <!-- URL Display -->
          <div v-if="collection.details.url" class="mb-6 p-4 bg-gray-50 rounded-lg border border-gray-200">
            <div class="flex items-center gap-2 mb-2">
              <ExternalLinkIcon class="w-4 h-4 text-gray-500" />
              <span class="text-sm font-medium text-black">原文链接</span>
            </div>
            <a
              :href="collection.details.url"
              target="_blank"
              rel="noopener noreferrer"
              class="text-sm text-gray-600 hover:text-black transition-colors break-all"
            >
              {{ collection.details.url }}
            </a>
          </div>

          <!-- Content Preview -->
          <div v-if="collection.details.content">
            <h3 class="text-lg font-semibold text-black mb-4">内容预览</h3>
            <div class="prose prose-gray max-w-none">
              <div class="text-gray-700 leading-relaxed space-y-4">
                <p v-for="(paragraph, index) in contentParagraphs" :key="index" class="text-sm">
                  {{ paragraph }}
                </p>
              </div>
            </div>
          </div>

          <!-- 如果没有内容预览 -->
          <div v-else class="text-center py-8">
            <div class="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <FileText class="w-8 h-8 text-gray-400" />
            </div>
            <p class="text-gray-500">暂无内容预览</p>
          </div>
        </div>
      </div>
    </main>

    <!-- Footer -->
    <footer class="border-t border-gray-200 mt-16">
      <div class="max-w-4xl mx-auto px-6 py-8">
        <div class="text-center text-sm text-gray-500">
          <p>© 2025 网页收藏系统 · 简约 · 现代 · 高效</p>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getPostCollectionDetails } from '../services/community'
import { getPublicCollectionDetails } from '../services/collection'

// Icons
const BookmarkIcon = {
  template: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m19 21-7-4-7 4V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2v16z"/></svg>`
}

const ExternalLinkIcon = {
  template: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15,3 21,3 21,9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>`
}

const CalendarIcon = {
  template: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>`
}

const ClockIcon = {
  template: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12,6 12,12 16,14"/></svg>`
}

const TagIcon = {
  template: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"/><line x1="7" y1="7" x2="7.01" y2="7"/></svg>`
}

const HashIcon = {
  template: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="4" y1="9" x2="20" y2="9"/><line x1="4" y1="15" x2="20" y2="15"/><line x1="10" y1="3" x2="8" y2="21"/><line x1="16" y1="3" x2="14" y2="21"/></svg>`
}

const AlertCircle = {
  template: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>`
}

const FileText = {
  template: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14,2 14,8 20,8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10,9 9,9 8,9"/></svg>`
}

const route = useRoute()
const router = useRouter()
const postId = route.params.post_id
const collectionId = route.params.collection_id

const collection = ref(null)
const loading = ref(true)
const error = ref(null)

const fetchCollectionDetails = async () => {
  loading.value = true
  error.value = null
  
  try {
    let result
    
    // 如果有postId，使用推文收藏详情接口
    if (postId) {
      result = await getPostCollectionDetails(postId)
      if (result.status === 'success' && result.data && result.data.collection) {
        collection.value = result.data.collection
      } else {
        throw new Error('无法获取收藏详情')
      }
    } 
    // 如果有collectionId，使用公共收藏详情接口
    else if (collectionId) {
      result = await getPublicCollectionDetails(collectionId)
      if (result.status === 'success' && result.data && result.data.collection) {
        collection.value = result.data.collection
      } else {
        throw new Error('无法获取收藏详情')
      }
    } else {
      throw new Error('缺少必要的参数')
    }
  } catch (e) {
    error.value = e.message || '加载失败'
    console.error('获取收藏详情失败:', e)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchCollectionDetails()
})

const tagList = computed(() => {
  if (!collection.value?.tags) return []
  return collection.value.tags.split(',').map(tag => tag.trim()).filter(tag => tag)
})

const contentParagraphs = computed(() => {
  if (!collection.value?.details?.content) return []
  return collection.value.details.content.split('\n\n').filter(p => p.trim())
})

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const openOriginalLink = () => {
  if (collection.value?.details?.url) {
    window.open(collection.value.details.url, '_blank', 'noopener,noreferrer')
  }
}
</script>

<style scoped>
.prose {
  max-width: none;
}

.prose p {
  margin: 0;
  line-height: 1.6;
}
</style> 