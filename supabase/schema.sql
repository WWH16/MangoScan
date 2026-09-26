-- MangoScan: saved scans for signed-in users.
-- Run this once in the Supabase dashboard: SQL Editor > New query > paste > Run.
-- Safe to run again; every statement checks before it creates.

-- 1. Scans table ------------------------------------------------------------

create table if not exists public.scans (
    id          uuid primary key default gen_random_uuid(),
    user_id     uuid not null default auth.uid() references auth.users (id) on delete cascade,
    created_at  timestamptz not null default now(),
    filename    text,
    label       text not null,
    confidence  real,
    telemetry   jsonb not null default '{}'::jsonb,
    metrics     jsonb not null default '{}'::jsonb,
    raw_path    text not null,
    ann_path    text not null
);

create index if not exists scans_user_created_idx on public.scans (user_id, created_at desc);

-- Row Level Security: each user sees and changes only their own scans.
alter table public.scans enable row level security;

drop policy if exists "Users read own scans" on public.scans;
create policy "Users read own scans" on public.scans
    for select to authenticated
    using ((select auth.uid()) = user_id);

drop policy if exists "Users add own scans" on public.scans;
create policy "Users add own scans" on public.scans
    for insert to authenticated
    with check ((select auth.uid()) = user_id);

drop policy if exists "Users delete own scans" on public.scans;
create policy "Users delete own scans" on public.scans
    for delete to authenticated
    using ((select auth.uid()) = user_id);

-- New tables are not exposed to the Data API automatically; grant only what the app uses.
revoke all on public.scans from anon;
grant select, insert, delete on public.scans to authenticated;

-- 2. Private photo bucket ---------------------------------------------------
-- Photos live at scans/<user id>/<scan>/original.jpg and marked.jpg.

insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values ('scans', 'scans', false, 10485760, array['image/jpeg', 'image/png', 'image/webp'])
on conflict (id) do nothing;

drop policy if exists "Users read own scan photos" on storage.objects;
create policy "Users read own scan photos" on storage.objects
    for select to authenticated
    using (bucket_id = 'scans' and (storage.foldername(name))[1] = (select auth.uid())::text);

drop policy if exists "Users upload own scan photos" on storage.objects;
create policy "Users upload own scan photos" on storage.objects
    for insert to authenticated
    with check (bucket_id = 'scans' and (storage.foldername(name))[1] = (select auth.uid())::text);

drop policy if exists "Users delete own scan photos" on storage.objects;
create policy "Users delete own scan photos" on storage.objects
    for delete to authenticated
    using (bucket_id = 'scans' and (storage.foldername(name))[1] = (select auth.uid())::text);
