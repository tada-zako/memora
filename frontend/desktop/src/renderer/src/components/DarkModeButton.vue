<!-- 黑暗模式切换按钮 -->
<template>
  <button
    class="relative w-16 h-8 rounded-full bg-muted hover:bg-accent border border-primary-border hover:border-accent-border transition-smooth cursor-pointer focus:outline-none focus:ring-2 focus:ring-accent focus:ring-offset-2"
    :title="props.isDark ? '切换到浅色模式' : '切换到深色模式'"
    @click="emit('toggle')"
  >
    <!-- 滑块背景轨道 -->
    <div
      class="absolute inset-1 rounded-full bg-linear-[135deg] from-muted to-accent transition-all duration-300 ease-in-out"
    ></div>

    <!-- 滑动的图标容器 -->
    <div
      class="absolute top-1 w-6 h-6 bg-primary rounded-full shadow-lg/25 transform transition-all duration-300 ease-in-out flex items-center justify-center"
      :class="props.isDark ? 'translate-x-9' : 'translate-x-1'"
    >
      <Transition name="icon-switch" mode="out-in">
        <Sun
          v-if="!props.isDark"
          key="sun"
          :size="14"
          color="#ff8d7d"
          class="transition-all duration-200"
        />

        <Moon
          v-else
          key="moon"
          :size="14"
          color="#ffdf15"
          class="text-accent-text transition-all duration-200"
        />
      </Transition>
    </div>
  </button>
</template>

<script setup lang="ts">
import { Moon, Sun } from 'lucide-vue-next'

const props = defineProps<{
  isDark: boolean
}>()

const emit = defineEmits<{
  (e: 'toggle'): void
}>()
</script>

<style scoped>
/* 图标切换动画 - 更平滑的过渡 */
.icon-switch-enter-active,
.icon-switch-leave-active {
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

.icon-switch-enter-from {
  opacity: 0;
  transform: rotate(-45deg);
}

.icon-switch-leave-to {
  opacity: 0;
  transform: rotate(45deg);
}

.icon-switch-enter-to,
.icon-switch-leave-from {
  opacity: 1;
  transform: rotate(0deg);
}

/* 滑块容器悬停效果 */
button:hover {
  transform: scale(1.02);
}

button:active {
  transform: scale(0.98);
}
</style>
