<template>
  <div class="chat-area">
    <template v-if="!currentChat">
      <!-- 欢迎界面 -->
      <div class="suggestions fade-in">
        <div class="welcome-header">
          <div class="welcome-icon">
            <img src="/src/assets/ai_user.png" alt="Maidu Logo" width="120" height="120" />
          </div>
          <div class="welcome-text">
            <h2>我是 <span class="brand-name">Mllama</span>，很高兴见到你！</h2>
            <h5 class="welcome-subtitle">我可以回答认证相关的问题，请把你的任务交给我吧~</h5>
          </div>
        </div>
        <div class="suggestion-grid">
          <el-card 
            v-for="item in suggestions" 
            :key="item.desc"
            class="suggestion-card"
            @click="useExample(item)"
          >
            <h4>{{ item.title }}</h4>
            <p>{{ item.desc }}</p>
          </el-card>
        </div>
      </div>
    </template>
    <template v-else>
      <!-- 聊天消息列表 -->
      <div class="messages">
        <TransitionGroup name="message">
          <div v-for="(message, index) in currentChat.messages" 
            :key="message.time"
            class="message"
            :class="message.role"
          >
            <div class="message-avatar">
              <el-avatar 
                :size="36" 
                :class="message.role === 'assistant' ? 'ai-avatar' : 'user-avatar'"
                :src="message.role === 'assistant' ? '/src/assets/ai_user.png' : ''"
              >
                {{ message.role === 'assistant' ? '' : 'U' }}
              </el-avatar>
            </div>
            <div class="message-content">
              <div v-if="message.loading" class="message-loading">
                <el-skeleton animated>
                  <!-- ... 骨架屏代码 ... -->
                </el-skeleton>
              </div>
              <div v-else class="message-text" :class="{ 'thinking': message.role === 'assistant' }">
                <!-- 检索状态 -->
                <div v-if="message.searching" class="status-block searching">
                  <div class="status-header">
                    <el-icon><Search /></el-icon>
                    正在检索相关文档...
                  </div>
                </div>

                <!-- 来源信息 -->
                <div v-if="message.sources && message.sources.length > 0" class="sources-container">
                  <div class="sources-header">
                    <el-icon><Document /></el-icon>
                    找到以下相关文档
                  </div>
                  <div class="sources-list">
                    <div v-for="(source, index) in message.sources" 
                      :key="index" 
                      class="source-item"
                      :title="source"
                    >
                      <span class="source-index">{{ index + 1 }}</span>
                      {{ source }}
                    </div>
                  </div>
                </div>
              

                <!-- 最终答案 -->
                <div class="final-answer">
                  <div v-if="message.streaming" class="streaming-text">
                    <template v-if="message.content.includes('<think>')">
                      <span class="thinking-text">{{ extractThinkingContent(message.content) }}</span>
                      {{ extractFinalAnswer(message.content) }}
                    </template>
                    <template v-else>
                      {{ message.content }}
                    </template>
                    <span class="cursor"></span>
                  </div>
                  <div v-else>
                    <template v-if="message.content.includes('<think>')">
                      <span class="thinking-text">{{ extractThinkingContent(message.content) }}</span>
                      {{ extractFinalAnswer(message.content) }}
                    </template>
                    <template v-else>
                      {{ message.content }}
                    </template>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </TransitionGroup>
      </div>
    </template>

    <!-- 输入区域 -->
    <Transition name="slide-up">
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
              <el-button 
                class="send-btn" 
                @click="isGenerating ? stopGeneration() : sendMessage()" 
                :disabled="!inputMessage.trim() && !isGenerating"
              >
                <el-icon>
                  <component :is="isGenerating ? 'Close' : 'Position'" />
                </el-icon>
              </el-button>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted } from 'vue'
import { chatService } from '../api/chat'
import { ElMessage } from 'element-plus'
import {
  Search,
  Document,
  Loading,
  Cpu,
  Paperclip,
  Position,
  Close
} from '@element-plus/icons-vue'

// Props
const props = defineProps({
  currentChat: {
    type: Object,
    default: null
  },
  serverError: {
    type: String,
    default: null
  }
})

// Emits
const emit = defineEmits(['update:currentChat', 'create-chat'])

// 响应式变量
const inputMessage = ref('')
const isGenerating = ref(false)
const suggestions = ref([])

// 获取默认问题
const loadDefaultQuestions = async () => {
  try {
    const questions = await chatService.getDefaultQuestions()
    console.log('服务器返回的问题数据:', questions)
    
    // 确保 questions 是数组
    if (!Array.isArray(questions)) {
      console.error('服务器返回的数据不是数组:', questions)
      suggestions.value = []
      return
    }

    suggestions.value = questions.map(item => ({
      title: item.title,  // 只显示标题
      desc: item.question
    }))
  } catch (error) {
    console.error('加载默认问题失败:', error)
    ElMessage.error('加载默认问题失败')
    suggestions.value = []
  }
}

// 在组件挂载时获取默认问题
onMounted(() => {
  loadDefaultQuestions()
})

// 方法
const useExample = (item) => {
  inputMessage.value = item.desc
}

const extractThinkingContent = (content) => {
  const match = content.match(/<think>(.*?)<\/think>/s)
  return match ? match[1].trim() : ''
}

const extractFinalAnswer = (content) => {
  return content.replace(/<think>.*?<\/think>/s, '').trim()
}

// 发送消息
const sendMessage = async () => {
  if (!inputMessage.value.trim() && !isGenerating.value) return
  
  if (isGenerating.value) {
    await stopGeneration()
    return
  }

  if (props.serverError) {
    ElMessage.error(props.serverError)
    return
  }

  // 创建新对话
  if (!props.currentChat) {
    const newChat = {
      id: Date.now(),
      title: inputMessage.value.slice(0, 20) + (inputMessage.value.length > 20 ? '...' : ''),
      date: new Date().toLocaleString(),
      messages: []
    }
    emit('create-chat', newChat)
    // 等待父组件更新 currentChat
    await nextTick()
  }

  // 确保 currentChat 存在
  if (!props.currentChat) {
    ElMessage.error('创建对话失败')
    return
  }

  const userMessage = {
    role: 'user',
    content: inputMessage.value,
    time: new Date().toLocaleString()
  }
  props.currentChat.messages.push(userMessage)
  
  const messageToSend = inputMessage.value
  inputMessage.value = ''

  try {
    isGenerating.value = true
    let currentAnswer = ''
    let currentThinking = ''

    const assistantMessage = {
      role: 'assistant',
      content: '',
      time: new Date().toLocaleString(),
      streaming: true,
      sources: [],
      searching: true
    }
    props.currentChat.messages.push(assistantMessage)

    await chatService.streamMessage(messageToSend, {
      searching: () => {
        assistantMessage.searching = true
        assistantMessage.sources = []
        // 强制更新视图
        emit('update:currentChat', { ...props.currentChat })
      },
      source: (content, index) => {
        console.log('收到来源:', content)
        // 创建新数组以触发响应式更新
        assistantMessage.sources = [...assistantMessage.sources, content]
        
        if (index === 0) {
          assistantMessage.searching = false
        }
        // 每次收到新来源时都强制更新视图
        emit('update:currentChat', { ...props.currentChat })
      },
      thinking: (content) => {
        currentThinking = content
        assistantMessage.content = `<think>${content}</think>${currentAnswer}`
        // 强制更新视图
        emit('update:currentChat', { ...props.currentChat })
      },
      content: (content) => {
        currentAnswer += content
        assistantMessage.content = currentThinking ? 
          `<think>${currentThinking}</think>${currentAnswer}` : 
          currentAnswer
        // 强制更新视图
        emit('update:currentChat', { ...props.currentChat })
      },
      done: () => {
        assistantMessage.streaming = false
        isGenerating.value = false
      },
      stopped: () => {
        assistantMessage.streaming = false
        isGenerating.value = false
        assistantMessage.content += '\n[生成已停止]'
      },
      error: (content) => {
        assistantMessage.streaming = false
        isGenerating.value = false
        assistantMessage.error = true
        assistantMessage.content = content
      }
    })

    emit('update:currentChat', { ...props.currentChat })
  } catch (error) {
    console.error('发送消息错误:', error)
    props.currentChat.messages.push({
      role: 'assistant',
      content: '发送消息失败: ' + error.message,
      time: new Date().toLocaleString(),
      error: true
    })
    emit('update:currentChat', { ...props.currentChat })
  } finally {
    isGenerating.value = false
  }
}

// 停止生成
const stopGeneration = async () => {
  try {
    await chatService.stopGeneration()
    isGenerating.value = false
    
    if (props.currentChat?.messages?.length > 0) {
      const lastMessage = props.currentChat.messages[props.currentChat.messages.length - 1]
      if (lastMessage.loading) {
        props.currentChat.messages.pop()
      }
    }
    
    props.currentChat.messages.push({
      role: 'assistant',
      content: '生成已停止',
      time: new Date().toLocaleString(),
      error: true
    })
    
    emit('update:currentChat', { ...props.currentChat })
  } catch (error) {
    console.error('停止生成失败:', error)
    ElMessage.error('停止生成失败: ' + error.message)
  }
}
</script>

<style scoped>
.chat-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 24px;
  max-width: 1200px;
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

.brand-name {
  font-family: 'Nunito', var(--font-sans);
  font-weight: 800;
  color: #1a1a1a;
  padding: 0 2px;
  letter-spacing: 0.5px;
  margin-top: 5px;
}

.suggestion-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 16px;
  max-width: 800px;
  margin: 0 auto;
}

.suggestion-card {
  border: none;
  border-radius: 12px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  overflow: hidden;
  cursor: pointer;
  animation: cardFadeIn 0.5s ease-out backwards;
}

.suggestion-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
}

.suggestion-card h4 {
  margin: 0 0 8px 0;
  font-size: 15px;
  color: #3b82f6;
}

.suggestion-card p {
  margin: 0;
  font-size: 14px;
  color: #4b5563;
  line-height: 1.5;
}

.messages {
  flex: 1;
  overflow-y: auto;
  padding: 0 12px 120px 0;
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

.message-avatar {
  flex-shrink: 0;
  margin-top: 8px;
  width: 36px;
  height: 36px;
  padding: 2px;
  background-color: transparent;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.message-avatar :deep(.el-avatar) {
  width: 32px !important;
  height: 32px !important;
  border-radius: 50% !important;
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: transparent;
}

.ai-avatar {
  background-color: transparent !important;
}

.user-avatar {
  background-color: #f3f4f6 !important;
  color: #374151 !important;
}

.message-content {
  flex: 1;
  min-width: 0;
  margin-top: 0;
}

.message-text {
  font-size: 14px;
  line-height: 1.6;
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

.status-block {
  padding: 12px;
  border-radius: 8px;
  margin-bottom: 16px;
  font-size: 13px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.status-block.searching {
  background-color: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
  border: 1px solid rgba(59, 130, 246, 0.2);
}

.sources-container {
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}

.sources-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.source-item {
  font-family: var(--font-mono);
  font-size: 12px;
  color: #4b5563;
  padding: 8px 12px;
  background-color: rgba(243, 244, 246, 0.8);
  border-radius: 6px;
  line-height: 1.4;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: default;
}

.source-index {
  flex-shrink: 0;
  width: 16px;
  height: 16px;
  background-color: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 500;
}

.thinking-process {
  color: #6b7280;
  font-size: 13px;
  padding: 12px;
  background-color: rgba(243, 244, 246, 0.8);
  border-radius: 8px;
  margin-bottom: 16px;
  font-family: var(--font-mono);
  border: 1px solid rgba(156, 163, 175, 0.2);
}

.thinking-header {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #4b5563;
  font-size: 12px;
  margin-bottom: 8px;
  padding-bottom: 8px;
  border-bottom: 1px solid rgba(156, 163, 175, 0.2);
}

.streaming-text {
  position: relative;
  display: inline-block;
  animation: fadeIn 0.2s ease-out;
}

.cursor {
  display: inline-block;
  width: 2px;
  height: 1em;
  background-color: currentColor;
  margin-left: 2px;
  vertical-align: middle;
  animation: blink 1s infinite;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 美化滚动条 */
.messages::-webkit-scrollbar,
.suggestions::-webkit-scrollbar {
  width: 8px;
  height: 8px;
  background-color: transparent;
}

.messages::-webkit-scrollbar-thumb,
.suggestions::-webkit-scrollbar-thumb {
  background-color: #d1d5db;
  border-radius: 4px;
  border: 2px solid transparent;
  background-clip: content-box;
}

.messages::-webkit-scrollbar-thumb:hover,
.suggestions::-webkit-scrollbar-thumb:hover {
  background-color: #9ca3af;
}

.messages::-webkit-scrollbar-track,
.suggestions::-webkit-scrollbar-track {
  background-color: transparent;
}

/* 响应式设计 */
@media (max-width: 1400px) {
  .chat-area {
    max-width: 1000px;
  }
}

@media (max-width: 768px) {
  .chat-area {
    padding: 16px;
    max-width: 100%;
  }
  
  .messages {
    padding-right: 8px;
  }
}

.thinking-text {
  color: #9ca3af;
  display: block;
  margin-bottom: 12px;
  padding: 12px;
  background-color: rgba(243, 244, 246, 0.8);
  border-radius: 8px;
  font-family: var(--font-mono);
  font-size: 13px;
  line-height: 1.5;
  animation: fadeInScale 0.3s ease-out;
  border: 1px solid rgba(156, 163, 175, 0.2);
}

@keyframes fadeInScale {
  from {
    opacity: 0;
    transform: scale(0.98);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

/* 页面过渡动画 */
.fade-in {
  animation: fadeIn 0.5s ease-out;
}

/* 消息列表动画 */
.message-enter-active,
.message-leave-active {
  transition: all 0.3s ease;
}

.message-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

.message-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}

/* 确保消息不会在动画时重叠 */
.message-move {
  transition: transform 0.3s ease;
}

/* 输入框动画 */
.slide-up-enter-active,
.slide-up-leave-active {
  transition: all 0.3s ease;
}

.slide-up-enter-from,
.slide-up-leave-to {
  opacity: 0;
  transform: translateY(20px);
}

/* 为每个卡片设置不同的延迟 */
.suggestion-card:nth-child(1) { animation-delay: 0.1s; }
.suggestion-card:nth-child(2) { animation-delay: 0.2s; }
.suggestion-card:nth-child(3) { animation-delay: 0.3s; }
.suggestion-card:nth-child(4) { animation-delay: 0.4s; }
</style> 