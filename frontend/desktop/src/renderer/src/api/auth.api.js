import api from './api'

// 用户注册
export const registerApi = async (userData) => {
  return await api.post('/api/v1/auth/register', userData)
}

// 用户登录
export const loginApi = async (credentials) => {
  return await api.post('/api/v1/auth/login', credentials)
}

// 获取用户信息
export const getUserProfileApi = async () => {
  return await api.get('/api/v1/auth/profile')
}

// 更新用户信息
export const updateUserProfileApi = async (userData) => {
  return await api.put('/api/v1/auth/profile', userData)
}
