<template>
  <!-- 遮罩层 -->
  <view v-if="visible" class="sidebar-mask" @tap="$emit('close')" />
  <!-- 侧栏面板 -->
  <view class="sidebar" :class="{ 'sidebar-open': visible }">
    <!-- 顶部：Logo + 标题 + 关闭 -->
    <view class="sidebar-header">
      <view class="sidebar-brand">
        <view class="sidebar-logo">
          <text class="sidebar-logo-icon">👨‍🍳</text>
        </view>
        <text class="sidebar-title">AI 私人厨师</text>
      </view>
      <view class="btn-close" @tap="$emit('close')">
        <text class="btn-close-icon">✕</text>
      </view>
    </view>

    <!-- 新建会话和搜索按钮 -->
    <view class="action-buttons">
      <view class="btn-new" @tap="$emit('new-chat')">
        <text class="btn-new-icon">＋</text>
        <text class="btn-new-text">新建会话</text>
      </view>
      <view class="btn-search" @tap="goToSearch">
        <text class="btn-search-icon">🔍</text>
        <text class="btn-search-text">搜索</text>
      </view>
    </view>

    <!-- 历史会话列表 -->
    <view class="history-section">
      <text class="section-label">历史会话</text>
      <scroll-view class="history-list" scroll-y @scrolltolower="$emit('load-more')">
        <view v-if="threads.length === 0" class="history-empty">
          <text class="history-empty-text">暂无历史会话</text>
        </view>
        <view
          v-for="item in threads"
          :key="item.id"
          class="history-item"
          :class="{ 'history-item-active': item.id === currentThreadId }"
          @tap="$emit('select-thread', item.id)"
        >
          <text class="history-item-icon">💬</text>
          <view class="history-item-info">
            <text class="history-item-title">{{ item.content || '新会话' }}</text>
            <text class="history-item-time">{{ dateFormatter(item.created_at) }}</text>
          </view>
          <view class="btn-delete" @tap.stop="$emit('delete-thread', item.id)">
            <text class="btn-delete-icon">🗑</text>
          </view>
        </view>
        <!-- 加载更多 -->
        <view v-if="hasMore" class="sidebar-load-more">
          <text class="sidebar-load-more-text">{{ loading ? '加载中...' : '加载更多' }}</text>
        </view>
      </scroll-view>
    </view>

    <!-- 底部：用户信息和退出登录 -->
    <view class="sidebar-footer">
      <view class="user-info" @tap="goToProfile">
        <view class="user-avatar">
          <text class="user-avatar-text">👤</text>
        </view>
        <text class="user-name">{{ username || '用户' }}</text>
      </view>
      <view class="btn-logout" @tap="$emit('logout')">
        <text class="btn-logout-icon">⏻</text>
        <text class="btn-logout-text">退出登录</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import {dateFormatter} from '@/utils/formatTime.ts'
export interface ChatRecord {
  id: string
  user_id: number
  name: string
  content: string
  created_at: string
}

defineProps<{
  visible: boolean
  threads: ChatRecord[]
  currentThreadId: string
  username: string
  hasMore?: boolean
  loading?: boolean
}>()

defineEmits<{
  (e: 'close'): void
  (e: 'new-chat'): void
  (e: 'select-thread', id: string): void
  (e: 'delete-thread', id: string): void
  (e: 'logout'): void
  (e: 'load-more'): void
}>()

// 跳转到个人中心
function goToProfile() {
  uni.navigateTo({
    url: '/pages/profile/profile'
  })
}

// 跳转到搜索页面
function goToSearch() {
  uni.navigateTo({
    url: '/pages/search/search'
  })
}

</script>

<style lang="scss" scoped>
/* 遮罩层 */
.sidebar-mask {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.4);
  z-index: 998;
  animation: fadeIn 0.25s ease;
}

/* 侧栏面板 */
.sidebar {
  position: fixed;
  top: 0;
  left: 0;
  bottom: 0;
  width: 560rpx;
  background: #fff;
  z-index: 999;
  display: flex;
  flex-direction: column;
  transform: translateX(-100%);
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 8rpx 0 40rpx rgba(0, 0, 0, 0.1);
}

.sidebar-open {
  transform: translateX(0);
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

/* 顶部 */
.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 48rpx 32rpx 32rpx;
  padding-top: calc(48rpx + env(safe-area-inset-top));
  border-bottom: 1rpx solid #f0f0f0;
}

.sidebar-brand {
  display: flex;
  align-items: center;
  gap: 20rpx;
}

.sidebar-logo {
  width: 72rpx;
  height: 72rpx;
  background: linear-gradient(135deg, #f97316 0%, #ef4444 100%);
  border-radius: 20rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.sidebar-logo-icon {
  font-size: 40rpx;
}

.sidebar-title {
  font-size: 34rpx;
  font-weight: bold;
  color: #1a1a1a;
}

.btn-close {
  width: 56rpx;
  height: 56rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: #f5f5f5;
}

.btn-close:active {
  background: #e5e5e5;
}

.btn-close-icon {
  font-size: 28rpx;
  color: #666;
}

/* 操作按钮区域 */
.action-buttons {
  display: flex;
  gap: 16rpx;
  margin: 24rpx 32rpx;
}

/* 新建会话按钮 */
.btn-new {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8rpx;
  padding: 24rpx 0;
  background: linear-gradient(135deg, #f97316 0%, #ef4444 100%);
  border-radius: 16rpx;
}

.btn-new:active {
  opacity: 0.85;
  transform: scale(0.98);
}

.btn-new-icon {
  font-size: 32rpx;
  color: #fff;
  font-weight: bold;
}

.btn-new-text {
  font-size: 28rpx;
  color: #fff;
  font-weight: 600;
}

/* 搜索按钮 */
.btn-search {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8rpx;
  padding: 24rpx 0;
  background: rgba(0, 0, 0, 0.05);
  border-radius: 16rpx;
}

.btn-search:active {
  background: rgba(0, 0, 0, 0.1);
  transform: scale(0.98);
}

.btn-search-icon {
  font-size: 28rpx;
}

.btn-search-text {
  font-size: 28rpx;
  color: #666;
  font-weight: 500;
}

/* 历史会话 */
.history-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  padding: 0 32rpx;
  height: 0;
}

.section-label {
  font-size: 24rpx;
  color: #999;
  margin-bottom: 16rpx;
  font-weight: 500;
}

.history-list {
  flex: 1;
  height: 0;
}

.history-empty {
  display: flex;
  align-items: center;
  justify-content: center;
  padding-top: 80rpx;
}

.history-empty-text {
  font-size: 26rpx;
  color: #ccc;
}

.history-item {
  display: flex;
  align-items: center;
  gap: 20rpx;
  padding: 24rpx 20rpx;
  border-radius: 14rpx;
  margin-bottom: 8rpx;
  transition: background 0.15s;
}

.history-item:active {
  background: #f5f5f5;
}

.history-item-active {
  background: #fff7ed;
  border: 1rpx solid #fed7aa;
}

.history-item-icon {
  font-size: 32rpx;
  flex-shrink: 0;
}

.history-item-info {
  flex: 1;
  overflow: hidden;
}

.history-item-title {
  font-size: 28rpx;
  color: #333;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  display: block;
}

.history-item-time {
  font-size: 22rpx;
  color: #bbb;
  margin-top: 6rpx;
  display: block;
}

.btn-delete {
  flex-shrink: 0;
  width: 48rpx;
  height: 48rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 10rpx;
  margin-left: 8rpx;
}

.btn-delete:active {
  background: rgba(239, 68, 68, 0.12);
}

.btn-delete-icon {
  font-size: 28rpx;
}

/* 底部 */
.sidebar-footer {
  border-top: 1rpx solid #f0f0f0;
  padding: 24rpx 32rpx;
  padding-bottom: calc(24rpx + env(safe-area-inset-bottom));
}

.user-info {
  display: flex;
  align-items: center;
  gap: 16rpx;
  margin-bottom: 20rpx;
}

.user-avatar {
  width: 60rpx;
  height: 60rpx;
  background: #f0f0f0;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.user-avatar-text {
  font-size: 30rpx;
}

.user-name {
  font-size: 28rpx;
  color: #333;
  font-weight: 500;
}

.btn-logout {
  display: flex;
  align-items: center;
  gap: 12rpx;
  padding: 20rpx 24rpx;
  background: rgba(239, 68, 68, 0.08);
  border-radius: 12rpx;
}

.btn-logout:active {
  background: rgba(239, 68, 68, 0.15);
}

.btn-logout-icon {
  font-size: 28rpx;
  color: #ef4444;
}

.btn-logout-text {
  font-size: 28rpx;
  color: #ef4444;
  font-weight: 500;
}

/* 加载更多 */
.sidebar-load-more {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24rpx 0;
}

.sidebar-load-more-text {
  font-size: 24rpx;
  color: #f97316;
}
</style>
