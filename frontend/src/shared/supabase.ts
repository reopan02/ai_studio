import { createClient } from '@supabase/supabase-js';

const envSupabaseUrl = import.meta.env.VITE_SUPABASE_URL as string | undefined;
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY as string | undefined;

function isLocalhostHost(hostname: string): boolean {
  return hostname === 'localhost' || hostname === '127.0.0.1' || hostname === '[::1]';
}

function getDefaultSupabaseUrlFromLocation(): string | undefined {
  if (typeof window === 'undefined') return undefined;
  const { protocol, hostname } = window.location;
  if (!protocol || !hostname) return undefined;
  return `${protocol}//${hostname}:8000`;
}

function resolveSupabaseUrl(): string | undefined {
  const raw = envSupabaseUrl?.trim();
  const fallback = getDefaultSupabaseUrlFromLocation();

  if (typeof window === 'undefined') return raw;
  if (!raw) return fallback;

  try {
    const parsed = new URL(raw, window.location.href);
    const pageHost = window.location.hostname;
    if (isLocalhostHost(parsed.hostname) && !isLocalhostHost(pageHost) && fallback) {
      return fallback;
    }
  } catch {
    if (fallback) return fallback;
  }

  return raw;
}

const supabaseUrl = resolveSupabaseUrl();

if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error('Missing Supabase env: set VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY');
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey);

export async function getAccessToken(): Promise<string | null> {
  const { data, error } = await supabase.auth.getSession();
  if (error) return null;
  return data.session?.access_token || null;
}

export async function getUserId(): Promise<string | null> {
  const { data, error } = await supabase.auth.getSession();
  if (error) return null;
  return data.session?.user?.id || null;
}

function buildSafeNextPath(): string {
  const url = new URL(window.location.href);
  const candidate = `${url.pathname}${url.search}`;
  if (!candidate.startsWith('/') || candidate.includes('://') || candidate.startsWith('//')) return '/';
  return candidate;
}

export async function requireSession(nextPath: string = buildSafeNextPath()): Promise<void> {
  const { data, error } = await supabase.auth.getSession();
  if (!error && data.session) return;

  const next = nextPath.startsWith('/') ? nextPath : '/';
  window.location.href = `/login?next=${encodeURIComponent(next)}`;
}

export async function apiFetch(input: RequestInfo | URL, init: RequestInit = {}): Promise<Response> {
  const headers = new Headers(init.headers || {});
  const token = await getAccessToken();
  if (!token) {
    await requireSession();
    throw new Error('Not authenticated');
  }
  headers.set('Authorization', `Bearer ${token}`);

  const maxRetries = 3;
  let lastError: any;
  
  for (let i = 0; i < maxRetries; i++) {
    try {
      const res = await fetch(input, { ...init, headers });
      if (res.ok || (res.status < 500 && res.status !== 429)) {
        return res;
      }
    } catch (e) {
      lastError = e;
    }

    if (i < maxRetries - 1) {
      await new Promise(r => setTimeout(r, 1000 * Math.pow(2, i)));
    }
  }

  throw lastError || new Error('Fetch failed after retries');
}

export async function retrySupabase<T>(
  operation: () => Promise<{ data: T | null; error: any }>,
  maxRetries = 3
): Promise<{ data: T | null; error: any }> {
  let result: { data: T | null; error: any } = { data: null, error: null };
  
  for (let i = 0; i < maxRetries; i++) {
    try {
      result = await operation();
      if (!result.error) return result;
      
      const status = result.error?.status || result.error?.code;
      const isRetryable = 
        !status ||
        (typeof status === 'number' && (status >= 500 || status === 429)) ||
        (typeof status === 'string' && (status.startsWith('5') || status === '429'));

      if (!isRetryable) {
        return result;
      }
    } catch (e) {
      result = { data: null, error: e };
    }
    
    if (i < maxRetries - 1) {
      await new Promise(r => setTimeout(r, 1000 * Math.pow(2, i)));
    }
  }
  return result;
}

export function formatSupabaseError(err: any): string {
  const code = err?.code ? String(err.code) : '';
  const message = err?.message ? String(err.message) : '';

  if (code === 'PGRST205') {
    return 'Supabase 未找到表 public.user_images，请在 Supabase Studio 执行 infra/supabase/schema.sql 后刷新';
  }

  if (message.includes('No API key found in request')) {
    return 'Supabase 请求缺少 apikey：请确认 VITE_SUPABASE_ANON_KEY 与 VITE_SUPABASE_URL 配置正确，并重新构建前端';
  }

  return message?.trim() || '请求失败，请稍后重试';
}
