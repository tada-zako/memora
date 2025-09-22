import { createI18n } from 'vue-i18n'
import en from './locales/en.json'
import zh from './locales/zh.json'

const messages = {
  en,
  zh
}

const i18n = createI18n({
  locale: localStorage.getItem('language') || 'zh', // default locale
  fallbackLocale: 'en',
  messages,
  // 明确指定插值分隔符
  modifiers: {
    // 可以在这里添加自定义修饰符
  }
})

export default i18n
