<template>
  <div class="flex h-full bg-primary overflow-hidden">
    <!-- 侧边栏 -->
    <div
      class="bg-primary glass-effect border-r border-muted-border flex flex-col flex-shrink-0 transition-all duration-300 ease-in-out"
      :class="[sidebarExpanded ? 'w-56' : 'w-24']"
      @mouseenter="handleSidebarEnter"
      @mouseleave="handleSidebarLeave"
    >
      <!-- Logo区域 -->
      <div
        style="margin-left: 8px"
        :class="['transition-all duration-300 ease-in-out', sidebarExpanded ? 'p-6' : 'p-4']"
      >
        <div :class="['flex items-center']" style="gap: 8px">
          <logo :class="[sidebarExpanded ? 'w-8 h-8' : 'w-12 h-12']" />
          <div
            :class="[
              'transition-all duration-300 ease-in-out overflow-hidden',
              sidebarExpanded ? 'opacity-100 max-w-none' : 'opacity-0 max-w-0'
            ]"
          >
            <h1 class="text-xl font-bold text-accent-text whitespace-nowrap">
              {{ t('app.title') }}
            </h1>
          </div>
        </div>
      </div>
      <!-- 导航菜单 -->
      <nav
        :class="['flex-1 transition-all duration-300 ease-in-out', sidebarExpanded ? 'p-4' : 'p-4']"
      >
        <ul>
          <li
            v-for="item in menuItems"
            :key="item.id"
            style="margin-bottom: 12px"
            :class="[!sidebarExpanded ? 'flex justify-center' : '']"
          >
            <button
              class="text-primary-text hover:text-accent-text flex items-center rounded-lg text-left transition-all duration-0 ease-in-out btn-hover"
              :class="[
                sidebarExpanded ? 'w-full space-x-3 px-3 py-2.5' : 'w-12 h-12 justify-center',
                isActiveMenu(item) ? 'bg-vibrant/60 shadow-sm' : ' hover:bg-accent'
              ]"
              :title="!sidebarExpanded ? item.name : ''"
              @click="goMenu(item)"
            >
              <component
                :is="item.icon"
                :class="[
                  'flex-shrink-0 transition-all duration-300 ease-in-out',
                  sidebarExpanded ? 'w-4 h-4' : 'w-6 h-6'
                ]"
              />
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
    </div>
    <!-- 主内容区 -->
    <div class="flex-1 flex flex-col min-w-0">
      <router-view style="overflow-y: scroll" />
    </div>

    <!-- 黑夜模式切换按钮 -->
    <div
      class="fixed bottom-6 left-6 z-50"
      :class="[sidebarExpanded ? 'translate-x-0' : 'translate-x-12']"
      style="transition: transform 0.3s ease-in-out"
    >
      <DarkModeButton :is-dark="isDark" @toggle="toggleDarkMode" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, watch, provide, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { Star, Earth, User, Settings } from 'lucide-vue-next'
import DarkModeButton from './components/DarkModeButton.vue'
import Logo from './components/Logo.vue'

const { t } = useI18n()
const router = useRouter()
const route = useRoute()

const sidebarExpanded = ref(true)
const sidebarToggleCount = ref(0)

const menuItems = computed(() => [
  { id: 'collections', name: t('menu.collections'), icon: Star, route: { name: 'Home' } },
  { id: 'community', name: t('menu.community'), icon: Earth, route: { name: 'Community' } },
  { id: 'profile', name: t('menu.profile'), icon: User, route: { name: 'Profile' } },
  { id: 'settings', name: t('menu.settings'), icon: Settings, route: { name: 'Settings' } }
])

const handleSidebarEnter = () => {
  sidebarExpanded.value = true
}
const handleSidebarLeave = () => {
  // 默认展开状态下，鼠标离开时保持展开
  // 如果需要自动收缩，可以设置为 false
  // sidebarExpanded.value = false
}
const goMenu = (item) => {
  if (item.route) {
    router.push(item.route)
  }
}
const isActiveMenu = (item) => {
  // 根据菜单项的路由名称或ID来判断是否激活
  if (item.route && item.route.name) {
    // 对于收藏菜单，检查是否在首页或收藏相关页面
    if (item.id === 'collections') {
      return (
        route.name === 'Home' ||
        route.name === 'CollectionList' ||
        route.name === 'CollectionDetail' ||
        route.name === 'CollectionAttachmentList' ||
        route.name === 'CollectionAttachmentDetail'
      )
    }
    // 对于社区菜单
    if (item.id === 'community') {
      return route.name === 'Community'
    }
    // 对于个人中心菜单
    if (item.id === 'profile') {
      return route.name === 'Profile' || route.name === 'Login'
    }
    // 对于设置菜单
    if (item.id === 'settings') {
      return route.name === 'Settings'
    }
    // 默认匹配
    return route.name === item.route.name
  }
  return false
}

// 全局 isDark 状态
const isDark = ref(false)

provide('isDark', isDark)

// 监听系统主题变化
const watchSysPref = () => {
  if (window.matchMedia) {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
    mediaQuery.addEventListener('change', (e) => {
      // 只有在用户没有手动设置主题时才跟随系统
      if (!localStorage.getItem('theme')) {
        isDark.value = e.matches
      }
    })
  }
}

// 获取主题设置
const getTheme = () => {
  const savedTheme = localStorage.getItem('theme')
  if (savedTheme) {
    return savedTheme === 'dark'
  }
  return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches
}

// 改变主题
const toggleDarkMode = () => {
  isDark.value = !isDark.value
}

// 应用主题
const applyTheme = (dark) => {
  const html = document.documentElement
  if (dark) {
    html.classList.add('dark')
  } else {
    html.classList.remove('dark')
  }
}

// 保存主题设置
const saveTheme = (dark) => {
  localStorage.setItem('theme', dark ? 'dark' : 'light')
}

// 监听主题变化
watch(
  isDark,
  (newVal) => {
    applyTheme(newVal)
    saveTheme(newVal)
  },
  { immediate: true }
)

// 挂载后执行
onMounted(() => {
  isDark.value = getTheme()
  watchSysPref()
})
</script>

<style scoped>
.glass-effect {
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
}
.btn-hover {
  transition: background-color 0s ease-in-out;
  border-radius: 28px;
}
.btn-hover:hover {
  background-color: var(--color-accent);
  transform: none;
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
