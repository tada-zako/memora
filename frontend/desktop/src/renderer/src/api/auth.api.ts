import api from './api'
import type { ApiResponse, LoginCredentials, RegisterData, UserProfile, Token } from '@/types'

// 用户注册
export const registerApi = async (userData: RegisterData) => {
  const response: ApiResponse<UserProfile> = await api.post('/api/v1/auth/register', userData)
  return response
}

// 用户登录
export const loginApi = async (credentials: LoginCredentials) => {
  const response: ApiResponse<Token> = await api.post('/api/v1/auth/login', credentials)
  return response
}

// 获取用户信息
export const getUserProfileApi = async () => {
  const response: ApiResponse<UserProfile> = await api.get('/api/v1/auth/profile')
  return response
}

// 更新用户信息
export const updateUserProfileApi = async (userData: Partial<UserProfile>) => {
  const response: ApiResponse<UserProfile> = await api.put('/api/v1/auth/profile', userData)
  return response
}
