export function safeNextPath(): string {
  const url = new URL(window.location.href);
  const next = url.searchParams.get('next') || '/';
  if (!next.startsWith('/') || next.includes('://') || next.startsWith('//')) return '/';
  return next;
}

