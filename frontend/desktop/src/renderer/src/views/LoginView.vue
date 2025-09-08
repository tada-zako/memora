<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8">
      <div>
        <div class="mx-auto h-12 w-12 flex items-center justify-center">
          <img src="../assets/icon.png" alt="Memora Logo" class="h-12 w-12" />
        </div>
        <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">
          {{ isLogin ? '登录到你的账户' : '创建新账户' }}
        </h2>
        <p class="mt-2 text-center text-sm text-gray-600">
          <button @click="toggleMode" class="font-medium text-black hover:text-indigo-500">
            {{ isLogin ? '还没有账户？立即注册' : '已有账户？立即登录' }}
          </button>
        </p>
      </div>

      <form class="mt-8 space-y-6" @submit.prevent="handleSubmit">
        <div class="rounded-md shadow-sm -space-y-px">
          <!-- 注册时显示邮箱字段 -->
          <div v-if="!isLogin">
            <label for="email" class="sr-only">邮箱地址</label>
            <input
              id="email"
              name="email"
              type="email"
              autocomplete="email"
              required
              v-model="form.email"
              class="relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
              placeholder="邮箱地址"
            />
          </div>

          <div>
            <label for="username" class="sr-only">用户名</label>
            <input
              id="username"
              name="username"
              type="text"
              autocomplete="username"
              required
              v-model="form.username"
              :class="[
                'relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm',
                isLogin ? 'rounded-t-md' : ''
              ]"
              placeholder="用户名"
            />
          </div>

          <div>
            <label for="password" class="sr-only">密码</label>
            <input
              id="password"
              name="password"
              type="password"
              autocomplete="current-password"
              required
              v-model="form.password"
              class="relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
              placeholder="密码"
            />
          </div>
        </div>

        <!-- 错误提示 -->
        <div v-if="errorMessage" class="text-red-600 text-sm text-center">
          {{ errorMessage }}
        </div>

        <!-- 成功提示 -->
        <div v-if="successMessage" class="text-green-600 text-sm text-center">
          {{ successMessage }}
        </div>

        <div>
          <button
            type="submit"
            :disabled="loading"
            class="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-black focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
          >
            <span v-if="loading">处理中...</span>
            <span v-else>{{ isLogin ? '登录' : '注册' }}</span>
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { login, register } from '../services/auth'

const router = useRouter()
const isLogin = ref(true)
const loading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')

const form = reactive({
  username: '',
  email: '',
  password: ''
})

const toggleMode = () => {
  isLogin.value = !isLogin.value
  errorMessage.value = ''
  successMessage.value = ''
  // 清空表单
  form.username = ''
  form.email = ''
  form.password = ''
}

const handleSubmit = async () => {
  loading.value = true
  errorMessage.value = ''
  successMessage.value = ''

  try {
    if (isLogin.value) {
      // 登录
      const response = await login({
        username: form.username,
        password: form.password
      })

      // 本地存储 token
      localStorage.setItem('access_token', response.access_token)
      console.log('登录成功，token已保存:', response.access_token.substring(0, 20) + '...')

      successMessage.value = '登录成功！'
      setTimeout(() => {
        router.push({ name: 'Profile' })
      }, 1000)
    } else {
      // 注册
      await register({
        username: form.username,
        email: form.email,
        password: form.password
      })

      successMessage.value = '注册成功！请登录'
      setTimeout(() => {
        isLogin.value = true
        form.password = ''
      }, 1000)
    }
  } catch (error) {
    errorMessage.value = error.detail || error.message || '操作失败，请重试'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
/* 自定义样式可以在这里添加 */
</style>
