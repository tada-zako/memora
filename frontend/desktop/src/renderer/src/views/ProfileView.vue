<template>
    <div class="h-full bg-gray-50 overflow-y-auto">
        <div class="max-w-4xl mx-auto py-6 px-4 sm:px-6 lg:px-8">

            <div style="display: flex; gap: 24px; align-items: center; margin-bottom: 24px;">
                <div class="relative">
                    <div 
                        @click="triggerAvatarUpload"
                        class="h-35 w-35 rounded-full bg-gray-300 flex items-center justify-center overflow-hidden cursor-pointer hover:opacity-80 transition-opacity"
                    >
                        <img v-if="avatarUrl" :src="avatarUrl" alt="头像" class="h-full w-full object-cover" />
                        <User v-else class="h-10 w-10 text-gray-600" />
                        <div v-if="avatarUploading" class="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center">
                            <RefreshCw class="h-6 w-6 text-white animate-spin" />
                        </div>
                    </div>
                    <input
                        ref="avatarInput"
                        type="file"
                        accept="image/*"
                        @change="handleAvatarUpload"
                        class="hidden"
                    />
                </div>
                <div style="display: flex; justify-content: space-between;" class="flex-1">
                    <div style="display: flex; flex-direction: column; gap: 6px;">
                        <h2 class="text-3xl font-bold text-gray-900">{{ userInfo?.username }}</h2>
                        <p class="text-gray-600">{{ userInfo?.email }}</p>
                        <p class="text-sm text-gray-500">
                            注册时间: {{ formatDate(userInfo?.created_at) }}
                        </p>
                    </div>
                    <div style="display: flex; justify-content: center; align-items: center;">
                        <button @click="showEdit"
                            class="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
                            <Edit3 class="h-4 w-4 mr-1" />
                            编辑
                        </button>
                    </div>

                </div>

            </div>

        </div>

        <!-- 全局消息提示 -->
        <div v-if="editErrorMessage || editSuccessMessage" class="fixed top-4 right-4 z-50">
            <div v-if="editErrorMessage"
                class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded shadow-lg">
                {{ editErrorMessage }}
            </div>
            <div v-if="editSuccessMessage"
                class="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded shadow-lg">
                {{ editSuccessMessage }}
            </div>
        </div>

        <!-- 编辑用户信息模态框 -->
        <div v-if="showEditModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
            <div class="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
                <div class="mt-3">
                    <h3 class="text-lg font-medium text-gray-900 mb-4">编辑个人信息</h3>

                    <form @submit.prevent="updateProfile" class="space-y-4">
                        <div>
                            <label for="edit-email" class="block text-sm font-medium text-gray-700">邮箱</label>
                            <input id="edit-email" type="email" v-model="editForm.email"
                                class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm" />
                        </div>

                        <!-- 错误提示 -->
                        <div v-if="editErrorMessage" class="text-red-600 text-sm">
                            {{ editErrorMessage }}
                        </div>

                        <!-- 成功提示 -->
                        <div v-if="editSuccessMessage" class="text-green-600 text-sm">
                            {{ editSuccessMessage }}
                        </div>

                        <div class="flex space-x-3">
                            <button type="submit" :disabled="editLoading"
                                class="flex-1 inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50">
                                <span v-if="editLoading">保存中...</span>
                                <span v-else>保存</span>
                            </button>

                            <button type="button" @click="cancelEdit"
                                class="flex-1 inline-flex justify-center py-2 px-4 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
                                取消
                            </button>
                        </div>
                    </form>

                    <button @click="handleLogout" style="margin-top: 16px;"
                        class="w-full flex items-center justify-center px-4 py-2 border border-red-300 shadow-sm text-sm font-medium rounded-md text-red-700 bg-white hover:bg-red-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500">
                        <LogOut class="h-4 w-4 mr-2" />
                        退出登录
                    </button>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { User, Edit3, Star, Upload, Clock, RefreshCw, LogOut } from 'lucide-vue-next'
import {
    isAuthenticated,
    getLocalUserInfo,
    getUserProfile,
    updateUserProfile,
    logout,
    uploadUserAvatar,
    getUserAvatarUrl
} from '../services/auth'

const router = useRouter()
const isLoggedIn = ref(false)
const userInfo = ref(null)
const loading = ref(false)
const showEditModal = ref(false)
const editLoading = ref(false)
const editErrorMessage = ref('')
const editSuccessMessage = ref('')
const avatarUrl = ref(null)
const avatarInput = ref(null)
const avatarUploading = ref(false)

const editForm = reactive({
    email: ''
})

// 格式化日期
const formatDate = (dateString) => {
    if (!dateString) return '--'
    return new Date(dateString).toLocaleDateString('zh-CN')
}

// 检查登录状态并获取用户信息
const checkAuthAndLoadUser = async () => {
    isLoggedIn.value = isAuthenticated()

    if (!isLoggedIn.value) {
        // 未登录直接跳转到登录页面
        router.push({ name: 'Login' })
        return
    }

    // 先从本地存储获取用户信息
    userInfo.value = getLocalUserInfo()

    // 加载头像
    await loadAvatar()
    
    // 然后从服务器刷新用户信息
    await refreshUserInfo()
}

// 刷新用户信息
const refreshUserInfo = async () => {
    loading.value = true
    try {
        const response = await getUserProfile()
        if (response.status === 'success') {
            userInfo.value = response.data
            // 刷新头像
            await loadAvatar()
        }
    } catch (error) {
        console.error('获取用户信息失败:', error)
    } finally {
        loading.value = false
    }
}

// 加载头像
const loadAvatar = async () => {
    if (userInfo.value && userInfo.value.avatar_attachment_id) {
        try {
            avatarUrl.value = await getUserAvatarUrl(userInfo.value)
        } catch (error) {
            console.error('加载头像失败:', error)
        }
    }
}

// 显示编辑模态框
const showEdit = () => {
    editForm.email = userInfo.value?.email || ''
    editErrorMessage.value = ''
    editSuccessMessage.value = ''
    showEditModal.value = true
}

// 取消编辑
const cancelEdit = () => {
    showEditModal.value = false
    editErrorMessage.value = ''
    editSuccessMessage.value = ''
}

// 更新用户信息
const updateProfile = async () => {
    editLoading.value = true
    editErrorMessage.value = ''
    editSuccessMessage.value = ''

    try {
        const response = await updateUserProfile({
            email: editForm.email
        })

        if (response.status === 'success') {
            userInfo.value = response.data
            editSuccessMessage.value = '更新成功！'
            setTimeout(() => {
                showEditModal.value = false
            }, 1000)
        }
    } catch (error) {
        editErrorMessage.value = error.detail || error.message || '更新失败，请重试'
    } finally {
        editLoading.value = false
    }
}

// 触发头像上传
const triggerAvatarUpload = () => {
    if (avatarInput.value) {
        avatarInput.value.click()
    }
}

// 处理头像上传
const handleAvatarUpload = async (event) => {
    const file = event.target.files?.[0]
    if (!file) return

    avatarUploading.value = true

    try {
        const response = await uploadUserAvatar(file)
        if (response.status === 'success') {
            // 更新用户信息
            userInfo.value = response.data
            // 重新加载头像
            await loadAvatar()

            // 可以显示成功提示
            editSuccessMessage.value = '头像上传成功！'
            setTimeout(() => {
                editSuccessMessage.value = ''
            }, 3000)
        }
    } catch (error) {
        console.error('头像上传失败:', error)
        editErrorMessage.value = error.message || '头像上传失败，请重试'
        setTimeout(() => {
            editErrorMessage.value = ''
        }, 3000)
    } finally {
        avatarUploading.value = false
        // 清空文件选择
        if (avatarInput.value) {
            avatarInput.value.value = ''
        }
    }
}

// 退出登录
const handleLogout = () => {
    logout()
    isLoggedIn.value = false
    userInfo.value = null
    router.push({ name: 'Home' })
}

onMounted(() => {
    checkAuthAndLoadUser()
})
</script>

<style scoped>
/* 自定义样式可以在这里添加 */
</style>
