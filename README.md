# AI 私人厨师（AIPrivateChef）

基于 **LangChain / LangGraph + FastAPI + UniApp** 的智能私厨助手：上传食材照片或输入食材清单，AI 会识别食材、联网检索菜谱，并结合你的过敏源、忌口与口味偏好，输出结构化的菜谱推荐报告。

## 功能特性

- 📸 食材图片识别（拍照 / 相册，支持多图），自动评估食材新鲜度与可用量
- 🌐 Tavily 联网检索菜谱，按**营养价值**与**制作难度**多维打分排序
- ⚠️ 安全红线：过敏源绝对拦截、忌口默认过滤、口味偏好与烹饪水平适配
- 💬 流式对话输出（SSE），会话历史持久化（LangGraph SqliteSaver + MySQL）
- 🍳 菜谱收藏、收藏统计、收藏详情
- 👤 注册 / 登录（JWT + bcrypt）、用户偏好设置（过敏源、忌口、菜系、烹饪水平）
- 🗂 对话管理：会话摘要、上下文召回、对话分支、历史消息搜索
- ☁️ 阿里云 OSS 上传（预签名 / 后端代理转发），规避前端跨域
- 📱 前端支持 H5 / 微信小程序 / App 三端

## 技术栈

| 层级       | 技术                                                      |
| -------- | ------------------------------------------------------- |
| AI Agent | LangChain、LangGraph、langchain-deepseek、langchain-tavily |
| 后端       | Python 3.13、FastAPI、Uvicorn、PyJWT、bcrypt                |
| 数据库      | MySQL（业务数据）、SQLite（LangGraph checkpoint）                |
| 存储       | 阿里云 OSS（alibabacloud-oss-v2）                            |
| 前端       | UniApp 3.x、Vue 3、TypeScript、Vite、uview-plus、Pinia       |
| 依赖管理     | uv（镜像源：清华 TUNA / 阿里云）                                   |

## 项目结构

```
AIPrivateChef/
├── app/                          # 后端（分层：路由 / 业务 / 模型 / 工具）
│   ├── main.py                   # 入口，python -m app.main（默认 8001 端口）
│   ├── api/
│   │   ├── router.py             # FastAPI 实例 + 路由挂载 + 静态资源 SPA fallback
│   │   ├── public/               # 免登录接口（login）
│   │   └── v1/                   # 需鉴权接口（chat / recipe / conversation / oss）
│   ├── agents/                   # AI 智能体层
│   │   ├── personal_chief.py     # 私厨 Agent：系统提示词、工具、流式对话
│   │   └── conversation_manager.py  # 会话摘要 / 分支 / 搜索等会话能力
│   ├── models/                   # 数据模型与 Pydantic Schema
│   ├── configs/dbconfig.py       # MySQL 连接配置
│   ├── common/logger.py          # 日志模块
│   ├── utils/                    # JWT、密码、响应体、MySQL 连接等通用工具
│   └── db/                       # SQLite 数据文件（LangGraph checkpoint）
├── uniapp-frontend/              # UniApp 前端（页面按 名称/index.vue 组织）
│   └── src/
│       ├── pages/                # login / register / index / search / profile
│       ├── components/           # ChatInput、ChatMessage、SideBar 等复用组件
│       ├── api/index.ts          # 接口封装（登录、聊天、收藏、会话管理）
│       ├── utils/request.ts      # 请求封装（token 注入、401 跳转、流式请求）
│       └── types/                # TypeScript 类型定义
├── sql/                          # 建表与优化脚本
├── langgraph.json                # LangGraph 配置（chief_agent 图）
├── pyproject.toml                # 后端依赖（uv）
└── .env                          # 环境变量（本地私有，勿提交）
```

## 环境准备

### 1. 后端依赖

```bash
# 需要 Python >= 3.13
uv sync
```

### 2. 配置环境变量

在根目录创建 `.env`，按需填写以下变量（**请替换为你自己的密钥，切勿提交真实密钥**）：

```bash
# DeepSeek 模型
DEEPSEEK_API_KEY=
DEEPSEEK_BASE_URL=https://api.deepseek.com

# 其他模型渠道（可选）
DASHSCOPE_API_KEY=
DASHSCOPE_BASE_URL=
MIMO_API_KEY=
MIMO_BASE_URL=
CHATGPT_BASE_URL=
CHATGPT_API_KEY=

# 联网搜索
TAVILY_API_KEY=

# LangSmith 追踪（可选）
LANGSMITH_API_KEY=
LANGSMITH_TRACING=
LANGSMITH_PROJECT=

# 阿里云 OSS（菜谱图片上传）
OSS_ACCESS_KEY_ID=
OSS_ACCESS_KEY_SECRET=
OSS_BUCKET=

# JWT 签名密钥（务必保密）
JWT_SECRET_KEY=
```

同时修改 [app/configs/dbconfig.py](file:///e:/PycharmProjects/AIPrivateChef/app/configs/dbconfig.py) 中的 MySQL 连接信息（host / port / user / password / database）。

### 3. 初始化数据库

执行 [sql](file:///e:/PycharmProjects/AIPrivateChef/sql) 下的脚本创建业务表：

```bash
mysql -u root -p python_agent < sql/create_tables.sql
mysql -u root -p python_agent < sql/python_agent.sql
mysql -u root -p python_agent < sql/conversation_optimization.sql
```

主要数据表：`users`、`agent_record`（会话）、`agent_message`（消息）、`recipe_favorites`（收藏）、`user_preferences`（用户偏好）、`conversation_summaries`、`conversation_branches`、`message_search_index`。

## 快速开始

### 启动后端

```bash
# 方式一：直接启动 FastAPI（http://127.0.0.1:8001）
uv run python -m app.main

# 方式二：LangGraph 开发模式（调试 Agent 图）
uv run langgraph dev
```

接口文档：<http://127.0.0.1:8001/docs>

### 启动前端

```bash
cd uniapp-frontend
npm install

# H5 开发模式
npm run dev:h5

# 微信小程序（用微信开发者工具打开 dist/dev/mp-weixin）
npm run dev:mp-weixin

# App
npm run dev:app
```

- H5：通过 Vite 代理转发接口，无需额外配置
- 小程序 / App：接口地址在 [uniapp-frontend/src/utils/request.ts](file:///e:/PycharmProjects/AIPrivateChef/uniapp-frontend/src/utils/request.ts) 中配置（默认 `http://localhost:8001`）

### 构建部署

```bash
# 后端构建前端静态资源后放入 app/static，可由 FastAPI 直接托管（SPA fallback）
npm run build:h5

# 小程序构建
npm run build:mp-weixin
```

## 接口一览

### 免鉴权（/api/public）

| 方法   | 路径                   | 说明        |
| ---- | -------------------- | --------- |
| POST | /api/public/login    | 登录，返回 JWT |
| POST | /api/public/register | 注册        |

### 需鉴权（/api/v1，Bearer Token）

| 模块   | 路径                                        | 说明         |
| ---- | ----------------------------------------- | ---------- |
| 对话   | POST /api/v1/chat/create                  | 创建会话       |
| 对话   | GET /api/v1/chat/list                     | 会话列表（分页）   |
| 对话   | POST /api/v1/chat/stream                  | 流式对话（SSE）  |
| 对话   | GET /api/v1/chat/messages                 | 获取聊天历史     |
| 对话   | DELETE /api/v1/chat/messages              | 清空聊天历史     |
| 收藏   | POST /api/v1/recipe/favorite              | 添加收藏       |
| 收藏   | GET /api/v1/recipe/favorites              | 收藏列表       |
| 收藏   | GET /api/v1/recipe/favorite/{id}          | 收藏详情       |
| 收藏   | DELETE /api/v1/recipe/favorite/{id}       | 取消收藏       |
| 收藏   | GET /api/v1/recipe/stats                  | 收藏 / 对话统计  |
| 会话管理 | GET/POST /api/v1/conversation/summary     | 会话摘要       |
| 会话管理 | GET /api/v1/conversation/context          | 上下文召回      |
| 会话管理 | POST /api/v1/conversation/branch          | 创建对话分支     |
| 会话管理 | GET /api/v1/conversation/branches         | 分支列表       |
| 会话管理 | POST /api/v1/conversation/search          | 历史消息搜索     |
| 会话管理 | GET/POST /api/v1/conversation/preferences | 用户偏好       |
| OSS  | GET /api/v1/oss/presign                   | 获取预签名上传地址  |
| OSS  | GET /api/v1/oss/proxy                     | 图片代理（规避跨域） |
| OSS  | POST /api/v1/oss/upload                   | 后端转发上传     |

## Agent 工作流程

私厨 Agent（[app/agents/personal\_chief.py](file:///e:/PycharmProjects/AIPrivateChef/app/agents/personal_chief.py)）按以下流程执行：

1. **识别与评估食材** —— 图片输入时辨识食材、评估新鲜度与可用量，整理可用食材清单
2. **智能食谱检索** —— 调用 `web_search`（Tavily）以食材清单为关键词检索菜谱
3. **多维度评估排序** —— 营养价值 + 制作难度打分排序
4. **结构化方案输出** —— 输出食谱信息、得分、推荐理由、参考图片
5. **结果自检** —— 校验输出是否符合用户需求（文字 / 图片 / 地址完整）

安全规则：过敏源最高优先级绝对拦截 → 忌口默认过滤 → 口味偏好适配 → 优先组合常用食材。

会话状态由 LangGraph `SqliteSaver` 持久化到 `app/db/personal_chief.db`，按 `thread_id` 隔离。

## 开发规范

- 代码注释统一使用中文，函数上方需写明函数职责，字段需注明含义
- 后端按 功能层（api / utils / configs）与 业务层（agents / models）分离，模块化组织
- 前端页面采用 `页面名/index.vue` 目录式组织，接口与请求统一封装，可复用组件抽到 `components/`
- 新增功能需遵循现有代码风格，优先复用已有组件与工具函数

