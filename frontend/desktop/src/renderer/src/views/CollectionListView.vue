<template>
    <div class="min-h-screen bg-white">
      <!-- Header -->
      <header class="border-b border-gray-200">
        <div class="max-w-6xl mx-auto px-6 py-8">
          <button @click="$router.back()" class="mb-4 px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded text-gray-700 font-medium flex items-center gap-2">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M15 19l-7-7 7-7"/></svg>
            返回
          </button>
          <div class="flex items-center gap-3 mb-2">
            <BookmarkIcon class="w-6 h-6 text-black" />
            <h1 class="text-2xl font-bold text-black">分类 #{{ categoryId }} 的收藏</h1>
          </div>
        </div>
      </header>
  
      <!-- Main Content -->
      <main class="max-w-6xl mx-auto px-6 py-12">
        <div v-if="loading" class="text-center py-16 text-gray-500">加载中...</div>
        <div v-else>
          <div v-if="collections.length === 0" class="text-center py-16">
            <BookmarkIcon class="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h3 class="text-lg font-medium text-gray-900 mb-2">没有找到相关收藏</h3>
            <p class="text-gray-500">该分类下暂无收藏</p>
          </div>
          <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div
              v-for="item in collections"
              :key="item.id"
              class="border border-gray-200 rounded-lg bg-white hover:shadow-md transition-shadow cursor-pointer group"
              @click="$router.push({ name: 'CollectionDetail', params: { collection_id: item.id } })"
            >
              <div class="p-6">
                <div class="flex items-center justify-between mb-4">
                  <span class="px-2 py-1 bg-gray-100 text-gray-800 rounded text-xs font-medium">
                    分类ID: {{ item.category_id }}
                  </span>
                </div>
                <h3 class="text-lg font-semibold text-black mb-3 line-clamp-2 group-hover:text-gray-700 transition-colors">
                  Collection #{{ item.id }}
                </h3>
                <p class="text-sm text-gray-600 mb-4 line-clamp-3">
                  标签: {{ item.tags }}
                </p>
                <div class="flex items-center justify-between text-xs text-gray-500">
                  <div>
                    <div>创建时间: {{ formatDate(item.created_at) }}</div>
                    <div>更新: {{ formatDate(item.updated_at) }}</div>
                  </div>
                  <button
                    @click.stop="showPublishModal(item.id)"
                    class="px-3 py-1 bg-blue-600 text-white text-xs rounded hover:bg-blue-700 transition-colors flex items-center gap-1"
                  >
                    <ShareIcon class="w-3 h-3" />
                    分享
                  </button>
                </div>
                <div v-if="item.details && item.details.attachment" class="mt-4 pt-4 border-t border-gray-100">
                  <div class="flex items-center gap-2">
                    <span class="text-xs text-gray-500 truncate">附件ID: {{ item.details.attachment }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
  
      <!-- Footer -->
      <footer class="border-t border-gray-200 mt-16">
        <div class="max-w-6xl mx-auto px-6 py-8">
          <div class="text-center text-sm text-gray-500">
            <p>© 2025 网页收藏系统 · 简约 · 现代 · 高效</p>
          </div>
              </div>
    </footer>

    <!-- 发布到社区模态框 -->
    <PublishToCommunityModal
      :show="publishModalShow"
      :collection-id="selectedCollectionId"
      @close="publishModalShow = false"
      @success="handlePublishSuccess"
    />
  </div>
</template>
  
  <script setup>
  import { ref, onMounted } from 'vue'
  import { useRoute, useRouter } from 'vue-router'
  import { getCollectionsByCategory } from '../services/collection'
  import { isAuthenticated } from '../services/auth'
  import PublishToCommunityModal from '../components/PublishToCommunityModal.vue'

  // Icons
  const BookmarkIcon = {
    template: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m19 21-7-4-7 4V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2v16z"/></svg>`
  }

  const ShareIcon = {
    template: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 12v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8"/><polyline points="16,6 12,2 8,6"/><line x1="12" y1="2" x2="12" y2="15"/></svg>`
  }
  
  // 路由参数
  const route = useRoute()
  const router = useRouter()
  const categoryId = route.params.category_id

  const collections = ref([])
  const loading = ref(false)
  const publishModalShow = ref(false)
  const selectedCollectionId = ref(null)

  const fetchCollectionsByCategory = async () => {
    // 检查用户是否已登录
    if (!isAuthenticated()) {
      console.log('用户未登录，跳转到登录页面')
      router.push('/login')
      return
    }

    loading.value = true
    try {
      const result = await getCollectionsByCategory(categoryId)
      if (result.status === 'success' && result.data && result.data.collections) {
        collections.value = result.data.collections
      } else {
        collections.value = []
      }
    } catch (e) {
      collections.value = []
      // 如果是认证错误，重定向到登录页面
      if (e.detail === 'Not authenticated' || e.message?.includes('401')) {
        console.log('认证失败，跳转到登录页面')
        router.push('/login')
      }
    } finally {
      loading.value = false
    }
  }

  onMounted(() => {
    fetchCollectionsByCategory()
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

  const showPublishModal = (collectionId) => {
    selectedCollectionId.value = collectionId
    publishModalShow.value = true
  }

  const handlePublishSuccess = (result) => {
    console.log('发布成功:', result)
    alert('已成功发布到社区！')
  }
  </script>
  
  <style scoped>
  .line-clamp-2 {
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }
  
  .line-clamp-3 {
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }
  </style>
  