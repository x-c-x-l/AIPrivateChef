<template>
  <view class="input-container">
    <!-- 图片预览 -->
    <view v-if="previewUrl" class="preview-area">
      <view class="preview-wrapper">
        <image :src="previewUrl" mode="aspectFill" class="preview-image" />
        <view class="preview-close" @tap="removeFile">
          <text class="close-icon">✕</text>
        </view>
      </view>
    </view>

    <!-- 输入区域 -->
    <view class="input-bar">
      <!-- 图片上传按钮 -->
      <view class="btn-icon" @tap="chooseImage" :class="{ disabled }">
        <text class="icon-text">🖼</text>
      </view>

      <!-- 文本输入框 -->
      <textarea v-model="text" class="text-input" placeholder="描述你有的食材..." placeholder-class="placeholder"
        :disabled="disabled" :maxlength="2000" auto-height :style="{ height: inputHeight }" @confirm="handleSend"
        @keydown="onKeydown" @linechange="onLineChange" />

      <!-- 发送按钮 -->
      <view class="btn-send" :class="{ disabled: disabled || (!text.trim() && !file) }" @tap="handleSend">
        <text class="send-icon">➤</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const props = defineProps<{
  disabled?: boolean
}>()

const emit = defineEmits<{
  send: [text: string, file?: any]
}>()

const text = ref('')
const file = ref<any>(null)
const previewUrl = ref('')
const inputHeight = ref('72rpx')

// 选择图片
function chooseImage() {
  if (props.disabled) return

  uni.chooseImage({
    count: 1,
    sizeType: ['compressed'],
    sourceType: ['album', 'camera'],
    success: (res) => {
      const tempFile = res.tempFiles[0]
      file.value = tempFile
      previewUrl.value = tempFile.path
      console.log(file, '----file');
    },
  })
}

// 移除文件
function removeFile() {
  file.value = null
  previewUrl.value = ''
}

// 发送消息
function handleSend() {
  if (props.disabled) return
  if (!text.value.trim() && !file.value) return

  emit('send', text.value.trim(), file.value)
  text.value = ''
  removeFile()
  inputHeight.value = '72rpx'
}

// 回车发送，Shift+Enter 换行
function onKeydown(e: any) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault?.()
    handleSend()
  }
}

// 输入框高度自适应
function onLineChange(e: any) {
  const lineCount = e.detail?.lineCount || 1
  const height = Math.min(lineCount * 40 + 32, 200)
  inputHeight.value = `${height}rpx`
}
</script>

<style scoped>
.input-container {
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-top: 1rpx solid rgba(0, 0, 0, 0.06);
  padding: 16rpx 24rpx;
  padding-bottom: calc(16rpx + env(safe-area-inset-bottom));
}

.preview-area {
  margin-bottom: 16rpx;
}

.preview-wrapper {
  position: relative;
  display: inline-block;
}

.preview-image {
  width: 160rpx;
  height: 160rpx;
  border-radius: 16rpx;
}

.preview-close {
  position: absolute;
  top: -12rpx;
  right: -12rpx;
  width: 40rpx;
  height: 40rpx;
  background: #ef4444;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-icon {
  color: #ffffff;
  font-size: 20rpx;
  font-weight: bold;
}

.input-bar {
  display: flex;
  align-items: flex-end;
  gap: 16rpx;
}

.btn-icon {
  width: 72rpx;
  height: 72rpx;
  border-radius: 50%;
  background: #f9fafb;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: all 0.2s;
}

.btn-icon:active {
  background: #fff7ed;
  transform: scale(0.95);
}

.btn-icon.disabled {
  opacity: 0.5;
}

.icon-text {
  font-size: 36rpx;
}

.text-input {
  flex: 1;
  background: #f3f4f6;
  border-radius: 24rpx;
  padding: 16rpx 24rpx;
  font-size: 28rpx;
  line-height: 1.5;
  min-height: 72rpx;
  max-height: 400rpx;
}

.placeholder {
  color: #9ca3af;
}

.btn-send {
  width: 72rpx;
  height: 72rpx;
  border-radius: 50%;
  background: linear-gradient(135deg, #f97316 0%, #ef4444 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 4rpx 16rpx rgba(249, 115, 22, 0.4);
  transition: all 0.2s;
}

.btn-send:active {
  transform: scale(0.92);
}

.btn-send.disabled {
  background: linear-gradient(135deg, #d1d5db 0%, #9ca3af 100%);
  box-shadow: none;
}

.send-icon {
  color: #ffffff;
  font-size: 32rpx;
  font-weight: bold;
}
</style>
