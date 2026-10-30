# AI 私人厨师 - UniApp 前端

基于 UniApp + Vue 3 + TypeScript + Vite + uview-plus 构建的移动端前端。

## 功能特性

- 📸 食材图片上传（支持拍照/相册）
- 💬 AI 对话（流式输出）
- 📝 Markdown 渲染
- 🍳 食谱推荐
- 💾 会话历史记录
- 📱 支持 H5 / 微信小程序 / App

## 项目结构

```
uniapp-frontend/
├── src/
│   ├── api/              # API 接口
│   │   └── index.ts
│   ├── components/       # 组件
│   │   ├── ChatInput.vue
│   │   └── ChatMessage.vue
│   ├── pages/            # 页面
│   │   └── index/
│   │       └── index.vue
│   ├── types/            # 类型定义
│   │   └── chat.ts
│   ├── utils/            # 工具函数
│   │   └── request.ts
│   ├── static/           # 静态资源
│   ├── App.vue           # 根组件
│   ├── main.ts           # 入口文件
│   ├── manifest.json     # 应用配置
│   ├── pages.json        # 页面路由
│   └── uni.scss          # 全局样式
├── package.json
├── vite.config.ts
├── tsconfig.json
└── index.html
```

## 快速开始

### 1. 安装依赖

```bash
cd uniapp-frontend
npm install
```

> 如果遇到权限问题，请以管理员身份运行 PowerShell。

### 2. 启动后端

确保后端服务已启动：

```bash
cd E:\PycharmProjects\PythonAgentProject
$env:PYTHONUTF8 = "1"
uv run langgraph dev
```

### 3. 启动前端

```bash
# H5 开发模式
npm run dev:h5

# 微信小程序
npm run dev:mp-weixin

# App
npm run dev:app
```

### 4. 访问

- H5: http://localhost:3001
- 微信小程序: 使用微信开发者工具打开 `dist/dev/mp-weixin`
- App: 使用 HBuilderX 运行

## API 配置

H5 环境下使用 Vite 代理，无需额外配置。

小程序/App 环境下，API 地址在 `src/utils/request.ts` 中配置：

```typescript
const API_BASE = 'http://localhost:8001'
```

## 构建部署

```bash
# H5 构建
npm run build:h5

# 微信小程序构建
npm run build:mp-weixin
```

## 技术栈

- **框架**: UniApp 3.x + Vue 3
- **语言**: TypeScript
- **构建工具**: Vite
- **UI 组件库**: uview-plus
- **状态管理**: Vue 3 Composition API
