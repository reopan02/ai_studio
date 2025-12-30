export type CurrentUser = {
  id: string;
  username: string;
  email: string;
  is_admin: boolean;
};

export async function getCurrentUser(): Promise<CurrentUser | null> {
  const res = await fetch('/api/v1/auth/me', { credentials: 'include' });
  if (!res.ok) return null;
  return (await res.json()) as CurrentUser;
}

