-- App schema for Supabase Postgres (no data migration).
-- Run this in Supabase Studio -> SQL Editor.

create extension if not exists "pgcrypto";

-- ----------------------------
-- Videos
-- ----------------------------
create table if not exists public.user_videos (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null,
  title text,
  model text not null,
  prompt text not null,
  status text not null default 'completed',
  video_url text,
  metadata jsonb,
  request jsonb,
  response jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz
);

create index if not exists user_videos_user_id_idx on public.user_videos (user_id);
create index if not exists user_videos_created_at_idx on public.user_videos (created_at desc);

alter table public.user_videos enable row level security;

drop policy if exists user_videos_select_own on public.user_videos;
create policy user_videos_select_own on public.user_videos
  for select using (auth.uid() = user_id);

drop policy if exists user_videos_insert_own on public.user_videos;
create policy user_videos_insert_own on public.user_videos
  for insert with check (auth.uid() = user_id);

drop policy if exists user_videos_update_own on public.user_videos;
create policy user_videos_update_own on public.user_videos
  for update using (auth.uid() = user_id) with check (auth.uid() = user_id);

drop policy if exists user_videos_delete_own on public.user_videos;
create policy user_videos_delete_own on public.user_videos
  for delete using (auth.uid() = user_id);

-- ----------------------------
-- Images
-- ----------------------------
create table if not exists public.user_images (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null,
  title text,
  model text not null,
  prompt text not null,
  status text not null default 'completed',
  image_url text,
  metadata jsonb,
  request jsonb,
  response jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz
);

create index if not exists user_images_user_id_idx on public.user_images (user_id);
create index if not exists user_images_created_at_idx on public.user_images (created_at desc);

alter table public.user_images enable row level security;

drop policy if exists user_images_select_own on public.user_images;
create policy user_images_select_own on public.user_images
  for select using (auth.uid() = user_id);

drop policy if exists user_images_insert_own on public.user_images;
create policy user_images_insert_own on public.user_images
  for insert with check (auth.uid() = user_id);

drop policy if exists user_images_update_own on public.user_images;
create policy user_images_update_own on public.user_images
  for update using (auth.uid() = user_id) with check (auth.uid() = user_id);

drop policy if exists user_images_delete_own on public.user_images;
create policy user_images_delete_own on public.user_images
  for delete using (auth.uid() = user_id);

-- ----------------------------
-- Products
-- ----------------------------
create table if not exists public.products (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null,
  name text not null,
  dimensions text,
  features jsonb,
  characteristics jsonb,
  original_image_url text not null,
  recognition_confidence double precision,
  recognition_metadata jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz
);

create index if not exists products_user_id_idx on public.products (user_id);
create index if not exists products_created_at_idx on public.products (created_at desc);

alter table public.products enable row level security;

drop policy if exists products_select_own on public.products;
create policy products_select_own on public.products
  for select using (auth.uid() = user_id);

drop policy if exists products_insert_own on public.products;
create policy products_insert_own on public.products
  for insert with check (auth.uid() = user_id);

drop policy if exists products_update_own on public.products;
create policy products_update_own on public.products
  for update using (auth.uid() = user_id) with check (auth.uid() = user_id);

drop policy if exists products_delete_own on public.products;
create policy products_delete_own on public.products
  for delete using (auth.uid() = user_id);

create table if not exists public.product_images (
  id uuid primary key default gen_random_uuid(),
  product_id uuid not null references public.products(id) on delete cascade,
  user_id uuid not null,
  image_url text not null,
  is_primary boolean not null default false,
  created_at timestamptz not null default now(),
  updated_at timestamptz
);

create index if not exists product_images_product_id_idx on public.product_images (product_id);
create index if not exists product_images_user_id_idx on public.product_images (user_id);

alter table public.product_images enable row level security;

drop policy if exists product_images_select_own on public.product_images;
create policy product_images_select_own on public.product_images
  for select using (auth.uid() = user_id);

drop policy if exists product_images_insert_own on public.product_images;
create policy product_images_insert_own on public.product_images
  for insert with check (auth.uid() = user_id);

drop policy if exists product_images_update_own on public.product_images;
create policy product_images_update_own on public.product_images
  for update using (auth.uid() = user_id) with check (auth.uid() = user_id);

drop policy if exists product_images_delete_own on public.product_images;
create policy product_images_delete_own on public.product_images
  for delete using (auth.uid() = user_id);

