import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:3000/api', // 替换为实际的后端API地址
  timeout: 5000
})

// 请求拦截器
api.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  response => response.data,
  error => {
    ElMessage.error(error.response?.data?.message || '服务器错误')
    return Promise.reject(error)
  }
)

export default api 