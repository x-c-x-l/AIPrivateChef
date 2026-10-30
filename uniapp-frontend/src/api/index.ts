/**
 * API 调用封装
 */
import { request, streamRequest } from '@/utils/request'

// ==================== 通用响应类型 ====================

export interface ApiResponse<T = any> {
  message: string
  data: T
  code: string | number
}

// ==================== 登录相关 ====================

export interface LoginParams {
  username: string
  password: string
}

export interface RegisterParams {
  username: string
  password: string
  name: string
  email?: string
  phone?: string
}

export interface LoginData {
  token: string
  id: number
  username: string
}

/**
 * 登录
 */
export function loginApi(data: LoginParams): Promise<ApiResponse<LoginData>> {
  return request({
    url: '/api/public/login',
    method: 'POST',
    data,
  })
}

/**
 * 注册
 */
export function registerApi(data: RegisterParams): Promise<ApiResponse> {
  return request({
    url: '/api/public/register',
    method: 'POST',
    data,
  })
}

// #ifdef H5
const API_BASE = ''
// #endif
// #ifndef H5
const API_BASE = 'http://localhost:8001'
// #endif

/**
 * 上传图片（通过后端转发到 OSS，避免 CORS）
 */
export function uploadImage1(filePath: string): Promise<string> {
  return new Promise((resolve, reject) => {
    uni.uploadFile({
      url: `${API_BASE}/api/v1/oss/upload`,
      filePath,
      name: 'file',
      success: (res) => {
        if (res.statusCode === 200) {
          try {
            const data = JSON.parse(res.data as string)
            resolve(data.accessUrl)
          } catch {
            reject(new Error('解析上传结果失败'))
          }
        } else {
          reject(new Error(`上传失败: ${res.statusCode}`))
        }
      },
      fail: (err) => {
        reject(new Error(err.errMsg || '图片上传失败'))
      },
    })
  })
}

/**
 * 流式聊天
 * 返回 { abort } 供调用方中止流
 */
export function streamChat(
  message: string,
  onChunk: (chunk: string) => void,
  imageUrl?: string,
  onError?: (error: Error) => void,
  onComplete?: () => void,
  threadId?: string
): { abort: () => void } {
  return streamRequest(
    '/api/v1/chat/stream',
    {
      message,
      image_url: imageUrl,
      thread_id: threadId,
    },
    onChunk,
    onError!,
    onComplete!
  )
}

/**
 * 获取聊天历史
 */
export async function getChatHistory(
  threadId: string,
  page: number = 1,
  pageSize: number = 20
): Promise<{ list: { role: string; content: any; is_favorite?: boolean }[]; total: number; page: number; pageSize: number }> {
  const res = await request<ApiResponse<{ list: { role: string; content: any; is_favorite?: boolean }[]; total: number; page: number; pageSize: number }>>({
    url: `/api/v1/chat/messages?thread_id=${encodeURIComponent(threadId)}&page=${page}&pageSize=${pageSize}`,
  })
  return res.data || { list: [], total: 0, page: 1, pageSize: 20 }
}

/**
 * 清空聊天历史
 */
export async function clearChatHistory(threadId: string): Promise<void> {
  await request({
    url: `/api/v1/chat/messages?thread_id=${encodeURIComponent(threadId)}`,
    method: 'DELETE',
  })
}

/**
 * 创建会话记录
 */
export async function chatCreate(): Promise<ApiResponse<string>> {
  return request({
    url: '/api/v1/chat/create',
    method: 'POST',
  })
}

export interface ChatRecord {
  id: string
  user_id: number
  name: string
  content: string
  created_at: string
}

/**
 * 获取会话列表
 */
export async function chatList(page: number = 1, pageSize: number = 20): Promise<ApiResponse<{ list: ChatRecord[]; total: number; page: number; pageSize: number }>> {
  return request({
    url: `/api/v1/chat/list?page=${page}&pageSize=${pageSize}`,
    method: 'GET',
  })
}

/**
 * 上传预签名
 */
export async function uploadPresign(filename: string) {
  const res = await request<ApiResponse>({
    url: `/api/v1/oss/presign?filename=${encodeURIComponent(filename)}`,
    method: 'GET'
  })
  return res.data || ''
}

/**
 * 上传
 */
export async function uploadImage(file: File) {
  const { uploadUrl, accessUrl, contentType } = await uploadPresign(file.name)
  console.log(file, '----file')

  const response = await fetch(uploadUrl, {
    method: 'PUT',
    body: file,
    headers: {
      'Content-Type': contentType,
    },
  })
  return accessUrl || ''
}

// ==================== 收藏相关 ====================

export interface FavoriteItem {
  id: number
  user_id: number
  thread_id: string
  message_id?: string
  recipe_name?: string
  recipe_content: string
  recipe_image?: string
  created_at: string
}

/**
 * 添加收藏
 */
export async function addFavorite(threadId: string, messageId: string): Promise<ApiResponse> {
  return request({
    url: '/api/v1/recipe/favorite',
    method: 'POST',
    data: {
      thread_id: threadId,
      message_id: messageId,
    },
  })
}

/**
 * 获取收藏详情
 */
export async function getFavoriteDetail(favoriteId: number): Promise<ApiResponse<FavoriteItem>> {
  return request({
    url: `/api/v1/recipe/favorite/${favoriteId}`,
    method: 'GET',
  })
}

/**
 * 取消收藏
 */
export async function removeFavorite(favoriteId: number): Promise<ApiResponse> {
  return request({
    url: `/api/v1/recipe/favorite/${favoriteId}`,
    method: 'DELETE',
  })
}

/**
 * 获取收藏列表
 */
export async function getFavorites(page: number = 1, pageSize: number = 20): Promise<ApiResponse<{ list: FavoriteItem[] }>> {
  return request({
    url: `/api/v1/recipe/favorites?page=${page}&pageSize=${pageSize}`,
    method: 'GET',
  })
}

/**
 * 获取用户统计信息
 */
export async function getUserStats(): Promise<ApiResponse<{ total_favorites: number; total_chats: number }>> {
  return request({
    url: '/api/v1/recipe/stats',
    method: 'GET',
  })
}

// ==================== 对话管理相关 ====================

export interface ConversationSummary {
  id: number
  thread_id: string
  user_id: number
  summary: string
  key_points?: string
  created_at: string
}

export interface ConversationBranch {
  id: number
  thread_id: string
  parent_thread_id: string
  branch_message_id: number
  branch_name?: string
  created_at: string
}

export interface SearchResult {
  id: number
  thread_id: string
  role: string
  content: string
  created_at: string
}

export interface UserPreferences {
  dietary_restrictions?: string
  favorite_cuisines?: string
  cooking_skill?: string
  summary_enabled?: boolean
  summary_threshold?: number
}

/**
 * 获取对话摘要
 */
export async function getConversationSummary(threadId: string): Promise<ApiResponse<ConversationSummary>> {
  return request({
    url: `/api/v1/conversation/summary?thread_id=${encodeURIComponent(threadId)}`,
    method: 'GET',
  })
}

/**
 * 保存对话摘要
 */
export async function saveConversationSummary(threadId: string, summary: string, keyPoints?: string): Promise<ApiResponse> {
  return request({
    url: '/api/v1/conversation/summary',
    method: 'POST',
    data: {
      thread_id: threadId,
      summary,
      key_points: keyPoints,
    },
  })
}

/**
 * 获取上下文消息
 */
export async function getConversationContext(threadId: string, maxMessages: number = 10): Promise<ApiResponse<{
  has_summary: boolean
  summary?: string
  key_points?: string
  messages: { role: string; content: string; created_at: string }[]
}>> {
  return request({
    url: `/api/v1/conversation/context?thread_id=${encodeURIComponent(threadId)}&max_messages=${maxMessages}`,
    method: 'GET',
  })
}

/**
 * 创建对话分支
 */
export async function createConversationBranch(threadId: string, messageId: number, branchName?: string): Promise<ApiResponse<{ thread_id: string }>> {
  return request({
    url: '/api/v1/conversation/branch',
    method: 'POST',
    data: {
      thread_id: threadId,
      message_id: messageId,
      branch_name: branchName,
    },
  })
}

/**
 * 获取对话分支列表
 */
export async function getConversationBranches(threadId: string): Promise<ApiResponse<ConversationBranch[]>> {
  return request({
    url: `/api/v1/conversation/branches?thread_id=${encodeURIComponent(threadId)}`,
    method: 'GET',
  })
}

/**
 * 搜索历史消息
 */
export async function searchMessages(keyword: string, threadId?: string, page: number = 1, pageSize: number = 20): Promise<ApiResponse<{
  list: SearchResult[]
  total: number
  page: number
  pageSize: number
}>> {
  return request({
    url: '/api/v1/conversation/search',
    method: 'POST',
    data: {
      keyword,
      thread_id: threadId,
      page,
      page_size: pageSize,
    },
  })
}

/**
 * 获取用户偏好
 */
export async function getUserPreferences(): Promise<ApiResponse<UserPreferences>> {
  return request({
    url: '/api/v1/conversation/preferences',
    method: 'GET',
  })
}

/**
 * 保存用户偏好
 */
export async function saveUserPreferences(preferences: UserPreferences): Promise<ApiResponse> {
  return request({
    url: '/api/v1/conversation/preferences',
    method: 'POST',
    data: preferences,
  })
}
