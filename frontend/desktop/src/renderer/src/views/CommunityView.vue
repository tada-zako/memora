<template>
  <div class="flex-1 flex flex-col bg-gray-50/80">
    <!-- 顶部标题栏 -->
    <div class="bg-white/90 glass-effect border-b border-gray-100 px-6 py-4">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-xl font-semibold text-gray-900">社区</h1>
          <p class="text-sm text-gray-600 mt-1">发现和分享精彩内容</p>
        </div>
      </div>
    </div>

    <!-- 主内容区 -->
    <div class="flex-1 flex items-center justify-center p-6">
      <div class="text-center max-w-md">
        <div class="w-24 h-24 bg-gradient-to-br from-blue-100 to-purple-100 rounded-full flex items-center justify-center mx-auto mb-6">
          <Earth class="w-12 h-12 text-blue-600" />
        </div>
        <h2 class="text-2xl font-bold text-gray-900 mb-4">社区功能即将推出</h2>
        <p class="text-gray-600 mb-6">
          我们正在为您打造一个全新的社区体验，在这里您可以：
        </p>
        <div class="text-left space-y-2 mb-8">
          <div class="flex items-center space-x-3">
            <div class="w-2 h-2 bg-blue-500 rounded-full"></div>
            <span class="text-gray-700">分享您的收藏和见解</span>
          </div>
          <div class="flex items-center space-x-3">
            <div class="w-2 h-2 bg-blue-500 rounded-full"></div>
            <span class="text-gray-700">发现其他用户的精彩内容</span>
          </div>
          <div class="flex items-center space-x-3">
            <div class="w-2 h-2 bg-blue-500 rounded-full"></div>
            <span class="text-gray-700">参与讨论和互动</span>
          </div>
          <div class="flex items-center space-x-3">
            <div class="w-2 h-2 bg-blue-500 rounded-full"></div>
            <span class="text-gray-700">获取热门推荐</span>
          </div>
        </div>
        <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <p class="text-sm text-blue-800">
            预计上线时间：敬请期待
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Earth } from 'lucide-vue-next'
</script>

<style scoped>
.glass-effect {
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
}
</style>
