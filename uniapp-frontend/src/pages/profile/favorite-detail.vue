<template>
  <view class="page">
    <!-- 顶部标题栏 -->
    <view class="header">
      <view class="header-content">
        <view class="btn-back" @tap="goBack">
          <text class="btn-back-icon">←</text>
        </view>
        <text class="header-title">食谱详情</text>
        <view class="header-placeholder" />
      </view>
    </view>

    <!-- 加载状态 -->
    <view v-if="loading" class="loading-state">
      <text class="loading-text">加载中...</text>
    </view>

    <!-- 内容区域 -->
    <scroll-view v-else class="content-area" scroll-y>
      <!-- 食谱头部信息 -->
      <view class="recipe-header">
        <view class="recipe-icon-wrapper">
          <text class="recipe-icon">🍳</text>
        </view>
        <view class="recipe-info">
          <text class="recipe-title">{{ recipeName }}</text>
          <text class="recipe-time">收藏于 {{ formatDate(detail?.created_at) }}</text>
        </view>
      </view>

      <!-- 食谱内容 -->
      <view class="recipe-content">
        <mp-html :content="renderedContent" :tag-style="markdownStyles" selectable @linktap="onLinkTap" />
      </view>

      <!-- 底部间距 -->
      <view class="bottom-spacer" />
    </scroll-view>

    <!-- 底部操作栏 -->
    <view class="bottom-bar">
      <view class="btn-copy" @tap="copyContent">
        <text class="btn-icon">📋</text>
        <text class="btn-text">复制内容</text>
      </view>
      <view class="btn-share" @tap="shareContent">
        <text class="btn-icon">📤</text>
        <text class="btn-text">分享</text>
      </view>
      <view class="btn-delete" @tap="confirmDelete">
        <text class="btn-icon">🗑️</text>
        <text class="btn-text">取消收藏</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { marked } from 'marked'
import { getFavoriteDetail, removeFavorite } from '@/api'
import type { FavoriteItem } from '@/api'

// 详情数据
const detail = ref<FavoriteItem | null>(null)
const loading = ref(true)
const favoriteId = ref(0)

// 食谱名称（从内容中提取或使用默认值）
const recipeName = computed(() => {
  if (!detail.value?.recipe_content) return '食谱详情'
  const content = detail.value.recipe_content
  // 尝试从内容中提取标题
  const titleMatch = content.match(/^#\s+(.+)$/m)
  if (titleMatch) return titleMatch[1]
  // 取第一行作为标题
  const firstLine = content.split('\n')[0].trim()
  if (firstLine.length <= 30) return firstLine
  return firstLine.substring(0, 30) + '...'
})

// 渲染内容
const renderedContent = computed(() => {
  if (!detail.value?.recipe_content) return ''
  return marked.parse(detail.value.recipe_content, { breaks: true }) as string
})

// Markdown 样式
const markdownStyles: Record<string, string> = {
  h1: 'font-size:40rpx;font-weight:700;margin:24rpx 0 16rpx;color:#1e293b;',
  h2: 'font-size:36rpx;font-weight:700;margin:20rpx 0 12rpx;color:#1e293b;',
  h3: 'font-size:32rpx;font-weight:600;margin:16rpx 0 10rpx;color:#1e293b;',
  p: 'margin:10rpx 0;line-height:1.8;color:#334155;',
  pre: 'background:#f8fafc;padding:24rpx;border-radius:16rpx;overflow-x:auto;margin:16rpx 0;border:1rpx solid #e2e8f0;',
  code: 'background:#f1f5f9;padding:4rpx 12rpx;border-radius:8rpx;font-size:24rpx;color:#e11d48;',
  img: 'max-width:100%;border-radius:16rpx;margin:16rpx 0;',
  blockquote: 'border-left:8rpx solid #f97316;padding:16rpx 20rpx;background:#fff7ed;border-radius:0 16rpx 16rpx 0;margin:16rpx 0;color:#9a3412;',
  table: 'border-collapse:collapse;width:100%;margin:16rpx 0;border-radius:12rpx;overflow:hidden;',
  th: 'background:#fff7ed;padding:14rpx 18rpx;text-align:left;font-weight:600;color:#9a3412;border-bottom:2rpx solid #fed7aa;',
  td: 'padding:14rpx 18rpx;border-bottom:1rpx solid #f1f5f9;color:#475569;',
  ul: 'margin:12rpx 0;padding-left:32rpx;list-style:disc;',
  ol: 'margin:12rpx 0;padding-left:32rpx;list-style:decimal;',
  li: 'margin:8rpx 0;line-height:1.8;color:#334155;',
  hr: 'border:none;height:2rpx;background:#e2e8f0;margin:24rpx 0;',
  a: 'color:#f97316;text-decoration:none;border-bottom:2rpx solid #fdba74;',
  strong: 'font-weight:700;color:#1e293b;',
  em: 'font-style:italic;color:#64748b;',
}

onLoad((options) => {
  if (options?.id) {
    favoriteId.value = parseInt(options.id)
    loadDetail()
  } else {
    loading.value = false
    uni.showToast({ title: '参数错误', icon: 'none' })
    setTimeout(() => goBack(), 1500)
  }
})

// 加载详情
async function loadDetail() {
  loading.value = true
  try {
    const res = await getFavoriteDetail(favoriteId.value)
    if (String(res.code) === '200') {
      detail.value = res.data
      if (!detail.value) {
        uni.showToast({ title: '收藏不存在', icon: 'none' })
        setTimeout(() => goBack(), 1500)
      }
    } else {
      uni.showToast({ title: res.message || '加载失败', icon: 'none' })
      setTimeout(() => goBack(), 1500)
    }
  } catch (e) {
    console.error('加载详情失败:', e)
    uni.showToast({ title: '加载失败', icon: 'none' })
  } finally {
    loading.value = false
  }
}

// 复制内容
function copyContent() {
  const content = detail.value?.recipe_content
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

// 分享内容
function shareContent() {
  // #ifdef H5
  if (navigator.share) {
    navigator.share({
      title: recipeName.value,
      text: detail.value?.recipe_content || '',
    }).catch(() => {
      copyContent()
    })
  } else {
    copyContent()
  }
  // #endif

  // #ifndef H5
  // 小程序分享
  uni.showShareMenu({
    withShareTicket: true,
    menus: ['shareAppMessage', 'shareTimeline']
  })
  // #endif
}

// 确认删除
function confirmDelete() {
  uni.showModal({
    title: '提示',
    content: '确定要取消收藏吗？',
    success: async (res) => {
      if (!res.confirm) return
      try {
        const result = await removeFavorite(favoriteId.value)
        if (String(result.code) === '200') {
          uni.showToast({ title: '已取消收藏', icon: 'success' })
          setTimeout(() => goBack(), 1500)
        } else {
          uni.showToast({ title: result.message || '操作失败', icon: 'none' })
        }
      } catch (e) {
        console.error('取消收藏失败:', e)
        uni.showToast({ title: '操作失败', icon: 'none' })
      }
    }
  })
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

// 返回上一页
function goBack() {
  uni.navigateBack()
}

// 格式化日期
function formatDate(dateStr: string) {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  const now = new Date()
  const diff = now.getTime() - date.getTime()

  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
  if (diff < 2592000000) return `${Math.floor(diff / 86400000)}天前`

  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  return `${year}-${month}-${day} ${hours}:${minutes}`
}
</script>

<style scoped>
.page {
  min-height: 100vh;
  background: linear-gradient(135deg, #fffbeb 0%, #fff7ed 50%, #fef2f2 100%);
  display: flex;
  flex-direction: column;
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

.btn-back {
  width: 64rpx;
  height: 64rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 14rpx;
  background: rgba(0, 0, 0, 0.04);
}

.btn-back:active {
  background: rgba(0, 0, 0, 0.08);
}

.btn-back-icon {
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

/* 加载状态 */
.loading-state {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding-top: 200rpx;
}

.loading-text {
  font-size: 28rpx;
  color: #9ca3af;
}

/* 内容区域 */
.content-area {
  flex: 1;
  padding-top: calc(120rpx + env(safe-area-inset-top));
  padding-bottom: 180rpx;
}

/* 食谱头部 */
.recipe-header {
  margin: 24rpx 32rpx;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 24rpx;
  padding: 32rpx;
  display: flex;
  align-items: center;
  gap: 24rpx;
  box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.04);
  border: 1rpx solid rgba(255, 255, 255, 0.5);
}

.recipe-icon-wrapper {
  width: 80rpx;
  height: 80rpx;
  background: linear-gradient(135deg, #f97316 0%, #ef4444 100%);
  border-radius: 20rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4rpx 16rpx rgba(249, 115, 22, 0.3);
}

.recipe-icon {
  font-size: 40rpx;
}

.recipe-info {
  flex: 1;
}

.recipe-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #1f2937;
  display: block;
}

.recipe-time {
  font-size: 24rpx;
  color: #9ca3af;
  margin-top: 8rpx;
  display: block;
}

/* 食谱内容 */
.recipe-content {
  margin: 0 32rpx;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 24rpx;
  padding: 32rpx;
  box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.04);
  border: 1rpx solid rgba(255, 255, 255, 0.5);
}

.bottom-spacer {
  height: 40rpx;
}

/* 底部操作栏 */
.bottom-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 100;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  padding: 20rpx 32rpx;
  padding-bottom: calc(20rpx + env(safe-area-inset-bottom));
  display: flex;
  align-items: center;
  gap: 16rpx;
  box-shadow: 0 -4rpx 16rpx rgba(0, 0, 0, 0.06);
}

.btn-copy,
.btn-share,
.btn-delete {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8rpx;
  padding: 24rpx 16rpx;
  border-radius: 16rpx;
  transition: all 0.2s;
}

.btn-copy {
  background: linear-gradient(135deg, #f97316 0%, #ea580c 100%);
}

.btn-copy:active {
  opacity: 0.9;
  transform: scale(0.98);
}

.btn-share {
  background: rgba(59, 130, 246, 0.1);
}

.btn-share:active {
  background: rgba(59, 130, 246, 0.2);
  transform: scale(0.98);
}

.btn-delete {
  background: rgba(239, 68, 68, 0.1);
}

.btn-delete:active {
  background: rgba(239, 68, 68, 0.2);
  transform: scale(0.98);
}

.btn-icon {
  font-size: 28rpx;
}

.btn-text {
  font-size: 26rpx;
  font-weight: 500;
}

.btn-copy .btn-text {
  color: #fff;
}

.btn-share .btn-text {
  color: #3b82f6;
}

.btn-delete .btn-text {
  color: #ef4444;
}
</style>
