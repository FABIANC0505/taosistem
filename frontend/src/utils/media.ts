export const resolveMediaUrl = (url?: string) => {
  if (!url) return '';
  if (url.startsWith('http://') || url.startsWith('https://')) return url;
  if (url.startsWith('/img/')) return url;
  const base = String(import.meta.env.VITE_API_URL || 'http://localhost:8000').trim();
  return `${base}${url}`;
};
