<template>
  <div class="chat-container">
    <!-- 侧边栏 -->
    <div class="sidebar" :class="{ 'sidebar-collapsed': !sidebarOpen }">
      <div class="sidebar-header">
        <el-button text class="new-chat-btn" @click="createNewChat">
          <el-icon><ChatLineRound /></el-icon>
          <span>新对话</span>
        </el-button>
        <el-button text>
          <el-icon><Plus /></el-icon>
        </el-button>
      </div>

      <div class="search-container">
        <el-input
          v-model="searchQuery"
          placeholder="搜索"
          :prefix-icon="Search"
          size="small"
          class="search-input"
        />
      </div>

      <div class="workspace-section">
        <h3>聊天记录</h3>
        <div class="chat-list">
          <div v-for="chat in chatList" 
            :key="chat.id" 
            class="chat-item"
            :class="{ active: currentChat?.id === chat.id }"
          >
            <div class="chat-item-main" @click="selectChat(chat)">
              <el-icon><ChatLineRound /></el-icon>
              <div class="chat-item-content">
                <span class="chat-title">{{ chat.title }}</span>
                <span class="chat-date">{{ chat.date }}</span>
              </div>
            </div>
            <el-button 
              class="delete-btn" 
              @click.stop="deleteChat(chat)"
              text
            >
              <el-icon><Delete /></el-icon>
            </el-button>
          </div>
        </div>
      </div>

      <div class="user-profile">
        <el-avatar class="user-avatar" :src="'/user.png'"></el-avatar>
        <span class="username">{{ username }}</span>
      </div>
    </div>

    <!-- 主内容区 -->
    <div class="main-content">
      <div class="main-header">
        <div class="header-left">
          <el-button text @click="toggleSidebar">
            <el-icon><Menu /></el-icon>
          </el-button>
          <h2>{{ modelName }}</h2>
        </div>
        <div class="header-right">
          <el-button 
            text 
            class="sync-btn"
            :loading="syncing"
            @click="handleSync"
          >
            <el-icon><RefreshRight /></el-icon>
          </el-button>
          <el-button text>
            <el-icon><Setting /></el-icon>
          </el-button>
        </div>
      </div>

      <div class="chat-area">
        <template v-if="!currentChat">
          <div class="suggestions">
            <div class="welcome-header">
              <div class="welcome-icon">
                <img src="/src/assets/maidu_logo.png" alt="Maidu Logo" width="120" height="120" />
              </div>
              <div class="welcome-text">
                <h2>我是 <span class="brand-name">Mllama</span>，很高兴见到你！</h2>
                <h5 class="welcome-subtitle">我可以回答认证相关的问题，请把你的任务交给我吧~</h5>
              </div>
            </div>
            <div class="suggestion-grid">
              <el-card 
                v-for="item in suggestions" 
                :key="item.title"
                class="suggestion-card"
                @click="useExample(item)"
              >
                <h4>{{ item.title }}</h4>
                <p>{{ item.desc }}</p>
              </el-card>
            </div>
          </div>
          <div class="input-area">
            <div class="input-box">
              <el-input
                v-model="inputMessage"
                type="textarea"
                :rows="1"
                :autosize="{ minRows: 1, maxRows: 4 }"
                placeholder="给 Mllama 发送消息"
                @keydown.enter.exact.prevent="sendMessage"
                @keydown.enter.shift.exact.prevent="inputMessage += '\n'"
                resize="none"
                class="message-input"
              />
              
              <div class="input-footer">
                <div class="left-actions">
                  <el-button class="mode-btn">
                    <el-icon><Cpu /></el-icon>
                    深度思考 (R1)
                  </el-button>
                </div>
                <div class="right-actions">
                  <el-button class="action-btn">
                    <el-icon><Paperclip /></el-icon>
                  </el-button>
                  <el-button class="send-btn" @click="sendMessage" :disabled="!inputMessage.trim()">
                    <el-icon><Position /></el-icon>
                  </el-button>
                </div>
              </div>
            </div>
          </div>
        </template>
        <template v-else>
          <div class="messages">
            <div v-for="(message, index) in currentChat.messages" 
              :key="index"
              class="message"
              :class="message.role"
            >
              <div class="message-avatar">
                <el-avatar 
                  :size="36" 
                  :class="message.role === 'assistant' ? 'ai-avatar' : 'user-avatar'"
                >
                  {{ message.role === 'assistant' ? 'AI' : 'U' }}
                </el-avatar>
              </div>
              <div class="message-content">
                <div class="message-text">{{ message.content }}</div>
              </div>
            </div>
          </div>
          <div class="input-area" :class="{ 'input-fixed': currentChat }">
            <div class="input-box">
              <el-input
                v-model="inputMessage"
                type="textarea"
                :rows="1"
                :autosize="{ minRows: 1, maxRows: 4 }"
                placeholder="给 Mllama 发送消息"
                @keydown.enter.exact.prevent="sendMessage"
                @keydown.enter.shift.exact.prevent="inputMessage += '\n'"
                resize="none"
                class="message-input"
              />
              
              <div class="input-footer">
                <div class="left-actions">
                  <el-button class="mode-btn">
                    <el-icon><Cpu /></el-icon>
                    深度思考 (R1)
                  </el-button>
                </div>
                <div class="right-actions">
                  <el-button class="action-btn">
                    <el-icon><Paperclip /></el-icon>
                  </el-button>
                  <el-button class="send-btn" @click="sendMessage" :disabled="!inputMessage.trim()">
                    <el-icon><Position /></el-icon>
                  </el-button>
                </div>
              </div>
            </div>
          </div>
        </template>
      </div>
    </div>

    <!-- 添加服务器错误提示 -->
    <el-alert
      v-if="serverError"
      :title="serverError"
      type="error"
      :closable="false"
      show-icon
      class="server-error"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import {
  Menu,
  Plus,
  Search,
  Setting,
  ChatLineRound,
  Microphone,
  Headset,
  Cpu,
  Link,
  Paperclip,
  Position,
  Document,
  EditPen,
  StarFilled,
  CircleCloseFilled,
  Delete,
  RefreshRight
} from '@element-plus/icons-vue'
import Cookies from 'js-cookie'
import { useRouter } from 'vue-router'
import { chatService } from '../api/chat'
import { ElMessage, ElMessageBox } from 'element-plus'

const username = ref(Cookies.get('username') || 'Guest')
const sidebarOpen = ref(true)
const searchQuery = ref('')
const inputMessage = ref('')
const currentChat = ref(null)
const chatList = ref([])
const serverStatus = ref(null)
const serverError = ref(null)
const modelName = ref('No Model')
const syncing = ref(false)

const router = useRouter()
const checkAuth = () => {
  const savedUsername = Cookies.get('username')
  if (!savedUsername) {
    localStorage.removeItem('chatList')
    localStorage.removeItem('currentChatId')
    router.push('/login')
  }
}

// 检查服务器状态
const checkServer = async () => {
  try {
    serverError.value = null
    const status = await chatService.checkServerStatus()
    serverStatus.value = status
    console.log('服务器正常运行:', status)
    
    // 更新模型名称
    if (status?.model_info?.llm_model) {
      modelName.value = status.model_info.llm_model
    }
  } catch (error) {
    serverError.value = '服务器连接失败，请确保服务器已启动'
    console.error('服务器检查失败:', error)
  }
}

// 从 localStorage 加载状态
const loadState = () => {
  try {
    const savedChatList = localStorage.getItem('chatList')
    const savedCurrentChatId = localStorage.getItem('currentChatId')
    
    if (savedChatList) {
      chatList.value = JSON.parse(savedChatList)
      console.log('加载聊天记录:', chatList.value)
    }
    
    if (savedCurrentChatId) {
      const chat = chatList.value.find(c => c.id.toString() === savedCurrentChatId)
      if (chat) {
        currentChat.value = chat
        console.log('加载当前对话:', chat)
      }
    }
  } catch (error) {
    console.error('加载聊天记录失败:', error)
  }
}

// 保存状态到 localStorage
const saveState = () => {
  try {
    localStorage.setItem('chatList', JSON.stringify(chatList.value))
    localStorage.setItem('currentChatId', currentChat.value?.id?.toString() || '')
  } catch (error) {
    console.error('保存聊天记录失败:', error)
  }
}

// 监听状态变化
watch([chatList, currentChat], () => {
  saveState()
}, { deep: true })

onMounted(async () => {
  loadState()
  checkAuth()
  await checkServer()
})

const suggestions = [
  {
    title: 'Give me ideas',
    desc: 'for what to do with my kids\' art'
  },
  {
    title: 'Help me study',
    desc: 'vocabulary for a college entrance exam'
  },
  {
    title: 'Show me a code snippet',
    desc: 'of a website\'s sticky header'
  }
]

const toggleSidebar = () => {
  sidebarOpen.value = !sidebarOpen.value
}

const useExample = (item) => {
  inputMessage.value = item.title + ': ' + item.desc
}

const createNewChat = () => {
  currentChat.value = null
  inputMessage.value = ''
  saveState()
}

const selectChat = (chat) => {
  currentChat.value = chat
  saveState()
}

const sendMessage = async () => {
  if (!inputMessage.value.trim()) return
  
  // 检查服务器状态
  if (serverError.value) {
    ElMessage.error(serverError.value)
    return
  }

  if (!currentChat.value) {
    const newChat = {
      id: Date.now(),
      title: inputMessage.value.slice(0, 20) + (inputMessage.value.length > 20 ? '...' : ''),
      date: new Date().toLocaleString(),
      messages: []
    }
    chatList.value.unshift(newChat)
    currentChat.value = newChat
    saveState()
  }

  // 添加用户消息
  const userMessage = {
    role: 'user',
    content: inputMessage.value,
    time: new Date().toLocaleString()
  }
  currentChat.value.messages.push(userMessage)
  
  // 清空输入框
  const messageToSend = inputMessage.value
  inputMessage.value = ''

  try {
    const loadingMessage = {
      role: 'assistant',
      content: '正在思考...',
      time: new Date().toLocaleString(),
      loading: true
    }
    currentChat.value.messages.push(loadingMessage)

    console.log('开始请求API...')
    const response = await chatService.sendMessage(messageToSend)
    console.log('API返回结果:', response)
    
    currentChat.value.messages.pop()
    
    // 添加更详细的响应处理
    if (response.answer) {
      console.log('使用 answer 字段')
      currentChat.value.messages.push({
        role: 'assistant',
        content: response.answer,
        time: new Date().toLocaleString()
      })
    } else if (response.data) {
      console.log('使用 data 字段')
      currentChat.value.messages.push({
        role: 'assistant',
        content: response.data,
        time: new Date().toLocaleString()
      })
    } else {
      console.warn('响应中没有找到有效的回复内容:', response)
      currentChat.value.messages.push({
        role: 'assistant',
        content: '抱歉，返回的数据格式不正确',
        time: new Date().toLocaleString()
      })
    }

    // 每次消息更新后保存状态
    saveState()
  } catch (error) {
    console.error('发送消息错误:', error)
    currentChat.value.messages.pop()
    
    currentChat.value.messages.push({
      role: 'assistant',
      content: error.message,
      time: new Date().toLocaleString(),
      error: true
    })

    saveState()
  }
}

const logout = () => {
  Cookies.remove('username')
  localStorage.removeItem('chatList')
  localStorage.removeItem('currentChatId')
  router.push('/login')
}

// 添加删除聊天记录的函数
const deleteChat = (chat) => {
  ElMessageBox.confirm(
    '确定要删除这条聊天记录吗？',
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    const index = chatList.value.findIndex(item => item.id === chat.id)
    if (index > -1) {
      chatList.value.splice(index, 1)
      if (currentChat.value?.id === chat.id) {
        currentChat.value = null
      }
      ElMessage.success('删除成功')
    }
  }).catch(() => {
    // 取消删除
  })
}

// 添加同步函数
const handleSync = async () => {
  if (syncing.value) return
  
  try {
    syncing.value = true
    console.log('开始同步...')
    
    const response = await chatService.syncData()
    console.log('同步完成:', response)
    
    ElMessage.success('同步成功')
  } catch (error) {
    console.error('同步失败:', error)
    ElMessage.error('同步失败: ' + error.message)
  } finally {
    syncing.value = false
  }
}
</script>

<style>
/* 全局字体设置 */
:root {
  --font-sans: -apple-system, 'PingFang SC', 'Microsoft YaHei', 'Helvetica Neue', Helvetica, Arial, sans-serif;
  --font-mono: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace;
}

/* 添加到 scoped style 中 */
.chat-container {
  font-family: var(--font-sans);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  letter-spacing: -0.025em;
}

/* 标题字体优化 */
.main-header h2,
.suggestions h3 {
  font-family: var(--font-sans);
  font-weight: 600;
  letter-spacing: -0.02em;
}

/* 消息文本优化 */
.message-text {
  font-family: var(--font-sans);
  line-height: 1.6;
  letter-spacing: -0.01em;
}

/* 输入框字体优化 */
.message-input :deep(.el-textarea__inner) {
  font-family: var(--font-sans);
  letter-spacing: -0.01em;
  font-size: 15px;
}

/* 按钮文本优化 */
.mode-btn {
  font-family: var(--font-sans);
  font-weight: 500;
  letter-spacing: -0.01em;
}

/* 建议卡片文本优化 */
.suggestion-card h4 {
  font-family: var(--font-sans);
  font-weight: 600;
  letter-spacing: -0.01em;
}

.suggestion-card p {
  font-family: var(--font-sans);
  letter-spacing: -0.01em;
  line-height: 1.5;
}

/* 用户名文本优化 */
.username {
  font-family: var(--font-sans);
  font-weight: 500;
  letter-spacing: -0.01em;
}

/* 工作空间标题优化 */
.workspace-section h3 {
  font-family: var(--font-sans);
  font-weight: 600;
  letter-spacing: -0.01em;
}

/* 搜索框字体优化 */
.search-input :deep(.el-input__inner) {
  font-family: var(--font-sans);
  letter-spacing: -0.01em;
}

/* 按钮文本通用优化 */
:deep(.el-button) {
  font-family: var(--font-sans);
  font-weight: 500;
  letter-spacing: -0.01em;
}
</style>

<style scoped>
.chat-container {
  display: flex;
  height: 100vh;
  background-color: var(--el-bg-color);
}

.sidebar {
  width: 300px;
  border-right: 1px solid rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  background-color: #ffffff;
  box-shadow: 0 0 15px rgba(0, 0, 0, 0.05);
}

.sidebar-collapsed {
  width: 0;
  overflow: hidden;
}

.sidebar-header {
  height: 64px;
  display: flex;
  align-items: center;
  padding: 0 16px;
  gap: 8px;
}

.new-chat-btn {
  width: 100%;
  justify-content: flex-start;
  gap: 8px;
  background-color: #f3f4f6;
  border-radius: 8px;
  padding: 8px 12px;
  transition: all 0.3s ease;
}

.new-chat-btn:hover {
  background-color: #e5e7eb;
  transform: translateY(-1px);
}

.search-container {
  padding: 8px 16px;
}

.search-input {
  background-color: var(--el-fill-color-lighter);
}

.search-input :deep(.el-input__wrapper) {
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.search-input :deep(.el-input__wrapper:hover) {
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.search-input :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.2);
}

.workspace-section {
  padding: 16px;
  flex: 1;
}

.workspace-section h3 {
  margin-bottom: 12px;
  font-size: 16px;
  font-weight: 600;
}

.user-profile {
  padding: 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  border-top: 1px solid rgba(0, 0, 0, 0.05);
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 6px !important;
  background-color: transparent;
}

.username {
  font-size: 14px;
  color: #374151;
  font-weight: 500;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  position: relative;
}

.main-header {
  height: 64px;
  border-bottom: none;
  box-shadow: none;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
  background-color: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-left h2 {
  font-size: 20px;
  font-weight: 600;
  margin: 0;
}

.chat-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 24px;
  max-width: 1000px;
  margin: 0 auto;
  width: 100%;
  height: calc(100vh - 64px);
  position: relative;
  overflow: hidden;
}

.suggestions {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 0 20px;
  width: 100%;
  overflow-y: auto;
}

.suggestions h3 {
  font-size: 18px;
  margin-bottom: 16px;
}

.suggestion-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 16px;
  max-width: 800px;
  margin: 0 auto;
  margin-top: 0px;
}

.suggestion-card {
  border: none;
  border-radius: 12px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  overflow: hidden;
}

.suggestion-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
}

.suggestion-card h4 {
  color: #1f2937;
  font-weight: 600;
}

.suggestion-card p {
  color: #6b7280;
}

.messages {
  flex: 1;
  overflow-y: auto;
  padding: 0 0 120px 0;
  margin-bottom: 0;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.message {
  display: flex;
  gap: 16px;
  padding: 24px 24px;
  transition: all 0.3s ease;
}

.message:hover {
  background-color: transparent;
}

.message-avatar {
  flex-shrink: 0;
  margin-top: 8px;
  width: 36px;
  height: 36px;
  padding: 4px;
  background-color: #f3f4f6;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.message-avatar .el-avatar {
  border-radius: 6px;
  background-color: transparent;
  width: 28px;
  height: 28px;
}

.message-content {
  flex: 1;
  min-width: 0;
  margin-top: 0;
}

.message-text {
  font-size: 15px;
  line-height: 1.6;
  color: #374151;
  white-space: pre-wrap;
  word-break: break-word;
}

.message.assistant {
  background-color: transparent;
}

.message.assistant .message-text {
  background-color: #f3f4f6;
  padding: 12px 16px;
  border-radius: 12px;
  border-top-left-radius: 4px;
  max-width: 80%;
}

.message.assistant .message-avatar {
  background-color: #f3f4f6;
}

.message.user {
  flex-direction: row-reverse;
  background-color: transparent;
}

.message.user .message-content {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.message.user .message-text {
  background-color: #3b82f6;
  color: white;
  padding: 12px 16px;
  border-radius: 12px;
  border-top-right-radius: 4px;
  max-width: 80%;
}

.message.user .message-avatar {
  background-color: rgba(59, 130, 246, 0.1);
}

/* 添加动画效果 */
.message {
  animation: slideInLeft 0.3s ease;
}

@keyframes slideInLeft {
  from {
    opacity: 0;
    transform: translateX(-10px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.input-area {
  padding: 20px;
  background-color: transparent;
  z-index: 10;
}

.input-area.input-fixed {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background-color: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(8px);
  border-top: none;
  padding: 16px 20px;
}

.input-box {
  max-width: 800px;
  margin: 0 auto;
  background-color: #f3f4f6;
  border-radius: 24px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  backdrop-filter: blur(8px);
}

.message-input :deep(.el-textarea__inner) {
  border: none;
  padding: 8px 0;
  font-size: 14px;
  color: #374151;
  background: transparent;
  box-shadow: none;
  min-height: 24px !important;
}

.message-input :deep(.el-textarea__inner::placeholder) {
  color: #9ca3af;
}

.input-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 4px;
}

.left-actions,
.right-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.mode-btn {
  height: 32px;
  padding: 0 12px;
  border: none;
  border-radius: 6px;
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #3b82f6;
  background-color: rgba(59, 130, 246, 0.1);
  transition: all 0.2s ease;
}

.mode-btn:hover {
  background-color: rgba(59, 130, 246, 0.2);
}

.mode-btn .el-icon {
  color: #3b82f6;
}

.action-btn {
  width: 32px;
  height: 32px;
  padding: 0;
  border: none;
  border-radius: 6px;
  color: #6b7280;
  background-color: transparent;
  transition: all 0.2s ease;
}

.action-btn:hover {
  background-color: rgba(0, 0, 0, 0.05);
  color: #374151;
}

.send-btn {
  width: 32px;
  height: 32px;
  padding: 0;
  border: none;
  border-radius: 6px;
  color: white;
  background-color: #3b82f6;
  transition: all 0.2s ease;
}

.send-btn:hover {
  background-color: #2563eb;
}

.send-btn:disabled {
  background-color: #e5e7eb;
  color: #9ca3af;
  cursor: not-allowed;
}

/* 图标大小统一 */
.el-icon {
  font-size: 16px;
}

/* 加载动画 */
@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.5; }
  100% { opacity: 1; }
}

.loading {
  animation: pulse 1.5s infinite;
}

/* 滚动条美化 */
.messages::-webkit-scrollbar,
.suggestions::-webkit-scrollbar {
  width: 6px;
}

.messages::-webkit-scrollbar-track,
.suggestions::-webkit-scrollbar-track {
  background: transparent;
}

.messages::-webkit-scrollbar-thumb,
.suggestions::-webkit-scrollbar-thumb {
  background-color: #d1d5db;
  border-radius: 3px;
}

.messages::-webkit-scrollbar-thumb:hover,
.suggestions::-webkit-scrollbar-thumb:hover {
  background-color: #9ca3af;
}

/* 响应式设计优化 */
@media (max-width: 1200px) {
  .chat-area {
    max-width: 900px;
  }
}

@media (max-width: 768px) {
  .chat-area {
    padding: 16px;
  }
  
  .messages {
    padding-bottom: 100px;
  }
  
  .input-area.input-fixed {
    padding: 12px;
  }
}

.chat-list {
  margin-top: 12px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.chat-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.chat-item-main {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
  min-width: 0;
}

.delete-btn {
  opacity: 0;
  color: #9ca3af;
  transition: all 0.2s ease;
}

.delete-btn:hover {
  color: #ef4444;
}

.chat-item:hover .delete-btn {
  opacity: 1;
}

.chat-item.active .delete-btn {
  opacity: 1;
}

.chat-item-content {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.chat-title {
  font-size: 14px;
  color: #374151;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.chat-date {
  font-size: 12px;
  color: #6b7280;
}

/* 移除不需要的样式 */
.message-header,
.message-actions,
.action-icon,
.message.user .message-header,
.message.user .message-actions,
.message.user .action-icon,
.message.user .message-title,
.message.assistant .message-title {
  display: none;
}

/* 加载状态的消息样式 */
.message-text.loading {
  opacity: 0.7;
  animation: pulse 1.5s infinite;
}

/* 错误消息样式 */
.message-text.error {
  color: #dc2626;
  background-color: #fee2e2;
}

@keyframes pulse {
  0% { opacity: 0.7; }
  50% { opacity: 0.4; }
  100% { opacity: 0.7; }
}

.server-error {
  position: fixed;
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  z-index: 1000;
  width: auto;
  min-width: 300px;
  margin-top: 16px;
}

.ai-avatar {
  background-color: #3b82f6 !important;
  color: white !important;
}

.user-avatar {
  background-color: #f3f4f6 !important;
  color: #374151 !important;
}

.welcome-header {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 32px;
}

.welcome-icon {
  animation: fadeIn 0.5s ease;
}

.welcome-icon img {
  width: 100px;
  height: 100px;
  object-fit: contain;
}

.welcome-text {
  text-align: left;
}

.welcome-text h2 {
  margin: 0;
  font-size: 24px;
  line-height: 1.4;
  display: flex;
  align-items: center;
  gap: 4px;
  flex-wrap: wrap;
}

.welcome-subtitle {
  font-weight: normal;
  color: #6b7280;
  margin: 8px 0 0 0;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.brand-name {
  font-family: 'Nunito', var(--font-sans);
  font-weight: 800;
  color: #1a1a1a;
  padding: 0 2px;
  letter-spacing: 0.5px;
  background: none;
  -webkit-background-clip: initial;
  -webkit-text-fill-color: initial;
}

.sync-btn {
  position: relative;
}

.sync-btn :deep(.el-icon) {
  transition: transform 0.3s ease;
}

.sync-btn:hover :deep(.el-icon) {
  transform: rotate(180deg);
}

.sync-btn.is-loading:hover :deep(.el-icon) {
  transform: none;
}
</style> 