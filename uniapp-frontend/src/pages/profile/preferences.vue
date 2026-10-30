<template>
  <view class="page">
    <!-- 顶部标题栏 -->
    <view class="header">
      <view class="header-content">
        <view class="btn-back" @tap="goBack">
          <text class="btn-back-icon">←</text>
        </view>
        <text class="header-title">偏好设置</text>
        <view class="btn-save" @tap="savePreferences">
          <text class="save-text">保存</text>
        </view>
      </view>
    </view>

    <!-- 设置内容 -->
    <scroll-view class="settings-list" scroll-y>
      <!-- 饮食限制 -->
      <view class="settings-section">
        <text class="section-title">饮食限制</text>
        <view class="settings-card">
          <view class="setting-item">
            <text class="setting-label">素食主义</text>
            <switch :checked="isVegetarian" @change="isVegetarian = $event.detail.value" color="#f97316" />
          </view>
          <view class="setting-item">
            <text class="setting-label">无麸质</text>
            <switch :checked="isGlutenFree" @change="isGlutenFree = $event.detail.value" color="#f97316" />
          </view>
          <view class="setting-item">
            <text class="setting-label">低糖饮食</text>
            <switch :checked="isLowSugar" @change="isLowSugar = $event.detail.value" color="#f97316" />
          </view>
          <view class="setting-item">
            <text class="setting-label">低脂饮食</text>
            <switch :checked="isLowFat" @change="isLowFat = $event.detail.value" color="#f97316" />
          </view>
        </view>
      </view>

      <!-- 过敏源 -->
      <view class="settings-section">
        <text class="section-title">过敏源（不使用这些食材）</text>
        <view class="settings-card">
          <!-- 已选标签 -->
          <view v-if="selectedAllergies.length > 0" class="selected-tags-wrapper">
            <view
              v-for="tag in selectedAllergies"
              :key="'a-' + tag"
              class="tag-item tag-active tag-with-delete"
            >
              <text class="tag-text">{{ tag }}</text>
              <text class="tag-delete" @tap.stop="removeAllergy(tag)">✕</text>
            </view>
          </view>
          <!-- 预设选项 -->
          <view class="tags-wrapper">
            <view
              v-for="tag in allergyOptions"
              :key="tag"
              class="tag-item"
              :class="{ 'tag-active': selectedAllergies.includes(tag) }"
              @tap="toggleAllergy(tag)"
            >
              <text class="tag-text">{{ tag }}</text>
            </view>
          </view>
          <!-- 自定义输入 -->
          <view class="custom-input-wrapper">
            <input
              v-model="customAllergy"
              class="custom-input"
              placeholder="输入自定义过敏源..."
              @confirm="addAllergy"
            />
            <view class="btn-add" :class="{ 'btn-add-disabled': !customAllergy.trim() }" @tap="addAllergy">
              <text class="btn-add-text">添加</text>
            </view>
          </view>
        </view>
      </view>

      <!-- 偏好菜系 -->
      <view class="settings-section">
        <text class="section-title">偏好菜系</text>
        <view class="settings-card">
          <!-- 已选标签 -->
          <view v-if="selectedCuisines.length > 0" class="selected-tags-wrapper">
            <view
              v-for="tag in selectedCuisines"
              :key="'c-' + tag"
              class="tag-item tag-active tag-with-delete"
            >
              <text class="tag-text">{{ tag }}</text>
              <text class="tag-delete" @tap.stop="removeCuisine(tag)">✕</text>
            </view>
          </view>
          <!-- 预设选项 -->
          <view class="tags-wrapper">
            <view
              v-for="tag in cuisineOptions"
              :key="tag"
              class="tag-item"
              :class="{ 'tag-active': selectedCuisines.includes(tag) }"
              @tap="toggleCuisine(tag)"
            >
              <text class="tag-text">{{ tag }}</text>
            </view>
          </view>
          <!-- 自定义输入 -->
          <view class="custom-input-wrapper">
            <input
              v-model="customCuisine"
              class="custom-input"
              placeholder="输入自定义菜系..."
              @confirm="addCuisine"
            />
            <view class="btn-add" :class="{ 'btn-add-disabled': !customCuisine.trim() }" @tap="addCuisine">
              <text class="btn-add-text">添加</text>
            </view>
          </view>
        </view>
      </view>

      <!-- 烹饪水平 -->
      <view class="settings-section">
        <text class="section-title">烹饪水平</text>
        <view class="settings-card">
          <view
            v-for="level in skillLevels"
            :key="level.value"
            class="setting-item"
            @tap="cookingSkill = level.value"
          >
            <view class="skill-info">
              <text class="skill-icon">{{ level.icon }}</text>
              <view class="skill-text-wrapper">
                <text class="skill-name">{{ level.label }}</text>
                <text class="skill-desc">{{ level.description }}</text>
              </view>
            </view>
            <view class="radio-btn" :class="{ 'radio-active': cookingSkill === level.value }">
              <view v-if="cookingSkill === level.value" class="radio-dot" />
            </view>
          </view>
        </view>
      </view>

      <!-- 摘要设置 -->
      <view class="settings-section">
        <text class="section-title">对话摘要设置</text>
        <view class="settings-card">
          <view class="setting-item">
            <text class="setting-label">自动摘要</text>
            <switch :checked="summaryEnabled" @change="summaryEnabled = $event.detail.value" color="#f97316" />
          </view>
          <view v-if="summaryEnabled" class="setting-item">
            <text class="setting-label">摘要阈值（消息数）</text>
            <view class="threshold-wrapper">
              <slider
                :value="summaryThreshold"
                :min="10"
                :max="50"
                :step="5"
                activeColor="#f97316"
                @change="summaryThreshold = $event.detail.value"
              />
              <text class="threshold-value">{{ summaryThreshold }}条</text>
            </view>
          </view>
        </view>
      </view>

      <!-- 底部间距 -->
      <view class="bottom-spacer" />
    </scroll-view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { getUserPreferences, saveUserPreferences } from '@/api'

// 饮食限制
const isVegetarian = ref(false)
const isGlutenFree = ref(false)
const isLowSugar = ref(false)
const isLowFat = ref(false)

// 过敏源
const allergyOptions = ['花生', '牛奶', '鸡蛋', '海鲜', '大豆', '小麦', '坚果', '鱼类']
const selectedAllergies = ref<string[]>([])
const customAllergy = ref('')

// 偏好菜系
const cuisineOptions = ['川菜', '粤菜', '鲁菜', '湘菜', '江浙菜', '东北菜', '西餐', '日韩料理']
const selectedCuisines = ref<string[]>([])
const customCuisine = ref('')

// 烹饪水平
const cookingSkill = ref('beginner')
const skillLevels = [
  {
    value: 'beginner',
    icon: '🌱',
    label: '新手',
    description: '刚开始学做饭，需要简单易学的食谱'
  },
  {
    value: 'intermediate',
    icon: '👨‍🍳',
    label: '中级',
    description: '有一定基础，可以尝试复杂一些的菜品'
  },
  {
    value: 'advanced',
    icon: '🏆',
    label: '高手',
    description: '经验丰富，可以挑战高难度菜品'
  }
]

// 摘要设置
const summaryEnabled = ref(true)
const summaryThreshold = ref(20)

onLoad(() => {
  loadPreferences()
})

// 加载偏好设置
async function loadPreferences() {
  try {
    const res = await getUserPreferences()
    if (String(res.code) === '200' && res.data) {
      const data = res.data

      // 解析饮食限制
      if (data.dietary_restrictions) {
        try {
          const restrictions = JSON.parse(data.dietary_restrictions)
          isVegetarian.value = restrictions.vegetarian || false
          isGlutenFree.value = restrictions.gluten_free || false
          isLowSugar.value = restrictions.low_sugar || false
          isLowFat.value = restrictions.low_fat || false
          selectedAllergies.value = restrictions.allergies || []
        } catch (e) {
          console.error('解析饮食限制失败:', e)
        }
      }

      // 解析偏好菜系
      if (data.favorite_cuisines) {
        try {
          selectedCuisines.value = JSON.parse(data.favorite_cuisines)
        } catch (e) {
          console.error('解析偏好菜系失败:', e)
        }
      }

      // 烹饪水平
      if (data.cooking_skill) {
        cookingSkill.value = data.cooking_skill
      }

      // 摘要设置
      summaryEnabled.value = data.summary_enabled !== 0
      summaryThreshold.value = data.summary_threshold || 20
    }
  } catch (e) {
    console.error('加载偏好设置失败:', e)
  }
}

// 切换过敏源（预设选项）
function toggleAllergy(tag: string) {
  const index = selectedAllergies.value.indexOf(tag)
  if (index === -1) {
    selectedAllergies.value.push(tag)
  } else {
    selectedAllergies.value.splice(index, 1)
  }
}

// 添加自定义过敏源
function addAllergy() {
  const tag = customAllergy.value.trim()
  if (!tag) return
  if (selectedAllergies.value.includes(tag)) {
    uni.showToast({ title: '已存在该过敏源', icon: 'none' })
    return
  }
  selectedAllergies.value.push(tag)
  customAllergy.value = ''
}

// 移除过敏源
function removeAllergy(tag: string) {
  const index = selectedAllergies.value.indexOf(tag)
  if (index !== -1) {
    selectedAllergies.value.splice(index, 1)
  }
}

// 切换偏好菜系（预设选项）
function toggleCuisine(tag: string) {
  const index = selectedCuisines.value.indexOf(tag)
  if (index === -1) {
    selectedCuisines.value.push(tag)
  } else {
    selectedCuisines.value.splice(index, 1)
  }
}

// 添加自定义菜系
function addCuisine() {
  const tag = customCuisine.value.trim()
  if (!tag) return
  if (selectedCuisines.value.includes(tag)) {
    uni.showToast({ title: '已存在该菜系', icon: 'none' })
    return
  }
  selectedCuisines.value.push(tag)
  customCuisine.value = ''
}

// 移除菜系
function removeCuisine(tag: string) {
  const index = selectedCuisines.value.indexOf(tag)
  if (index !== -1) {
    selectedCuisines.value.splice(index, 1)
  }
}

// 保存偏好设置
async function savePreferences() {
  try {
    // 构建饮食限制
    const dietaryRestrictions = JSON.stringify({
      vegetarian: isVegetarian.value,
      gluten_free: isGlutenFree.value,
      low_sugar: isLowSugar.value,
      low_fat: isLowFat.value,
      allergies: selectedAllergies.value
    })

    // 构建偏好菜系
    const favoriteCuisines = JSON.stringify(selectedCuisines.value)

    const res = await saveUserPreferences({
      dietary_restrictions: dietaryRestrictions,
      favorite_cuisines: favoriteCuisines,
      cooking_skill: cookingSkill.value,
      summary_enabled: summaryEnabled.value,
      summary_threshold: summaryThreshold.value
    })

    if (String(res.code) === '200') {
      uni.showToast({ title: '保存成功', icon: 'success' })
      setTimeout(() => goBack(), 1500)
    } else {
      uni.showToast({ title: res.message || '保存失败', icon: 'none' })
    }
  } catch (e) {
    console.error('保存偏好设置失败:', e)
    uni.showToast({ title: '保存失败', icon: 'none' })
  }
}

// 返回
function goBack() {
  uni.navigateBack()
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

.btn-save {
  padding: 12rpx 24rpx;
  background: linear-gradient(135deg, #f97316 0%, #ea580c 100%);
  border-radius: 12rpx;
}

.btn-save:active {
  opacity: 0.9;
}

.save-text {
  font-size: 28rpx;
  color: #fff;
  font-weight: 500;
}

/* 设置列表 */
.settings-list {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  padding-top: calc(120rpx + env(safe-area-inset-top));
  padding-bottom: env(safe-area-inset-bottom);
}

/* 设置区域 */
.settings-section {
  margin: 24rpx;
}

.section-title {
  font-size: 26rpx;
  color: #9ca3af;
  margin-bottom: 16rpx;
  padding-left: 8rpx;
}

.settings-card {
  background: rgba(255, 255, 255, 0.9);
  border-radius: 20rpx;
  overflow: hidden;
  box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.04);
  border: 1rpx solid rgba(255, 255, 255, 0.5);
}

.setting-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 28rpx 32rpx;
  border-bottom: 1rpx solid #f3f4f6;
}

.setting-item:last-child {
  border-bottom: none;
}

.setting-label {
  font-size: 30rpx;
  color: #374151;
}

/* 已选标签 */
.selected-tags-wrapper {
  display: flex;
  flex-wrap: wrap;
  gap: 16rpx;
  padding: 24rpx 32rpx 0;
}

/* 标签 */
.tags-wrapper {
  display: flex;
  flex-wrap: wrap;
  gap: 16rpx;
  padding: 24rpx 32rpx;
}

.tag-item {
  padding: 12rpx 24rpx;
  background: #f3f4f6;
  border-radius: 32rpx;
  transition: all 0.2s;
}

.tag-item:active {
  transform: scale(0.95);
}

.tag-active {
  background: linear-gradient(135deg, #f97316 0%, #ea580c 100%);
}

.tag-with-delete {
  display: flex;
  align-items: center;
  gap: 8rpx;
  padding-right: 16rpx;
}

.tag-text {
  font-size: 26rpx;
  color: #666;
}

.tag-active .tag-text {
  color: #fff;
}

.tag-delete {
  font-size: 20rpx;
  color: rgba(255, 255, 255, 0.8);
  padding: 4rpx;
}

.tag-delete:active {
  color: #fff;
}

/* 自定义输入 */
.custom-input-wrapper {
  display: flex;
  align-items: center;
  gap: 16rpx;
  padding: 16rpx 32rpx 24rpx;
  border-top: 1rpx solid #f3f4f6;
}

.custom-input {
  flex: 1;
  background: #f9fafb;
  border-radius: 16rpx;
  padding: 16rpx 20rpx;
  font-size: 26rpx;
  border: 1rpx solid #e5e7eb;
}

.btn-add {
  padding: 16rpx 24rpx;
  background: linear-gradient(135deg, #f97316 0%, #ea580c 100%);
  border-radius: 16rpx;
  flex-shrink: 0;
}

.btn-add:active {
  opacity: 0.9;
}

.btn-add-disabled {
  background: #d1d5db;
}

.btn-add-text {
  font-size: 26rpx;
  color: #fff;
  font-weight: 500;
}

/* 烹饪水平 */
.skill-info {
  display: flex;
  align-items: center;
  gap: 20rpx;
}

.skill-icon {
  font-size: 40rpx;
}

.skill-text-wrapper {
  display: flex;
  flex-direction: column;
}

.skill-name {
  font-size: 30rpx;
  color: #374151;
  font-weight: 500;
}

.skill-desc {
  font-size: 24rpx;
  color: #9ca3af;
  margin-top: 4rpx;
}

.radio-btn {
  width: 40rpx;
  height: 40rpx;
  border-radius: 50%;
  border: 3rpx solid #d1d5db;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.radio-active {
  border-color: #f97316;
}

.radio-dot {
  width: 20rpx;
  height: 20rpx;
  border-radius: 50%;
  background: #f97316;
}

/* 摘要阈值 */
.threshold-wrapper {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 16rpx;
  margin-left: 32rpx;
}

.threshold-wrapper slider {
  flex: 1;
}

.threshold-value {
  font-size: 26rpx;
  color: #f97316;
  font-weight: 500;
  min-width: 80rpx;
  text-align: right;
}

.bottom-spacer {
  height: 60rpx;
}
</style>
