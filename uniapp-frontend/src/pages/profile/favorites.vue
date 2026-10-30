<template>
  <view class="page">
    <!-- 顶部标题栏 -->
    <view class="header">
      <view class="header-content">
        <view class="btn-back" @tap="goBack">
          <text class="btn-back-icon">←</text>
        </view>
        <text class="header-title">我的收藏</text>
        <view class="header-placeholder" />
      </view>
    </view>

    <!-- 收藏列表 -->
    <scroll-view
      class="favorites-list"
      scroll-y
      @scrolltolower="loadMore"
      :scroll-top="scrollTop"
      refresher-enabled
      :refresher-triggered="refreshing"
      @refresherrefresh="onRefresh"
    >
      <!-- 空状态 -->
      <view v-if="favorites.length === 0 && !loading" class="empty-state">
        <view class="empty-icon-wrapper">
          <text class="empty-icon">⭐</text>
        </view>
        <text class="empty-title">还没有收藏的食谱</text>
        <text class="empty-subtitle">在对话中点击收藏按钮即可添加</text>
      </view>

      <!-- 收藏列表 -->
      <view v-else class="favorites-container">
        <view
          v-for="item in favorites"
          :key="item.id"
          class="favorite-item"
          @tap="viewDetail(item)"
        >
          <!-- 收藏内容 -->
          <view class="favorite-content">
            <view class="favorite-header">
              <view class="favorite-title-row">
                <text class="favorite-icon">🍳</text>
                <text class="favorite-name">{{ getRecipeName(item.recipe_content) }}</text>
              </view>
              <text class="favorite-time">{{ formatDate(item.created_at) }}</text>
            </view>
            <text class="favorite-text">{{ getPreview(item.recipe_content) }}</text>
          </view>

          <!-- 操作按钮 -->
          <view class="favorite-actions">
            <view class="btn-copy" @tap.stop="copyContent(item.recipe_content)">
              <text class="action-icon">📋</text>
            </view>
            <view class="btn-delete" @tap.stop="confirmDelete(item)">
              <text class="action-icon">🗑️</text>
            </view>
          </view>
        </view>

        <!-- 加载状态 -->
        <view class="load-status">
          <view v-if="loading" class="loading-indicator">
            <text class="loading-text">加载中...</text>
          </view>
          <view v-else-if="!hasMore && favorites.length > 0" class="no-more">
            <text class="no-more-text">— 没有更多了 —</text>
          </view>
        </view>
      </view>
    </scroll-view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { getFavorites, removeFavorite } from '@/api'
import type { FavoriteItem } from '@/api'

// 收藏列表
const favorites = ref<FavoriteItem[]>([])
const page = ref(1)
const pageSize = 20
const hasMore = ref(true)
const loading = ref(false)
const refreshing = ref(false)
const scrollTop = ref(0)

onLoad(() => {
  loadFavorites(true)
})

// 加载收藏列表
async function loadFavorites(reset: boolean = false) {
  if (loading.value) return

  if (reset) {
    page.value = 1
    favorites.value = []
    hasMore.value = true
  }

  loading.value = true
  try {
    const res = await getFavorites(page.value, pageSize)
    if (String(res.code) === '200') {
      const list = res.data?.list || []
      if (reset) {
        favorites.value = list
      } else {
        favorites.value = [...favorites.value, ...list]
      }
      hasMore.value = list.length >= pageSize
    }
  } catch (e) {
    console.error('加载收藏列表失败:', e)
    uni.showToast({ title: '加载失败', icon: 'none' })
  } finally {
    loading.value = false
    refreshing.value = false
  }
}

// 加载更多
function loadMore() {
  if (!hasMore.value || loading.value) return
  page.value++
  loadFavorites()
}

// 下拉刷新
function onRefresh() {
  refreshing.value = true
  loadFavorites(true)
}

// 获取食谱名称
function getRecipeName(content: string) {
  if (!content) return '食谱详情'
  // 尝试从内容中提取标题
  const titleMatch = content.match(/^#\s+(.+)$/m)
  if (titleMatch) return titleMatch[1]
  // 取第一行作为标题
  const firstLine = content.split('\n')[0].trim()
  if (firstLine.length <= 20) return firstLine
  return firstLine.substring(0, 20) + '...'
}

// 获取预览内容
function getPreview(content: string) {
  if (!content) return '食谱内容'
  // 移除Markdown标记
  const plainText = content
    .replace(/^#+\s+/gm, '')
    .replace(/\*\*(.+?)\*\*/g, '$1')
    .replace(/\*(.+?)\*/g, '$1')
    .replace(/`(.+?)`/g, '$1')
    .replace(/\[(.+?)\]\(.+?\)/g, '$1')
    .replace(/\n+/g, ' ')
    .trim()
  if (plainText.length <= 80) return plainText
  return plainText.substring(0, 80) + '...'
}

// 查看详情
function viewDetail(item: FavoriteItem) {
  uni.navigateTo({
    url: `/pages/profile/favorite-detail?id=${item.id}`
  })
}

// 复制内容
function copyContent(content: string) {
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

// 确认删除
function confirmDelete(item: FavoriteItem) {
  uni.showModal({
    title: '提示',
    content: '确定要取消收藏吗？',
    success: async (res) => {
      if (!res.confirm) return
      try {
        const result = await removeFavorite(item.id)
        if (String(result.code) === '200') {
          uni.showToast({ title: '已取消收藏', icon: 'success' })
          // 从列表中移除
          favorites.value = favorites.value.filter(f => f.id !== item.id)
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
  return `${year}-${month}-${day}`
}
</script>

<style scoped>
.page {
  min-height: 100vh;
  background: linear-gradient(135deg, #fffbeb 0%, #fff7ed 50%, #fef2f2 100%);
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

/* 收藏列表 */
.favorites-list {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  padding-top: calc(120rpx + env(safe-area-inset-top));
  padding-bottom: env(safe-area-inset-bottom);
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

/* 收藏容器 */
.favorites-container {
  padding: 16rpx 24rpx;
}

/* 收藏项 */
.favorite-item {
  background: rgba(255, 255, 255, 0.9);
  border-radius: 20rpx;
  padding: 28rpx;
  margin-bottom: 20rpx;
  display: flex;
  align-items: flex-start;
  gap: 20rpx;
  box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.04);
  border: 1rpx solid rgba(255, 255, 255, 0.5);
  transition: all 0.2s;
}

.favorite-item:active {
  transform: scale(0.98);
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.06);
}

.favorite-content {
  flex: 1;
  overflow: hidden;
}

.favorite-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 12rpx;
}

.favorite-title-row {
  display: flex;
  align-items: center;
  gap: 12rpx;
  flex: 1;
}

.favorite-icon {
  font-size: 32rpx;
  flex-shrink: 0;
}

.favorite-name {
  font-size: 30rpx;
  font-weight: 600;
  color: #1f2937;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.favorite-time {
  font-size: 22rpx;
  color: #9ca3af;
  flex-shrink: 0;
  margin-left: 16rpx;
}

.favorite-text {
  font-size: 26rpx;
  color: #6b7280;
  line-height: 1.6;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* 操作按钮 */
.favorite-actions {
  display: flex;
  flex-direction: column;
  gap: 12rpx;
  flex-shrink: 0;
}

.btn-copy,
.btn-delete {
  width: 64rpx;
  height: 64rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.2s;
}

.btn-copy {
  background: rgba(249, 115, 22, 0.1);
}

.btn-copy:active {
  background: rgba(249, 115, 22, 0.2);
  transform: scale(0.95);
}

.btn-delete {
  background: rgba(239, 68, 68, 0.1);
}

.btn-delete:active {
  background: rgba(239, 68, 68, 0.2);
  transform: scale(0.95);
}

.action-icon {
  font-size: 28rpx;
}

/* 加载状态 */
.load-status {
  padding: 32rpx 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.loading-indicator {
  display: flex;
  align-items: center;
  gap: 12rpx;
}

.loading-text {
  font-size: 26rpx;
  color: #9ca3af;
}

.no-more {
  display: flex;
  align-items: center;
}

.no-more-text {
  font-size: 24rpx;
  color: #d1d5db;
}
</style>
