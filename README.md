# Video API Dashboard

本项目包含一个 **Vue 3 + TypeScript** 前端（源码位于 `frontend/`），通过 **Vite 多页面（MPA）** 构建输出到 `app/static/`，由 FastAPI 作为静态资源对外提供。

## 前端开发/构建

```bash
cd frontend
npm install
npm run typecheck
npm run build
```

构建完成后，服务端会直接读取 `app/static/*.html`（以及 `app/static/assets/*`）对外提供页面与资源。

## 后端（FastAPI）+ PostgreSQL（新增）

本项目的后端接口位于 `/api/v1/...`，并支持将请求/响应日志与用户信息持久化到 PostgreSQL（SQLAlchemy Async）。

### 环境变量（.env）

至少需要配置：

- `API_KEY`：提供商 Key（现有逻辑使用）
- `LLM_MODEL`：用于产品识别的模型名（默认：`openai/gpt-4o-mini`，需支持图片输入）
- `DATABASE_URL`：例如 `postgresql+asyncpg://user:password@127.0.0.1:5432/video_api`
- `JWT_SECRET_KEY`：用于签发登录 Token（务必自行设置高强度随机值）
- `STORAGE_MASTER_KEY`：用于加密存储每个用户的视频请求/响应数据（务必自行设置高强度随机值）

可选配置：`DB_POOL_SIZE`、`DB_MAX_OVERFLOW`、`DB_POOL_TIMEOUT`、`JWT_ACCESS_TOKEN_EXPIRE_MINUTES`、`JWT_SESSION_EXPIRE_DAYS`、`COOKIE_SECURE`、`COOKIE_SAMESITE`、`DEFAULT_STORAGE_QUOTA_BYTES`、`BACKUP_ENABLED`、`BACKUP_DIR`、`BACKUP_INTERVAL_HOURS`、`BACKUP_RETENTION_DAYS`、`REQUEST_LOG_MAX_BODY_BYTES`

### 网站访问（需要登录）

- 登录页：`GET /login`
- 主页面：`GET /`（登录后可访问，支持生成并加密保存记录）
- 存储库：`GET /storage`（查看/删除已保存的视频记录）
- 视频生成：`GET /video`（同样需要登录）
- 产品库：`GET /products`（上传产品图片并进行 AI 识别）
- 站点图标：`GET /favicon.ico`（文件位于 `app/static/favicon.ico`）

### 静态资源缓存（304 说明）

`GET /static/...` 会携带 `ETag`，浏览器请求时可能带上 `If-None-Match`，命中缓存时返回 `304 Not Modified`，属于正常行为。

默认缓存策略：

- 开发环境（`ENV=development`）：`Cache-Control: no-store`（避免前端资源修改后仍命中缓存）
- 生产环境（`ENV=production`）：`Cache-Control: public, max-age=31536000, immutable`

也可以通过 `STATIC_CACHE_CONTROL` 显式覆盖缓存策略（例如：`public, max-age=0`）。

### 认证接口

- `POST /api/v1/auth/register`：注册
- `POST /api/v1/auth/login`：登录（返回 Bearer Token；`?set_cookie=1` 会同时写入 Cookie）
- `GET  /api/v1/auth/me`：获取当前用户
- `POST /api/v1/auth/logout`：注销当前会话

### Cookie 登录 + CSRF（重要）

如果使用 `POST /api/v1/auth/login?set_cookie=1` 的 Cookie 登录方式：

- 对所有非 `GET/HEAD/OPTIONS` 的 `/api/*` 请求，需要携带 `X-CSRF-Token` 请求头，值必须与 `csrf_token` Cookie 相同
- 如果使用 `Authorization: Bearer <token>` 方式调用 API，则不需要 CSRF 请求头

### 数据管理接口（请求日志 + 分类）

需要 `Authorization: Bearer <token>`：

- `POST /api/v1/categories` / `GET /api/v1/categories` / `PATCH /api/v1/categories/{id}` / `DELETE /api/v1/categories/{id}`
- `GET /api/v1/logs` / `GET /api/v1/logs/{id}` / `PATCH /api/v1/logs/{id}` / `DELETE /api/v1/logs/{id}`
- `POST /api/v1/videos/generate/sync` / `GET /api/v1/videos` / `GET /api/v1/videos/{id}` / `PATCH /api/v1/videos/{id}` / `DELETE /api/v1/videos/{id}`
- `GET /api/v1/storage/me`（查看存储配额/使用量）

> 注意：请求日志中会自动对 `password`、`access_token` 等敏感字段做脱敏处理。

## 前端配置（重要）

页面顶部「配置」中的两项含义如下：

- `Base URL（中转 API）`：填写 **API 提供商/中转服务** 的根地址（必须是 `https://`），例如：`https://api.gpt-best.com`
  - 仅填写根地址即可，页面会在其后拼接固定的 RESTful 路径（例如 `/v2/videos/generations`）
- `API Key（提供商）`：填写 **API 提供商** 下发的正式 Key
  - 页面会以请求头 `Authorization: Bearer <key>` 的方式传递鉴权信息

## 使用到的接口路径（RESTful）

前端直接调用中转/提供商 API（不会调用本地 FastAPI 的 `/api/v1/...` 路径）：

- Sora（sora-2 / sora-2-pro）
  - 创建任务：`POST {base_url}/v2/videos/generations`
  - 查询状态：`GET  {base_url}/v2/videos/generations/{task_id}`（`task_id` 会做 URL 编码）
- Veo
  - 创建任务：`POST {base_url}/v1/video/veo/text-to-video`
  - 查询状态：`GET  {base_url}/v1/video/veo/tasks/{task_id}`
- Seedance
  - 创建任务：`POST {base_url}/v1/video/seedance/text-to-video`
  - 查询状态：`GET  {base_url}/v1/video/seedance/tasks/{task_id}`
- New Model
  - 创建任务：`POST {base_url}/v1/video/newmodel/text-to-video`
  - 查询状态：`GET  {base_url}/v1/video/newmodel/tasks/{task_id}`

## Sora 图片输入说明

在 Sora 参数区支持：

- 拖拽/选择/粘贴图片：会自动转为 `data:image/...;base64,...` 并作为 `images` 数组提交
- 填写图片 URL 或 Base64：一行一个，添加后可预览/编辑

> 说明：是否为图生视频由 `images` 是否为空决定。

## Troubleshooting

- `POST /api/v1/videos` 返回 `500`：
  - 确认已设置 `STORAGE_MASTER_KEY`（用于加密存储）
  - 确认 `DATABASE_URL` 可用且服务已启动（应用启动时会自动 `create_all`）
  - 若使用 Cookie 登录（`?set_cookie=1`），请带 `X-CSRF-Token` 请求头
