export function getCookie(name: string, cookieString?: string): string | null {
  const source = typeof cookieString === 'string' ? cookieString : document.cookie || '';
  const value = `; ${source}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop()!.split(';').shift() || null;
  return null;
}

export function csrfHeaders(): Record<string, string> {
  const token = getCookie('csrf_token');
  return token ? { 'X-CSRF-Token': token } : {};
}

