import './assets/styles.css'
import { createApp } from 'vue'
import App from './App.vue'
import QuickApp from './components/QuickWindow.vue'
import router from './router'

// 根据URL hash决定加载哪个应用组件
const isQuickMode = window.location.hash === '#/quick'

if (isQuickMode) {
  // 快速模式，不使用router
  createApp(QuickApp).mount('#app')
} else {
  // 普通模式，使用router
  const app = createApp(App)
  app.use(router)
  app.mount('#app')
}
