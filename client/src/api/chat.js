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

  // 停止生成
  async stopGeneration() {
    try {
      console.log('发送停止生成请求...')
      const response = await api.post('/knowledge/stop')
      console.log('停止生成响应:', response.data)
      return response.data
    } catch (error) {
      console.error('停止生成请求错误:', {
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
  },

  // 流式请求
  async streamMessage(message, callbacks) {
    try {
      console.log('发送流式请求:', {
        url: '/knowledge/query',
        data: { question: message, stream: true }
      })

      const response = await fetch('http://localhost:8000/api/v1/knowledge/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question: message,
          stream: true
        })
      })

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { value, done } = await reader.read()
        if (done) break

        // 解码新的数据块
        const chunk = decoder.decode(value, { stream: true })
        buffer += chunk

        // 处理缓冲区中的完整行
        while (true) {
          const newlineIndex = buffer.indexOf('\n')
          if (newlineIndex === -1) break

          const line = buffer.slice(0, newlineIndex)
          buffer = buffer.slice(newlineIndex + 1)

          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(5))
              console.log('收到数据:', data) // 添加日志
              callbacks?.[data.type]?.(data.content, data.index)
            } catch (e) {
              console.error('解析数据失败:', e, line)
            }
          }
        }
      }

      // 处理最后可能剩余的数据
      if (buffer.length > 0 && buffer.startsWith('data: ')) {
        try {
          const data = JSON.parse(buffer.slice(5))
          console.log('收到最后的数据:', data) // 添加日志
          callbacks?.[data.type]?.(data.content, data.index)
        } catch (e) {
          console.error('解析最后数据失败:', e, buffer)
        }
      }
    } catch (error) {
      console.error('流式请求错误:', error)
      throw error
    }
  },

  // 获取默认问题
  async getDefaultQuestions() {
    try {
      console.log('获取默认问题...')
      const response = await fetch('http://localhost:8000/api/v1/knowledge/default-questions', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        }
      })
      
      const data = await response.json()
      console.log('获取到的默认问题:', data)
      return data
    } catch (error) {
      console.error('获取默认问题失败:', error)
      throw error
    }
  }
}