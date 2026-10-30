/**
 * 聊天相关类型定义
 */

export type MessageRole = 'user' | 'assistant' | 'system'

// 多模态消息内容项
export type MessageContentPart =
  | { type: 'text'; text: string }
  | { type: 'image'; url: string }

export interface Message {
  id: string
  messageId?: string
  role: MessageRole
  content: string
  contentParts?: MessageContentPart[]
  imageUrl?: string
  timestamp: number
  loading?: boolean
  streaming?: boolean
  is_favorite?: boolean
}

export interface Recipe {
  title: string
  score?: number
  reason?: string
  difficulty?: string
  url?: string
  steps?: string[]
  seasonings?: string[]
  cooking_time?: string
}
