import axios from 'axios'

const api = axios.create({
  baseURL: 'https://memora.soulter.top',
  timeout: 10000,
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
      data: error.response?.data
    })
    
    if (error.response?.status === 401 || error.response?.status === 403) {
      console.log('认证失败，清除本地存储')
      localStorage.removeItem('access_token')
      localStorage.removeItem('user_info')
    }
    return Promise.reject(error)
  }
)

export default api
