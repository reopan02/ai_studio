export async function readErrorText(res: Response): Promise<string> {
  const text = await res.text();
  try {
    const data = JSON.parse(text);
    return String(data?.detail || data?.error || data?.message || text);
  } catch {
    return text || `HTTP ${res.status}`;
  }
}

