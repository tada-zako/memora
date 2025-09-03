import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 30000, // 增加超时时间到30秒，因为AI查询可能需要更长时间
  headers: {
    'Content-Type': 'application/json'
  }
})

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
      console.log('API请求携带token:', token.substring(0, 20) + '...')
    } else {
      console.log('API请求无token')
    }
    console.log('请求URL:', config.baseURL + config.url)
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

api.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    console.log('API响应错误:', {
      status: error.response?.status,
      statusText: error.response?.statusText,
      url: error.config?.url,
      method: error.config?.method,
      data: error.response?.data,
      timeout: error.code === 'ECONNABORTED'
    })
    
    if (error.response?.status === 401 || error.response?.status === 403) {
      console.log('认证失败，清除本地存储')
      localStorage.removeItem('access_token')
      localStorage.removeItem('user_info')
    }
    
    // 为超时错误提供更友好的消息
    if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
      error.customMessage = '请求超时，请检查网络连接或稍后重试'
    }
    
    return Promise.reject(error)
  }
)

export default api
