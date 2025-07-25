import './assets/styles.css'
import { createApp } from 'vue'
import App from './App.vue'
import QuickApp from './QuickApp.vue'

// 根据URL hash决定加载哪个应用组件
const isQuickMode = window.location.hash === '#/quick'
const AppComponent = isQuickMode ? QuickApp : App

createApp(AppComponent).mount('#app')
