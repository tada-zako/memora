// 调试工具 - 用于诊断认证问题
import { isAuthenticated, getLocalUserInfo, refreshAuthStatus } from './auth'
import { getCategories } from './category'

// 调试认证状态
export const debugAuthStatus = () => {
  console.log('=== 认证状态调试 ===')
  
  const token = localStorage.getItem('access_token')
  const userInfo = localStorage.getItem('user_info')
  
  console.log('1. localStorage中的token:', token ? 'YES' : 'NO')
  if (token) {
    console.log('   Token预览:', token.substring(0, 50) + '...')
    console.log('   Token长度:', token.length)
  }
  
  console.log('2. localStorage中的用户信息:', userInfo ? 'YES' : 'NO')
  if (userInfo) {
    try {
      const parsed = JSON.parse(userInfo)
      console.log('   用户信息:', parsed)
    } catch (e) {
      console.log('   用户信息解析错误:', e.message)
    }
  }
  
  console.log('3. isAuthenticated()返回:', isAuthenticated())
  
  console.log('4. 所有localStorage项:')
  for (let i = 0; i < localStorage.length; i++) {
    const key = localStorage.key(i)
    console.log(`   ${key}:`, localStorage.getItem(key)?.substring(0, 100))
  }
}

// 测试API调用
export const testApiCall = async () => {
  console.log('=== 测试API调用 ===')
  
  try {
    console.log('正在调用getCategories()...')
    const result = await getCategories()
    console.log('API调用成功:', result)
    return true
  } catch (error) {
    console.log('API调用失败:')
    console.log('  错误对象:', error)
    console.log('  错误响应:', error.response)
    console.log('  错误状态码:', error.response?.status)
    console.log('  错误数据:', error.response?.data)
    return false
  }
}

// 完整调试
export const fullDebug = async () => {
  console.log('========== 完整调试开始 ==========')
  debugAuthStatus()
  console.log('')
  await testApiCall()
  console.log('========== 完整调试结束 ==========')
}

// 清理认证状态
export const clearAuth = () => {
  console.log('清理认证状态...')
  localStorage.removeItem('access_token')
  localStorage.removeItem('user_info')
  console.log('认证状态已清理')
}

// 将调试函数挂载到全局对象
if (typeof window !== 'undefined') {
  window.debugAuth = {
    status: debugAuthStatus,
    test: testApiCall,
    full: fullDebug,
    clear: clearAuth
  }
  console.log('调试工具已挂载到 window.debugAuth')
  console.log('可用命令:')
  console.log('  window.debugAuth.status() - 检查认证状态')
  console.log('  window.debugAuth.test() - 测试API调用')
  console.log('  window.debugAuth.full() - 完整调试')
  console.log('  window.debugAuth.clear() - 清理认证状态')
} 