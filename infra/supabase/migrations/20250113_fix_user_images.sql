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
