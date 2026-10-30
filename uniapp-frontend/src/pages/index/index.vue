<template>
  <view class="page">
    <!-- 顶部标题栏 -->
    <view class="header">
      <view class="header-content">
        <view class="btn-menu" @tap="sidebarVisible = true">
          <text class="btn-menu-icon">☰</text>
        </view>
        <text class="header-title">AI 私人厨师</text>
        <view class="header-placeholder" />
      </view>
    </view>

    <!-- 侧栏 -->
    <SideBar :visible="sidebarVisible" :threads="chatThreads" :current-thread-id="threadId"
      :username="userInfo.username" :has-more="chatThreads.length < chatListTotal" :loading="chatListLoading"
      @close="sidebarVisible = false" @new-chat="handleNewChat" @select-thread="handleSelectThread"
      @delete-thread="handleDeleteThread" @logout="handleLogout" @load-more="loadMoreChatList" />

    <!-- 消息列表 -->
    <view class="message-list-wrapper">
      <scroll-view
        class="message-list"
        scroll-y
        :scroll-into-view="scrollIntoViewId"
        :scroll-with-animation="true"
      >
        <!-- 空状态 -->
        <view v-if="messages.length === 0" class="empty-state">
          <view class="empty-icon-wrapper">
            <text class="empty-icon">🍽</text>
          </view>
          <text class="empty-title">上传食材图片开始吧</text>
          <text class="empty-subtitle">我会帮您识别食材并推荐食谱</text>
        </view>

        <!-- 消息列表 -->
        <view v-else class="messages">
          <!-- 加载更多历史消息 -->
          <view v-if="hasMoreHistory" class="load-more" @tap="loadMoreHistory">
            <text class="load-more-text">{{ historyLoading ? '加载中...' : '加载更早的消息' }}</text>
          </view>
          <view v-for="message in messages" :key="message.id" :id="'msg-' + message.id">
            <ChatMessage :message="message" :thread-id="threadId" />
          </view>
          <view class="bottom-spacer" id="msg-bottom" />
        </view>
      </scroll-view>
    </view>

    <!-- 停止生成按钮 -->
    <view v-if="processing" class="stop-bar">
      <view class="btn-stop" @tap="handleStopGeneration">
        <text class="stop-icon">■</text>
        <text class="stop-text">停止生成</text>
      </view>
    </view>

    <!-- 输入区域 -->
    <view class="input-area">
      <ChatInput :disabled="processing" @send="handleSend" />
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, nextTick, reactive } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import ChatMessage from '@/components/ChatMessage.vue'
import ChatInput from '@/components/ChatInput.vue'
import SideBar from '@/components/SideBar.vue'
import type { ChatRecord } from '@/components/SideBar.vue'
import { streamChat, getChatHistory, clearChatHistory, chatCreate, chatList } from '@/api'
import type { Message } from '@/types/chat'

// ===== 状态 =====
const messages = ref<Message[]>([])
const processing = ref(false)
const threadId = ref('')
const messageIdCounter = ref(0)
const sidebarVisible = ref(false)
const chatThreads = ref<ChatRecord[]>([])
const userInfo = reactive({ username: '' })
const scrollIntoViewId = ref('msg-bottom')
const abortStream = ref<{ abort: () => void } | null>(null)

// ===== 会话列表 =====
const chatListPage = ref(1)
const chatListTotal = ref(0)
const chatListLoading = ref(false)

async function loadChatList(reset: boolean = false) {
  if (chatListLoading.value) return
  if (reset) {
    chatListPage.value = 1
    chatThreads.value = []
  }
  chatListLoading.value = true
  try {
    const res = await chatList(chatListPage.value, 20)
    if (String(res.code) === '200') {
      const { list, total } = res.data
      if (reset) {
        chatThreads.value = list || []
      } else {
        chatThreads.value = [...chatThreads.value, ...(list || [])]
      }
      chatListTotal.value = total || 0
    }
  } catch (e) {
    console.error('加载会话列表失败:', e)
  } finally {
    chatListLoading.value = false
  }
}

function loadMoreChatList() {
  if (chatThreads.value.length >= chatListTotal.value) return
  chatListPage.value++
  loadChatList()
}

// ===== 消息操作 =====
function addMessage(msg: Omit<Message, 'id' | 'timestamp'>): Message {
  messageIdCounter.value++
  const newMessage: Message = {
    ...msg,
    id: `msg_${messageIdCounter.value}_${Date.now()}`,
    timestamp: Date.now(),
  }
  messages.value.push(newMessage)
  // 新消息时强制滚动到底部
  scrollToBottom()
  return newMessage
}

// 滚动到底部
function scrollToBottom(immediate = false) {
  const delay = immediate ? 100 : 50
  nextTick(() => {
    scrollIntoViewId.value = ''
    setTimeout(() => {
      nextTick(() => {
        scrollIntoViewId.value = 'msg-bottom'
      })
    }, delay)
  })
}

// 节流滚动（流式输出时使用，避免频繁 DOM 操作导致抖动）
let lastScrollTime = 0
function throttledScrollToBottom() {
  const now = Date.now()
  if (now - lastScrollTime > 300) {
    lastScrollTime = now
    scrollToBottom()
  }
}

// ===== 加载历史 =====
const historyPage = ref(1)
const historyTotal = ref(0)
const historyLoading = ref(false)
const hasMoreHistory = ref(true)

async function loadHistory(id: string, loadMore: boolean = false) {
  if (historyLoading.value) return
  if (!loadMore) {
    historyPage.value = 1
    hasMoreHistory.value = true
    messages.value = []
    messageIdCounter.value = 0
  }
  historyLoading.value = true
  try {
    const res = await getChatHistory(id, historyPage.value, 20)
    const history = res.list || []
    historyTotal.value = res.total || 0

    if (history.length > 0) {
      const loaded: Message[] = history.map((msg, index) => {
        let content = ''
        let imageUrl: string | undefined

        if (typeof msg.content === 'string') {
          content = msg.content
        } else if (Array.isArray(msg.content)) {
          const parts = msg.content as { type: string; text?: string; url?: string }[]
          for (const part of parts) {
            if (part.type === 'text' && part.text) {
              content += part.text
            } else if (part.type === 'image' && part.url) {
              imageUrl = part.url
            }
          }
        }

        return {
          id: `history_${historyPage.value}_${index}_${Date.now()}`,
          messageId: msg.id,
          role: msg.role as 'user' | 'assistant',
          content,
          imageUrl,
          timestamp: Date.now() - (history.length - index) * 1000,
          is_favorite: msg.is_favorite || false,
        }
      })

      if (loadMore) {
        // 加载更多：插入到消息列表前面
        messages.value = [...loaded, ...messages.value]
      } else {
        messages.value = loaded
        messageIdCounter.value = loaded.length
        scrollToBottom(true)
      }

      // 检查是否还有更多
      hasMoreHistory.value = messages.value.length < historyTotal.value
    } else {
      hasMoreHistory.value = false
    }
  } catch (error) {
    console.error('加载历史消息失败:', error)
  } finally {
    historyLoading.value = false
  }
}

function loadMoreHistory() {
  if (!hasMoreHistory.value || historyLoading.value) return
  historyPage.value++
  loadHistory(threadId.value, true)
}

// 上传图片（UniApp 专用，通过后端转发到 OSS）
// #ifdef H5
const API_BASE = ''
// #endif
// #ifndef H5
const API_BASE = 'http://localhost:8001'
// #endif

function uploadImageUniApp(filePath: string): Promise<string> {
  return new Promise((resolve, reject) => {
    const ext = filePath.split('.').pop() || 'jpg'
    const filename = `${Date.now()}_${Math.random().toString(36).slice(2, 8)}.${ext}`
    uni.uploadFile({
      url: `${API_BASE}/api/v1/oss/upload`,
      filePath,
      name: 'file',
      formData: { filename },
      success: (res) => {
        if (res.statusCode === 200) {
          try {
            const data = JSON.parse(res.data as string)
            resolve(data.accessUrl)
          } catch {
            reject(new Error('解析上传结果失败'))
          }
        } else {
          reject(new Error(`上传失败: ${res.statusCode}`))
        }
      },
      fail: (err) => reject(new Error(err.errMsg || '上传失败')),
    })
  })
}

// ===== 发送消息 =====
async function handleSend(text: string, file?: any) {
  if (processing.value) return

  let imageUrl: string | undefined

  if (file) {
    try {
      uni.showLoading({ title: '上传图片中...' })
      imageUrl = await uploadImageUniApp(file.path || file)
      uni.hideLoading()
    } catch (error) {
      uni.hideLoading()
      console.error('图片上传失败:', error)
      addMessage({ role: 'assistant', content: '图片上传失败，请稍后重试。' })
      return
    }
  }

  addMessage({
    role: 'user',
    content: text || '上传了一张食材图片',
    imageUrl,
  })

  processing.value = true
  lastScrollTime = 0

  const assistantMsg = addMessage({
    role: 'assistant',
    content: '',
    streaming: true,
  })

  try {
    const { abort } = streamChat(
      text || '这是我冰箱里的食物，帮我看看能做什么佳肴？',
      (chunk) => {
        const msg = messages.value.find((m) => m.id === assistantMsg.id)
        if (msg) {
          msg.content += chunk
          throttledScrollToBottom()
        }
      },
      imageUrl,
      (error) => {
        console.error('聊天失败:', error)
        const msg = messages.value.find((m) => m.id === assistantMsg.id)
        if (msg) {
          msg.content += `\n[错误]: ${error.message}`
          msg.streaming = false
        }
        processing.value = false
        abortStream.value = null
      },
      () => {
        const msg = messages.value.find((m) => m.id === assistantMsg.id)
        if (msg) {
          msg.streaming = false
        }
        processing.value = false
        abortStream.value = null
        scrollToBottom(true)
      },
      threadId.value
    )
    abortStream.value = { abort }
  } catch (error) {
    processing.value = false
    abortStream.value = null
  }
}

// ===== 停止生成 =====
function handleStopGeneration() {
  if (abortStream.value) {
    abortStream.value.abort()
    // 标记最后一条助手消息为已停止
    const lastAssistant = [...messages.value].reverse().find((m) => m.role === 'assistant' && m.streaming)
    if (lastAssistant) {
      lastAssistant.streaming = false
    }
    processing.value = false
    abortStream.value = null
  }
}

// ===== 会话操作 =====
async function handleNewChat() {
  sidebarVisible.value = false

  // 调用后端创建会话记录，获取 UUID
  try {
    const res = await chatCreate()
    if (String(res.code) === '200') {
      const newId = res.data
      uni.setStorageSync('thread_id', newId)
      threadId.value = newId
      messages.value = []
      messageIdCounter.value = 0
      // 刷新会话列表
      loadChatList()
    } else {
      uni.showToast({ title: res.message || '创建会话失败', icon: 'none' })
    }
  } catch (e) {
    console.error('创建会话失败:', e)
    uni.showToast({ title: '创建会话失败', icon: 'none' })
  }
}

async function handleSelectThread(id: string) {
  sidebarVisible.value = false
  if (id === threadId.value) return

  uni.setStorageSync('thread_id', id)
  threadId.value = id
  messages.value = []
  messageIdCounter.value = 0
  await loadHistory(id)
}

async function handleDeleteThread(id: string) {
  uni.showModal({
    title: '删除会话',
    content: '确定要删除这个会话吗？',
    success: async (modalRes) => {
      if (!modalRes.confirm) return

      try {
        // 调用删除接口
        await clearChatHistory(id)

        // 从列表中直接移除该项
        const index = chatThreads.value.findIndex(item => item.id === id)
        if (index !== -1) {
          chatThreads.value.splice(index, 1)
          chatListTotal.value = Math.max(0, chatListTotal.value - 1)
        }

        // 如果删除的是当前会话
        if (id === threadId.value) {
          if (chatThreads.value.length > 0) {
            // 还有其他会话，切换到最新的一条
            const latest = chatThreads.value[0]
            threadId.value = latest.id
            uni.setStorageSync('thread_id', latest.id)
            messages.value = []
            messageIdCounter.value = 0
            loadHistory(latest.id)
          } else {
            // 没有会话记录了，创建新会话
            try {
              const res = await chatCreate()
              if (String(res.code) === '200') {
                threadId.value = res.data
                uni.setStorageSync('thread_id', res.data)
                messages.value = []
                messageIdCounter.value = 0
              }
            } catch (e) {
              console.error('创建会话失败:', e)
            }
          }
        }

        uni.showToast({ title: '删除成功', icon: 'success' })
      } catch (e) {
        console.error('删除会话失败:', e)
        uni.showToast({ title: '删除失败', icon: 'none' })
      }
    },
  })
}

function handleLogout() {
  sidebarVisible.value = false
  uni.showModal({
    title: '提示',
    content: '确定要退出登录吗？',
    success: (res) => {
      if (res.confirm) {
        uni.removeStorageSync('token')
        uni.removeStorageSync('userInfo')
        uni.removeStorageSync('thread_id')
        uni.reLaunch({ url: '/pages/login/login' })
      }
    },
  })
}

function onScrollToUpper() {
  // 可扩展：加载更多历史消息
}

// ===== 页面加载 =====
onLoad(async () => {
  const token = uni.getStorageSync('token')
  if (!token) {
    uni.reLaunch({ url: '/pages/login/login' })
    return
  }

  // 加载用户信息
  try {
    const info = uni.getStorageSync('userInfo')
    if (info) userInfo.username = info.username || ''
  } catch { }

  // 从后端加载会话列表
  await loadChatList()

  if (chatThreads.value.length > 0) {
    // 有历史记录，默认选最新的一条（列表已按 created_at desc 排序）
    const latest = chatThreads.value[0]
    threadId.value = latest.id
    uni.setStorageSync('thread_id', latest.id)
    await loadHistory(latest.id)
  } else {
    // 没有历史记录，才调用 create 创建新会话
    try {
      const res = await chatCreate()
      if (String(res.code) === '200') {
        threadId.value = res.data
        uni.setStorageSync('thread_id', res.data)
        loadChatList()
      }
    } catch (e) {
      console.error('创建会话失败:', e)
    }
  }
})
</script>

<style scoped>
.page {
  min-height: 100vh;
  background: linear-gradient(135deg, #fffbeb 0%, #fff7ed 50%, #fef2f2 100%);
  position: relative;
}

/* 背景装饰 */
.page::before {
  content: '';
  position: fixed;
  top: 160rpx;
  left: 40rpx;
  width: 288rpx;
  height: 288rpx;
  background: rgba(253, 186, 116, 0.3);
  border-radius: 50%;
  filter: blur(80rpx);
  z-index: 0;
  animation: pulse 4s ease-in-out infinite;
}

.page::after {
  content: '';
  position: fixed;
  top: 320rpx;
  right: 40rpx;
  width: 384rpx;
  height: 384rpx;
  background: rgba(251, 191, 36, 0.25);
  border-radius: 50%;
  filter: blur(80rpx);
  z-index: 0;
  animation: pulse 4s ease-in-out infinite 1s;
}

@keyframes pulse {

  0%,
  100% {
    opacity: 0.3;
  }

  50% {
    opacity: 0.5;
  }
}

/* 顶部标题栏 */
.header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
  padding: 12rpx 24rpx;
  padding-top: calc(12rpx + env(safe-area-inset-top));
}

.header-content {
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-radius: 20rpx;
  padding: 20rpx 28rpx;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 4rpx 24rpx rgba(0, 0, 0, 0.08);
  border: 1rpx solid rgba(255, 255, 255, 0.5);
}

.btn-menu {
  width: 64rpx;
  height: 64rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 14rpx;
  background: rgba(0, 0, 0, 0.04);
}

.btn-menu:active {
  background: rgba(0, 0, 0, 0.08);
}

.btn-menu-icon {
  font-size: 36rpx;
  color: #333;
}

.header-title {
  font-size: 34rpx;
  font-weight: bold;
  background: linear-gradient(135deg, #ea580c 0%, #dc2626 100%);
  -webkit-background-clip: text;
  color: transparent;
}

.header-placeholder {
  width: 64rpx;
}

/* 消息列表包装器 */
.message-list-wrapper {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 1;
  padding-top: calc(120rpx + env(safe-area-inset-top));
  padding-bottom: 160rpx;
}

/* 消息列表 */
.message-list {
  height: 100%;
}

.messages {
  padding: 0 16rpx;
}

.bottom-spacer {
  height: 24rpx;
}

/* 加载更多 */
.load-more {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20rpx 0;
  margin-bottom: 16rpx;
}

.load-more-text {
  font-size: 24rpx;
  color: #f97316;
  background: rgba(249, 115, 22, 0.08);
  padding: 12rpx 32rpx;
  border-radius: 32rpx;
}

.load-more-text:active {
  opacity: 0.7;
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding-top: 30vh;
}

.empty-icon-wrapper {
  width: 160rpx;
  height: 160rpx;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 32rpx;
  box-shadow: 0 8rpx 32rpx rgba(0, 0, 0, 0.06);
}

.empty-icon {
  font-size: 72rpx;
}

.empty-title {
  font-size: 34rpx;
  font-weight: 600;
  color: #374151;
}

.empty-subtitle {
  font-size: 26rpx;
  color: #9ca3af;
  margin-top: 12rpx;
}

/* 停止生成栏 */
.stop-bar {
  position: fixed;
  bottom: 160rpx;
  left: 0;
  right: 0;
  z-index: 99;
  display: flex;
  justify-content: center;
  padding-bottom: env(safe-area-inset-bottom);
}

.btn-stop {
  display: flex;
  align-items: center;
  gap: 8rpx;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  padding: 14rpx 28rpx;
  border-radius: 32rpx;
  box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.1);
  border: 1rpx solid rgba(0, 0, 0, 0.06);
}

.btn-stop:active {
  opacity: 0.7;
  transform: scale(0.96);
}

.stop-icon {
  font-size: 22rpx;
  color: #ef4444;
  font-weight: bold;
}

.stop-text {
  font-size: 24rpx;
  color: #374151;
  font-weight: 500;
}

/* 输入区域 */
.input-area {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 100;
  padding-bottom: env(safe-area-inset-bottom);
}
</style>
