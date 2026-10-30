/**
 * HTTP 请求封装
 */

// #ifdef H5
const API_BASE = ''
// #endif
// #ifndef H5
const API_BASE = 'http://localhost:8001'
// #endif

interface RequestOptions {
  url: string
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE'
  data?: any
  header?: Record<string, string>
  responseType?: 'text' | 'arraybuffer'
}

export function request<T = any>(options: RequestOptions): Promise<T> {
  const method = options.method || 'GET'
  const header: Record<string, string> = { ...options.header }

  // 只在有 body 时设置 Content-Type
  if (method === 'POST' || method === 'PUT') {
    header['Content-Type'] = header['Content-Type'] || 'application/json'
  }

  // 自动附加 token
  const token = uni.getStorageSync('token')
  if (token && !header['Authorization']) {
    header['Authorization'] = `Bearer ${token}`
  }

  return new Promise((resolve, reject) => {
    uni.request({
      url: `${API_BASE}${options.url}`,
      method,
      data: options.data,
      header,
      responseType: options.responseType as any,
      success: (res: any) => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data as T)
        } else if (res.statusCode === 401) {
          // token 过期或无效，清除登录状态并跳转登录页
          uni.removeStorageSync('token')
          uni.removeStorageSync('userInfo')
          uni.reLaunch({ url: '/pages/login/login' })
          reject(new Error('登录已过期，请重新登录'))
        } else {
          reject(new Error(`请求失败: ${res.statusCode}`))
        }
      },
      fail: (err: any) => {
        reject(new Error(err.errMsg || '网络请求失败'))
      },
    })
  })
}

/**
 * 流式请求（H5 专用，使用 fetch）
 * 返回 { abort } 供调用方中止流
 */
export function streamRequest(
  url: string,
  data: any,
  onChunk: (chunk: string) => void,
  onError: (error: Error) => void,
  onComplete: () => void
): { abort: () => void } {
  const fullUrl = `${API_BASE}${url}`

  // #ifdef H5
  const controller = new AbortController()
  const token = uni.getStorageSync('token')
  fetch(fullUrl, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
    },
    body: JSON.stringify(data),
    signal: controller.signal,
  })
    .then((response) => {
      if (!response.ok) {
        throw new Error(`请求失败: ${response.status}`)
      }
      const reader = response.body?.getReader()
      if (!reader) {
        throw new Error('无法读取响应流')
      }
      const decoder = new TextDecoder()

      function read() {
        reader!.read().then(({ done, value }) => {
          if (done) {
            onComplete()
            return
          }
          const chunk = decoder.decode(value, { stream: true })
          onChunk(chunk)
          read()
        }).catch((err) => {
          // AbortError 是用户主动中止，不触发 onError
          if (err.name === 'AbortError') return
          onError(err)
        })
      }

      read()
    })
    .catch((err) => {
      if (err.name === 'AbortError') return
      onError(err)
    })

  return { abort: () => controller.abort() }
  // #endif

  // #ifndef H5
  // 非 H5 环境使用普通请求（小程序/App 不支持流式）
  let aborted = false
  request({
    url,
    method: 'POST',
    data,
    responseType: 'text',
  })
    .then((res: any) => {
      if (aborted) return
      onChunk(typeof res === 'string' ? res : JSON.stringify(res))
      onComplete()
    })
    .catch((err) => {
      if (aborted) return
      onError(err)
    })

  return { abort: () => { aborted = true } }
  // #endif
}
