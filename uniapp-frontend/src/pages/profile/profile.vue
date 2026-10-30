<template>
  <view class="page">
    <!-- 顶部标题栏 -->
    <view class="header">
      <view class="header-content">
        <view class="btn-back" @tap="goBack">
          <text class="btn-back-icon">←</text>
        </view>
        <text class="header-title">个人中心</text>
        <view class="header-placeholder" />
      </view>
    </view>

    <!-- 用户信息卡片 -->
    <view class="user-card">
      <view class="user-avatar-large">
        <text class="user-avatar-emoji">👤</text>
      </view>
      <view class="user-details">
        <text class="user-name">{{ username || '用户' }}</text>
        <text class="user-id">ID: {{ userId }}</text>
      </view>
    </view>

    <!-- 统计信息 -->
    <view class="stats-section">
      <view class="stat-item" @tap="goToHistory">
        <text class="stat-number">{{ stats.total_chats || 0 }}</text>
        <text class="stat-label">对话次数</text>
      </view>
      <view class="stat-divider" />
      <view class="stat-item" @tap="goToFavorites">
        <text class="stat-number">{{ stats.total_favorites || 0 }}</text>
        <text class="stat-label">收藏食谱</text>
      </view>
    </view>

    <!-- 功能菜单 -->
    <view class="menu-section">
      <view class="menu-item" @tap="goToFavorites">
        <view class="menu-icon-wrapper">
          <text class="menu-icon">⭐</text>
        </view>
        <text class="menu-text">我的收藏</text>
        <view class="menu-badge" v-if="stats.total_favorites > 0">
          <text class="badge-text">{{ stats.total_favorites }}</text>
        </view>
        <text class="menu-arrow">›</text>
      </view>

      <view class="menu-item" @tap="goToHistory">
        <view class="menu-icon-wrapper">
          <text class="menu-icon">📋</text>
        </view>
        <text class="menu-text">历史会话</text>
        <text class="menu-arrow">›</text>
      </view>

      <view class="menu-item" @tap="goToPreferences">
        <view class="menu-icon-wrapper">
          <text class="menu-icon">⚙️</text>
        </view>
        <text class="menu-text">偏好设置</text>
        <text class="menu-arrow">›</text>
      </view>

      <view class="menu-item" @tap="clearCache">
        <view class="menu-icon-wrapper">
          <text class="menu-icon">🗑️</text>
        </view>
        <text class="menu-text">清除缓存</text>
        <text class="menu-arrow">›</text>
      </view>

      <view class="menu-item" @tap="showAbout">
        <view class="menu-icon-wrapper">
          <text class="menu-icon">ℹ️</text>
        </view>
        <text class="menu-text">关于我们</text>
        <text class="menu-arrow">›</text>
      </view>
    </view>

    <!-- 退出登录 -->
    <view class="logout-section">
      <view class="btn-logout" @tap="handleLogout">
        <text class="logout-text">退出登录</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { getUserStats } from '@/api'

// 用户信息
const username = ref('')
const userId = ref('')
const stats = ref({ total_favorites: 0, total_chats: 0 })

onLoad(() => {
  // 获取用户信息
  const userInfo = uni.getStorageSync('userInfo')
  if (userInfo) {
    username.value = userInfo.username || ''
    userId.value = userInfo.id || ''
  }

  // 加载统计信息
  loadStats()
})

// 加载统计信息
async function loadStats() {
  try {
    const res = await getUserStats()
    if (String(res.code) === '200') {
      stats.value = res.data || { total_favorites: 0, total_chats: 0 }
    }
  } catch (e) {
    console.error('加载统计信息失败:', e)
  }
}

// 返回上一页
function goBack() {
  uni.navigateBack()
}

// 跳转到收藏列表
function goToFavorites() {
  uni.navigateTo({
    url: '/pages/profile/favorites'
  })
}

// 跳转到历史会话
function goToHistory() {
  // 返回主页并打开侧边栏
  uni.navigateBack()
  // 通过存储标记来触发侧边栏打开
  uni.setStorageSync('openSidebar', true)
}

// 跳转到偏好设置
function goToPreferences() {
  uni.navigateTo({
    url: '/pages/profile/preferences'
  })
}

// 清除缓存
function clearCache() {
  uni.showModal({
    title: '提示',
    content: '确定要清除缓存吗？',
    success: (res) => {
      if (res.confirm) {
        // 清除除了token和userInfo外的缓存
        uni.removeStorageSync('thread_id')
        uni.removeStorageSync('openSidebar')
        uni.showToast({ title: '清除成功', icon: 'success' })
      }
    }
  })
}

// 显示关于
function showAbout() {
  uni.showModal({
    title: 'AI 私人厨师',
    content: '版本：1.0.0\n\n您的智能美食助手，帮您识别食材并推荐美味食谱。',
    showCancel: false
  })
}

// 退出登录
function handleLogout() {
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
    }
  })
}
</script>

<style scoped>
.page {
  min-height: 100vh;
  background: linear-gradient(135deg, #fffbeb 0%, #fff7ed 50%, #fef2f2 100%);
  padding-bottom: 40rpx;
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

/* 用户信息卡片 */
.user-card {
  margin: 140rpx 32rpx 32rpx;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 24rpx;
  padding: 40rpx;
  display: flex;
  align-items: center;
  gap: 32rpx;
  box-shadow: 0 8rpx 32rpx rgba(0, 0, 0, 0.06);
  border: 1rpx solid rgba(255, 255, 255, 0.5);
}

.user-avatar-large {
  width: 120rpx;
  height: 120rpx;
  background: linear-gradient(135deg, #f97316 0%, #ef4444 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8rpx 24rpx rgba(249, 115, 22, 0.3);
}

.user-avatar-emoji {
  font-size: 60rpx;
}

.user-details {
  flex: 1;
}

.user-name {
  font-size: 36rpx;
  font-weight: bold;
  color: #1a1a1a;
  display: block;
}

.user-id {
  font-size: 24rpx;
  color: #999;
  margin-top: 8rpx;
  display: block;
}

/* 统计信息 */
.stats-section {
  margin: 0 32rpx 32rpx;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 24rpx;
  padding: 32rpx;
  display: flex;
  align-items: center;
  justify-content: space-around;
  box-shadow: 0 8rpx 32rpx rgba(0, 0, 0, 0.06);
  border: 1rpx solid rgba(255, 255, 255, 0.5);
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8rpx;
  padding: 16rpx 32rpx;
  border-radius: 16rpx;
  transition: background 0.2s;
}

.stat-item:active {
  background: rgba(0, 0, 0, 0.04);
}

.stat-number {
  font-size: 48rpx;
  font-weight: bold;
  background: linear-gradient(135deg, #f97316 0%, #ef4444 100%);
  -webkit-background-clip: text;
  color: transparent;
}

.stat-label {
  font-size: 24rpx;
  color: #666;
}

.stat-divider {
  width: 1rpx;
  height: 60rpx;
  background: #e5e7eb;
}

/* 功能菜单 */
.menu-section {
  margin: 0 32rpx 32rpx;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 24rpx;
  overflow: hidden;
  box-shadow: 0 8rpx 32rpx rgba(0, 0, 0, 0.06);
  border: 1rpx solid rgba(255, 255, 255, 0.5);
}

.menu-item {
  display: flex;
  align-items: center;
  padding: 32rpx;
  border-bottom: 1rpx solid #f3f4f6;
  transition: background 0.2s;
}

.menu-item:last-child {
  border-bottom: none;
}

.menu-item:active {
  background: #f9fafb;
}

.menu-icon-wrapper {
  width: 48rpx;
  height: 48rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 24rpx;
}

.menu-icon {
  font-size: 36rpx;
}

.menu-text {
  flex: 1;
  font-size: 30rpx;
  color: #333;
}

.menu-badge {
  background: linear-gradient(135deg, #f97316 0%, #ef4444 100%);
  border-radius: 20rpx;
  padding: 4rpx 16rpx;
  margin-right: 16rpx;
}

.badge-text {
  font-size: 22rpx;
  color: #fff;
  font-weight: 600;
}

.menu-arrow {
  font-size: 36rpx;
  color: #ccc;
}

/* 退出登录 */
.logout-section {
  margin: 0 32rpx;
  padding-top: 20rpx;
}

.btn-logout {
  background: rgba(239, 68, 68, 0.1);
  border-radius: 16rpx;
  padding: 28rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-logout:active {
  background: rgba(239, 68, 68, 0.2);
}

.logout-text {
  font-size: 30rpx;
  color: #ef4444;
  font-weight: 500;
}
</style>
