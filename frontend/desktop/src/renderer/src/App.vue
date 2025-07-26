<template>
  <div class="flex h-screen bg-gray-50/80 overflow-hidden">
    <!-- 侧边栏 -->
    <div 
      @mouseenter="handleSidebarEnter"
      @mouseleave="handleSidebarLeave"
      :class="[
        'bg-white/90 glass-effect border-r border-gray-100 flex flex-col flex-shrink-0 transition-all duration-300 ease-in-out',
        sidebarExpanded ? 'w-56' : 'w-24'
      ]"
    >
      <!-- Logo区域 -->
      <div :class="['border-b border-gray-50 transition-all duration-300 ease-in-out', sidebarExpanded ? 'p-6' : 'p-4']">
        <div :class="['flex items-center', sidebarExpanded ? 'space-x-3' : 'justify-center']">
          <div :class="[
            'bg-gradient-to-br from-slate-700 to-slate-900 rounded-lg flex items-center justify-center shadow-minimal flex-shrink-0 transition-all duration-300 ease-in-out',
            sidebarExpanded ? 'w-8 h-8' : 'w-12 h-12'
          ]">
            <Camera :class="[
              'text-white transition-all duration-300 ease-in-out',
              sidebarExpanded ? 'w-4 h-4' : 'w-6 h-6'
            ]" />
          </div>
          <div 
            :class="[
              'transition-all duration-300 ease-in-out overflow-hidden',
              sidebarExpanded ? 'opacity-100 max-w-none' : 'opacity-0 max-w-0'
            ]"
          >
            <h1 class="text-base font-bold text-gray-900 whitespace-nowrap">Memora</h1>
          </div>
        </div>
      </div>
      <!-- 导航菜单 -->
      <nav :class="['flex-1 transition-all duration-300 ease-in-out', sidebarExpanded ? 'p-4' : 'p-4']">
        <ul :class="[sidebarExpanded ? 'space-y-1' : 'space-y-2']">
          <li v-for="item in menuItems" :key="item.id" :class="[!sidebarExpanded ? 'flex justify-center' : '']">
            <button
              @click="goMenu(item)"
              :class="[
                'flex items-center rounded-lg text-left transition-all duration-300 ease-in-out btn-hover',
                sidebarExpanded ? 'w-full space-x-3 px-3 py-2.5' : 'w-12 h-12 justify-center',
                isActiveMenu(item) 
                  ? 'bg-gray-900 text-white shadow-minimal' 
                  : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
              ]"
              :title="!sidebarExpanded ? item.name : ''"
            >
              <component :is="item.icon" :class="[
                'flex-shrink-0 transition-all duration-300 ease-in-out',
                sidebarExpanded ? 'w-4 h-4' : 'w-6 h-6'
              ]" />
              <span 
                :class="[
                  'font-medium text-sm transition-all duration-300 ease-in-out overflow-hidden whitespace-nowrap',
                  sidebarExpanded ? 'opacity-100 max-w-none' : 'opacity-0 max-w-0'
                ]"
              >
                {{ item.name }}
              </span>
            </button>
          </li>
        </ul>
      </nav>
      <!-- 用户信息 -->
      <div :class="['border-t border-gray-50 transition-all duration-300 ease-in-out', sidebarExpanded ? 'p-4' : 'p-3']">
        <div :class="['flex items-center', sidebarExpanded ? 'space-x-3' : 'justify-center']">
          <div :class="[
            'bg-gray-100 rounded-lg flex items-center justify-center flex-shrink-0 transition-all duration-300 ease-in-out',
            sidebarExpanded ? 'w-8 h-8' : 'w-12 h-12'
          ]">
            <User :class="[
              'text-gray-600 transition-all duration-300 ease-in-out',
              sidebarExpanded ? 'w-4 h-4' : 'w-6 h-6'
            ]" />
          </div>
          <div 
            :class="[
              'transition-all duration-300 ease-in-out overflow-hidden',
              sidebarExpanded ? 'opacity-100 max-w-none' : 'opacity-0 max-w-0'
            ]"
          >
            <p class="font-medium text-gray-900 text-sm whitespace-nowrap">用户 {{ currentUserId }}</p>
            <p class="text-xs text-gray-500 whitespace-nowrap">{{ todayEvents }} 个事件</p>
          </div>
        </div>
      </div>
    </div>
    <!-- 主内容区 -->
    <div class="flex-1 flex flex-col overflow-hidden min-w-0">
      <router-view />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Camera, User, Star } from 'lucide-vue-next'

const router = useRouter()
const route = useRoute()

const sidebarExpanded = ref(false)
const sidebarToggleCount = ref(0)

const menuItems = [
  { id: 'collections', name: '收藏', icon: Star, route: { name: 'Home' } },
]

const currentUserId = ref(1)
const todayEvents = ref(0)

const handleSidebarEnter = () => {
  if (!sidebarExpanded.value) {
    sidebarToggleCount.value++
  }
  sidebarExpanded.value = true
}
const handleSidebarLeave = () => {
  sidebarExpanded.value = false
}
const goMenu = (item) => {
  if (item.route) {
    router.push(item.route)
  }
}
const isActiveMenu = (item) => {
  // 只高亮首页（收藏）
  if (item.route && item.route.name === 'Home') {
    return route.name === 'Home'
  }
  return false
}
</script>

<style scoped>
.glass-effect {
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
}
.shadow-minimal {
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
}
.btn-hover:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}
.transition-smooth {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: rgba(156, 163, 175, 0.3);
  border-radius: 3px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: rgba(156, 163, 175, 0.5);
}
</style>