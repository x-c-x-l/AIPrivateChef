<template>
  <view class="page">
    <!-- 顶部搜索栏 -->
    <view class="search-header">
      <view class="search-bar">
        <view class="btn-back" @tap="goBack">
          <text class="btn-back-icon">←</text>
        </view>
        <view class="search-input-wrapper">
          <text class="search-icon">🔍</text>
          <input
            v-model="keyword"
            class="search-input"
            placeholder="搜索历史消息..."
            placeholder-class="search-placeholder"
            confirm-type="search"
            @confirm="handleSearch"
            @input="onInput"
          />
          <view v-if="keyword" class="btn-clear" @tap="clearKeyword">
            <text class="clear-icon">✕</text>
          </view>
        </view>
        <view class="btn-search" @tap="handleSearch">
          <text class="btn-search-text">搜索</text>
        </view>
      </view>
    </view>

    <!-- 搜索结果 -->
    <scroll-view
      class="result-list"
      scroll-y
      @scrolltolower="loadMore"
    >
      <!-- 空状态 -->
      <view v-if="!hasSearched" class="empty-state">
        <view class="empty-icon-wrapper">
          <text class="empty-icon">🔍</text>
        </view>
        <text class="empty-title">搜索历史消息</text>
        <text class="empty-subtitle">输入关键词搜索对话内容</text>
      </view>

      <!-- 搜索中 -->
      <view v-else-if="loading && results.length === 0" class="loading-state">
        <text class="loading-text">搜索中...</text>
      </view>

      <!-- 无结果 -->
      <view v-else-if="results.length === 0" class="empty-state">
        <view class="empty-icon-wrapper">
          <text class="empty-icon">😔</text>
        </view>
        <text class="empty-title">未找到相关内容</text>
        <text class="empty-subtitle">试试其他关键词</text>
      </view>

      <!-- 结果列表 -->
      <view v-else class="results-container">
        <view class="result-count">
          <text class="count-text">找到 {{ total }} 条结果</text>
        </view>

        <view
          v-for="item in results"
          :key="item.id"
          class="result-item"
          @tap="goToChat(item)"
        >
          <view class="result-header">
            <view class="result-role" :class="item.role">
              <text class="role-icon">{{ item.role === 'user' ? '👤' : '🤖' }}</text>
              <text class="role-text">{{ item.role === 'user' ? '我' : 'AI助手' }}</text>
            </view>
            <text class="result-time">{{ formatDate(item.created_at) }}</text>
          </view>
          <text class="result-content" v-html="highlightKeyword(item.content)"></text>
        </view>

        <!-- 加载状态 -->
        <view class="load-status">
          <view v-if="loading" class="loading-indicator">
            <text class="loading-text">加载中...</text>
          </view>
          <view v-else-if="!hasMore && results.length > 0" class="no-more">
            <text class="no-more-text">— 没有更多了 —</text>
          </view>
        </view>
      </view>
    </scroll-view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { searchMessages } from '@/api'
import type { SearchResult } from '@/api'

const keyword = ref('')
const results = ref<SearchResult[]>([])
const page = ref(1)
const pageSize = 20
const total = ref(0)
const hasMore = ref(true)
const loading = ref(false)
const hasSearched = ref(false)
const currentThreadId = ref('')

onLoad((options) => {
  if (options?.thread_id) {
    currentThreadId.value = options.thread_id
  }
})

// 输入事件
function onInput() {
  // 可以添加防抖搜索
}

// 清空关键词
function clearKeyword() {
  keyword.value = ''
  results.value = []
  hasSearched.value = false
  total.value = 0
}

// 执行搜索
async function handleSearch() {
  if (!keyword.value.trim()) {
    uni.showToast({ title: '请输入关键词', icon: 'none' })
    return
  }

  page.value = 1
  results.value = []
  hasMore.value = true
  hasSearched.value = true
  await search()
}

// 搜索请求
async function search() {
  if (loading.value) return

  loading.value = true
  try {
    const res = await searchMessages(
      keyword.value.trim(),
      currentThreadId.value || undefined,
      page.value,
      pageSize
    )

    if (String(res.code) === '200') {
      const data = res.data
      if (page.value === 1) {
        results.value = data.list || []
      } else {
        results.value = [...results.value, ...(data.list || [])]
      }
      total.value = data.total || 0
      hasMore.value = results.value.length < total.value
    }
  } catch (e) {
    console.error('搜索失败:', e)
    uni.showToast({ title: '搜索失败', icon: 'none' })
  } finally {
    loading.value = false
  }
}

// 加载更多
function loadMore() {
  if (!hasMore.value || loading.value) return
  page.value++
  search()
}

// 跳转到对话
function goToChat(item: SearchResult) {
  uni.navigateTo({
    url: `/pages/index/index?thread_id=${item.thread_id}`
  })
}

// 返回
function goBack() {
  uni.navigateBack()
}

// 高亮关键词
function highlightKeyword(content: string) {
  if (!keyword.value.trim() || !content) return content
  const regex = new RegExp(`(${keyword.value.trim()})`, 'gi')
  return content.replace(regex, '<span class="highlight">$1</span>')
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

/* 搜索头部 */
.search-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
  padding: 12rpx 24rpx;
  padding-top: calc(12rpx + env(safe-area-inset-top));
}

.search-bar {
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-radius: 20rpx;
  padding: 16rpx 20rpx;
  display: flex;
  align-items: center;
  gap: 16rpx;
  box-shadow: 0 4rpx 24rpx rgba(0, 0, 0, 0.08);
  border: 1rpx solid rgba(255, 255, 255, 0.5);
}

.btn-back {
  width: 56rpx;
  height: 56rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.btn-back-icon {
  font-size: 32rpx;
  color: #333;
}

.search-input-wrapper {
  flex: 1;
  display: flex;
  align-items: center;
  background: #f3f4f6;
  border-radius: 12rpx;
  padding: 12rpx 16rpx;
  gap: 12rpx;
}

.search-icon {
  font-size: 28rpx;
  flex-shrink: 0;
}

.search-input {
  flex: 1;
  font-size: 28rpx;
  color: #333;
}

.search-placeholder {
  color: #9ca3af;
}

.btn-clear {
  width: 40rpx;
  height: 40rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #d1d5db;
  border-radius: 50%;
  flex-shrink: 0;
}

.clear-icon {
  font-size: 20rpx;
  color: #666;
}

.btn-search {
  padding: 12rpx 20rpx;
  background: linear-gradient(135deg, #f97316 0%, #ea580c 100%);
  border-radius: 12rpx;
  flex-shrink: 0;
}

.btn-search:active {
  opacity: 0.9;
}

.btn-search-text {
  font-size: 28rpx;
  color: #fff;
  font-weight: 500;
}

/* 结果列表 */
.result-list {
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
  width: 120rpx;
  height: 120rpx;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 24rpx;
}

.empty-icon {
  font-size: 56rpx;
}

.empty-title {
  font-size: 32rpx;
  font-weight: 600;
  color: #374151;
}

.empty-subtitle {
  font-size: 26rpx;
  color: #9ca3af;
  margin-top: 12rpx;
}

/* 加载状态 */
.loading-state {
  display: flex;
  align-items: center;
  justify-content: center;
  padding-top: 30vh;
}

.loading-text {
  font-size: 28rpx;
  color: #9ca3af;
}

/* 结果容器 */
.results-container {
  padding: 16rpx 24rpx;
}

.result-count {
  padding: 12rpx 0;
}

.count-text {
  font-size: 24rpx;
  color: #9ca3af;
}

/* 结果项 */
.result-item {
  background: rgba(255, 255, 255, 0.9);
  border-radius: 16rpx;
  padding: 24rpx;
  margin-bottom: 16rpx;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.04);
  border: 1rpx solid rgba(255, 255, 255, 0.5);
}

.result-item:active {
  background: rgba(255, 255, 255, 0.95);
}

.result-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12rpx;
}

.result-role {
  display: flex;
  align-items: center;
  gap: 8rpx;
  padding: 6rpx 12rpx;
  border-radius: 8rpx;
}

.result-role.user {
  background: rgba(59, 130, 246, 0.1);
}

.result-role.assistant {
  background: rgba(249, 115, 22, 0.1);
}

.role-icon {
  font-size: 24rpx;
}

.role-text {
  font-size: 22rpx;
  font-weight: 500;
}

.result-role.user .role-text {
  color: #3b82f6;
}

.result-role.assistant .role-text {
  color: #f97316;
}

.result-time {
  font-size: 22rpx;
  color: #9ca3af;
}

.result-content {
  font-size: 28rpx;
  color: #374151;
  line-height: 1.6;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.result-content :deep(.highlight) {
  background: rgba(249, 115, 22, 0.2);
  color: #ea580c;
  padding: 2rpx 4rpx;
  border-radius: 4rpx;
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

.no-more-text {
  font-size: 24rpx;
  color: #d1d5db;
}
</style>
