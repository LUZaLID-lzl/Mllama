import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
  timeout: 300000,
  headers: {
    'Content-Type': 'application/json'
  }
})

export const chatService = {
  // 检查服务器状态
  async checkServerStatus() {
    try {
      console.log('检查服务器状态...')
      const response = await api.get('/status')
      console.log('服务器状态:', response.data)
      return response.data
    } catch (error) {
      console.error('服务器状态检查失败:', error)
      throw error
    }
  },

  // 发送消息并获取回复
  async sendMessage(message) {
    try {
      console.log('发送请求:', {
        url: '/knowledge/query',
        data: { question: message }
      })

      const response = await api.post('/knowledge/query', {
        question: message
      })

      console.log('API响应:', {
        status: response.status,
        headers: response.headers,
        data: response.data
      })

      return response.data
    } catch (error) {
      console.error('API错误详情:', {
        message: error.message,
        status: error?.response?.status,
        data: error?.response?.data,
        config: {
          url: error?.config?.url,
          method: error?.config?.method,
          headers: error?.config?.headers,
          data: error?.config?.data
        }
      })

      if (error.response) {
        throw new Error(`服务器错误 (${error.response.status}): ${error.response.data?.message || '未知错误'}`)
      } else if (error.request) {
        throw new Error('无法连接到服务器，请检查网络连接')
      } else {
        throw new Error(`请求错误: ${error.message}`)
      }
    }
  },

  // 同步数据
  async syncData() {
    try {
      console.log('发送同步请求...')
      const response = await api.post('/data/process')
      console.log('同步响应:', response.data)
      return response.data
    } catch (error) {
      console.error('同步请求错误:', {
        message: error.message,
        status: error?.response?.status,
        data: error?.response?.data,
        config: {
          url: error?.config?.url,
          method: error?.config?.method,
          headers: error?.config?.headers,
          data: error?.config?.data
        }
      })

      if (error.response) {
        throw new Error(`服务器错误 (${error.response.status}): ${error.response.data?.message || '未知错误'}`)
      } else if (error.request) {
        throw new Error('无法连接到服务器，请检查网络连接')
      } else {
        throw new Error(`请求错误: ${error.message}`)
      }
    }
  }
}