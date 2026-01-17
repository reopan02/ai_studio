# AI Studio (FastAPI + Vue MPA + Supabase)

本项目包含一个 **Vue 3 + TypeScript** 前端（源码位于 `frontend/`），通过 **Vite 多页面（MPA）** 构建输出到 `app/static/`，由 FastAPI 作为静态资源对外提供。

## 1) 快速启动（推荐）

使用自动化脚本一键设置 Supabase 和前端环境：

```bash
./setup-supabase.sh
```

这个脚本会自动：
1. 克隆并设置 Supabase
2. 配置前端和后端环境变量
3. 启动 Supabase 容器
4. 构建前端

脚本完成后，在 Supabase Studio (`http://localhost:3000`) 的 SQL Editor 中执行：
- `infra/supabase/schema.sql`

然后启动后端：
```bash
./start.sh
```

## 2) 手动设置（可选）

### 2.1) 启动 Supabase

本项目使用 `supabase/supabase` 作为 **Auth + Postgres + PostgREST**。

按 `infra/supabase/README.md` 启动 Supabase，并在 Supabase Studio SQL Editor 里执行：

- `infra/supabase/schema.sql`

### 2.2) 环境变量

后端（`.env`）至少需要：

- `LLM_API_KEY`：LLM Key（产品识别/LLM 能力）
- `LLM_API_BASE_URL`：LLM 接口地址
- `IMAGE_GEN_API_KEY`：图像生成 Key
- `IMAGE_GEN_API_BASE_URL`：图像生成接口地址
- `IMAGE_EDIT_API_KEY`：图像编辑 Key
- `IMAGE_EDIT_API_BASE_URL`：图像编辑接口地址
- `VIDEO_GEN_API_KEY`：视频生成 Key
- `VIDEO_GEN_API_BASE_URL`：视频生成接口地址
- `SUPABASE_JWT_SECRET`：必须与 Supabase `JWT_SECRET` 一致（后端用来校验 Supabase Access Token）

前端（`frontend/.env`）需要：

- `VITE_SUPABASE_URL`：**留空以自动使用当前访问的 hostname**（推荐），或手动设置为 `http://<局域网IP>:8000`
- `VITE_SUPABASE_ANON_KEY`：Supabase `ANON_KEY`（从 `.supabase/docker/.env` 获取）

**重要说明**：
- 如果 `VITE_SUPABASE_URL` 留空或不设置，前端会自动使用当前浏览器访问的 hostname + 端口 8000
- 这样无论从 localhost、局域网 IP 还是公网 IP 访问，都能正确连接到对应的 Supabase
- 只有在需要固定 Supabase 地址时才手动设置 `VITE_SUPABASE_URL`

示例文件：

- 后端：`.env.example`
- 前端：`frontend/.env.example`

### 2.3) 前端开发/构建

```bash
cd frontend
npm install
npm run typecheck
npm run build
```

构建完成后，服务端会直接读取 `app/static/*.html`（以及 `app/static/assets/*`）对外提供页面与资源。

### 2.4) 后端启动

```bash
./scripts/manage.sh start
```

默认监听：`http://0.0.0.0:8887`

## 认证模型（重要）

- 前端使用 Supabase Auth（Email/Password）登录。
- 前端访问后端 `/api/v1/...` 时，会带上 `Authorization: Bearer <supabase_access_token>`。
- 后端通过 `SUPABASE_JWT_SECRET` 验证 JWT，并从 `sub` 提取 `user_id`。
- 页面访问不由后端做 Cookie 重定向；由前端在各页面入口执行 “需要登录” 的跳转逻辑。

## 数据持久化（Supabase Postgres）

用户资产记录由前端通过 Supabase PostgREST 直接写入/读取：

- `user_videos`
- `user_images`
- `products`
- `product_images`

以上表均启用 RLS，并通过 `user_id = auth.uid()` 限制仅能访问自己的数据。

## 本地文件上传（产品图片）

产品图片仍由后端落盘到 `app/static/uploads/products/<user_id>/...`，并通过 `/uploads/...` 对外提供 URL；产品元数据与图片 URL 存在 Supabase 表中。

## 管理后台

内置 `/admin` 已移除，请使用 Supabase Studio 进行管理。
