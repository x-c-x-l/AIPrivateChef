<template>
  <view class="login-page">
    <view class="logo-area">
      <image class="logo" src="/static/logo.png" mode="aspectFit" />
      <text class="title">AI 私人厨师</text>
      <text class="subtitle">智能烹饪，从这里开始</text>
    </view>

    <view class="form-area">
      <view class="input-group">
        <text class="label">用户名</text>
        <input
          class="input"
          v-model="form.username"
          placeholder="请输入用户名"
          maxlength="30"
        />
      </view>

      <view class="input-group">
        <text class="label">密码</text>
        <input
          class="input"
          v-model="form.password"
          placeholder="请输入密码"
          password
          maxlength="30"
        />
      </view>

      <button class="btn-login" :loading="loading" @click="handleLogin">
        登 录
      </button>

      <view class="register-link" @click="goRegister">
        <text>还没有账号？</text>
        <text class="link">立即注册</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { loginApi } from '@/api/index'

const form = reactive({
  username: '',
  password: '',
})
const loading = ref(false)

async function handleLogin() {
  if (!form.username.trim()) {
    uni.showToast({ title: '请输入用户名', icon: 'none' })
    return
  }
  if (!form.password.trim()) {
    uni.showToast({ title: '请输入密码', icon: 'none' })
    return
  }

  loading.value = true
  try {
    const res = await loginApi({
      username: form.username.trim(),
      password: form.password.trim(),
    })

    if (String(res.code) === '200' && res.data?.token) {
      // 存储 token 和用户信息
      uni.setStorageSync('token', res.data.token)
      uni.setStorageSync('userInfo', {
        id: res.data.id,
        username: res.data.username,
      })

      uni.showToast({ title: '登录成功', icon: 'success' })
      setTimeout(() => {
        uni.reLaunch({ url: '/pages/index/index' })
      }, 800)
    } else {
      uni.showToast({ title: res.message || '登录失败', icon: 'none' })
    }
  } catch (e: any) {
    uni.showToast({ title: e.message || '网络异常', icon: 'none' })
  } finally {
    loading.value = false
  }
}

function goRegister() {
  uni.navigateTo({ url: '/pages/register/register' })
}
</script>

<style lang="scss" scoped>
.login-page {
  height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: linear-gradient(180deg, #fffbeb 0%, #fff7ed 50%, #fef2f2 100%);
  overflow-y: auto;
}

.logo-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 80rpx;
}

.logo {
  width: 160rpx;
  height: 160rpx;
  margin-bottom: 24rpx;
}

.title {
  font-size: 44rpx;
  font-weight: bold;
  color: #1a1a1a;
  margin-bottom: 12rpx;
}

.subtitle {
  font-size: 28rpx;
  color: #999;
}

.form-area {
  width: 100%;
  max-width: 650rpx;
}

.input-group {
  margin-bottom: 36rpx;
}

.label {
  font-size: 28rpx;
  color: #333;
  margin-bottom: 12rpx;
  display: block;
}

.input {
  width: 100%;
  height: 88rpx;
  background: #fff;
  border: 2rpx solid #e5e5e5;
  border-radius: 16rpx;
  padding: 0 28rpx;
  font-size: 30rpx;
  box-sizing: border-box;
}

.input:focus {
  border-color: #f59e0b;
}

.btn-login {
  width: 100%;
  height: 88rpx;
  line-height: 88rpx;
  background: linear-gradient(135deg, #f59e0b 0%, #ef4444 100%);
  color: #fff;
  font-size: 32rpx;
  font-weight: bold;
  border-radius: 16rpx;
  border: none;
  margin-top: 20rpx;
}

.btn-login::after {
  border: none;
}

.register-link {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 36rpx;
  font-size: 26rpx;
  color: #999;
}

.link {
  color: #f59e0b;
  margin-left: 8rpx;
  font-weight: 500;
}
</style>
