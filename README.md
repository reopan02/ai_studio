# AI Studio (FastAPI + Vue MPA + Supabase)

本项目包含一个 **Vue 3 + TypeScript** 前端（源码位于 `frontend/`），通过 **Vite 多页面（MPA）** 构建输出到 `app/static/`，由 FastAPI 作为静态资源对外提供。

## 1) 启动 Supabase（自建）

本项目使用 `supabase/supabase` 作为 **Auth + Postgres + PostgREST**。

按 `infra/supabase/README.md` 启动 Supabase，并在 Supabase Studio SQL Editor 里执行：

- `infra/supabase/schema.sql`

## 2) 环境变量

后端（`.env`）至少需要：

- `API_KEY`：中转/提供商 Key（部分功能用到）
- `SUPABASE_JWT_SECRET`：必须与 Supabase `JWT_SECRET` 一致（后端用来校验 Supabase Access Token）
- `RUNNINGHUB_API_KEY`（可选）：RunningHub 默认 Token（也可在页面里手动输入）

前端（`frontend/.env`）需要：

- `VITE_SUPABASE_URL`：例如 `http://<局域网IP>:8000`（必须能从浏览器访问，不能用 `localhost`）
- `VITE_SUPABASE_ANON_KEY`：Supabase `ANON_KEY`

示例文件：

- 后端：`.env.example`
- 前端：`frontend/.env.example`

## 3) 前端开发/构建

```bash
cd frontend
npm install
npm run typecheck
npm run build
```

构建完成后，服务端会直接读取 `app/static/*.html`（以及 `app/static/assets/*`）对外提供页面与资源。

## 4) 后端启动

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
