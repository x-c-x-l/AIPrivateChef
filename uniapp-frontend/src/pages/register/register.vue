<template>
  <view class="register-page">
    <view class="header">
      <text class="title">注册账号</text>
      <text class="subtitle">创建您的专属厨师账号</text>
    </view>

    <view class="form-area">
      <view class="input-group">
        <text class="label">用户名 *</text>
        <input
          class="input"
          v-model="form.username"
          placeholder="请输入用户名"
          maxlength="30"
        />
      </view>

      <view class="input-group">
        <text class="label">密码 *</text>
        <input
          class="input"
          v-model="form.password"
          placeholder="请输入密码"
          password
          maxlength="30"
        />
      </view>

      <view class="input-group">
        <text class="label">昵称 *</text>
        <input
          class="input"
          v-model="form.name"
          placeholder="请输入昵称"
          maxlength="20"
        />
      </view>

      <view class="input-group">
        <text class="label">邮箱</text>
        <input
          class="input"
          v-model="form.email"
          placeholder="请输入邮箱（选填）"
          maxlength="50"
        />
      </view>

      <view class="input-group">
        <text class="label">手机号</text>
        <input
          class="input"
          v-model="form.phone"
          placeholder="请输入手机号（选填）"
          maxlength="11"
          type="number"
        />
      </view>

      <button class="btn-register" :loading="loading" @click="handleRegister">
        注 册
      </button>

      <view class="login-link" @click="goLogin">
        <text>已有账号？</text>
        <text class="link">去登录</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { registerApi } from '@/api/index'

const form = reactive({
  username: '',
  password: '',
  name: '',
  email: '',
  phone: '',
})
const loading = ref(false)

async function handleRegister() {
  if (!form.username.trim()) {
    uni.showToast({ title: '请输入用户名', icon: 'none' })
    return
  }
  if (!form.password.trim()) {
    uni.showToast({ title: '请输入密码', icon: 'none' })
    return
  }
  if (!form.name.trim()) {
    uni.showToast({ title: '请输入昵称', icon: 'none' })
    return
  }

  loading.value = true
  try {
    const res = await registerApi({
      username: form.username.trim(),
      password: form.password.trim(),
      name: form.name.trim(),
      email: form.email.trim() || undefined,
      phone: form.phone.trim() || undefined,
    })

    uni.showToast({ title: res.message || '注册成功', icon: 'success' })
    setTimeout(() => {
      uni.navigateBack()
    }, 800)
  } catch (e: any) {
    uni.showToast({ title: e.message || '注册失败', icon: 'none' })
  } finally {
    loading.value = false
  }
}

function goLogin() {
  uni.navigateBack()
}
</script>

<style lang="scss" scoped>
.register-page {
  height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  background: linear-gradient(180deg, #fffbeb 0%, #fff7ed 50%, #fef2f2 100%);
  overflow-y: auto;
}

.header {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 60rpx;
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
  margin-bottom: 30rpx;
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

.btn-register {
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

.btn-register::after {
  border: none;
}

.login-link {
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
