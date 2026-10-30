<template>
  <view class="message-item" :class="isUser ? 'is-user' : 'is-assistant'">
    <!-- 助手消息 -->
    <template v-if="!isUser">
      <view class="msg-row assistant-row">
        <view class="msg-body">
          <view class="bubble assistant-bubble">
            <!-- 图片 -->
            <image v-if="message.imageUrl" :src="proxyImageUrl(message.imageUrl)" mode="widthFix" class="msg-image"
              @tap="previewImage" />
            <!-- Markdown 渲染 -->
            <view class="markdown-wrap">
              <mp-html :content="displayContent" :tag-style="markdownStyles" selectable @linktap="onLinkTap" />
            </view>
            <!-- 流式指示器 -->
            <view v-if="message.streaming" class="typing-dots">
              <view class="tdot" />
              <view class="tdot" />
              <view class="tdot" />
            </view>
          </view>
          <!-- 操作按钮 -->
          <view v-if="!message.streaming" class="msg-actions">
            <view class="btn-action" @tap="handleCopy">
              <text class="action-icon">📋</text>
            </view>
            <view class="btn-action" :class="{ 'is-favorited': isFavorited }" @tap="handleFavorite">
              <text class="action-icon">{{ isFavorited ? '⭐' : '☆' }}</text>
            </view>
          </view>
        </view>
      </view>
    </template>

    <!-- 用户消息 -->
    <template v-else>
      <view class="msg-row user-row">
        <view class="msg-body user-body">
          <!-- 图片 -->
          <image v-if="message.imageUrl" :src="proxyImageUrl(message.imageUrl)" mode="widthFix" class="msg-image"
            @tap="previewImage" />
          <!-- 文本 -->
          <view class="bubble user-bubble">
            <text class="user-text">{{ message.content }}</text>
          </view>
        </view>
      </view>
    </template>
  </view>
</template>

<script setup lang="ts">
import { computed, ref, watch, onBeforeUnmount } from 'vue'
import { marked } from 'marked'
import type { Message } from '@/types/chat'
import { addFavorite } from '@/api'

const props = defineProps<{
  message: Message
  threadId?: string
}>()

const emit = defineEmits<{
  (e: 'favorite', messageId: string): void
}>()

const isUser = computed(() => props.message.role === 'user')
// 从消息中获取收藏状态，如果没有则默认为false
const isFavorited = ref(props.message.is_favorite || false)

// 监听消息变化，更新收藏状态
watch(() => props.message.is_favorite, (newVal) => {
  isFavorited.value = newVal || false
})

// 复制消息内容
function handleCopy() {
  const content = props.message.content || ''
  if (!content) {
    uni.showToast({ title: '没有可复制的内容', icon: 'none' })
    return
  }

  // #ifdef H5
  navigator.clipboard.writeText(content).then(() => {
    uni.showToast({ title: '已复制到剪贴板', icon: 'success' })
  }).catch(() => {
    uni.showToast({ title: '复制失败', icon: 'none' })
  })
  // #endif

  // #ifndef H5
  uni.setClipboardData({
    data: content,
    success: () => {
      uni.showToast({ title: '已复制到剪贴板', icon: 'success' })
    }
  })
  // #endif
}

// 收藏消息
async function handleFavorite() {
  if (isFavorited.value) {
    uni.showToast({ title: '已收藏过该食谱', icon: 'none' })
    return
  }

  if (!props.threadId || !props.message.messageId) {
    uni.showToast({ title: '收藏失败：缺少必要信息', icon: 'none' })
    return
  }

  try {
    const res = await addFavorite(props.threadId, props.message.messageId)
    if (String(res.code) === '200') {
      isFavorited.value = true
      uni.showToast({ title: '收藏成功', icon: 'success' })
      emit('favorite', props.message.id)
    } else {
      uni.showToast({ title: res.message || '收藏失败', icon: 'none' })
    }
  } catch (e) {
    console.error('收藏失败:', e)
    uni.showToast({ title: '收藏失败', icon: 'none' })
  }
}

// 代理图片 URL
function proxyImageUrl(url: string): string {
  if (!url) return url
  // #ifdef H5
  return `/api/v1/oss/proxy?url=${encodeURIComponent(url)}`
  // #endif
  // #ifndef H5
  return url
  // #endif
}

// HTML 转义（流式中显示纯文本用）
function escapeHtml(text: string): string {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/\n/g, '<br>')
}

// Markdown 渲染（流结束后使用）
const renderedMarkdown = computed(() => {
  const text = props.message.content || ''
  if (!text) return ''
  let html = marked.parse(text, { breaks: true }) as string
  // 1. 去掉包裹 <img> 的 <p> 标签（mp-html rich-text 不支持 img）
  html = html.replace(/<p>\s*(<img\s[^>]*\/?>)\s*<\/p>/gi, '$1')
  // 2. 所有外部图片走后端代理，绕过防盗链 Referer 检查
  html = html.replace(/(<img\s[^>]*\bsrc=")(https?:\/\/[^"]+)("[^>]*\/?>)/gi, (match, prefix, url, suffix) => {
    // 已经是代理地址的不处理
    if (url.includes('/api/v1/oss/proxy')) return match
    return `${prefix}/api/v1/oss/proxy?url=${encodeURIComponent(url)}${suffix}`
  })
  return html
})

// 流式输出：纯文本 + 光标 / 流结束后：完整 markdown
// 流式中 100ms 防抖，结束后立即更新
const displayContent = ref('')
let debounceTimer: any = null

watch(
  () => [props.message.content, props.message.streaming] as const,
  ([content, streaming]) => {
    const text = content || ''
    if (streaming) {
      // 流式中：纯文本 + 闪烁光标，100ms 防抖
      if (debounceTimer) clearTimeout(debounceTimer)
      debounceTimer = setTimeout(() => {
        displayContent.value = escapeHtml(text) + '<span class="cursor-blink">▊</span>'
      }, 100)
    } else {
      // 流结束：立即渲染完整 markdown
      if (debounceTimer) clearTimeout(debounceTimer)
      displayContent.value = renderedMarkdown.value
    }
  },
  { immediate: true }
)

// 流结束后，content 可能还会微调（如拼接错误信息），同步更新 markdown
watch(
  () => renderedMarkdown.value,
  (newVal) => {
    if (!props.message.streaming) {
      displayContent.value = newVal
    }
  }
)

onBeforeUnmount(() => {
  if (debounceTimer) clearTimeout(debounceTimer)
})

// mp-html 标签样式
const markdownStyles: Record<string, string> = {
  h1: 'font-size:36rpx;font-weight:700;margin:20rpx 0 12rpx;color:#1e293b;',
  h2: 'font-size:32rpx;font-weight:700;margin:16rpx 0 10rpx;color:#1e293b;',
  h3: 'font-size:28rpx;font-weight:600;margin:12rpx 0 8rpx;color:#1e293b;',
  p: 'margin:6rpx 0;line-height:1.75;color:#334155;',
  pre: 'background:#f8fafc;padding:20rpx;border-radius:16rpx;overflow-x:auto;margin:12rpx 0;border:1rpx solid #e2e8f0;',
  code: 'background:#f1f5f9;padding:4rpx 10rpx;border-radius:8rpx;font-size:24rpx;color:#e11d48;',
  img: 'max-width:100%;border-radius:16rpx;margin:12rpx 0;',
  blockquote: 'border-left:6rpx solid #f97316;padding:12rpx 16rpx;background:#fff7ed;border-radius:0 12rpx 12rpx 0;margin:12rpx 0;color:#9a3412;',
  table: 'border-collapse:collapse;width:100%;margin:12rpx 0;border-radius:12rpx;overflow:hidden;',
  th: 'background:#fff7ed;padding:10rpx 14rpx;text-align:left;font-weight:600;color:#9a3412;border-bottom:2rpx solid #fed7aa;',
  td: 'padding:10rpx 14rpx;border-bottom:1rpx solid #f1f5f9;color:#475569;',
  ul: 'margin:8rpx 0;padding-left:28rpx;list-style:disc;',
  ol: 'margin:8rpx 0;padding-left:28rpx;list-style:decimal;',
  li: 'margin:4rpx 0;line-height:1.7;color:#334155;',
  hr: 'border:none;height:1rpx;background:#e2e8f0;margin:16rpx 0;',
  a: 'color:#f97316;text-decoration:none;border-bottom:1rpx solid #fdba74;',
  strong: 'font-weight:700;color:#1e293b;',
  em: 'font-style:italic;color:#64748b;',
}

// 链接点击
function onLinkTap(e: { href: string }) {
  // #ifdef H5
  window.open(e.href, '_blank')
  // #endif
  // #ifndef H5
  uni.setClipboardData({
    data: e.href,
    success: () => {
      uni.showToast({ title: '链接已复制', icon: 'none' })
    },
  })
  // #endif
}

// 图片预览
function previewImage() {
  if (props.message.imageUrl) {
    uni.previewImage({
      urls: [proxyImageUrl(props.message.imageUrl)],
    })
  }
}
</script>

<style scoped>
.message-item {
  padding: 12rpx 24rpx;
}

.is-user {
  padding-top: 20rpx;
}

.is-assistant {
  padding-top: 20rpx;
}

/* 消息行 */
.msg-row {
  display: flex;
  align-items: flex-start;
  gap: 16rpx;
}

.user-row {
  flex-direction: row-reverse;
}

.assistant-row {
  flex-direction: row;
}

/* 头像 */
.avatar {
  width: 64rpx;
  height: 64rpx;
  border-radius: 20rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  margin-top: 4rpx;
}

.assistant-avatar {
  background: linear-gradient(145deg, #fb923c, #f97316);
  box-shadow: 0 6rpx 20rpx rgba(249, 115, 22, 0.3);
}

.user-avatar {
  background: linear-gradient(145deg, #60a5fa, #3b82f6);
  box-shadow: 0 6rpx 20rpx rgba(59, 130, 246, 0.3);
}

.avatar-emoji {
  font-size: 30rpx;
}

/* 消息主体 */
.msg-body {
  min-width: 80rpx;
}

.user-body {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

/* 气泡 */
.bubble {
  padding: 20rpx 28rpx;
  border-radius: 24rpx;
  position: relative;
  word-break: break-all;
}

.assistant-bubble {
  background: #ffffff;
  color: #334155;
  border-radius: 4rpx 24rpx 24rpx 24rpx;
  box-shadow:
    0 2rpx 8rpx rgba(0, 0, 0, 0.04),
    0 8rpx 32rpx rgba(0, 0, 0, 0.04);
  border: 1rpx solid rgba(0, 0, 0, 0.04);
}

.user-bubble {
  background: linear-gradient(135deg, #f97316 0%, #ea580c 100%);
  color: #ffffff;
  border-radius: 24rpx 4rpx 24rpx 24rpx;
  box-shadow: 0 6rpx 24rpx rgba(249, 115, 22, 0.25);
}

.user-text {
  font-size: 28rpx;
  line-height: 1.65;
  white-space: pre-wrap;
}

/* 图片 */
.msg-image {
  width: 400rpx;
  border-radius: 16rpx;
  margin-bottom: 12rpx;
  box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.08);
}

/* Markdown 区域 */
.markdown-wrap {
  font-size: 28rpx;
  line-height: 1.75;
}

/* 流式光标闪烁 */
.markdown-wrap :deep(.cursor-blink) {
  color: #f97316;
  font-weight: bold;
  animation: cursor-pulse 0.8s ease-in-out infinite;
}

@keyframes cursor-pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.2; }
}

/* 流式打字指示器 */
.typing-dots {
  display: flex;
  align-items: center;
  gap: 8rpx;
  margin-top: 16rpx;
  padding-top: 12rpx;
  border-top: 1rpx solid #f1f5f9;
}

.tdot {
  width: 12rpx;
  height: 12rpx;
  border-radius: 50%;
  background: #f97316;
  opacity: 0.4;
  animation: tdot-bounce 1.4s ease-in-out infinite;
}

.tdot:nth-child(2) {
  animation-delay: 0.16s;
}

.tdot:nth-child(3) {
  animation-delay: 0.32s;
}

@keyframes tdot-bounce {

  0%,
  80%,
  100% {
    transform: scale(0.6);
    opacity: 0.3;
  }

  40% {
    transform: scale(1);
    opacity: 0.8;
  }
}

/* 消息操作按钮 */
.msg-actions {
  display: flex;
  align-items: center;
  gap: 16rpx;
  margin-top: 12rpx;
  padding-left: 8rpx;
}

.btn-action {
  width: 56rpx;
  height: 56rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.04);
  transition: all 0.2s;
}

.btn-action:active {
  background: rgba(0, 0, 0, 0.08);
  transform: scale(0.95);
}

.btn-action.is-favorited {
  background: rgba(249, 115, 22, 0.1);
}

.action-icon {
  font-size: 28rpx;
}
</style>
